import json
import os

OUT_DIR = "monitoring/grafana/dashboards"
os.makedirs(OUT_DIR, exist_ok=True)

# Common Dashboard config wrapper
def wrap_dashboard(title, panels, uid=None):
    return {
        "title": title,
        "uid": uid or title.lower().replace(" ", "-"),
        "timezone": "browser",
        "schemaVersion": 39,
        "refresh": "5s",
        "panels": panels,
        "templating": {
            "list": [
                {
                    "name": "provider",
                    "type": "query",
                    "datasource": "Prometheus",
                    "query": "label_values(llm_engine_inference_provider_requests_total, provider_id)",
                    "refresh": 1,
                    "includeAll": True,
                    "allValue": ".*"
                },
                {
                    "name": "instance",
                    "type": "query",
                    "datasource": "Prometheus",
                    "query": "label_values(llm_engine_inference_provider_requests_total{provider_id=~\"$provider\"}, instance_id)",
                    "refresh": 1,
                    "includeAll": True,
                    "allValue": ".*"
                }
            ]
        }
    }

def create_panel(id, title, expr, type="timeseries", x=0, y=0, w=12, h=8, format="short"):
    return {
        "id": id,
        "title": title,
        "type": type,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{"expr": expr, "refId": "A"}],
        "fieldConfig": {
            "defaults": {
                "unit": format
            }
        }
    }

# 1. System Overview
system_panels = [
    create_panel(1, "Total Requests (Rate)", "rate(llm_engine_inference_api_requests_total[1m])", x=0, y=0, w=12, format="reqps"),
    create_panel(2, "Error Rate", "rate(llm_engine_inference_api_errors_total[1m]) / rate(llm_engine_inference_api_requests_total[1m])", x=12, y=0, w=12, format="percentunit"),
    create_panel(3, "Active Requests", "llm_engine_inference_active_requests", type="stat", x=0, y=8, w=8, format="short"),
    create_panel(4, "Uptime", "llm_engine_inference_uptime_seconds", type="stat", x=8, y=8, w=8, format="s"),
    create_panel(5, "Build / Version", "llm_engine_inference_app_info", type="stat", x=16, y=8, w=8, format="none")
]
with open(f"{OUT_DIR}/system-overview.json", "w") as f:
    json.dump(wrap_dashboard("System Overview", system_panels), f, indent=2)

# 2. Scheduler Dashboard
scheduler_panels = [
    create_panel(1, "Queue Depth", "llm_engine_inference_scheduler_queue_depth", x=0, y=0),
    create_panel(2, "Scheduler Throughput", "rate(llm_engine_inference_scheduler_processed_total[1m])", x=12, y=0),
    create_panel(3, "Queue Wait Duration (95th)", "histogram_quantile(0.95, sum(rate(llm_engine_inference_scheduler_wait_duration_seconds_bucket[1m])) by (le))", x=0, y=8, format="s")
]
with open(f"{OUT_DIR}/scheduler.json", "w") as f:
    json.dump(wrap_dashboard("Scheduler", scheduler_panels), f, indent=2)

# 3. Batching Dashboard
batching_panels = [
    create_panel(1, "Active Batches", "llm_engine_inference_batching_active_batches", x=0, y=0),
    create_panel(2, "Largest Batch", "llm_engine_inference_batching_largest_batch", x=12, y=0),
    create_panel(3, "Dispatch Delay (95th)", "histogram_quantile(0.95, sum(rate(llm_engine_inference_batching_dispatch_delay_seconds_bucket[1m])) by (le))", x=0, y=8, format="s"),
    create_panel(4, "Total Batches Dispatched", "rate(llm_engine_inference_batching_batches_dispatched_total[1m])", x=12, y=8)
]
with open(f"{OUT_DIR}/batching.json", "w") as f:
    json.dump(wrap_dashboard("Batching", batching_panels), f, indent=2)

# 4. Provider Dashboard
provider_panels = [
    create_panel(1, "Requests per Provider", "rate(llm_engine_inference_provider_requests_total{provider_id=~\"$provider\", instance_id=~\"$instance\"}[1m])", x=0, y=0),
    create_panel(2, "Provider Failures", "rate(llm_engine_inference_provider_failures_total{provider_id=~\"$provider\", instance_id=~\"$instance\"}[1m])", x=12, y=0),
    create_panel(3, "Provider Latency (95th)", "histogram_quantile(0.95, sum by(le, provider_id) (rate(llm_engine_inference_provider_latency_seconds_bucket{provider_id=~\"$provider\"}[1m])))", x=0, y=8, format="s"),
    create_panel(4, "Active/Healthy Instances", "llm_engine_inference_provider_active_instances{provider_id=~\"$provider\"}", type="stat", x=12, y=8)
]
with open(f"{OUT_DIR}/provider.json", "w") as f:
    json.dump(wrap_dashboard("Provider", provider_panels), f, indent=2)

# 5. Cache Dashboard
cache_panels = [
    create_panel(1, "Cache Lookups (Hits vs Misses)", "rate(llm_engine_inference_cache_lookups_total[1m])", x=0, y=0),
    create_panel(2, "Cache Hit Ratio", "record:llm_engine_inference_cache_hit_ratio", x=12, y=0, format="percentunit"),
    create_panel(3, "Cache Writes", "rate(llm_engine_inference_cache_writes_total[1m])", x=0, y=8),
    create_panel(4, "Cache Evictions", "rate(llm_engine_inference_cache_evictions_total[1m])", x=12, y=8),
    create_panel(5, "Cache Lookup Latency (95th)", "histogram_quantile(0.95, sum(rate(llm_engine_inference_cache_lookup_latency_seconds_bucket[1m])) by (le))", x=0, y=16, format="s")
]
with open(f"{OUT_DIR}/cache.json", "w") as f:
    json.dump(wrap_dashboard("Cache", cache_panels), f, indent=2)

# 6. Streaming Dashboard
streaming_panels = [
    # Currently streaming metrics are not deeply instrumented in MetricsService but we can use api requests rate vs non-streaming as placeholder if we don't have active_streams
    # Wait, the prompt says display active streams, stream duration, throughput, completed streams.
    # The MetricsService doesn't have active streams tracked. I must not modify MetricsService!
    # I'll add panels that use existing API metrics filtered by streaming if possible, otherwise placeholder queries.
    create_panel(1, "Placeholder for Streaming (Requires additional MetricsService instrumentation in future)", "up", x=0, y=0)
]
with open(f"{OUT_DIR}/streaming.json", "w") as f:
    json.dump(wrap_dashboard("Streaming", streaming_panels), f, indent=2)

print("Dashboards generated successfully.")
