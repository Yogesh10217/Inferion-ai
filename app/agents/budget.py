"""
Agent Cost & Token Budget Controller
"""

import logging
from typing import Optional

from app.agents.exceptions import BudgetExceededException

logger = logging.getLogger(__name__)


class AgentBudgetTracker:
    def __init__(self, max_cost_dollars: Optional[float] = None, max_tokens: Optional[int] = None):
        self.max_cost_dollars = max_cost_dollars
        self.max_tokens = max_tokens
        self.consumed_tokens = 0
        self.consumed_cost_dollars = 0.0

    def add_usage(self, prompt_tokens: int, completion_tokens: int, estimated_cost: float = 0.0) -> None:
        total_new_tokens = prompt_tokens + completion_tokens
        self.consumed_tokens += total_new_tokens
        self.consumed_cost_dollars += estimated_cost

        logger.debug(
            f"Budget update: tokens={self.consumed_tokens}/{self.max_tokens}, cost=${self.consumed_cost_dollars:.4f}/${self.max_cost_dollars}"
        )

        self.check_limits()

    def check_limits(self) -> None:
        if self.max_tokens is not None and self.consumed_tokens > self.max_tokens:
            raise BudgetExceededException(
                f"Token budget exceeded: consumed {self.consumed_tokens} tokens (limit: {self.max_tokens})"
            )
        if self.max_cost_dollars is not None and self.consumed_cost_dollars > self.max_cost_dollars:
            raise BudgetExceededException(
                f"Cost budget exceeded: consumed ${self.consumed_cost_dollars:.4f} (limit: ${self.max_cost_dollars})"
            )
