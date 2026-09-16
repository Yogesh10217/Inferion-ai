"""
Memory Extraction Engine: Facts, Preferences, Entities & Episodic Extraction
"""

from typing import Any, Dict, List, Optional


class ExtractedMemoryCandidate:
    def __init__(
        self,
        candidate_type: str,
        content: str,
        confidence: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.candidate_type = candidate_type
        self.content = content
        self.confidence = confidence
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_type": self.candidate_type,
            "content": self.content,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


class MemoryExtractor:
    """Extracts memory candidates (facts, preferences, technologies, entities, episodes) from raw content."""

    def extract_from_text(self, text: str, source: str = "conversation") -> List[ExtractedMemoryCandidate]:
        candidates: List[ExtractedMemoryCandidate] = []
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        for line in lines:
            lowered = line.lower()
            if "prefer" in lowered or "i like" in lowered or "my stack is" in lowered:
                candidates.append(ExtractedMemoryCandidate(
                    candidate_type="preference",
                    content=line,
                    confidence=0.9,
                    metadata={"source": source}
                ))
            elif "uses" in lowered or "framework" in lowered or "technology" in lowered:
                candidates.append(ExtractedMemoryCandidate(
                    candidate_type="technology",
                    content=line,
                    confidence=0.85,
                    metadata={"source": source}
                ))
            elif "decided to" in lowered or "configured" in lowered:
                candidates.append(ExtractedMemoryCandidate(
                    candidate_type="decision",
                    content=line,
                    confidence=0.8,
                    metadata={"source": source}
                ))
            else:
                candidates.append(ExtractedMemoryCandidate(
                    candidate_type="fact",
                    content=line,
                    confidence=0.7,
                    metadata={"source": source}
                ))

        return candidates
