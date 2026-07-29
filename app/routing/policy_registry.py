from .routing_policy import RoutingPolicy

class PolicyRegistry:
    def __init__(self):
        self.policies = {}
        
    def add_policy(self, policy: RoutingPolicy):
        self.policies[policy.name] = policy
