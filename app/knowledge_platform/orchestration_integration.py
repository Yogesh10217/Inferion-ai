"""Orchestration Platform Knowledge Adapter."""

import logging
from typing import Dict, Any, Optional

from app.knowledge_platform.context import ContextStrategy

logger = logging.getLogger(__name__)


class OrchestrationKnowledgeAdapter:
    """Selects context engineering strategies for the Orchestration Engine based on risk and cost criteria."""

    def select_context_strategy(self, risk_score: float = 0.0, max_budget: Optional[float] = None) -> ContextStrategy:
        if risk_score > 70.0:
            return ContextStrategy.RISK_AWARE
        if max_budget is not None and max_budget < 0.50:
            return ContextStrategy.COST_OPTIMIZED
        return ContextStrategy.RELEVANCE_FIRST
