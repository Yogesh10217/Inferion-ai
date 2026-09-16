"""
Task Working Memory (Agent Scratchpad)
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkingMemory(BaseModel):
    goal: str = ""
    scratchpad: List[Dict[str, Any]] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)

    def add_step(self, step_name: str, result: Any) -> None:
        self.scratchpad.append({
            "step_name": step_name,
            "result": result
        })

    def set_variable(self, name: str, val: Any) -> None:
        self.variables[name] = val

    def get_variable(self, name: str, default: Optional[Any] = None) -> Any:
        return self.variables.get(name, default)

    def format_scratchpad(self) -> str:
        lines = []
        for idx, item in enumerate(self.scratchpad, 1):
            lines.append(f"[{idx}] {item['step_name']}: {item['result']}")
        return "\n".join(lines)
