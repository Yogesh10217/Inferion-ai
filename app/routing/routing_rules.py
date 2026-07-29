class RoutingRule:
    def __init__(self, priority: int, condition: str, target_policy: str):
        self.priority = priority
        self.condition = condition
        self.target_policy = target_policy

class RuleEngine:
    def evaluate(self, context) -> str:
        return "default"
