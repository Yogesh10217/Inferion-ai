"""Pytest Suite for Kubernetes Helm Chart Validation & HA Cluster Failover."""

import os

import yaml

from deploy.scripts.dr.pg_redis_failover import HAFailoverOrchestrator
from scripts.validate_helm_k8s import validate_helm_chart


def test_helm_chart_validation():
    chart_dir = os.path.abspath("deploy/helm/llm-engine")
    assert validate_helm_chart(chart_dir) is True


def test_helm_values_yaml_structure():
    values_path = os.path.abspath("deploy/helm/llm-engine/values.yaml")
    assert os.path.exists(values_path)

    with open(values_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["replicaCount"] == 3
    assert data["autoscaling"]["enabled"] is True
    assert data["autoscaling"]["minReplicas"] == 3
    assert data["highAvailability"]["postgresql"]["mode"] == "ha_cluster"
    assert data["highAvailability"]["redis"]["mode"] == "sentinel"
    assert data["env"]["SECRET_MANAGER_BACKEND"] == "vault"


def test_pg_cluster_failover_orchestrator():
    orchestrator = HAFailoverOrchestrator(
        pg_primary="pg-primary-01",
        pg_replicas=["pg-replica-01", "pg-replica-02"],
        redis_sentinels=["redis-sentinel-01:26379", "redis-sentinel-02:26379"],
    )

    health = orchestrator.check_pg_cluster_health()
    assert health["primary"]["status"] == "HEALTHY"

    res = orchestrator.trigger_pg_failover()
    assert res["status"] == "COMPLETED"
    assert res["previous_primary"] == "pg-primary-01"
    assert res["new_primary"] == "pg-replica-01"
    assert orchestrator.active_primary == "pg-replica-01"


def test_redis_sentinel_failover_orchestrator():
    orchestrator = HAFailoverOrchestrator(
        pg_primary="pg-primary-01",
        pg_replicas=["pg-replica-01"],
        redis_sentinels=["redis-sentinel-01:26379", "redis-sentinel-02:26379"],
    )

    health = orchestrator.check_redis_sentinel_health()
    assert health["quorum_size"] == 3

    res = orchestrator.trigger_redis_failover()
    assert res["status"] == "COMPLETED"
    assert res["previous_master"] == "redis-master-01"
    assert res["new_master"] == "redis-master-02"
