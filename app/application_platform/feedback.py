"""Feedback & Continuous Improvement Engine (Phase 5.22 - Component 11).

Captures user and operational feedback:
- Feedback types: POSITIVE, NEGATIVE, RATING, CORRECTION, ABANDONMENT, RETRY, ESCALATION, FAILURE_SIGNAL
- Generates governance-gated improvement recommendations. No automatic production changes without governance evaluation.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FeedbackType(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    RATING = "RATING"
    CORRECTION = "CORRECTION"
    ABANDONMENT = "ABANDONMENT"
    RETRY = "RETRY"
    ESCALATION = "ESCALATION"
    FAILURE_SIGNAL = "FAILURE_SIGNAL"


class FeedbackSignal(BaseModel):
    """Raw feedback signal data."""

    signal_id: str = Field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:12]}")
    feedback_type: FeedbackType
    score: Optional[float] = None  # e.g. 1-5 rating or -1.0 to +1.0
    text_comment: str = ""
    corrected_output: str = ""


class ImprovementRecommendation(BaseModel):
    """Continuous improvement recommendation requiring governance review prior to production application."""

    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    application_id: str
    tenant_id: str
    target_component: str = "PROMPT"  # PROMPT, KNOWLEDGE, MODEL, WORKFLOW
    proposed_change: str
    evidence_count: int = 1
    requires_approval: bool = True
    approved_by_governance: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ApplicationFeedback(BaseModel):
    """Recorded application feedback entity."""

    feedback_id: str = Field(default_factory=lambda: f"fb_{uuid.uuid4().hex[:12]}")
    application_id: str
    tenant_id: str
    execution_id: str
    user_id: str = "anonymous"
    signal: FeedbackSignal
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FeedbackManager:
    """Manages collection of feedback signals and generation of recommendations."""

    def __init__(self) -> None:
        self._feedback_records: Dict[str, ApplicationFeedback] = {}
        self._recommendations: Dict[str, ImprovementRecommendation] = {}

    def submit_feedback(
        self,
        tenant_id: str,
        application_id: str,
        execution_id: str,
        feedback_type: FeedbackType,
        score: Optional[float] = None,
        comment: str = "",
        corrected_output: str = "",
        user_id: str = "anonymous",
    ) -> ApplicationFeedback:
        sig = FeedbackSignal(
            feedback_type=feedback_type,
            score=score,
            text_comment=comment,
            corrected_output=corrected_output,
        )
        fb = ApplicationFeedback(
            application_id=application_id,
            tenant_id=tenant_id,
            execution_id=execution_id,
            user_id=user_id,
            signal=sig,
        )
        self._feedback_records[fb.feedback_id] = fb
        logger.info(f"[FEEDBACK MANAGER] Submitted feedback {fb.feedback_id} ({feedback_type.value}) for app {application_id}")

        # Automatically generate improvement recommendation if correction is supplied
        if corrected_output:
            self.create_recommendation(
                tenant_id=tenant_id,
                application_id=application_id,
                target_component="PROMPT",
                proposed_change=f"Refine prompt instructions using corrected output: '{corrected_output[:50]}...'",
            )

        return fb

    def create_recommendation(
        self,
        tenant_id: str,
        application_id: str,
        target_component: str,
        proposed_change: str,
    ) -> ImprovementRecommendation:
        rec = ImprovementRecommendation(
            application_id=application_id,
            tenant_id=tenant_id,
            target_component=target_component,
            proposed_change=proposed_change,
            requires_approval=True,
            approved_by_governance=False,
        )
        self._recommendations[rec.recommendation_id] = rec
        return rec

    def list_feedback(self, tenant_id: str, application_id: str) -> List[ApplicationFeedback]:
        return [
            fb for fb in self._feedback_records.values()
            if fb.tenant_id == tenant_id and fb.application_id == application_id
        ]

    def list_recommendations(self, tenant_id: str, application_id: str) -> List[ImprovementRecommendation]:
        return [
            rec for rec in self._recommendations.values()
            if rec.tenant_id == tenant_id and rec.application_id == application_id
        ]
