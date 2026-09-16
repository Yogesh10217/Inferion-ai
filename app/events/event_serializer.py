import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class EventEnvelope:
    """Standardized event envelope structure for all engine events."""

    def __init__(
        self,
        event_type: str,
        payload: Dict[str, Any],
        event_id: Optional[str] = None,
        version: str = "1.0",
        timestamp: Optional[str] = None,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        actor: Optional[str] = None,
        source: str = "llm-inference-engine",
        correlation_id: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.event_id = event_id or str(uuid.uuid4())
        self.event_type = event_type
        self.version = version
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.organization_id = organization_id
        self.workspace_id = workspace_id
        self.actor = actor
        self.source = source
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.request_id = request_id
        self.payload = payload or {}
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "version": self.version,
            "timestamp": self.timestamp,
            "organization_id": self.organization_id,
            "workspace_id": self.workspace_id,
            "actor": self.actor,
            "source": self.source,
            "correlation_id": self.correlation_id,
            "request_id": self.request_id,
            "payload": self.payload,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventEnvelope":
        return cls(
            event_id=data.get("event_id"),
            event_type=data.get("event_type", "unknown"),
            version=data.get("version", "1.0"),
            timestamp=data.get("timestamp"),
            organization_id=data.get("organization_id"),
            workspace_id=data.get("workspace_id"),
            actor=data.get("actor"),
            source=data.get("source", "llm-inference-engine"),
            correlation_id=data.get("correlation_id"),
            request_id=data.get("request_id"),
            payload=data.get("payload", {}),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "EventEnvelope":
        data = json.loads(json_str)
        return cls.from_dict(data)


class EventSerializer:
    """Helper methods for serializing and deserializing event envelopes."""

    @staticmethod
    def serialize(envelope: EventEnvelope) -> str:
        return envelope.to_json()

    @staticmethod
    def deserialize(json_str: str) -> EventEnvelope:
        return EventEnvelope.from_json(json_str)
