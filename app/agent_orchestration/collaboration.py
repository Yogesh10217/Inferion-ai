"""Multi-Agent Collaboration Subsystem (Phase 5.36)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.agent_orchestration.exceptions import (
    AgentCollaborationException,
    CrossTenantAgentAccessException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.platform_contracts.tenant import TenantAccessGuard


class CollaborationType(str, Enum):
    SUPERVISOR_WORKER = "SUPERVISOR_WORKER"
    PLANNER_EXECUTOR = "PLANNER_EXECUTOR"
    PEER_COLLABORATION = "PEER_COLLABORATION"
    SPECIALIST_ROUTING = "SPECIALIST_ROUTING"
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"


class CollaborationStatus(str, Enum):
    INITIATED = "INITIATED"
    ACTIVE = "ACTIVE"
    WAITING_FOR_WORKER = "WAITING_FOR_WORKER"
    DECISION_REACHED = "DECISION_REACHED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TERMINATED = "TERMINATED"


class AgentParticipant(BaseModel):
    agent_id: str
    tenant_id: str
    role: str = "WORKER"  # SUPERVISOR, PLANNER, WORKER, SPECIALIST, AUDITOR
    capabilities: List[str] = Field(default_factory=list)


class CollaborationMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:10]}")
    session_id: str
    sender_agent_id: str
    recipient_agent_id: str
    tenant_id: str
    message_type: str = "INSTRUCTION"  # INSTRUCTION, PROPOSAL, FEEDBACK, RESULT, QUERY
    content_sanitized: Dict[str, Any] = Field(default_factory=dict)
    references: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CollaborationDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"coldec_{uuid.uuid4().hex[:10]}")
    consensus_type: str = "SUPERVISOR_APPROVAL"
    selected_action: str
    participating_agents: List[str] = Field(default_factory=list)
    agreed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentCollaborationSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"collab_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    collaboration_type: CollaborationType = CollaborationType.SUPERVISOR_WORKER
    status: CollaborationStatus = CollaborationStatus.INITIATED
    participants: List[AgentParticipant] = Field(default_factory=list)
    messages: List[CollaborationMessage] = Field(default_factory=list)
    decision: Optional[CollaborationDecision] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentCollaborationManager:
    """Manages multi-agent collaboration sessions with strict tenant isolation and sanitized messages."""

    def __init__(
        self,
        sanitizer: Optional[SensitiveDataSanitizer] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.sanitizer = sanitizer or SensitiveDataSanitizer()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._sessions: Dict[str, AgentCollaborationSession] = {}

    def create_session(
        self,
        tenant_id: str,
        collaboration_type: CollaborationType,
        participants: List[AgentParticipant],
        session_id: Optional[str] = None,
    ) -> AgentCollaborationSession:
        # Validate that ALL participants belong to the same tenant
        for p in participants:
            if p.tenant_id != tenant_id and tenant_id != "global":
                raise CrossTenantAgentAccessException(tenant_id, p.tenant_id)

        sid = session_id or f"collab_{uuid.uuid4().hex[:12]}"
        session = AgentCollaborationSession(
            session_id=sid,
            tenant_id=tenant_id,
            collaboration_type=collaboration_type,
            status=CollaborationStatus.ACTIVE,
            participants=participants,
        )
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str, tenant_id: str) -> AgentCollaborationSession:
        session = self._sessions.get(session_id)
        if not session:
            raise AgentCollaborationException(f"Collaboration session '{session_id}' not found.")

        try:
            self.tenant_guard.enforce_isolation(tenant_id, session.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, session.tenant_id)

        return session

    def send_message(
        self,
        session_id: str,
        tenant_id: str,
        sender_agent_id: str,
        recipient_agent_id: str,
        message_type: str,
        content: Dict[str, Any],
        references: Optional[List[str]] = None,
    ) -> CollaborationMessage:
        session = self.get_session(session_id, tenant_id)

        # Sanitize message payload
        sanitized_content = self.sanitizer.sanitize_copy(content)
        msg = CollaborationMessage(
            session_id=session_id,
            sender_agent_id=sender_agent_id,
            recipient_agent_id=recipient_agent_id,
            tenant_id=tenant_id,
            message_type=message_type,
            content_sanitized=(
                sanitized_content if isinstance(sanitized_content, dict) else {"data": str(sanitized_content)}
            ),
            references=references or [],
        )

        session.messages.append(msg)
        session.updated_at = datetime.now(timezone.utc)
        return msg

    def finalize_decision(
        self,
        session_id: str,
        tenant_id: str,
        selected_action: str,
        consensus_type: str = "SUPERVISOR_APPROVAL",
    ) -> AgentCollaborationSession:
        session = self.get_session(session_id, tenant_id)
        part_ids = [p.agent_id for p in session.participants]
        session.decision = CollaborationDecision(
            consensus_type=consensus_type,
            selected_action=selected_action,
            participating_agents=part_ids,
        )
        session.status = CollaborationStatus.COMPLETED
        session.updated_at = datetime.now(timezone.utc)
        return session
