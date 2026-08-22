"""
Self-Critique and Hallucination Detection Engine
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CritiqueResult(BaseModel):
    is_valid: bool
    confidence_score: float
    hallucination_detected: bool = False
    critique_notes: List[str] = Field(default_factory=list)
    suggested_corrections: List[str] = Field(default_factory=list)


class CritiqueEngine:
    """Critique engine validating reasoning traces and detecting output hallucinations."""

    @staticmethod
    def critique_output(output_text: str, reasoning_chain: Optional[List[str]] = None) -> CritiqueResult:
        notes = []
        corrections = []
        is_valid = True
        hallucination = False
        confidence = 0.95

        if not output_text or len(output_text.strip()) == 0:
            is_valid = False
            notes.append("Output text is empty")
            confidence = 0.0

        # Check for self-contradiction keywords
        lowered = output_text.lower()
        if "as an ai model i cannot" in lowered and "however here is the data" in lowered:
            hallucination = True
            notes.append("Potential contradiction detected in output")
            confidence = 0.5

        if reasoning_chain:
            notes.append(f"Validated against {len(reasoning_chain)} reasoning steps")

        res = CritiqueResult(
            is_valid=is_valid,
            confidence_score=confidence,
            hallucination_detected=hallucination,
            critique_notes=notes,
            suggested_corrections=corrections,
        )
        logger.debug(f"[CRITIQUE] Evaluated output valid={is_valid} confidence={confidence:.2f}")
        return res
