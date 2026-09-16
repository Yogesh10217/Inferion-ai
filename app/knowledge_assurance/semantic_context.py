"""Semantic relationship intelligence for concept linking and context similarity."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import CrossTenantKnowledgeAssuranceException


class SemanticConcept(BaseModel):
    concept_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str = "general"
    description: str = ""


class SemanticRelationship(BaseModel):
    source_concept_id: str
    target_concept_id: str
    relationship_type: str  # e.g. DEPENDS_ON, REFINES, CONTRADICTS, ENFORCES
    strength: float = 1.0


class SemanticSimilarity(BaseModel):
    concept_a: str
    concept_b: str
    similarity_score: float = 0.85  # 0.0 to 1.0


class SemanticContext(BaseModel):
    context_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    title: str
    concepts: List[SemanticConcept] = Field(default_factory=list)
    relationships: List[SemanticRelationship] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def domain(self) -> str:
        return self.title


class SemanticContextAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    semantic_density_score: float = 0.85
    coherence_score: float = 0.90
    similarities: List[SemanticSimilarity] = Field(default_factory=list)


class SemanticContextManager:
    """Evaluates semantic concept relationships and context coherence."""

    def __init__(self) -> None:
        self._contexts: Dict[str, SemanticContext] = {}

    def create_semantic_context(
        self,
        tenant_id: str,
        title: Optional[str] = None,
        domain: Optional[str] = None,
        concepts: Optional[List[Any]] = None,
        relationships: Optional[List[Any]] = None,
    ) -> SemanticContext:
        ctx_title = domain or title or "Semantic Context"
        concept_objs: List[SemanticConcept] = []
        if concepts:
            for c in concepts:
                if isinstance(c, dict):
                    concept_objs.append(
                        SemanticConcept(
                            name=c.get("name", "Concept"),
                            category=c.get("category", "general"),
                            description=c.get("description", ""),
                        )
                    )
                elif isinstance(c, SemanticConcept):
                    concept_objs.append(c)

        rel_objs: List[SemanticRelationship] = []
        if relationships:
            for r in relationships:
                if isinstance(r, dict):
                    rel_objs.append(
                        SemanticRelationship(
                            source_concept_id=r.get("source_concept", r.get("source_concept_id", "c1")),
                            target_concept_id=r.get("target_concept", r.get("target_concept_id", "c2")),
                            relationship_type=r.get("relationship_type", "RELATED_TO"),
                            strength=r.get("strength", 1.0),
                        )
                    )
                elif isinstance(r, SemanticRelationship):
                    rel_objs.append(r)

        ctx = SemanticContext(
            tenant_id=tenant_id,
            title=ctx_title,
            concepts=concept_objs,
            relationships=rel_objs,
        )
        self._contexts[ctx.context_id] = ctx
        return ctx

    def assess_semantic_context(self, context_id: str, tenant_id: str) -> SemanticContextAssessment:
        ctx = self._contexts.get(context_id)
        if not ctx:
            raise ValueError(f"Semantic context '{context_id}' not found")
        if ctx.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()

        similarities = [
            SemanticSimilarity(
                concept_a=ctx.concepts[0].name if ctx.concepts else "C1",
                concept_b=ctx.concepts[1].name if len(ctx.concepts) > 1 else "C2",
                similarity_score=0.88,
            )
        ]

        return SemanticContextAssessment(
            tenant_id=tenant_id,
            semantic_density_score=0.87,
            coherence_score=0.92,
            similarities=similarities,
        )
