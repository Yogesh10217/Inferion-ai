"""
Memory Summarizer Engine for Conversations, Sessions, Agent Runs & Workflows
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class MemorySummarizer:
    """Generates structured summaries for runs, sessions, and conversation histories."""

    def __init__(self, provider_factory: Optional[Any] = None):
        self.provider_factory = provider_factory

    async def summarize_text(self, text: str, max_words: int = 100) -> str:
        """Summarizes text content."""
        if not text:
            return ""

        words = text.split()
        if len(words) <= max_words:
            return text

        return " ".join(words[:max_words]) + "..."

    async def summarize_run(self, run_id: str, steps: List[Dict[str, Any]]) -> str:
        """Summarizes agent or workflow run execution steps."""
        step_names = [s.get("node_id", s.get("step_id", f"step_{i}")) for i, s in enumerate(steps)]
        return f"Run '{run_id}' executed {len(steps)} steps: {', '.join(step_names)} at {datetime.now(timezone.utc).isoformat()}."
