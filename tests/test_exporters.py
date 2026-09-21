from app.tracing.exporter import (
    BatchSpanProcessor,
    ConsoleExporter,
    ExporterRegistry,
    OTLPHTTPExporter,
)


def test_exporter_registry():
    registry = ExporterRegistry()
    assert "console" in registry.list_exporters()
    assert "otlp_http" in registry.list_exporters()

    registry.set_active("otlp_http")
    assert isinstance(registry.get_active(), OTLPHTTPExporter)


def test_batch_span_processor():
    exporter = ConsoleExporter()
    processor = BatchSpanProcessor(exporter, schedule_delay_sec=0.1)
    assert processor._running is True
    processor.shutdown()
    assert processor._running is False
