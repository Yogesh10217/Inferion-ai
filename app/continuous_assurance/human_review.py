"""Human review lifecycle states for Continuous Assurance (Phase 5.54)."""

from app.continuous_assurance.models import HumanReviewState


class HumanReviewLifecycle:
    """Manages human review lifecycle state machine."""

    @staticmethod
    def transition(current: HumanReviewState, target: HumanReviewState) -> HumanReviewState:
        valid_targets = {
            HumanReviewState.PENDING: {
                HumanReviewState.IN_REVIEW,
                HumanReviewState.APPROVED,
                HumanReviewState.REJECTED,
                HumanReviewState.CANCELLED,
            },
            HumanReviewState.IN_REVIEW: {
                HumanReviewState.APPROVED,
                HumanReviewState.REJECTED,
                HumanReviewState.ESCALATED,
                HumanReviewState.EXPIRED,
            },
            HumanReviewState.APPROVED: set(),
            HumanReviewState.REJECTED: set(),
            HumanReviewState.ESCALATED: {HumanReviewState.APPROVED, HumanReviewState.REJECTED},
            HumanReviewState.EXPIRED: set(),
            HumanReviewState.CANCELLED: set(),
        }

        if target in valid_targets.get(current, set()):
            return target
        return current
