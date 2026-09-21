from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ProviderUnavailableException
from app.resilience.bulkhead import BulkheadRegistry
from app.resilience.circuit_breaker import CircuitBreakerRegistry, CircuitState
from app.routing.request_router import RoutingDecision
from app.schemas.request import ChatMessage, InferenceRequest
from app.services.batching.batch_entry import Batch, BatchKey
from app.services.batching.batch_executor import BatchExecutor
from app.services.dead_letter_queue import DeadLetterQueue, DLQEntry
from app.services.request_scheduler import QueueEntry


@pytest.mark.asyncio
async def test_dead_letter_queue_operations():
    dlq = DeadLetterQueue(max_size=5)
    assert await dlq.count() == 0

    entry1 = DLQEntry(model="gpt-4o-mini", provider_id="openai", error="Timeout after 3 retries")
    await dlq.put(entry1)

    assert await dlq.count() == 1
    entries = await dlq.get_entries()
    assert entries[0].model == "gpt-4o-mini"
    assert entries[0].provider_id == "openai"

    await dlq.clear()
    assert await dlq.count() == 0


@pytest.mark.asyncio
async def test_circuit_breaker_state_transitions():
    registry = CircuitBreakerRegistry()
    cb = registry.get_breaker("openai")
    assert cb.state == CircuitState.CLOSED

    # Record failures up to threshold (default 5)
    for i in range(5):
        cb.record_failure(Exception("HTTP 503"))

    assert cb.state == CircuitState.OPEN
    assert cb.allow_request() is False

    # After recovery timeout simulate half-open
    cb.last_failure_time = 0.0  # Force timeout past
    assert cb.allow_request() is True
    assert cb.state == CircuitState.HALF_OPEN


@pytest.mark.asyncio
async def test_batch_executor_circuit_breaker_and_dlq_integration():
    failover_policy = AsyncMock()
    metrics = MagicMock()
    cb_registry = CircuitBreakerRegistry()
    bulkhead_registry = BulkheadRegistry()
    dlq = DeadLetterQueue()

    executor = BatchExecutor(
        failover_policy=failover_policy,
        metrics=metrics,
        circuit_breaker_registry=cb_registry,
        bulkhead_registry=bulkhead_registry,
        dead_letter_queue=dlq,
    )

    # Force failover_policy to raise an exception
    failover_policy.execute_with_failover.side_effect = ProviderUnavailableException("Provider completely dead")

    req = InferenceRequest(model="gpt-4o-mini", messages=[ChatMessage(role="user", content="Test")])
    decision = RoutingDecision(provider_id="openai", model_id="gpt-4o-mini")
    batch_entry = QueueEntry(request=req, decision=decision, is_streaming=False)
    batch = Batch(key=BatchKey(provider_id="openai", model_id="gpt-4o-mini", stream=False), entries=[batch_entry])

    await executor.execute_batch(batch)

    # Future should have exception
    with pytest.raises(ProviderUnavailableException):
        await batch_entry.result_future

    # DLQ should contain the failed request
    assert await dlq.count() == 1
    entries = await dlq.get_entries()
    assert entries[0].provider_id == "openai"
    assert "Provider completely dead" in entries[0].error
