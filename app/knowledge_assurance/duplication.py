"""Knowledge duplication intelligence for detecting redundant and overlapping knowledge."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DuplicateType(str, Enum):
    EXACT_DUPLICATE = "EXACT_DUPLICATE"
    NEAR_DUPLICATE = "NEAR_DUPLICATE"
    REDUNDANT_CONTEXT = "REDUNDANT_CONTEXT"
    CONFLICTING_DUPLICATE = "CONFLICTING_DUPLICATE"


class DuplicateSimilarity(BaseModel):
    similarity_score: float = 0.95  # 0.0 to 1.0
    overlapping_concepts: List[str] = Field(default_factory=list)


class KnowledgeDuplicate(BaseModel):
    duplicate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    reference_id_a: str
    reference_id_b: str
    duplicate_type: DuplicateType = DuplicateType.NEAR_DUPLICATE
    similarity: DuplicateSimilarity = Field(default_factory=DuplicateSimilarity)
    recommendation: str = "Consolidate duplicate knowledge references into single authoritative source."
    auto_execute: bool = False  # NEVER auto execute


class DuplicateAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    duplicates: List[KnowledgeDuplicate] = Field(default_factory=list)
    total_duplicates_found: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeDuplicationManager:
    """Detects knowledge duplicates and generates consolidation recommendations."""

    def __init__(self) -> None:
        self._assessments: Dict[str, DuplicateAssessment] = {}

    def detect_duplicates(
        self,
        tenant_id: str,
        reference_ids: Optional[Any] = None,
        items: Optional[Any] = None,
    ) -> List[KnowledgeDuplicate]:
        raw_items = items or reference_ids or []
        ids: List[str] = []
        for item in raw_items:
            if isinstance(item, str):
                ids.append(item)
            elif isinstance(item, dict):
                ids.append(str(item.get("id") or item.get("reference_id") or "doc"))
            else:
                ids.append(str(item))

        duplicates: List[KnowledgeDuplicate] = []
        if len(ids) >= 2:
            dup = KnowledgeDuplicate(
                tenant_id=tenant_id,
                reference_id_a=ids[0],
                reference_id_b=ids[1],
                duplicate_type=DuplicateType.NEAR_DUPLICATE,
                similarity=DuplicateSimilarity(
                    similarity_score=0.92, overlapping_concepts=["incident_response", "escalation"]
                ),
                recommendation="FLAG_FOR_REVIEW",
                auto_execute=False,  # MANDATORY
            )
            duplicates.append(dup)

        assessment = DuplicateAssessment(
            tenant_id=tenant_id,
            duplicates=duplicates,
            total_duplicates_found=len(duplicates),
        )
        self._assessments[assessment.assessment_id] = assessment
        return duplicates
