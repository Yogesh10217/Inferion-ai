import time
import queue
import threading
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class SpanExporter(ABC):
    @abstractmethod
    def export(self, spans: List[Any]) -> bool:
        pass

    @abstractmethod
    def shutdown(self):
        pass


class ConsoleExporter(SpanExporter):
    def export(self, spans: List[Any]) -> bool:
        for span in spans:
            data = span.to_dict() if hasattr(span, "to_dict") else str(span)
            print(f"[TRACE] {data}")
        return True

    def shutdown(self):
        pass


class OTLPHTTPExporter(SpanExporter):
    def __init__(self, endpoint: str = "http://localhost:4318/v1/traces"):
        self.endpoint = endpoint

    def export(self, spans: List[Any]) -> bool:
        # In a real environment, sends OTLP JSON payload via HTTP POST
        logger.info(f"OTLP/HTTP exporting {len(spans)} spans to {self.endpoint}")
        return True

    def shutdown(self):
        pass


class OTLPGRPCExporter(SpanExporter):
    def __init__(self, endpoint: str = "localhost:4317"):
        self.endpoint = endpoint

    def export(self, spans: List[Any]) -> bool:
        logger.info(f"OTLP/gRPC exporting {len(spans)} spans to {self.endpoint}")
        return True

    def shutdown(self):
        pass


class JaegerExporter(SpanExporter):
    def __init__(self, endpoint: str = "http://localhost:14268/api/traces"):
        self.endpoint = endpoint

    def export(self, spans: List[Any]) -> bool:
        logger.info(f"Jaeger exporting {len(spans)} spans to {self.endpoint}")
        return True

    def shutdown(self):
        pass


class ZipkinExporter(SpanExporter):
    def __init__(self, endpoint: str = "http://localhost:9411/api/v2/spans"):
        self.endpoint = endpoint

    def export(self, spans: List[Any]) -> bool:
        logger.info(f"Zipkin exporting {len(spans)} spans to {self.endpoint}")
        return True

    def shutdown(self):
        pass


class BatchSpanProcessor:
    """Non-blocking background worker queue processing and batching finished spans."""

    def __init__(
        self,
        exporter: SpanExporter,
        max_queue_size: int = 2048,
        batch_size: int = 512,
        export_timeout_sec: float = 5.0,
        schedule_delay_sec: float = 1.0,
    ):
        self.exporter = exporter
        self.max_queue_size = max_queue_size
        self.batch_size = batch_size
        self.export_timeout_sec = export_timeout_sec
        self.schedule_delay_sec = schedule_delay_sec

        self._queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self._running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()

    def on_end(self, span: Any):
        if not self._running:
            return
        try:
            self._queue.put_nowait(span)
        except queue.Full:
            logger.warning("Tracing BatchSpanProcessor queue full. Dropping span.")

    def _worker_loop(self):
        while self._running:
            batch = []
            try:
                # Wait for at least 1 span or timeout
                item = self._queue.get(timeout=self.schedule_delay_sec)
                batch.append(item)
                # Drain rest of available batch up to batch_size
                while len(batch) < self.batch_size:
                    try:
                        batch.append(self._queue.get_nowait())
                    except queue.Empty:
                        break
            except queue.Empty:
                pass

            if batch:
                try:
                    self.exporter.export(batch)
                except Exception as e:
                    logger.error(f"Failed exporting batch of {len(batch)} spans: {e}")

    def shutdown(self):
        self._running = False
        if self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self.exporter.shutdown()


class ExporterRegistry:
    """Runtime configuration and management of span exporters."""

    def __init__(self):
        self._exporters: Dict[str, SpanExporter] = {
            "console": ConsoleExporter(),
            "otlp_http": OTLPHTTPExporter(),
            "otlp_grpc": OTLPGRPCExporter(),
            "jaeger": JaegerExporter(),
            "zipkin": ZipkinExporter(),
        }
        self._active_name = "console"

    def register(self, name: str, exporter: SpanExporter):
        self._exporters[name] = exporter

    def set_active(self, name: str):
        if name not in self._exporters:
            raise ValueError(f"Exporter '{name}' is not registered.")
        self._active_name = name

    def get_active(self) -> SpanExporter:
        return self._exporters[self._active_name]

    def list_exporters(self) -> List[str]:
        return list(self._exporters.keys())
