"""
Memory Subsystem Type Definitions & Enums
"""

from enum import Enum


class MemoryType(str, Enum):
    WORKING = "WORKING"
    CONVERSATION = "CONVERSATION"
    SEMANTIC = "SEMANTIC"
    PROFILE = "PROFILE"
    SESSION = "SESSION"
    EPISODIC = "EPISODIC"


class RetentionPolicy(str, Enum):
    EPHEMERAL = "EPHEMERAL"
    SESSION = "SESSION"
    TTL_30_DAYS = "TTL_30_DAYS"
    TTL_90_DAYS = "TTL_90_DAYS"
    PERMANENT = "PERMANENT"
    ARCHIVE = "ARCHIVE"


class MemoryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    EXPIRED = "EXPIRED"
    DELETED = "DELETED"
