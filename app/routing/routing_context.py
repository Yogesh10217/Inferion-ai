from dataclasses import dataclass, field
from typing import Any

@dataclass
class RoutingContext:
    request_metadata: dict = field(default_factory=dict)
    shadow_routing: bool = False
    decision_explanation: dict = field(default_factory=dict)
