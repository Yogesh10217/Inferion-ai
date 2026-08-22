"""
Chain-of-Thought & Multi-Path Reasoning Engine
"""

import logging
from typing import Dict, Any, List, Optional
from app.reasoning.tree_of_thoughts import TreeOfThoughtsEngine
from app.reasoning.reflection_engine import ReflectionEngine
from app.reasoning.critique_engine import CritiqueEngine
from app.reasoning.decision_engine import PlanningDecisionEngine, StrategyOption

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """Orchestrates Chain of Thought, Tree of Thoughts, Self-Critique, and Strategy Evaluation."""

    def __init__(self):
        self.tot_engine = TreeOfThoughtsEngine()
        self.reflection_engine = ReflectionEngine()
        self.critique_engine = CritiqueEngine()
        self.decision_engine = PlanningDecisionEngine()

    def reason(self, prompt: str, strategy: str = "chain_of_thought") -> Dict[str, Any]:
        """Perform reasoning on a prompt using specified strategy."""
        if strategy == "tree_of_thoughts":
            tot_res = self.tot_engine.search_best_path(prompt)
            steps = tot_res["best_path"]
            confidence = tot_res["best_score"]
        else:
            # Chain of Thought
            steps = [
                f"Step 1: Understand the objective '{prompt}'",
                f"Step 2: Identify constraints and required resources",
                f"Step 3: Formulate execution plan and verify safety boundaries",
                f"Step 4: Execute actions and synthesize final answer",
            ]
            confidence = 0.95

        output_text = f"Reasoning output for '{prompt}':\n" + "\n".join(steps)
        critique = self.critique_engine.critique_output(output_text, reasoning_chain=steps)

        return {
            "prompt": prompt,
            "strategy": strategy,
            "reasoning_steps": steps,
            "confidence_score": confidence,
            "is_valid": critique.is_valid,
            "critique": critique.model_dump(),
        }

    def generate_alternatives(self, prompt: str) -> List[StrategyOption]:
        return [
            StrategyOption(name="Fast Strategy", description="Minimal latency path", estimated_cost=0.005, estimated_duration_seconds=3.0, confidence_score=0.85),
            StrategyOption(name="Balanced Strategy", description="Recommended standard path", estimated_cost=0.01, estimated_duration_seconds=8.0, confidence_score=0.92),
            StrategyOption(name="Thorough Strategy", description="Comprehensive verification path", estimated_cost=0.025, estimated_duration_seconds=20.0, confidence_score=0.98),
        ]

    def evaluate_options(self, prompt: str) -> Dict[str, Any]:
        alts = self.generate_alternatives(prompt)
        outcome = self.decision_engine.evaluate_strategies(alts)
        return outcome.model_dump()
