"""
Agent Team Lifecycle State Management
"""

from enum import Enum
from typing import Dict


class TeamStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TeamLifecycleManager:
    """Manages state transitions and active execution sessions for Agent Teams."""

    def __init__(self):
        self._states: Dict[str, TeamStatus] = {}

    def set_status(self, team_id: str, status: TeamStatus) -> None:
        self._states[team_id] = status

    def get_status(self, team_id: str) -> TeamStatus:
        return self._states.get(team_id, TeamStatus.CREATED)

    def pause(self, team_id: str) -> TeamStatus:
        self._states[team_id] = TeamStatus.PAUSED
        return TeamStatus.PAUSED

    def resume(self, team_id: str) -> TeamStatus:
        self._states[team_id] = TeamStatus.RUNNING
        return TeamStatus.RUNNING

    def cancel(self, team_id: str) -> TeamStatus:
        self._states[team_id] = TeamStatus.CANCELLED
        return TeamStatus.CANCELLED
