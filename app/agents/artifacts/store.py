"""
Agent Artifact Storage Repository
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IArtifactStore(ABC):
    @abstractmethod
    async def save(self, artifact_id: str, data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def get(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def list_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        pass


class InMemoryArtifactStore(IArtifactStore):
    def __init__(self):
        self._artifacts: Dict[str, Dict[str, Any]] = {}

    async def save(self, artifact_id: str, data: Dict[str, Any]) -> None:
        data["created_at"] = data.get("created_at", time.time())
        self._artifacts[artifact_id] = data

    async def get(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        return self._artifacts.get(artifact_id)

    async def list_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        return [
            item for item in self._artifacts.values()
            if item.get("session_id") == session_id
        ]
