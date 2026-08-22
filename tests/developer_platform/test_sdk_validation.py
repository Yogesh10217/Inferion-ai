"""Unit tests for SDKConsistencyValidator."""

import pytest
from app.developer_platform.sdk_validation import SDKConsistencyValidator


def test_sdk_contract_validation():
    validator = SDKConsistencyValidator()
    implemented = [
        "projects", "extensions", "install", "enable", "disable",
        "upgrade", "rollback", "items", "submit", "approve",
        "publish", "subscriptions",
    ]

    report = validator.validate_sdk_contract("Python", implemented)
    assert report.is_compliant is True
    assert len(report.missing_endpoints) == 0
