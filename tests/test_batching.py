import asyncio
import time
from unittest.mock import AsyncMock

import pytest

from app.schemas.request import InferenceRequest
from app.services.batching.batch_config import BatchConfig
from app.services.batching.batch_policy import BatchPolicy
from app.services.batching.batch_executor import BatchExecutor
from app.services.batching.batch_collector import BatchCollector
from app.services.metrics_service import MetricsService
from app.services.request_scheduler import QueueEntry


@pytest.fixture
def mock_router():
    router = AsyncMock()
    provider = AsyncMock()
    provider.generate.return_value = type("Response", (), {"text": "mocked", "model": "test-model"})()
    provider.name = "mock-provider"
    router.route.return_value = provider
    return router


@pytest.fixture
def metrics_service():
    return MetricsService()


@pytest.fixture
def batch_config():
    return BatchConfig(enabled=True, max_batch_size=2, max_batch_wait_ms=100)


@pytest.mark.asyncio
async def test_batch_collector_groups_by_batch_key(mock_router, metrics_service, batch_config):
    policy = BatchPolicy(config=batch_config)
    executor = BatchExecutor(router=mock_router, metrics=metrics_service)
    
    # Mock the execute_batch to track the batches executed
    executed_batches = []
    async def mock_execute(batch):
        executed_batches.append(batch)
        for entry in batch.entries:
            entry.result_future.set_result(type("Response", (), {"text": "mocked", "model": batch.key.model_id})())
            
    executor.execute_batch = AsyncMock(side_effect=mock_execute)
    
    collector = BatchCollector(policy=policy, executor=executor, router=mock_router, metrics=metrics_service)
    
    req1 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "1"}])
    req2 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "2"}])
    
    entry1 = QueueEntry(request=req1, is_streaming=False)
    entry2 = QueueEntry(request=req2, is_streaming=False)
    
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
async def test_batch_collector_timeout_dispatch(mock_router, metrics_service, batch_config):
    policy = BatchPolicy(config=batch_config)
    executor = BatchExecutor(router=mock_router, metrics=metrics_service)
    
    executed_batches = []
    async def mock_execute(batch):
        executed_batches.append(batch)
        for entry in batch.entries:
            entry.result_future.set_result(type("Response", (), {"text": "mocked"})())
            
    executor.execute_batch = AsyncMock(side_effect=mock_execute)
    collector = BatchCollector(policy=policy, executor=executor, router=mock_router, metrics=metrics_service)
    
    req1 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "1"}])
    entry1 = QueueEntry(request=req1, is_streaming=False)
    
    await collector.add_entry(entry1)
    
    # Before timeout, shouldn't be executed
    await asyncio.sleep(0.01)
    assert len(executed_batches) == 0
    
    # Wait past timeout (max_batch_wait_ms = 100)
    await asyncio.sleep(0.15)
    
    assert len(executed_batches) == 1
    assert executed_batches[0].size() == 1
    
    await collector.shutdown()


@pytest.mark.asyncio
async def test_batch_collector_respects_policy_batchability(mock_router, metrics_service, batch_config):
    policy = BatchPolicy(config=batch_config)
    executor = BatchExecutor(router=mock_router, metrics=metrics_service)
    
    executed_batches = []
    async def mock_execute(batch):
        executed_batches.append(batch)
        for entry in batch.entries:
            # We don't need to resolve the streams here, just check grouping
            pass
            
    executor.execute_batch = AsyncMock(side_effect=mock_execute)
    collector = BatchCollector(policy=policy, executor=executor, router=mock_router, metrics=metrics_service)
    
    # Streaming requests should not be batched together according to our policy
    req1 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "1"}], stream=True)
    req2 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "2"}], stream=True)
    
    entry1 = QueueEntry(request=req1, is_streaming=True)
    entry2 = QueueEntry(request=req2, is_streaming=True)
    
    await collector.add_entry(entry1)
    await collector.add_entry(entry2)
    
    await asyncio.sleep(0.01)
    
    # Both should be dispatched immediately in separate single-item batches
    assert len(executed_batches) == 2
    assert executed_batches[0].size() == 1
    assert executed_batches[1].size() == 1
    
    await collector.shutdown()


@pytest.mark.asyncio
async def test_batch_executor_sequencing(mock_router, metrics_service):
    executor = BatchExecutor(router=mock_router, metrics=metrics_service)
    
    execution_order = []
    async def mock_generate(*args, **kwargs):
        req = kwargs.get("request")
        execution_order.append(req.messages[0].content)
        return type("Response", (), {"text": "mocked", "model": req.model})()
        
    mock_router.route.return_value.generate.side_effect = mock_generate
    
    from app.services.batching.batch_entry import Batch, BatchKey
    batch = Batch(key=BatchKey(provider_id="mock-provider", model_id="model-1", stream=False))
    
    req1 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "A"}])
    req2 = InferenceRequest(model="model-1", messages=[{"role": "user", "content": "B"}])
    
    entry1 = QueueEntry(request=req1, is_streaming=False)
    entry2 = QueueEntry(request=req2, is_streaming=False)
    
    batch.add_entry(entry1)
    batch.add_entry(entry2)
    
    await executor.execute_batch(batch)
    
    assert execution_order == ["A", "B"]
    assert entry1.result_future.done()
    assert entry2.result_future.done()
