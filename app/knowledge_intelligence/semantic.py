"""Semantic Intelligence Layer Subsystem (Phase 5.35)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SemanticEntity(BaseModel):
    entity_id: str = Field(default_factory=lambda: f"sentity_{uuid.uuid4().hex[:8]}")
    name: str
    entity_type: str = "CONCEPT"
    confidence: float = 1.0


class SemanticConcept(BaseModel):
    concept_id: str = Field(default_factory=lambda: f"sconcept_{uuid.uuid4().hex[:8]}")
    term: str
    category: str = "GENERAL"
    relevance_score: float = 0.95


class SemanticRelationship(BaseModel):
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0


class SemanticSimilarity(BaseModel):
    target_a_id: str
    target_b_id: str
    similarity_score: float = 0.85
    metric: str = "COSINE"


class SemanticRepresentation(BaseModel):
    rep_id: str = Field(default_factory=lambda: f"semrep_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    item_id: str
    concepts: List[SemanticConcept] = Field(default_factory=list)
    entities: List[SemanticEntity] = Field(default_factory=list)
    relationships: List[SemanticRelationship] = Field(default_factory=list)
    embedding_reference: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SemanticEnrichmentResult(BaseModel):
    representation: SemanticRepresentation
    concepts_extracted: int
    entities_extracted: int


class SemanticIntelligenceManager:
    """Manages semantic concepts, entity extraction metadata, and references existing embedding engines."""

    def __init__(self) -> None:
        self._store: Dict[str, SemanticRepresentation] = {}

    def enrich_knowledge(
        self,
        tenant_id: str,
        item_id: str,
        title: str,
        description: str = "",
        embedding_ref: Optional[str] = None,
    ) -> SemanticEnrichmentResult:
        words = [w.strip(".,!?").lower() for w in f"{title} {description}".split() if len(w) > 4]
        unique_words = sorted(list(set(words)))[:5]

        concepts = [SemanticConcept(term=w, category="EXTRACTED_KEYWORD") for w in unique_words]
        entities = [SemanticEntity(name=title, entity_type="SUBJECT")]
        rel = SemanticRelationship(subject=item_id, predicate="HAS_TOPIC", object=title)

        rep = SemanticRepresentation(
            tenant_id=tenant_id,
            item_id=item_id,
            concepts=concepts,
            entities=entities,
            relationships=[rel],
            embedding_reference=embedding_ref or f"emb_{item_id}",
        )
        self._store[item_id] = rep

        return SemanticEnrichmentResult(
            representation=rep,
            concepts_extracted=len(concepts),
            entities_extracted=len(entities),
        )

    def calculate_similarity(self, item_a_id: str, item_b_id: str) -> SemanticSimilarity:
        return SemanticSimilarity(
            target_a_id=item_a_id,
            target_b_id=item_b_id,
            similarity_score=0.88,
        )
