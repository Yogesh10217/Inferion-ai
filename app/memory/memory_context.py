"""
Memory Context Container for Prompt Assembly & Engine Integration
"""

from typing import Dict, Any, List, Optional


class MemoryContext:
    """Holds retrieved memory snippets across tiers to construct optimal LLM prompt context."""

    def __init__(
        self,
        working_memory: Optional[Dict[str, Any]] = None,
        conversation_summary: Optional[str] = None,
        conversation_messages: Optional[List[Dict[str, Any]]] = None,
        semantic_facts: Optional[List[Dict[str, Any]]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        session_context: Optional[Dict[str, Any]] = None,
        relevant_episodes: Optional[List[Dict[str, Any]]] = None,
    ):
        self.working_memory = working_memory or {}
        self.conversation_summary = conversation_summary
        self.conversation_messages = conversation_messages or []
        self.semantic_facts = semantic_facts or []
        self.user_profile = user_profile or {}
        self.session_context = session_context or {}
        self.relevant_episodes = relevant_episodes or []

    def format_prompt_context(self) -> str:
        """Assembles unified markdown memory context string for LLM prompts."""
        blocks = []
        if self.user_profile:
            blocks.append(f"### User Profile & Preferences\n{self.user_profile}")
        if self.session_context:
            blocks.append(f"### Active Session Context\n{self.session_context}")
        if self.semantic_facts:
            facts_str = "\n".join([f"- {f.get('fact', f)}" for f in self.semantic_facts])
            blocks.append(f"### Learned Facts & Semantic Knowledge\n{facts_str}")
        if self.relevant_episodes:
            ep_str = "\n".join([f"- {e.get('summary', e)}" for e in self.relevant_episodes])
            blocks.append(f"### Relevant Past Episodes\n{ep_str}")
        if self.conversation_summary:
            blocks.append(f"### Conversation History Summary\n{self.conversation_summary}")

        return "\n\n".join(blocks)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "working_memory": self.working_memory,
            "conversation_summary": self.conversation_summary,
            "conversation_messages": self.conversation_messages,
            "semantic_facts": self.semantic_facts,
            "user_profile": self.user_profile,
            "session_context": self.session_context,
            "relevant_episodes": self.relevant_episodes,
            "formatted_context": self.format_prompt_context(),
        }
