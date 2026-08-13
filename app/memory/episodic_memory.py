"""
Episodic Memory (Tier 6): Completed Event Episode Logging & Historical Recall
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class EpisodeRecord:
    def __init__(
        self,
        episode_type: str,
        source_id: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None,
        episode_id: Optional[str] = None,
    ):
        self.episode_id = episode_id or f"ep_{uuid.uuid4().hex[:12]}"
        self.episode_type = episode_type
        self.source_id = source_id
        self.summary = summary
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "episode_type": self.episode_type,
            "source_id": self.source_id,
            "summary": self.summary,
            "details": self.details,
            "timestamp": self.timestamp,
        }


class EpisodicMemory:
    """Stores completed event episodes enabling historical reasoning and recall."""

    def __init__(self):
        self._episodes: Dict[str, EpisodeRecord] = {}

    def record_episode(
        self,
        episode_type: str,
        source_id: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> EpisodeRecord:
        record = EpisodeRecord(
            episode_type=episode_type,
            source_id=source_id,
            summary=summary,
            details=details,
        )
        self._episodes[record.episode_id] = record
        return record

    def retrieve_episode(self, episode_id: str) -> EpisodeRecord:
        if episode_id not in self._episodes:
            raise KeyError(f"Episode '{episode_id}' not found")
        return self._episodes[episode_id]

    def search_episodes(self, query: str, episode_type: Optional[str] = None, top_k: int = 10) -> List[EpisodeRecord]:
        results = list(self._episodes.values())
        if episode_type:
            results = [ep for ep in results if ep.episode_type == episode_type]
        
        query_words = set(query.lower().split())
        
        def match_score(ep: EpisodeRecord) -> int:
            words = set(ep.summary.lower().split())
            return len(query_words.intersection(words))

        results.sort(key=match_score, reverse=True)
        return results[:top_k]

    def summarize_episode(self, episode_id: str) -> str:
        record = self.retrieve_episode(episode_id)
        return f"Episode [{record.episode_type}] ({record.source_id}): {record.summary}"
