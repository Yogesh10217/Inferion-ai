"""Enterprise Intelligence Context Assembly."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.knowledge_platform.manager import KnowledgePlatformManager
from app.intelligence_platform.signals import IntelligenceSignal
from app.intelligence_platform.exceptions import ContextAssemblyException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ContextSource(str, Enum):
    KNOWLEDGE_BASE = "KNOWLEDGE_BASE"
    OPERATIONAL_SIGNALS = "OPERATIONAL_SIGNALS"
    INCIDENTS = "INCIDENTS"
    CHANGES = "CHANGES"
    COST_LEDGER = "COST_LEDGER"
    MODEL_METRICS = "MODEL_METRICS"
    SECURITY_EVENTS = "SECURITY_EVENTS"


class ContextEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:10]}")
    source: ContextSource
    title: str
    content: str
    relevance_score: float = 1.0
    provenance_reference: str = "system"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContextWindow(BaseModel):
    max_tokens: int = 4096
    tokens_used: int = 0
    max_cost_usd: float = 0.05
    cost_usd: float = 0.001


class IntelligenceContext(BaseModel):
    context_id: str = Field(default_factory=lambda: f"ctx_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    primary_resource_id: Optional[str] = None
    signals: List[IntelligenceSignal] = Field(default_factory=list)
    evidences: List[ContextEvidence] = Field(default_factory=list)
    recent_deployments: List[Dict[str, Any]] = Field(default_factory=list)
    recent_cost_events: List[Dict[str, Any]] = Field(default_factory=list)
    context_window: ContextWindow = Field(default_factory=ContextWindow)
    assembled_at: datetime = Field(default_factory=_now)


class ContextBuilder:
    """Assembles enterprise intelligence context by composing signals and Knowledge Platform records."""

    def __init__(self, knowledge_platform_manager: Optional[KnowledgePlatformManager] = None) -> None:
        self.knowledge_platform_manager = knowledge_platform_manager or KnowledgePlatformManager()

    def assemble_context(
        self,
        tenant_id: str,
        primary_resource_id: Optional[str] = None,
        signals: Optional[List[IntelligenceSignal]] = None,
        recent_deployments: Optional[List[Dict[str, Any]]] = None,
        recent_cost_events: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
    ) -> IntelligenceContext:
        if not tenant_id:
            raise ContextAssemblyException("Tenant ID is required for context assembly.")

        evidences: List[ContextEvidence] = []

        # Convert signals into context evidence
        for sig in signals or []:
            ev = ContextEvidence(
                source=ContextSource.OPERATIONAL_SIGNALS,
                title=f"Signal [{sig.source.value}] {sig.message}",
                content=sig.message,
                relevance_score=0.95,
                provenance_reference=f"signal:{sig.signal_id}",
                metadata={"metrics": sig.metrics, "payload": sig.payload},
            )
            evidences.append(ev)

        # Retrieve knowledge records if available
        try:
            k_items = self.knowledge_platform_manager.list_knowledge_items(tenant_id)
            for k in k_items[:5]:  # token budget bounds
                evidences.append(
                    ContextEvidence(
                        source=ContextSource.KNOWLEDGE_BASE,
                        title=k.title,
                        content=k.content,
                        relevance_score=0.85,
                        provenance_reference=f"knowledge:{k.item_id}",
                    )
                )
        except Exception as e:
            logger.debug(f"Knowledge platform consultation fallback: {e}")

        win = ContextWindow(max_tokens=max_tokens, tokens_used=len(evidences) * 150)

        ctx = IntelligenceContext(
            tenant_id=tenant_id,
            primary_resource_id=primary_resource_id,
            signals=signals or [],
            evidences=evidences,
            recent_deployments=recent_deployments or [],
            recent_cost_events=recent_cost_events or [],
            context_window=win,
        )

        logger.info(f"[CONTEXT BUILDER] Assembled intelligence context '{ctx.context_id}' with {len(evidences)} evidence items for tenant '{tenant_id}'")
        return ctx
