"""
Memory Ranking Engine: Composite Scoring (Similarity, Recency, Importance, Confidence)
"""

from typing import Dict, Any, List


class MemoryRanker:
    """Ranks candidate memory entries using composite weighted scoring."""

    def __init__(
        self,
        similarity_weight: float = 0.4,
        recency_weight: float = 0.2,
        importance_weight: float = 0.2,
        confidence_weight: float = 0.2,
    ):
        self.similarity_weight = similarity_weight
        self.recency_weight = recency_weight
        self.importance_weight = importance_weight
        self.confidence_weight = confidence_weight

    def rank(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks candidate dictionaries containing:
        - similarity_score (0.0 to 1.0)
        - recency_score (0.0 to 1.0)
        - importance_score (0.0 to 1.0)
        - confidence_score (0.0 to 1.0)
        """
        ranked = []
        for cand in candidates:
            sim = cand.get("similarity_score", 0.5)
            rec = cand.get("recency_score", 0.5)
            imp = cand.get("importance_score", 0.5)
            conf = cand.get("confidence_score", 0.5)

            final_score = (
                (self.similarity_weight * sim)
                + (self.recency_weight * rec)
                + (self.importance_weight * imp)
                + (self.confidence_weight * conf)
            )
            cand_copy = dict(cand)
            cand_copy["final_score"] = final_score
            ranked.append(cand_copy)

        ranked.sort(key=lambda x: x["final_score"], reverse=True)
        return ranked
