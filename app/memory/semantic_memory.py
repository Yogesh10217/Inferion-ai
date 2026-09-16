"""
Semantic Memory (Tier 3): Learned Facts & Domain Knowledge Base
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class SemanticMemoryItem:
    def __init__(
        self,
        fact: str,
        category: str = "general",
        importance_score: float = 0.5,
        confidence_score: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        fact_id: Optional[str] = None,
    ):
        self.fact_id = fact_id or f"sem_{uuid.uuid4().hex[:12]}"
        self.fact = fact
        self.category = category
        self.importance_score = importance_score
        self.confidence_score = confidence_score
        self.metadata = metadata or {}
        self.status = "ACTIVE"
        self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fact_id": self.fact_id,
            "fact": self.fact,
            "category": self.category,
            "importance_score": self.importance_score,
            "confidence_score": self.confidence_score,
            "metadata": self.metadata,
            "status": self.status,
            "created_at": self.created_at,
        }


class SemanticMemory:
    """Stores and searches learned facts and semantic knowledge."""

    def __init__(self, organization_id: str = "default_org", workspace_id: str = "default_workspace"):
        self.organization_id = organization_id
        self.workspace_id = workspace_id
        self._facts: Dict[str, SemanticMemoryItem] = {}

    def store_fact(
        self,
        fact: str,
        category: str = "general",
        importance_score: float = 0.5,
        confidence_score: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SemanticMemoryItem:
        item = SemanticMemoryItem(
            fact=fact,
            category=category,
            importance_score=importance_score,
            confidence_score=confidence_score,
            metadata=metadata,
        )
        self._facts[item.fact_id] = item
        return item

    def update_fact(self, fact_id: str, fact: Optional[str] = None, importance_score: Optional[float] = None) -> SemanticMemoryItem:
        if fact_id not in self._facts:
            raise KeyError(f"Semantic fact '{fact_id}' not found")
        item = self._facts[fact_id]
        if fact:
            item.fact = fact
        if importance_score is not None:
            item.importance_score = importance_score
        return item

    def get_fact(self, fact_id: str) -> SemanticMemoryItem:
        if fact_id not in self._facts:
            raise KeyError(f"Semantic fact '{fact_id}' not found")
        return self._facts[fact_id]

    def search(self, query: str, category: Optional[str] = None, top_k: int = 10) -> List[SemanticMemoryItem]:
        results = list(self._facts.values())
        if category:
            results = [item for item in results if item.category == category]
        query_words = set(query.lower().split())

        def match_score(item: SemanticMemoryItem) -> float:
            words = set(item.fact.lower().split())
            overlap = len(query_words.intersection(words))
            return overlap * item.importance_score * item.confidence_score

        results.sort(key=match_score, reverse=True)
        return results[:top_k]

    def archive(self, fact_id: str) -> SemanticMemoryItem:
        item = self.get_fact(fact_id)
        item.status = "ARCHIVED"
        return item
