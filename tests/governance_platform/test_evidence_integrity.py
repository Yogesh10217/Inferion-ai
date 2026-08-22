"""Unit tests for immutable evidence content hashing and previous hash chaining."""

import pytest
from app.governance_platform.evidence import EvidenceCollector, EvidenceSource


def test_evidence_hashing_and_chaining():
    collector = EvidenceCollector()

    e1 = collector.collect_evidence(EvidenceSource.DEPLOYMENT, "dep_1", "res_1", {"status": "SUCCESS"}, tenant_id="t_hash")
    e2 = collector.collect_evidence(EvidenceSource.APPROVAL, "appr_1", "res_1", {"status": "APPROVED"}, tenant_id="t_hash")

    assert e1.previous_hash is None
    assert e2.previous_hash == e1.content_hash
