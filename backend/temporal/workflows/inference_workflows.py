import asyncio
import dataclasses
from datetime import timedelta
from enum import Enum

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker


# ──────────────────────────────────────────────────────────────────────────────
# Data Classes & Enums
# ──────────────────────────────────────────────────────────────────────────────

class ModelStatus(str, Enum):
    UNLOADED = "unloaded"
    LOADING = "loading"
    WARMING_UP = "warming_up"
    READY = "ready"
    DEGRADED = "degraded"
    SWAPPING = "swapping"
    FAILED = "failed"


class ModelProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    GEMINI = "gemini"


@dataclasses.dataclass
class ModelSpec:
    """Specification for a model to load/manage."""
    model_id: str              # e.g. "llama-3.1-8b", "gpt-4o-mini"
    provider: ModelProvider
    version: str
    max_context_length: int
    config: dict               # Provider-specific config


@dataclasses.dataclass
class ModelLifecycleRequest:
    """Input to the ModelLifecycleWorkflow."""
    model_spec: ModelSpec
    action: str   # "load" | "warm_up" | "hot_swap" | "unload"
    target_model_spec: ModelSpec | None = None   # For hot_swap action


@dataclasses.dataclass
class ModelLifecycleResult:
    """Output of the ModelLifecycleWorkflow."""
    model_id: str
    status: ModelStatus
    warmup_latency_ms: float
    health_check_passed: bool
    workflow_run_id: str


@dataclasses.dataclass
class HealthCheckResult:
    """Result of a model health check."""
    model_id: str
    is_healthy: bool
    latency_ms: float
    error: str | None = None


@dataclasses.dataclass
class MetricSnapshot:
    """A snapshot of inference engine metrics."""
    timestamp: str
    total_requests: int
    active_requests: int
    queue_depth: int
    avg_latency_ms: float
    p99_latency_ms: float
    tokens_per_second: float
    error_rate: float
    models_loaded: list[str]


# ──────────────────────────────────────────────────────────────────────────────
# Activities — Model Lifecycle
# ──────────────────────────────────────────────────────────────────────────────

@activity.defn
async def load_model(spec: ModelSpec) -> bool:
    """
    Pull and load a model into the inference engine.
    For Ollama: runs `ollama pull <model>`.
    For OpenAI/Gemini: validates API connectivity and model availability.
    Returns True if the model was successfully loaded.
    """
    activity.logger.info(
        f"Loading model {spec.model_id} via provider {spec.provider}"
    )
    # TODO: Provider-specific loading logic
    # if spec.provider == ModelProvider.OLLAMA:
    #     subprocess.run(["ollama", "pull", spec.model_id], check=True)
    # elif spec.provider == ModelProvider.OPENAI:
    #     # Validate API key and model availability
    #     client = OpenAI()
    #     client.models.retrieve(spec.model_id)

    # ── STUB ──
    await asyncio.sleep(0.1)   # Simulate loading time
    return True


@activity.defn
async def warmup_model(spec: ModelSpec, num_passes: int = 3) -> float:
    """
    Run warm-up inference passes to prime the model and measure baseline latency.
    Returns the average warm-up latency in milliseconds.
    """
    activity.logger.info(
        f"Warming up model {spec.model_id} with {num_passes} passes"
    )
    import time
    latencies = []
    for i in range(num_passes):
        start = time.monotonic()
        # TODO: Send a warm-up prompt to the provider
        # response = await provider.complete("Hello", model=spec.model_id, max_tokens=5)
        await asyncio.sleep(0.05)   # STUB: simulate inference
        latencies.append((time.monotonic() - start) * 1000)
        activity.logger.info(f"Warm-up pass {i+1}: {latencies[-1]:.1f}ms")

    avg_latency = sum(latencies) / len(latencies)
    activity.logger.info(f"Warm-up complete. Avg latency: {avg_latency:.1f}ms")
    return avg_latency


