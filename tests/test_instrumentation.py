import pytest
from app.tracing.instrumentation import AutoInstrumentor


def test_auto_instrumentor():
    AutoInstrumentor.instrument_all()
    # Ensure no exception is thrown during instrumentation setup
    assert True
