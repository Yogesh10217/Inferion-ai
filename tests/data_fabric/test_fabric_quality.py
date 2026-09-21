"""Unit tests for DataQualityEngine."""

from app.data_fabric.quality import DataQualityEngine


def test_data_quality_evaluation():
    engine = DataQualityEngine()

    records = [
        {"id": "1", "name": "Alice", "email": "alice@acme.com"},
        {"id": "2", "name": "Bob", "email": None},
        {"id": "2", "name": "Bob Duplicate", "email": "bob@acme.com"},
    ]

    result = engine.evaluate_quality(asset_id="asset_test", records=records)

    assert result.overall_score > 0.0
    assert len(result.warnings) > 0  # Duplicate record warning
