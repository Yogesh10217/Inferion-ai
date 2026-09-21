"""Unit tests for Python SDK IntelligenceClient."""

from unittest.mock import MagicMock

from sdk.python.llm_engine.intelligence import IntelligenceClient


def test_python_sdk_intelligence_client():
    mock_http = MagicMock()
    mock_http.post.return_value = {"signal_id": "sig_100"}
    mock_http.get.return_value = [{"insight_id": "ins_100"}]

    client = IntelligenceClient(mock_http)
    sig = client.ingest_signal("OPERATIONS", "METRIC_THRESHOLD", "Message", "t1")
    assert sig["signal_id"] == "sig_100"

    insights = client.list_insights("t1")
    assert len(insights) == 1
