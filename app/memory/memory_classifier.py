"""
Memory Classification Engine: Type Detection, Importance & Retention Policy Selection
"""

from typing import Dict, Any, Optional
from app.memory.memory_types import MemoryType, RetentionPolicy


class MemoryClassificationResult:
    def __init__(
        self,
        memory_type: MemoryType,
        importance_score: float,
        confidence_score: float,
        retention_policy: RetentionPolicy,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.memory_type = memory_type
        self.importance_score = importance_score
        self.confidence_score = confidence_score
        self.retention_policy = retention_policy
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_type": self.memory_type.value,
            "importance": self.importance_score,
            "confidence": self.confidence_score,
            "retention_policy": self.retention_policy.value,
            "metadata": self.metadata,
        }


class MemoryClassifier:
    """Classifies memory candidate text into tiers, importance scores, and retention policies."""

    def classify(self, text: str, context_hint: Optional[str] = None) -> MemoryClassificationResult:
        lowered = text.lower()

        # Heuristic rules
        if context_hint == "profile" or "prefer" in lowered or "my language is" in lowered or "i use" in lowered:
            return MemoryClassificationResult(
                memory_type=MemoryType.PROFILE,
                importance_score=0.9,
                confidence_score=0.95,
                retention_policy=RetentionPolicy.PERMANENT,
            )

        if "always" in lowered or "architecture" in lowered or "decision" in lowered or "fact:" in lowered:
            return MemoryClassificationResult(
                memory_type=MemoryType.SEMANTIC,
                importance_score=0.8,
                confidence_score=0.9,
                retention_policy=RetentionPolicy.PERMANENT,
            )

        if "run" in lowered or "executed" in lowered or "result of" in lowered or "completed" in lowered:
            return MemoryClassificationResult(
                memory_type=MemoryType.EPISODIC,
                importance_score=0.6,
                confidence_score=0.85,
                retention_policy=RetentionPolicy.TTL_30_DAYS,
            )

        if "session" in lowered or "current task" in lowered or "active project" in lowered:
            return MemoryClassificationResult(
                memory_type=MemoryType.SESSION,
                importance_score=0.5,
                confidence_score=0.8,
                retention_policy=RetentionPolicy.SESSION,
            )

        # Default fallback conversation memory
        return MemoryClassificationResult(
            memory_type=MemoryType.CONVERSATION,
            importance_score=0.4,
            confidence_score=0.75,
            retention_policy=RetentionPolicy.TTL_30_DAYS,
        )
