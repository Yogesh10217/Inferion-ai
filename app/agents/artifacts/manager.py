"""
Agent Artifact Manager
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

from app.agents.artifacts.store import IArtifactStore, InMemoryArtifactStore

logger = logging.getLogger(__name__)


class ArtifactManager:
    def __init__(self, store: Optional[IArtifactStore] = None):
        self.store = store or InMemoryArtifactStore()

    async def create_artifact(
        self,
        session_id: str,
        name: str,
        content_type: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        artifact_id = f"art_{uuid.uuid4().hex[:12]}"
        artifact_data = {
            "artifact_id": artifact_id,
            "session_id": session_id,
            "name": name,
            "content_type": content_type,
            "content": content,
            "metadata": metadata or {}
        }
        await self.store.save(artifact_id, artifact_data)
        logger.info(f"Created artifact '{name}' ({artifact_id}) for session '{session_id}'")
        return artifact_data

    async def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        return await self.store.get(artifact_id)

    async def list_artifacts(self, session_id: str) -> List[Dict[str, Any]]:
        return await self.store.list_by_session(session_id)
