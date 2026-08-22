"""Unit tests for DataNormalizer."""

import pytest
from app.data_fabric.normalization import DataNormalizer, DataTransformation


def test_normalization_and_transformations():
    normalizer = DataNormalizer()
    raw = {"user_email": "jane@acme.com", "user_age": 30, "user_role": "admin"}

    transformation = DataTransformation(
        name="Rename fields",
        field_mapping={"email": "user_email", "role": "user_role"},
    )

    rec = normalizer.normalize_record(
        raw_data=raw,
        source_id="ds_1",
        source_record_id="usr_10",
        tenant_id="tenant_x",
        transformation=transformation,
    )

    assert rec.tenant_id == "tenant_x"
    assert rec.payload["email"] == "jane@acme.com"
    assert rec.payload["role"] == "admin"
    assert "user_age" not in rec.payload
