"""
Persistent Conversation Memory with Summarization & Compression
"""

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConversationMessage(BaseModel):
    role: str  # user, assistant, system, tool
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationMemory:
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: List[ConversationMessage] = []
        self.summary: Optional[str] = None

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.messages.append(ConversationMessage(role=role, content=content, metadata=metadata or {}))
        if len(self.messages) > self.max_messages:
            self._compress()

    def _compress(self) -> None:
        # Keep latest half of max_messages, compress older ones into summary
        cutoff = len(self.messages) - (self.max_messages // 2)
        old_messages = self.messages[:cutoff]
        self.messages = self.messages[cutoff:]

        summary_text = "\n".join([f"{m.role}: {m.content[:100]}" for m in old_messages])
        if self.summary:
            self.summary += f"\n{summary_text}"
        else:
            self.summary = f"Summary of previous messages:\n{summary_text}"
        logger.info(f"Compressed conversation memory: kept {len(self.messages)} messages, updated summary.")

    def get_formatted_history(self) -> List[Dict[str, str]]:
        res = []
        if self.summary:
            res.append({"role": "system", "content": self.summary})
        for msg in self.messages:
            res.append({"role": msg.role, "content": msg.content})
        return res
