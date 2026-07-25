import asyncio
import time
from unittest.mock import AsyncMock

import pytest

from app.routing.request_router import RoutingDecision
from app.routing.provider_pool import ProviderInstance
from app.schemas.request import InferenceRequest
from app.services.batching.batch_config import BatchConfig
from app.services.batching.batch_policy import BatchPolicy
from app.services.batching.batch_executor import BatchExecutor
from app.services.batching.batch_collector import BatchCollector
from app.services.metrics_service import MetricsService
from app.services.request_scheduler import QueueEntry


@pytest.fixture
def mock_failover_policy():
    policy = AsyncMock()
    # execute_with_failover takes (provider_id, execute_fn)
    # We will simulate calling execute_fn immediately with a mock instance
    provider = AsyncMock()
    provider.generate.return_value = type("Response", (), {"text": "mocked", "model": "test-model"})()
    provider.name = "mock-provider"
    
    mock_instance = ProviderInstance(provider_id="mock-provider", instance_id="mock-inst", provider=provider)
    
    async def mock_execute_with_failover(provider_id, execute_fn):
        return await execute_fn(mock_instance)
        
    policy.execute_with_failover.side_effect = mock_execute_with_failover
    return policy


@pytest.fixture
def metrics_service():
    return MetricsService()


@pytest.fixture
def batch_config():
    return BatchConfig(enabled=True, max_batch_size=2, max_batch_wait_ms=100)


@pytest.mark.asyncio
async def test_batch_collector_groups_by_batch_key(mock_failover_policy, metrics_service, batch_config):
    policy = BatchPolicy(config=batch_config)
    executor = BatchExecutor(failover_policy=mock_failover_policy, metrics=metrics_service)
    
    # Mock the execute_batch to track the batches executed
    executed_batches = []
    async def mock_execute(batch):
        executed_batches.append(batch)
        for entry in batch.entries:
            entry.result_future.set_result(type("Response", (), {"text": "mocked", "model": batch.key.model_id})())
            
    executor.execute_batch = AsyncMock(side_effect=mock_execute)
    
    collector = BatchCollector(policy=policy, executor=executor, metrics=metrics_service)
    
    req1 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "1"}])
    req2 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "2"}])
    
    decision = RoutingDecision(provider_id="mock-provider", model_id="model-1")
    entry1 = QueueEntry(request=req1, decision=decision, is_streaming=False)
    entry2 = QueueEntry(request=req2, decision=decision, is_streaming=False)
    
    # Send requests. max_batch_size is 2, so the second one should trigger dispatch
    await collector.add_entry(entry1)
    await collector.add_entry(entry2)
    
    # Let event loop run the dispatch task
    await asyncio.sleep(0.01)
    
    assert len(executed_batches) == 1
    assert executed_batches[0].size() == 2
    assert executed_batches[0].key.model_id == "model-1"
    
    await collector.shutdown()


@pytest.mark.asyncio
async def test_batch_collector_timeout_dispatch(mock_failover_policy, metrics_service, batch_config):
    policy = BatchPolicy(config=batch_config)
    executor = BatchExecutor(failover_policy=mock_failover_policy, metrics=metrics_service)
    
    executed_batches = []
    async def mock_execute(batch):
        executed_batches.append(batch)
        for entry in batch.entries:
            entry.result_future.set_result(type("Response", (), {"text": "mocked"})())
            
    executor.execute_batch = AsyncMock(side_effect=mock_execute)
    collector = BatchCollector(policy=policy, executor=executor, metrics=metrics_service)
    
    req1 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "1"}])
    decision = RoutingDecision(provider_id="mock-provider", model_id="model-1")
    entry1 = QueueEntry(request=req1, decision=decision, is_streaming=False)
    
    await collector.add_entry(entry1)
    
    # Before timeout, shouldn't be executed
    await asyncio.sleep(0.01)
    assert len(executed_batches) == 0
    
    # Wait past timeout (max_batch_wait_ms = 100)
    await asyncio.sleep(0.25)
    
    assert len(executed_batches) == 1
    assert executed_batches[0].size() == 1
    
    await collector.shutdown()


@pytest.mark.asyncio
async def test_batch_collector_respects_policy_batchability(mock_failover_policy, metrics_service, batch_config):
    policy = BatchPolicy(config=batch_config)
    executor = BatchExecutor(failover_policy=mock_failover_policy, metrics=metrics_service)
    
    executed_batches = []
    async def mock_execute(batch):
        executed_batches.append(batch)
        for entry in batch.entries:
            pass
            
    executor.execute_batch = AsyncMock(side_effect=mock_execute)
    collector = BatchCollector(policy=policy, executor=executor, metrics=metrics_service)
    
    req1 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "1"}], stream=True)
    req2 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "2"}], stream=True)
    
    decision = RoutingDecision(provider_id="mock-provider", model_id="model-1")
    entry1 = QueueEntry(request=req1, decision=decision, is_streaming=True)
    entry2 = QueueEntry(request=req2, decision=decision, is_streaming=True)
    
    await collector.add_entry(entry1)
    await collector.add_entry(entry2)
    
    await asyncio.sleep(0.01)
    
    # Both should be dispatched immediately in separate single-item batches
    assert len(executed_batches) == 2
    assert executed_batches[0].size() == 1
    assert executed_batches[1].size() == 1
    
    await collector.shutdown()


@pytest.mark.asyncio
async def test_batch_executor_sequencing(mock_failover_policy, metrics_service):
    executor = BatchExecutor(failover_policy=mock_failover_policy, metrics=metrics_service)
    
    execution_order = []
    async def mock_generate(*args, **kwargs):
        req = kwargs.get("request")
        execution_order.append(req.messages[0].content)
        return type("Response", (), {"text": "mocked", "model": req.model})()
        
    # Inject custom mock_generate into the provider instance yielded by mock_failover_policy
    async def custom_execute_with_failover(provider_id, execute_fn):
        provider = AsyncMock()
        provider.generate.side_effect = mock_generate
        mock_instance = ProviderInstance(provider_id="mock-provider", instance_id="mock-inst", provider=provider)
        return await execute_fn(mock_instance)
        
    mock_failover_policy.execute_with_failover.side_effect = custom_execute_with_failover
    
    from app.services.batching.batch_entry import Batch, BatchKey
    batch = Batch(key=BatchKey(provider_id="mock-provider", model_id="model-1", stream=False))
    
    req1 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "A"}])
    req2 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "B"}])
    
    decision = RoutingDecision(provider_id="mock-provider", model_id="model-1")
    entry1 = QueueEntry(request=req1, decision=decision, is_streaming=False)
    entry2 = QueueEntry(request=req2, decision=decision, is_streaming=False)
    
    batch.add_entry(entry1)
    batch.add_entry(entry2)
    
    await executor.execute_batch(batch)
    
    assert execution_order == ["A", "B"]
    assert entry1.result_future.done()
    assert entry2.result_future.done()

