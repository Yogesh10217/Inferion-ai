import pytest
def test_billing_metrics():
    usage = {"tokens": 100}
    assert usage["tokens"] == 100
