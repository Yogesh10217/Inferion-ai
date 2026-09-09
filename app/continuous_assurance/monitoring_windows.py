"""Monitoring window definitions and policies for Continuous Assurance (Phase 5.54)."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class MonitoringWindowType(str, Enum):
    REALTIME = "REALTIME"
    SHORT_TERM = "SHORT_TERM"
    MEDIUM_TERM = "MEDIUM_TERM"
    LONG_TERM = "LONG_TERM"
    CUSTOM = "CUSTOM"


@dataclass
class MonitoringWindowPolicy:
    window_type: MonitoringWindowType
    duration_seconds: int
    max_observations_capacity: int = 1000
    prune_stale: bool = True
