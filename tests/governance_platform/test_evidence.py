"""Unit tests for EvidenceCollector collection and indexing."""

import pytest
from app.governance_platform.evidence import EvidenceCollector, EvidenceSource


def test_evidence_collection():
    collector = EvidenceCollector()
    evd = collector.collect_evidence(
        source_system=EvidenceSource.AUDIT_LOG,
        source_record_id="rec_100",
        resource_id="db_main",
        payload={"action": "POLICY_UPDATE", "actor": "admin"},
        tenant_id="t_evd",
    )

    assert evd.source_system == EvidenceSource.AUDIT_LOG
    assert evd.resource_id == "db_main"
    assert evd.content_hash != ""
