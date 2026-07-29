from typing import Dict, Any, Optional


class RoutingPolicy:
    """Configurable routing policy defining scoring weights and constraints."""

    DEFAULT_WEIGHTS = {
        "health": 0.35,
        "latency": 0.25,
        "cost": 0.15,
        "success_rate": 0.15,
        "capability_match": 0.05,
        "org_policy": 0.05,
    }

    def __init__(
        self,
        name: str,
        weights: Optional[Dict[str, float]] = None,
        priority: int = 10,
        description: str = "",
        organization_id: Optional[str] = None,
        is_default: bool = False,
    ):
        self.name = name
        self.weights = self._normalize_weights(weights or self.DEFAULT_WEIGHTS)
        self.priority = priority
        self.description = description
        self.organization_id = organization_id
        self.is_default = is_default

    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        total = sum(weights.values())
        if total <= 0:
            return dict(self.DEFAULT_WEIGHTS)
        return {k: v / total for k, v in weights.items()}

    def get_weight(self, key: str) -> float:
        return self.weights.get(key, 0.0)

    def calculate_score(self, metrics: Dict[str, float]) -> float:
        """Calculate weighted score given normalized metric components (0.0 to 1.0 each)."""
        score = 0.0
        for key, weight in self.weights.items():
            value = metrics.get(key, 0.5)
            # Clamp value between 0.0 and 1.0
            clamped_val = max(0.0, min(1.0, value))
            score += weight * clamped_val
        return score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "weights": self.weights,
            "priority": self.priority,
            "description": self.description,
            "organization_id": self.organization_id,
            "is_default": self.is_default,
        }
