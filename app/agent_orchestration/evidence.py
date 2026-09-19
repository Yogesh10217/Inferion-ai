"""Agent Evidence References Subsystem (Phase 5.36)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.agent_orchestration.exceptions import CrossTenantAgentAccessException
from app.platform_contracts.evidence import (
    EvidenceIntegrity,
    EvidenceMetadata,
    EvidenceReference,
    EvidenceSourceReference,
    EvidenceStrength,
)
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.tenant import TenantAccessGuard


class AgentEvidenceIntegrity(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    AUDITED = "AUDITED"


class AgentEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    evidence_type: str = "EXECUTION_TRACE"
    reference: EvidenceReference
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: f"bundle_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    trace_id: str
    evidence_list: List[AgentEvidence] = Field(default_factory=list)
    overall_fingerprint: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentEvidenceManager:
    """Manages audit evidence collection and bundles reusing platform_contracts EvidenceReference."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._bundles: Dict[str, AgentEvidenceBundle] = {}

    def assemble_evidence_bundle(
        self,
        tenant_id: str,
        trace_id: str,
        source_subsystem: str = "AGENT_ORCHESTRATION",
        evidence_descriptions: Optional[List[str]] = None,
    ) -> AgentEvidenceBundle:
        ev_items = []
        descriptions = evidence_descriptions or [
            "Agent execution trace verification",
            "Governance policy compliance proof",
        ]

        for desc in descriptions:
            meta = EvidenceMetadata(
                tenant_id=tenant_id,
                source=EvidenceSourceReference(source_subsystem=source_subsystem, source_entity_id=trace_id),
                strength=EvidenceStrength.STRONG,
                integrity=EvidenceIntegrity.VERIFIED,
            )
            ev_ref = EvidenceReference(
                metadata=meta,
                description=desc,
                attributes={"trace_id": trace_id},
            )
            ev_items.append(
                AgentEvidence(
                    tenant_id=tenant_id,
                    evidence_type="AUDIT_PROOF",
                    reference=ev_ref,
                )
            )

        fp = FingerprintGenerator.generate(
            {
                "tenant_id": tenant_id,
                "trace_id": trace_id,
                "items": [i.model_dump() for i in ev_items],
            }
        )

        bundle = AgentEvidenceBundle(
            tenant_id=tenant_id,
            trace_id=trace_id,
            evidence_list=ev_items,
            overall_fingerprint=fp,
        )
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def get_bundle(self, bundle_id: str, tenant_id: str) -> AgentEvidenceBundle:
        bundle = self._bundles.get(bundle_id)
        if not bundle:
            return AgentEvidenceBundle(bundle_id=bundle_id, tenant_id=tenant_id, trace_id="unknown")

        try:
            self.tenant_guard.enforce_isolation(tenant_id, bundle.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, bundle.tenant_id)

        return bundle
