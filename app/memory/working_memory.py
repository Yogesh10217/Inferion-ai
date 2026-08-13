"""
Working Memory (Tier 1): In-Memory Execution Scratchpad
"""

from typing import Dict, Any, Optional


class WorkingMemory:
    """In-memory scratchpad for execution context, tool results, planner & reflection states."""

    def __init__(self, execution_id: Optional[str] = None):
        self.execution_id = execution_id or "local"
        self._store: Dict[str, Any] = {}

    def put(self, key: str, value: Any) -> None:
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def remove(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> None:
        self._store.clear()

    def snapshot(self) -> Dict[str, Any]:
        return dict(self._store)

    def restore(self, snapshot_data: Dict[str, Any]) -> None:
        self._store = dict(snapshot_data)
