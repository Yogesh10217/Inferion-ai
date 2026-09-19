"""
Session Memory (Tier 5): Active Session Context & Snapshots
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional


class SessionContext:
    def __init__(
        self,
        session_id: str,
        context_data: Optional[Dict[str, Any]] = None,
        ttl_seconds: float = 86400.0,
    ):
        self.session_id = session_id
        self.context_data = context_data or {}
        self.created_at = datetime.now(timezone.utc)
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "context_data": self.context_data,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_expired": self.is_expired(),
        }


class SessionMemory:
    """Manages active task and session state with automatic TTL expiration and snapshots."""

    def __init__(self):
        self._sessions: Dict[str, SessionContext] = {}

    def create_session(
        self, session_id: str, context_data: Optional[Dict[str, Any]] = None, ttl_seconds: float = 86400.0
    ) -> SessionContext:
        session = SessionContext(session_id=session_id, context_data=context_data, ttl_seconds=ttl_seconds)
        self._sessions[session_id] = session
        return session

    def update_session(self, session_id: str, context_data: Dict[str, Any]) -> SessionContext:
        if session_id not in self._sessions or self._sessions[session_id].is_expired():
            return self.create_session(session_id, context_data)
        sess = self._sessions[session_id]
        sess.context_data.update(context_data)
        return sess

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        sess = self._sessions.get(session_id)
        if sess and not sess.is_expired():
            return sess
        return None

    def expire_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def recover_session(self, session_id: str) -> Dict[str, Any]:
        sess = self.get_session(session_id)
        if not sess:
            return {}
        return sess.context_data
