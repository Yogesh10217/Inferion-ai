"""
Retrieval Profiles.
Pre-defined configurations for different retrieval strategies.
"""
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class RetrievalStrategy(str, Enum):
    DENSE = "dense"
    SPARSE = "sparse"
    HYBRID = "hybrid"

class RetrievalProfile(BaseModel):
    """Configuration profile for retrieval."""
    name: str
    strategy: RetrievalStrategy
    top_k: int
    alpha: Optional[float] = 0.5  # For hybrid search weighting
    use_reranker: bool = False
    reranker_top_n: Optional[int] = None
    namespace: Optional[str] = None

class Profiles:
    """Pre-defined retrieval profiles."""
    FAST_SEARCH = RetrievalProfile(
        name="Fast Search",
        strategy=RetrievalStrategy.DENSE,
        top_k=5,
        use_reranker=False
    )
    
    BALANCED = RetrievalProfile(
        name="Balanced",
        strategy=RetrievalStrategy.HYBRID,
        top_k=10,
        alpha=0.5,
        use_reranker=True,
        reranker_top_n=5
    )
    
    HIGH_RECALL = RetrievalProfile(
        name="High Recall",
        strategy=RetrievalStrategy.HYBRID,
        top_k=25,
        alpha=0.3,
        use_reranker=True,
        reranker_top_n=10
    )
    
    HIGH_PRECISION = RetrievalProfile(
        name="High Precision",
        strategy=RetrievalStrategy.DENSE,
        top_k=20,
        use_reranker=True,
        reranker_top_n=3
    )
    
    SEMANTIC = RetrievalProfile(
        name="Semantic",
        strategy=RetrievalStrategy.DENSE,
        top_k=10,
        use_reranker=False
    )
    
    HYBRID = RetrievalProfile(
        name="Hybrid",
        strategy=RetrievalStrategy.HYBRID,
        top_k=15,
        alpha=0.5,
        use_reranker=False
    )
    
    CITATION_HEAVY = RetrievalProfile(
        name="Citation Heavy",
        strategy=RetrievalStrategy.HYBRID,
        top_k=30,
        alpha=0.5,
        use_reranker=True,
        reranker_top_n=10
    )
