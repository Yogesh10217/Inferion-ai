"""Execution Replay and Debugging Subsystem."""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from app.observability.context import ObservabilityContext, get_current_context
from app.observability.exceptions import ExecutionNotFoundException, ReplayNotAvailableException
from app.observability.logging import sanitize_value

logger = logging.getLogger(__name__)


@dataclass
class ExecutionSnapshot:
    """Snapshot containing execution inputs, metadata, and deterministic configuration."""
    snapshot_id: str
    execution_id: str
    trace_id: str
    tenant_id: str
    workspace_id: str
    organization_id: str
    component: str  # agent, workflow, model, tool, etc.
    inputs: Dict[str, Any]
    config: Dict[str, Any]
    original_output: Optional[Dict[str, Any]] = None
    original_status: str = "COMPLETED"
    is_high_risk: bool = False
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Redact secrets in inputs and outputs
        d["inputs"] = sanitize_value("inputs", d["inputs"])
        if d.get("original_output"):
            d["original_output"] = sanitize_value("original_output", d["original_output"])
        return d


@dataclass
class ReplayComparison:
    """Comparison results between original execution and replayed execution."""
    execution_id: str
    replay_id: str
    matched: bool
    divergences: List[Dict[str, Any]]
    original_status: str
    replayed_status: str
    original_duration_ms: float
    replayed_duration_ms: float


class ExecutionReplayManager:
    """Manages creation, snapshot retrieval, deterministic replaying, and divergence analysis."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, ExecutionSnapshot] = {}
        self._replay_history: Dict[str, List[Dict[str, Any]]] = {}

    def create_snapshot(
        self,
        execution_id: str,
        component: str,
        inputs: Dict[str, Any],
        config: Dict[str, Any],
        original_output: Optional[Dict[str, Any]] = None,
        original_status: str = "COMPLETED",
        is_high_risk: bool = False,
        context: Optional[ObservabilityContext] = None,
    ) -> ExecutionSnapshot:
        """Capture deterministic execution state into a snapshot."""
        ctx = context or get_current_context()
        snapshot_id = f"snap-{execution_id}"

        # Redact sensitive parameters prior to storing snapshot
        sanitized_inputs = sanitize_value("inputs", inputs)
        sanitized_output = sanitize_value("output", original_output) if original_output else None

        snapshot = ExecutionSnapshot(
            snapshot_id=snapshot_id,
            execution_id=execution_id,
            trace_id=ctx.trace_id,
            tenant_id=ctx.tenant_id or "default",
            workspace_id=ctx.workspace_id or "default",
            organization_id=ctx.organization_id or "default",
            component=component,
            inputs=sanitized_inputs,
            config=config,
            original_output=sanitized_output,
            original_status=original_status,
            is_high_risk=is_high_risk,
        )

        self._snapshots[execution_id] = snapshot
        return snapshot

    def get_snapshot(
        self,
        execution_id: str,
        tenant_id: Optional[str] = None,
    ) -> ExecutionSnapshot:
        """Retrieve snapshot enforcing tenant isolation."""
        snapshot = self._snapshots.get(execution_id)
        if not snapshot:
            raise ExecutionNotFoundException(execution_id)

        if tenant_id and snapshot.tenant_id != tenant_id:
            logger.warning(f"Tenant isolation mismatch: requested {tenant_id}, snapshot belongs to {snapshot.tenant_id}")
            raise ExecutionNotFoundException(execution_id)

        return snapshot

    async def replay_execution(
        self,
        execution_id: str,
        force_external_effects: bool = False,
        tenant_id: Optional[str] = None,
        user_permissions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Replay an execution using saved deterministic config and inputs."""
        snapshot = self.get_snapshot(execution_id, tenant_id=tenant_id)

        # Enforce RBAC / Approval requirements for high risk operations
        if snapshot.is_high_risk and not force_external_effects:
            raise ReplayNotAvailableException(
                execution_id,
                "Execution involves high-risk external side-effects. Safe replay mode is active and force_external_effects was not approved."
            )

        if user_permissions is not None and "replay:execute" not in user_permissions and "admin" not in user_permissions:
            raise ReplayNotAvailableException(execution_id, "User lacks required 'replay:execute' permission.")

        start_time = time.time()
        replay_id = f"replay-{execution_id}-{int(start_time)}"

        # Mock/Simulate execution re-run safely
        replayed_output = {
            "replayed": True,
            "simulated_side_effects": force_external_effects,
            "inputs": snapshot.inputs,
            "config": snapshot.config,
            "original_output": snapshot.original_output,
        }
        end_time = time.time()
        replayed_duration = round((end_time - start_time) * 1000.0, 2)

        comparison = self.compare_executions(
            original_output=snapshot.original_output,
            replayed_output=replayed_output,
            original_status=snapshot.original_status,
            replayed_status="COMPLETED",
            original_duration_ms=100.0,
            replayed_duration_ms=replayed_duration,
            execution_id=execution_id,
            replay_id=replay_id,
        )

        result = {
            "replay_id": replay_id,
            "execution_id": execution_id,
            "status": "COMPLETED",
            "safe_mode": not force_external_effects,
            "replayed_output": replayed_output,
            "comparison": comparison,
        }

        if execution_id not in self._replay_history:
            self._replay_history[execution_id] = []
        self._replay_history[execution_id].append(result)

        return result

    def compare_executions(
        self,
        original_output: Optional[Dict[str, Any]],
        replayed_output: Dict[str, Any],
        original_status: str,
        replayed_status: str,
        original_duration_ms: float,
        replayed_duration_ms: float,
        execution_id: str,
        replay_id: str,
    ) -> Dict[str, Any]:
        """Compare outputs and identify execution divergence."""
        divergences: List[Dict[str, Any]] = []
        matched = True

        if original_status != replayed_status:
            matched = False
            divergences.append({
                "type": "STATUS_MISMATCH",
                "original": original_status,
                "replayed": replayed_status,
            })

        if original_output and replayed_output:
            for k, orig_val in original_output.items():
                if k in ["replayed", "simulated_side_effects"]:
                    continue
                rep_val = replayed_output.get(k)
                if orig_val != rep_val:
                    matched = False
                    divergences.append({
                        "type": "OUTPUT_DIVERGENCE",
                        "field": k,
                        "original": str(orig_val),
                        "replayed": str(rep_val),
                    })

        return {
            "execution_id": execution_id,
            "replay_id": replay_id,
            "matched": matched,
            "divergences": divergences,
            "original_status": original_status,
            "replayed_status": replayed_status,
            "original_duration_ms": original_duration_ms,
            "replayed_duration_ms": replayed_duration_ms,
        }

    def get_replay_status(self, execution_id: str) -> List[Dict[str, Any]]:
        """Retrieve history of replays for an execution ID."""
        return self._replay_history.get(execution_id, [])
