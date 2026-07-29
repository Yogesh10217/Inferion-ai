from typing import Dict, Any, Optional
from .tracer import get_tracer, Span
from .trace_attributes import TraceAttributes


class SpanFactory:
    """Helper factory generating structured child spans across subsystem boundaries."""

    @staticmethod
    def _tracer():
        return get_tracer("factory")

    @classmethod
    def create_routing_span(cls, model_id: str, organization_id: Optional[str] = None) -> Span:
        span = cls._tracer().start_span("routing.decision")
        span.set_attribute(TraceAttributes.COMPONENT, "routing")
        span.set_attribute(TraceAttributes.LLM_MODEL, model_id)
        if organization_id:
            span.set_attribute(TraceAttributes.ORG_ID, organization_id)
        return span

    @classmethod
    def create_inference_span(cls, provider: str, model: str) -> Span:
        span = cls._tracer().start_span("inference.execution")
        span.set_attribute(TraceAttributes.COMPONENT, "inference")
        span.set_attribute(TraceAttributes.LLM_PROVIDER, provider)
        span.set_attribute(TraceAttributes.LLM_MODEL, model)
        return span

    @classmethod
    def create_plugin_span(cls, plugin_id: str, hook: str) -> Span:
        span = cls._tracer().start_span(f"plugin.execution.{plugin_id}")
        span.set_attribute(TraceAttributes.COMPONENT, "plugin")
        span.set_attribute(TraceAttributes.PLUGIN_ID, plugin_id)
        span.set_attribute(TraceAttributes.PLUGIN_HOOK, hook)
        return span

    @classmethod
    def create_storage_span(cls, operation: str, bucket: str) -> Span:
        span = cls._tracer().start_span(f"storage.{operation}")
        span.set_attribute(TraceAttributes.COMPONENT, "storage")
        span.set_attribute("storage.bucket", bucket)
        return span

    @classmethod
    def create_database_span(cls, query_type: str, table: str) -> Span:
        span = cls._tracer().start_span(f"db.{query_type}")
        span.set_attribute(TraceAttributes.COMPONENT, "database")
        span.set_attribute("db.sql.table", table)
        return span

    @classmethod
    def create_scheduler_span(cls, job_id: str) -> Span:
        span = cls._tracer().start_span(f"scheduler.job.{job_id}")
        span.set_attribute(TraceAttributes.COMPONENT, "scheduler")
        span.set_attribute("scheduler.job_id", job_id)
        return span

    @classmethod
    def create_webhook_span(cls, target_url: str) -> Span:
        span = cls._tracer().start_span("webhook.dispatch")
        span.set_attribute(TraceAttributes.COMPONENT, "webhook")
        span.set_attribute(TraceAttributes.HTTP_URL, target_url)
        return span

    @classmethod
    def create_background_job_span(cls, job_name: str) -> Span:
        span = cls._tracer().start_span(f"background_task.{job_name}")
        span.set_attribute(TraceAttributes.COMPONENT, "background_job")
        return span