@activity.defn
async def health_check_model(spec: ModelSpec) -> HealthCheckResult:
    """
    Perform a health check on a loaded model by sending a minimal inference request.
    """
    import time
    activity.logger.info(f"Health checking model {spec.model_id}")
    start = time.monotonic()
    try:
        # TODO: Send minimal inference request to provider
        await asyncio.sleep(0.02)   # STUB
        latency_ms = (time.monotonic() - start) * 1000
        return HealthCheckResult(
            model_id=spec.model_id,
            is_healthy=True,
            latency_ms=latency_ms,
        )
    except Exception as e:
        return HealthCheckResult(
            model_id=spec.model_id,
            is_healthy=False,
            latency_ms=-1.0,
            error=str(e),
        )


@activity.defn
async def hot_swap_model(
    current_spec: ModelSpec,
    new_spec: ModelSpec,
) -> bool:
    """
    Hot-swap a model version without downtime.
    Loads the new model alongside the current one, validates it,
    then atomically switches the router to the new model and unloads the old one.
    """
    activity.logger.info(
        f"Hot-swapping {current_spec.model_id} -> {new_spec.model_id}"
    )
    # TODO: Load new model without unloading current
    # TODO: Run health check on new model
    # TODO: Atomically update router to point to new model
    # TODO: Unload old model to free resources

    # ── STUB ──
    return True


@activity.defn
async def collect_metrics() -> MetricSnapshot:
    """
    Collect current inference engine metrics from the running server.
    Pushes metrics to Prometheus/OpenTelemetry.
    """
    activity.logger.info("Collecting inference engine metrics")
    # TODO: Query FastAPI metrics endpoint
    # TODO: Push to Prometheus pushgateway

    # ── STUB ──
    import random
    from datetime import datetime, timezone
    return MetricSnapshot(
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_requests=random.randint(1000, 5000),
        active_requests=random.randint(0, 50),
        queue_depth=random.randint(0, 20),
        avg_latency_ms=random.uniform(150, 400),
        p99_latency_ms=random.uniform(500, 2000),
        tokens_per_second=random.uniform(200, 600),
        error_rate=random.uniform(0.0, 0.02),
        models_loaded=["gpt-4o-mini", "llama-3.1-8b"],
    )


# ──────────────────────────────────────────────────────────────────────────────
# Workflows
# ──────────────────────────────────────────────────────────────────────────────

@workflow.defn
class ModelLifecycleWorkflow:
    """
    Temporal workflow for managing LLM model lifecycle.

    Handles:
    - Loading a new model and warming it up
    - Running health checks to confirm readiness
    - Hot-swapping to a new model version without downtime
    - Graceful model unloading

    All steps are durable — if the server restarts during a long model
    download (e.g., a 70B model), the workflow resumes from the last
    completed activity.
    """

    @workflow.run
    async def run(self, request: ModelLifecycleRequest) -> ModelLifecycleResult:
        spec = request.model_spec
        workflow.logger.info(
            f"ModelLifecycleWorkflow: action={request.action}, "
            f"model={spec.model_id}, provider={spec.provider}"
        )

        warmup_latency = 0.0
        health_check_passed = False

        if request.action == "load":
            # ── Load ──────────────────────────────────────────────────────
            loaded: bool = await workflow.execute_activity(
                load_model,
                spec,
                start_to_close_timeout=timedelta(minutes=30),  # Large models can be slow
                retry_policy=workflow.RetryPolicy(maximum_attempts=2),
            )
            if not loaded:
                return ModelLifecycleResult(
                    model_id=spec.model_id,
                    status=ModelStatus.FAILED,
                    warmup_latency_ms=0.0,
                    health_check_passed=False,
                    workflow_run_id=workflow.info().run_id,
                )

            # ── Warm up ────────────────────────────────────────────────────
            warmup_latency = await workflow.execute_activity(
                warmup_model,
                args=[spec, 3],
                start_to_close_timeout=timedelta(minutes=5),
            )

            # ── Health check ───────────────────────────────────────────────
            health: HealthCheckResult = await workflow.execute_activity(
                health_check_model,
                spec,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=workflow.RetryPolicy(maximum_attempts=3),
            )
            health_check_passed = health.is_healthy
            final_status = ModelStatus.READY if health_check_passed else ModelStatus.DEGRADED

        elif request.action == "hot_swap" and request.target_model_spec:
            # ── Hot swap ───────────────────────────────────────────────────
            swapped: bool = await workflow.execute_activity(
                hot_swap_model,
                args=[spec, request.target_model_spec],
                start_to_close_timeout=timedelta(minutes=30),
            )
            final_status = ModelStatus.READY if swapped else ModelStatus.FAILED
            health_check_passed = swapped

        else:
            workflow.logger.error(f"Unknown action: {request.action}")
            final_status = ModelStatus.FAILED

        return ModelLifecycleResult(
            model_id=spec.model_id,
            status=final_status,
            warmup_latency_ms=warmup_latency,
            health_check_passed=health_check_passed,
            workflow_run_id=workflow.info().run_id,
        )


