"""
Memory Platform Analytics & Storage Metrics Aggregator
"""

from typing import Any, Dict


class MemoryAnalyticsService:
    """Aggregates memory usage stats, storage consumption, and tier counts."""

    def __init__(self):
        self._reads = 0
        self._writes = 0
        self._searches = 0
        self._compressions = 0
        self._expirations = 0

    def record_read(self) -> None:
        self._reads += 1

    def record_write(self) -> None:
        self._writes += 1

    def record_search(self) -> None:
        self._searches += 1

    def record_compression(self) -> None:
        self._compressions += 1

    def record_expiration(self) -> None:
        self._expirations += 1

    def get_analytics(self) -> Dict[str, Any]:
        return {
            "total_reads": self._reads,
            "total_writes": self._writes,
            "total_searches": self._searches,
            "total_compressions": self._compressions,
            "total_expirations": self._expirations,
        }
