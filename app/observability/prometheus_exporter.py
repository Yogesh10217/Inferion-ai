from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.observability.metrics_mapper import MetricsMapper


class PrometheusExporter:
    """Exports Prometheus metrics via the text format."""

    def __init__(self, mapper: MetricsMapper):
        self.mapper = mapper

    def export(self) -> tuple[bytes, str]:
        """Synchronizes metrics and returns (encoded_payload, content_type)."""
        self.mapper.synchronize()
        payload = generate_latest(self.mapper.registry.registry)
        return payload, CONTENT_TYPE_LATEST
