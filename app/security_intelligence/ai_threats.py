"""AI-Specific Threat Intelligence Subsystem (Phase 5.32)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.security_intelligence.exceptions import CrossTenantSecurityAccessException


class AIThreatType(str, Enum):
    PROMPT_INJECTION = "PROMPT_INJECTION"
    INDIRECT_PROMPT_INJECTION = "INDIRECT_PROMPT_INJECTION"
    JAILBREAK_ATTEMPT = "JAILBREAK_ATTEMPT"
    TOOL_MISUSE = "TOOL_MISUSE"
    EXCESSIVE_AGENT_AUTONOMY = "EXCESSIVE_AGENT_AUTONOMY"
    UNAUTHORIZED_DATA_ACCESS = "UNAUTHORIZED_DATA_ACCESS"
    SENSITIVE_CONTEXT_LEAKAGE = "SENSITIVE_CONTEXT_LEAKAGE"
    MODEL_EXTRACTION_ATTEMPT = "MODEL_EXTRACTION_ATTEMPT"
    MODEL_ABUSE = "MODEL_ABUSE"
    RAG_POISONING = "RAG_POISONING"
    KNOWLEDGE_POISONING = "KNOWLEDGE_POISONING"
    AGENT_LOOP = "AGENT_LOOP"
    UNSAFE_DELEGATION = "UNSAFE_DELEGATION"
    CROSS_TENANT_CONTEXT_LEAKAGE = "CROSS_TENANT_CONTEXT_LEAKAGE"


class AIThreatSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AIThreatDetection(BaseModel):
    detection_id: str = Field(default_factory=lambda: f"aidtd_{uuid.uuid4().hex[:12]}")
    signal_id: str
    confidence_score: float = 0.95
    indicator: str


class AIThreat(BaseModel):
    ai_threat_id: str = Field(default_factory=lambda: f"aithrt_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    model_or_agent_id: str
    threat_type: AIThreatType
    severity: AIThreatSeverity = AIThreatSeverity.HIGH
    detections: List[AIThreatDetection] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AIThreatManager:
    """Analyzes AI/LLM/Agent-specific security threats analytically without executing defensive actions."""

    def __init__(self) -> None:
        self._ai_threats: Dict[str, AIThreat] = {}

    def analyze_ai_threat(
        self,
        tenant_id: str,
        model_or_agent_id: str,
        threat_type: AIThreatType,
        severity: AIThreatSeverity = AIThreatSeverity.HIGH,
        signal_id: str = "sig_default",
        indicator: str = "Pattern match prompt_injection",
    ) -> AIThreat:
        dtd = AIThreatDetection(signal_id=signal_id, indicator=indicator)
        thrt = AIThreat(
            tenant_id=tenant_id,
            model_or_agent_id=model_or_agent_id,
            threat_type=threat_type,
            severity=severity,
            detections=[dtd],
        )
        self._ai_threats[thrt.ai_threat_id] = thrt
        return thrt

    def list_ai_threats(self, tenant_id: str) -> List[AIThreat]:
        return [t for t in self._ai_threats.values() if t.tenant_id == tenant_id]
