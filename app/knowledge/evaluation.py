from typing import List

from pydantic import BaseModel


class RetrievalResult(BaseModel):
    """Mock Retrieval Result for evaluation."""

    chunk_id: str
    document_id: str
    score: float
    content: str
    is_relevant: bool = False


class EvaluationMetrics(BaseModel):
    """Retrieval metrics structure."""

    recall_at_k: float = 0.0
    mrr: float = 0.0
    ndcg: float = 0.0
    precision_at_k: float = 0.0
    hit_rate: float = 0.0


def calculate_recall_at_k(results: List[RetrievalResult], total_relevant: int, k: int) -> float:
    if total_relevant == 0:
        return 0.0
    top_k = results[:k]
    relevant_in_top_k = sum(1 for r in top_k if r.is_relevant)
    return relevant_in_top_k / total_relevant


def calculate_mrr(results: List[RetrievalResult]) -> float:
    for i, r in enumerate(results):
        if r.is_relevant:
            return 1.0 / (i + 1)
    return 0.0


def calculate_hit_rate(results: List[RetrievalResult], k: int) -> float:
    top_k = results[:k]
    return 1.0 if any(r.is_relevant for r in top_k) else 0.0


def evaluate_retrieval(results: List[RetrievalResult], total_relevant: int, k: int = 5) -> EvaluationMetrics:
    """
    Calculate core retrieval metrics (Recall@K, MRR, nDCG placeholder, Precision@K, Hit Rate).
    """
    if not results:
        return EvaluationMetrics()

    metrics = EvaluationMetrics()
    metrics.recall_at_k = calculate_recall_at_k(results, total_relevant, k)
    metrics.mrr = calculate_mrr(results)
    metrics.hit_rate = calculate_hit_rate(results, k)
    # Simple Precision at K
    metrics.precision_at_k = sum(1 for r in results[:k] if r.is_relevant) / min(len(results), k) if results else 0.0

    return metrics
