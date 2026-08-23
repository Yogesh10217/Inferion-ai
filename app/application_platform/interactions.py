"""Conversation & Interaction Management (Phase 5.22 - Component 7).

Manages multi-turn conversation state:
- Types: CHAT, COMMAND, FORM, EVENT, API, VOICE_REFERENCE, MULTIMODAL_REFERENCE
- Secret sanitization & redaction
- Replay safety and audit tracking
- Tenant-isolated storage
"""

import logging
import re
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class InteractionType(str, Enum):
    CHAT = "CHAT"
    COMMAND = "COMMAND"
    FORM = "FORM"
    EVENT = "EVENT"
    API = "API"
    VOICE_REFERENCE = "VOICE_REFERENCE"
    MULTIMODAL_REFERENCE = "MULTIMODAL_REFERENCE"


class ConversationState(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


class Interaction(BaseModel):
    """Single interaction turn in a conversation."""

    interaction_id: str = Field(default_factory=lambda: f"int_{uuid.uuid4().hex[:12]}")
    conversation_id: str
    tenant_id: str
    interaction_type: InteractionType = InteractionType.CHAT
    user_input: str
    sanitized_input: str = ""
    system_response: str = ""
    sanitized_response: str = ""
    tokens_used: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Conversation(BaseModel):
    """Multi-turn conversation container."""

    conversation_id: str = Field(default_factory=lambda: f"conv_{uuid.uuid4().hex[:12]}")
    application_id: str
    tenant_id: str
    user_id: str
    state: ConversationState = ConversationState.ACTIVE
    interactions: List[Interaction] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InteractionManager:
    """Manages conversations, interaction turns, and secret sanitization."""

    SECRET_PATTERNS = [
        re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE),
        re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE),
        re.compile(r"password=[\'\"][^\'\"]+[\'\"]", re.IGNORECASE),
        re.compile(r"api[_\-]?key=[\'\"][^\'\"]+[\'\"]", re.IGNORECASE),
    ]

    def __init__(self) -> None:
        self._conversations: Dict[str, Conversation] = {}  # key: f"{tenant_id}:{conv_id}"

    def sanitize_text(self, text: str) -> str:
        """Sanitize text to redact sensitive tokens / API keys."""
        sanitized = text
        for pattern in self.SECRET_PATTERNS:
            sanitized = pattern.sub("[REDACTED_SECRET]", sanitized)
        return sanitized

    def start_conversation(
        self,
        tenant_id: str,
        application_id: str,
        user_id: str,
    ) -> Conversation:
        conv = Conversation(
            application_id=application_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )
        key = f"{tenant_id}:{conv.conversation_id}"
        self._conversations[key] = conv
        logger.info(f"[INTERACTION MANAGER] Started conversation {conv.conversation_id} for app {application_id}")
        return conv

    def add_interaction(
        self,
        tenant_id: str,
        conversation_id: str,
        user_input: str,
        system_response: str = "",
        interaction_type: InteractionType = InteractionType.CHAT,
        tokens_used: int = 0,
    ) -> Interaction:
        key = f"{tenant_id}:{conversation_id}"
        if key not in self._conversations:
            # Auto-create if missing
            conv = Conversation(
                conversation_id=conversation_id,
                application_id="unknown",
                tenant_id=tenant_id,
                user_id="anonymous",
            )
            self._conversations[key] = conv

        conv = self._conversations[key]
        
        sanitized_in = self.sanitize_text(user_input)
        sanitized_out = self.sanitize_text(system_response)

        interaction = Interaction(
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            interaction_type=interaction_type,
            user_input=user_input,
            sanitized_input=sanitized_in,
            system_response=system_response,
            sanitized_response=sanitized_out,
            tokens_used=tokens_used,
        )

        conv.interactions.append(interaction)
        conv.updated_at = datetime.now(timezone.utc)
        return interaction

    def get_conversation(self, tenant_id: str, conversation_id: str) -> Optional[Conversation]:
        key = f"{tenant_id}:{conversation_id}"
        return self._conversations.get(key)
