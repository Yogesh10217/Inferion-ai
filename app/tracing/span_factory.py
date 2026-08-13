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

    @classmethod
    def create_workflow_start_span(cls, workflow_id: str, run_id: str) -> Span:
        span = cls._tracer().start_span("workflow.start")
        span.set_attribute(TraceAttributes.COMPONENT, "workflow")
        span.set_attribute("workflow.id", workflow_id)
        span.set_attribute("workflow.run_id", run_id)
        return span

    @classmethod
    def create_workflow_node_span(cls, workflow_id: str, run_id: str, node_id: str, node_type: str) -> Span:
        span = cls._tracer().start_span("workflow.node")
        span.set_attribute(TraceAttributes.COMPONENT, "workflow")
        span.set_attribute("workflow.id", workflow_id)
        span.set_attribute("workflow.run_id", run_id)
        span.set_attribute("workflow.node_id", node_id)
        span.set_attribute("workflow.node_type", node_type)
        return span

    @classmethod
    def create_workflow_approval_span(cls, workflow_id: str, run_id: str, node_id: str) -> Span:
        span = cls._tracer().start_span("workflow.approval")
        span.set_attribute(TraceAttributes.COMPONENT, "workflow")
        span.set_attribute("workflow.id", workflow_id)
        span.set_attribute("workflow.run_id", run_id)
        span.set_attribute("workflow.node_id", node_id)
        return span

    @classmethod
    def create_memory_store_span(cls, memory_id: str, memory_type: str) -> Span:
        span = cls._tracer().start_span("memory.store")
        span.set_attribute(TraceAttributes.COMPONENT, "memory")
        span.set_attribute("memory.id", memory_id)
        span.set_attribute("memory.type", memory_type)
        return span

    @classmethod
    def create_memory_retrieve_span(cls, query: str) -> Span:
        span = cls._tracer().start_span("memory.retrieve")
        span.set_attribute(TraceAttributes.COMPONENT, "memory")
        span.set_attribute("memory.query", query)
        return span

    @classmethod
    def create_memory_search_span(cls, query: str) -> Span:
        span = cls._tracer().start_span("memory.search")
        span.set_attribute(TraceAttributes.COMPONENT, "memory")
        span.set_attribute("memory.query", query)
        return span

    @classmethod
    def create_memory_compress_span(cls, session_id: str) -> Span:
        span = cls._tracer().start_span("memory.compress")
        span.set_attribute(TraceAttributes.COMPONENT, "memory")
        span.set_attribute("memory.session_id", session_id)
        return span

    @classmethod
    def create_memory_summarize_span(cls, text_len: int) -> Span:
        span = cls._tracer().start_span("memory.summarize")
        span.set_attribute(TraceAttributes.COMPONENT, "memory")
        span.set_attribute("memory.text_length", text_len)
        return span

    @classmethod
    def create_memory_embed_span(cls, text: str) -> Span:
        span = cls._tracer().start_span("memory.embed")
        span.set_attribute(TraceAttributes.COMPONENT, "memory")
        span.set_attribute("memory.text", text)
        return span

    @classmethod
    def create_memory_archive_span(cls, memory_id: str) -> Span:
        span = cls._tracer().start_span("memory.archive")
        span.set_attribute(TraceAttributes.COMPONENT, "memory")
        span.set_attribute("memory.id", memory_id)
        return span

    @classmethod
    def create_memory_expire_span(cls, count: int) -> Span:
        span = cls._tracer().start_span("memory.expire")
        span.set_attribute(TraceAttributes.COMPONENT, "memory")
        span.set_attribute("memory.count", count)
        return span
