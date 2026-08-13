"""
Workflow Edge Definition & Condition Evaluator
"""

from typing import Optional, Dict, Any, Callable


class Edge:
    """Represents a directional edge between two graph nodes in a workflow DAG."""

    def __init__(
        self,
        source_node: str,
        target_node: str,
        condition: Optional[str] = None,
        condition_fn: Optional[Callable[[Dict[str, Any]], bool]] = None,
        priority: int = 0,
    ):
        self.source_node = source_node
        self.target_node = target_node
        self.condition = condition
        self.condition_fn = condition_fn
        self.priority = priority

    def evaluate_condition(self, context: Dict[str, Any]) -> bool:
        """Evaluates whether this edge condition passes based on execution context."""
        if self.condition_fn is not None:
            return self.condition_fn(context)

        if not self.condition or self.condition.strip() == "" or self.condition == "True":
            return True

        variables = context.get("variables", {})
        node_outputs = context.get("node_outputs", {})
        combined_env = {**variables, "node_outputs": node_outputs, "inputs": context.get("initial_inputs", {})}

        try:
            # Safe evaluation for simple expressions
            return bool(eval(self.condition, {"__builtins__": {}}, combined_env))
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_node": self.source_node,
            "target_node": self.target_node,
            "condition": self.condition,
            "priority": self.priority,
        }
