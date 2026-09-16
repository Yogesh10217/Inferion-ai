"""
Memory Compressor Engine: Conversation Compression & Fact Deduplication
"""

from typing import Any, Dict, List


class MemoryCompressor:
    """Compresses conversation histories and deduplicates semantic memory items."""

    def compress_messages(self, messages: List[Dict[str, Any]], max_tokens: int = 2048) -> Dict[str, Any]:
        """Compresses message list into a canonical summary block."""
        if not messages:
            return {"summary": "", "messages": []}

        summary = f"Compressed conversation history of {len(messages)} messages."
        recent_messages = messages[-5:]
        return {
            "summary": summary,
            "messages": recent_messages,
            "compressed_count": len(messages) - len(recent_messages),
        }

    def deduplicate_facts(self, facts: List[str]) -> List[str]:
        """Deduplicates facts preserving order."""
        seen = set()
        deduped = []
        for fact in facts:
            normalized = fact.strip().lower()
            if normalized not in seen:
                seen.add(normalized)
                deduped.append(fact)
        return deduped
