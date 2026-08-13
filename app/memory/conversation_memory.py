"""
Conversation Memory (Tier 2): Multi-Turn Chat History Buffer & Trimming
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class ConversationMemory:
    """Manages multi-turn conversation history, sliding context windows, and summarization."""

    def __init__(
        self,
        session_id: str,
        max_messages: int = 50,
        max_tokens: int = 4096
    ):
        self.session_id = session_id
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.messages: List[Dict[str, Any]] = []
        self.summary: Optional[str] = None

    def append_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        self.messages.append(msg)
        self.trim_history()
        return msg

    def trim_history(self) -> None:
        """Enforces max_messages boundary via sliding window."""
        if len(self.messages) > self.max_messages:
            trimmed_count = len(self.messages) - self.max_messages
            overflow = self.messages[:trimmed_count]
            self.messages = self.messages[trimmed_count:]
            # Append brief note to summary
            summary_addition = f" Earlier conversation had {len(overflow)} turns."
            self.summary = (self.summary or "Summary of prior context:") + summary_addition

    def compress(self) -> Dict[str, Any]:
        """Compresses conversation messages into a canonical summary block."""
        if not self.messages:
            return {"summary": self.summary, "message_count": 0}
        
        recent_text = "\n".join([f"{m['role']}: {m['content']}" for m in self.messages[-5:]])
        self.summary = f"Conversation summary up to {datetime.now(timezone.utc).isoformat()}: Recent turns included:\n{recent_text}"
        return {"summary": self.summary, "message_count": len(self.messages)}

    def summarize(self) -> str:
        if not self.summary:
            self.compress()
        return self.summary or ""

    def retrieve_context(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "summary": self.summary,
            "messages": self.messages,
            "message_count": len(self.messages),
        }
