"""Human review lifecycle states for Reliability Intelligence (Phase 5.55)."""

from app.reliability_intelligence.models import ReliabilityHumanReviewState


class ReliabilityHumanReviewLifecycle:
    """Manages human review lifecycle state machine."""

    @staticmethod
    def transition(current: ReliabilityHumanReviewState, target: ReliabilityHumanReviewState) -> ReliabilityHumanReviewState:
        valid_targets = {
            ReliabilityHumanReviewState.PENDING: {ReliabilityHumanReviewState.IN_REVIEW, ReliabilityHumanReviewState.APPROVED, ReliabilityHumanReviewState.REJECTED, ReliabilityHumanReviewState.CANCELLED},
            ReliabilityHumanReviewState.IN_REVIEW: {ReliabilityHumanReviewState.APPROVED, ReliabilityHumanReviewState.REJECTED, ReliabilityHumanReviewState.ESCALATED, ReliabilityHumanReviewState.EXPIRED},
            ReliabilityHumanReviewState.APPROVED: set(),
            ReliabilityHumanReviewState.REJECTED: set(),
            ReliabilityHumanReviewState.ESCALATED: {ReliabilityHumanReviewState.APPROVED, ReliabilityHumanReviewState.REJECTED},
            ReliabilityHumanReviewState.EXPIRED: set(),
            ReliabilityHumanReviewState.CANCELLED: set(),
        }

        if target in valid_targets.get(current, set()):
            return target
        return current