@workflow.defn
class InferenceMonitorWorkflow:
    """
    Temporal cron workflow that periodically collects inference metrics,
    runs health checks on all loaded models, and triggers alerts if needed.

    Schedule: every 5 minutes via Temporal schedules.
    """

    @workflow.run
    async def run(self) -> MetricSnapshot:
        workflow.logger.info("InferenceMonitorWorkflow: collecting metrics snapshot")

        # ── Collect metrics ────────────────────────────────────────────────
        snapshot: MetricSnapshot = await workflow.execute_activity(
            collect_metrics,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=workflow.RetryPolicy(maximum_attempts=3),
        )

        # ── Alert if error rate too high ───────────────────────────────────
        if snapshot.error_rate > 0.05:
            workflow.logger.warning(
                f"⚠️  High error rate detected: {snapshot.error_rate:.1%} "
                f"(threshold: 5%)"
            )
            # TODO: Send alert (Slack, PagerDuty, email)

        # ── Alert if queue depth too high ──────────────────────────────────
        if snapshot.queue_depth > 100:
            workflow.logger.warning(
                f"⚠️  Queue depth too high: {snapshot.queue_depth} pending requests"
            )
            # TODO: Trigger auto-scaling or load shedding

        workflow.logger.info(
            f"Metrics: {snapshot.total_requests} total requests, "
            f"{snapshot.tokens_per_second:.0f} tok/s, "
            f"P99 latency: {snapshot.p99_latency_ms:.0f}ms, "
            f"error rate: {snapshot.error_rate:.1%}"
        )

        return snapshot


# ──────────────────────────────────────────────────────────────────────────────
# Worker Entry Point
# ──────────────────────────────────────────────────────────────────────────────

TASK_QUEUE = "inference-engine-queue"


async def run_worker():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ModelLifecycleWorkflow, InferenceMonitorWorkflow],
        activities=[
            load_model,
            warmup_model,
            health_check_model,
            hot_swap_model,
            collect_metrics,
        ],
    )
    print(f"⚡ Inference Engine Worker started — polling queue: {TASK_QUEUE}")
    await worker.run()


# ──────────────────────────────────────────────────────────────────────────────
# CLI: Register monitoring cron schedule
# ──────────────────────────────────────────────────────────────────────────────

async def setup_monitoring_schedule():
    """Register the InferenceMonitorWorkflow as a Temporal cron schedule."""
    from temporalio.client import ScheduleActionStartWorkflow, Schedule, ScheduleSpec, ScheduleIntervalSpec

    client = await Client.connect("localhost:7233")

    await client.create_schedule(
        "inference-monitor-cron",
        Schedule(
            action=ScheduleActionStartWorkflow(
                InferenceMonitorWorkflow.run,
                id="inference-monitor",
                task_queue=TASK_QUEUE,
            ),
            spec=ScheduleSpec(
                intervals=[ScheduleIntervalSpec(every=timedelta(minutes=5))],
            ),
        ),
    )
    print("✅ Monitoring cron schedule registered (every 5 minutes)")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        asyncio.run(run_worker())
    elif len(sys.argv) > 1 and sys.argv[1] == "monitor":
        asyncio.run(setup_monitoring_schedule())
    else:
        print("Usage: python inference_workflows.py [worker|monitor]")
