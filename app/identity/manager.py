"""Master Identity Security Manager & Zero-Trust Orchestration Engine."""

import logging
from typing import Dict, Any, Optional, List

from app.identity.identity import IdentityManager, IdentityType, IdentityStatus
from app.identity.authentication import AuthenticationManager, AuthenticationMethod, AuthenticationAssuranceLevel
from app.identity.access_control import AccessControlManager, AccessContext, AccessDecision
from app.identity.privileged_access import PrivilegedAccessManager, PrivilegedRole, PrivilegedAccessStatus
from app.identity.zero_trust import ZeroTrustEngine, TrustLevel, ZeroTrustAction
from app.identity.session import SessionManager, SessionState
from app.identity.workload_identity import WorkloadIdentityManager, WorkloadType
from app.identity.credentials import CredentialManager, CredentialType, CredentialStatus
from app.identity.risk import IdentityRiskEngine, AnomalyType, IdentityRiskSeverity
from app.identity.agent_identity import AgentIdentityManager, AgentPermissionBoundary
from app.identity.explainability import ExplainabilityEngine, AuthorizationExplanation
from app.identity.audit import IdentityAuditManager
from app.identity.lifecycle import IdentityLifecycleManager
from app.identity.observability import IdentityMetricsCollector

logger = logging.getLogger(__name__)


class IdentitySecurityManager:
    """Master manager orchestrating all 14 Identity, Access & Zero-Trust Security domain subsystems."""

    def __init__(
        self,
        identity_manager: Optional[IdentityManager] = None,
        auth_manager: Optional[AuthenticationManager] = None,
        access_control_manager: Optional[AccessControlManager] = None,
        privileged_access_manager: Optional[PrivilegedAccessManager] = None,
        zero_trust_engine: Optional[ZeroTrustEngine] = None,
        session_manager: Optional[SessionManager] = None,
        workload_identity_manager: Optional[WorkloadIdentityManager] = None,
        credential_manager: Optional[CredentialManager] = None,
        identity_risk_engine: Optional[IdentityRiskEngine] = None,
        agent_identity_manager: Optional[AgentIdentityManager] = None,
        explainability_engine: Optional[ExplainabilityEngine] = None,
        audit_manager: Optional[IdentityAuditManager] = None,
        lifecycle_manager: Optional[IdentityLifecycleManager] = None,
        metrics_collector: Optional[IdentityMetricsCollector] = None,
    ) -> None:
        self.identity_manager = identity_manager or IdentityManager()
        self.auth_manager = auth_manager or AuthenticationManager()
        self.access_control_manager = access_control_manager or AccessControlManager()
        self.privileged_access_manager = privileged_access_manager or PrivilegedAccessManager()
        self.zero_trust_engine = zero_trust_engine or ZeroTrustEngine()
        self.session_manager = session_manager or SessionManager()
        self.workload_identity_manager = workload_identity_manager or WorkloadIdentityManager()
        self.credential_manager = credential_manager or CredentialManager()
        self.identity_risk_engine = identity_risk_engine or IdentityRiskEngine()
        self.agent_identity_manager = agent_identity_manager or AgentIdentityManager()
        self.explainability_engine = explainability_engine or ExplainabilityEngine()
        self.audit_manager = audit_manager or IdentityAuditManager()
        self.lifecycle_manager = lifecycle_manager or IdentityLifecycleManager()
        self.metrics_collector = metrics_collector or IdentityMetricsCollector()

        logger.info("[IDENTITY SECURITY MANAGER] Master IdentitySecurityManager initialized with all 14 domain subsystems")
