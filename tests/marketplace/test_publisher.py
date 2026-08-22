"""Unit tests for PublisherManager."""

import pytest
from app.marketplace.publisher import PublisherManager
from app.marketplace.exceptions import PublisherNotFoundException


def test_publisher_registration_and_verification():
    mgr = PublisherManager()
    pub = mgr.register_publisher(
        developer_id="dev_100",
        name="Acme AI Solutions",
        email="info@acme.com",
        tenant_id="t_pub",
    )
    assert pub.verification.is_verified is False

    verified = mgr.verify_publisher(pub.publisher_id, tier="ENTERPRISE_PARTNER")
    assert verified.verification.is_verified is True
    assert verified.verification.verification_tier == "ENTERPRISE_PARTNER"
