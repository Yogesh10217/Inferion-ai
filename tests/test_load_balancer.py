import asyncio

import pytest

from app.routing.failover_policy import FailoverPolicy
from app.routing.load_balancer import LoadBalancer
from app.routing.load_balancing_policy import (
    LeastConnectionsPolicy,
    RoundRobinPolicy,
    WeightedRoundRobinPolicy,
)
from app.routing.provider_health import ProviderHealthMonitor
from app.routing.provider_pool import ProviderInstance, ProviderPool


class DummyProvider:
    def __init__(self, name: str):
        self.name = name


@pytest.fixture
def provider_pool():
    pool = ProviderPool()
    # Create 3 instances for provider "test_provider"
    pool.register_instance(
        ProviderInstance(provider_id="test_provider", instance_id="inst_1", provider=DummyProvider("inst_1"), weight=1)
    )
    pool.register_instance(
        ProviderInstance(provider_id="test_provider", instance_id="inst_2", provider=DummyProvider("inst_2"), weight=2)
    )
    pool.register_instance(
        ProviderInstance(provider_id="test_provider", instance_id="inst_3", provider=DummyProvider("inst_3"), weight=1)
    )
    return pool


def test_round_robin_policy(provider_pool):
    policy = RoundRobinPolicy()
    lb = LoadBalancer(provider_pool, policy)

    # Order should be inst_1, inst_2, inst_3, inst_1...
    inst1 = lb.get_instance("test_provider")
    assert inst1.instance_id == "inst_1"

    inst2 = lb.get_instance("test_provider")
    assert inst2.instance_id == "inst_2"

    inst3 = lb.get_instance("test_provider")
    assert inst3.instance_id == "inst_3"

    inst4 = lb.get_instance("test_provider")
    assert inst4.instance_id == "inst_1"


def test_weighted_round_robin_policy(provider_pool):
    policy = WeightedRoundRobinPolicy()
    lb = LoadBalancer(provider_pool, policy)

    # Flattened list: inst_1, inst_2, inst_2, inst_3
    expected_order = ["inst_1", "inst_2", "inst_2", "inst_3", "inst_1"]

    for expected in expected_order:
        inst = lb.get_instance("test_provider")
        assert inst.instance_id == expected


@pytest.mark.asyncio
async def test_least_connections_policy(provider_pool):
    policy = LeastConnectionsPolicy()
    lb = LoadBalancer(provider_pool, policy)

    instances = provider_pool.get_instances("test_provider")
    # Simulate active requests
    await instances[0].health.record_active()  # inst_1 has 1
    await instances[0].health.record_active()  # inst_1 has 2

    await instances[1].health.record_active()  # inst_2 has 1

    # inst_3 has 0

    # Should pick inst_3
    selected = lb.get_instance("test_provider")
    assert selected.instance_id == "inst_3"


@pytest.mark.asyncio
async def test_failover_policy_success():
    pool = ProviderPool()
    instance = ProviderInstance("test", "1", DummyProvider("1"))
    pool.register_instance(instance)

    lb = LoadBalancer(pool, RoundRobinPolicy())
    failover = FailoverPolicy(lb, max_retries=2)

    async def mock_execute(inst):
        return "success"

    result = await failover.execute_with_failover("test", mock_execute)
    assert result == "success"
    assert instance.health._consecutive_successes == 1


@pytest.mark.asyncio
async def test_failover_policy_retry_then_success(provider_pool):
    lb = LoadBalancer(provider_pool, RoundRobinPolicy())
    failover = FailoverPolicy(lb, max_retries=2)

    attempts = []

    async def mock_execute(inst):
        attempts.append(inst.instance_id)
        if len(attempts) < 2:
            raise ValueError("Simulated network failure")
        return "success"

    result = await failover.execute_with_failover("test_provider", mock_execute)

    assert result == "success"
    assert len(attempts) == 2
    assert attempts[0] == "inst_1"
    assert attempts[1] == "inst_2"

    # Check health states
    instances = provider_pool.get_instances("test_provider")
    assert instances[0].health._consecutive_failures == 1
    assert instances[1].health._consecutive_successes == 1


@pytest.mark.asyncio
async def test_failover_policy_exhausted(provider_pool):
    lb = LoadBalancer(provider_pool, RoundRobinPolicy())
    failover = FailoverPolicy(lb, max_retries=2)

    async def mock_execute(inst):
        raise ValueError("Simulated network failure")

    with pytest.raises(ValueError, match="Simulated network failure"):
        await failover.execute_with_failover("test_provider", mock_execute)

    # Check all 3 got hit and failed
    instances = provider_pool.get_instances("test_provider")
    for inst in instances:
        assert inst.health._consecutive_failures == 1


@pytest.mark.asyncio
async def test_health_state_transitions():
    health = ProviderHealthMonitor(failure_threshold=3, recovery_time_s=0.1)

    assert health.is_healthy()

    await health.record_failure()
    await health.record_failure()
    assert health.is_healthy()  # Still under threshold

    await health.record_failure()
    assert not health.is_healthy()  # Reached threshold

    # Wait for recovery
    await asyncio.sleep(0.15)

    assert health.is_healthy()  # Cooldown expired

    # A single success should reset failures
    await health.record_success(latency_ms=10)
    assert health._consecutive_failures == 0
    assert health.is_healthy()
