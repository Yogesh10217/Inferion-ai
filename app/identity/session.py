"""Session Security, Token Rotation & Emergency Forced Logout Engine."""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.identity.exceptions import SessionRevokedException
from app.security.secrets import SecretManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SessionState(str, Enum):
    ACTIVE = "ACTIVE"
    IDLE = "IDLE"
    CHALLENGED = "CHALLENGED"
    RESTRICTED = "RESTRICTED"
    SUSPICIOUS = "SUSPICIOUS"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class Session(BaseModel):
    session_id: str = Field(default_factory=lambda: f"sess_{uuid.uuid4().hex[:10]}")
    identity_id: str
    tenant_id: str = "global"

    state: SessionState = SessionState.ACTIVE
    access_token: str = Field(default_factory=lambda: f"tok_{uuid.uuid4().hex}")
    refresh_token: str = Field(default_factory=lambda: f"ref_{uuid.uuid4().hex}")

    ip_address: str = "127.0.0.1"
    user_agent: str = "Mozilla/5.0"
    is_restricted: bool = False

    created_at: datetime = Field(default_factory=_now)
    last_active_at: datetime = Field(default_factory=_now)
    expires_at: datetime = Field(default_factory=lambda: _now() + timedelta(hours=8))


class SessionManager:
    """Manages active sessions, token rotation, idle timeouts, and emergency session termination."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.secret_manager = secret_manager or SecretManager()
        self._sessions: Dict[str, Session] = {}

    def create_session(self, identity_id: str, tenant_id: str = "global", ip_address: str = "127.0.0.1") -> Session:
        sess = Session(identity_id=identity_id, tenant_id=tenant_id, ip_address=ip_address)
        self._sessions[sess.session_id] = sess
        logger.info(f"[SESSION MANAGER] Created session '{sess.session_id}' for identity '{identity_id}' ({tenant_id})")
        return sess

    def rotate_tokens(self, session_id: str, refresh_token: str) -> Session:
        sess = self.get_session(session_id)
        if sess.state != SessionState.ACTIVE:
            raise SessionRevokedException(session_id, f"Cannot rotate tokens for session in state '{sess.state.value}'")

        sess.access_token = f"tok_{uuid.uuid4().hex}"
        sess.refresh_token = f"ref_{uuid.uuid4().hex}"
        sess.last_active_at = _now()
        logger.info(f"[SESSION MANAGER] Rotated tokens for session '{session_id}'")
        return sess

    def restrict_session(self, session_id: str, reason: str = "Suspicious activity detected") -> Session:
        sess = self.get_session(session_id)
        sess.state = SessionState.RESTRICTED
        sess.is_restricted = True
        logger.warning(f"[SESSION MANAGER] Session '{session_id}' RESTRICTED: {reason}")
        return sess

    def revoke_session(self, session_id: str, reason: str = "Forced logout") -> Session:
        sess = self.get_session(session_id)
        sess.state = SessionState.REVOKED
        logger.warning(f"[SESSION MANAGER] Session '{session_id}' REVOKED: {reason}")
        return sess

    def get_session(self, session_id: str) -> Session:
        sess = self._sessions.get(session_id)
        if not sess:
            raise KeyError(f"Session '{session_id}' not found")
        if sess.state == SessionState.REVOKED:
            raise SessionRevokedException(session_id)
        return sess

    def list_sessions(self, tenant_id: Optional[str] = None) -> List[Session]:
        res = list(self._sessions.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        return res
