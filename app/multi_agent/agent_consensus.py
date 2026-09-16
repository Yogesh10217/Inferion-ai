"""
Consensus & Voting Engine for Multi-Agent Decision Making
"""

import logging
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.multi_agent.exceptions import ConsensusFailedError

logger = logging.getLogger(__name__)


class ConsensusStrategy(str, Enum):
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_VOTE = "weighted_vote"
    UNANIMOUS_APPROVAL = "unanimous_approval"
    SUPERVISOR_APPROVAL = "supervisor_approval"
    CONFIDENCE_SCORING = "confidence_scoring"


class ConsensusResult(BaseModel):
    decision: str
    is_agreed: bool
    strategy: ConsensusStrategy
    confidence_score: float = 1.0
    voting_breakdown: Dict[str, Any] = Field(default_factory=dict)
    summary: str = ""


class ConsensusEngine:
    """Consensus engine for resolving decisions across multi-agent votes."""

    @staticmethod
    def evaluate_consensus(
        votes: Dict[str, str],  # agent_id -> option/choice
        strategy: ConsensusStrategy = ConsensusStrategy.MAJORITY_VOTE,
        weights: Optional[Dict[str, float]] = None,
        threshold: float = 0.5,
    ) -> ConsensusResult:
        if not votes:
            raise ConsensusFailedError("No votes provided for consensus evaluation")

        total_votes = len(votes)
        counts: Dict[str, float] = {}

        if strategy == ConsensusStrategy.WEIGHTED_VOTE and weights:
            for aid, choice in votes.items():
                w = weights.get(aid, 1.0)
                counts[choice] = counts.get(choice, 0.0) + w
            total_weight = sum(weights.values()) or 1.0
            winning_choice, win_score = max(counts.items(), key=lambda x: x[1])
            confidence = win_score / total_weight
            agreed = confidence >= threshold
        elif strategy == ConsensusStrategy.UNANIMOUS_APPROVAL:
            unique_choices = set(votes.values())
            winning_choice = list(unique_choices)[0]
            agreed = len(unique_choices) == 1
            confidence = 1.0 if agreed else (1.0 / len(unique_choices))
            for choice in votes.values():
                counts[choice] = counts.get(choice, 0.0) + 1.0
        else:
            # Default Majority Vote / Confidence Scoring
            for choice in votes.values():
                counts[choice] = counts.get(choice, 0.0) + 1.0
            winning_choice, win_count = max(counts.items(), key=lambda x: x[1])
            confidence = win_count / float(total_votes)
            agreed = (win_count / float(total_votes)) >= threshold

        result = ConsensusResult(
            decision=winning_choice,
            is_agreed=agreed,
            strategy=strategy,
            confidence_score=confidence,
            voting_breakdown={"raw_votes": votes, "counts": counts, "total": total_votes},
            summary=f"Consensus '{winning_choice}' agreed={agreed} confidence={confidence:.2f} ({strategy.value})",
        )
        logger.info(f"[CONSENSUS] Decision '{winning_choice}' (agreed={agreed}, confidence={confidence:.2f})")
        return result
