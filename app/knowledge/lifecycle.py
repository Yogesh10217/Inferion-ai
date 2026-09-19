from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from .exceptions import StateTransitionError


class DocumentState(str, Enum):
    """Allowed states for a knowledge document lifecycle."""

    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    PURGED = "PURGED"


def transition_document_state(document, new_state: DocumentState, user_id: Optional[str] = None):
    """
    Handles state transitions for a document.
    Enforces soft-delete rules (ACTIVE -> ARCHIVED -> PURGED).

    Args:
        document: The KnowledgeDocument instance.
        new_state: The target DocumentState.
        user_id: The ID of the user requesting the state change.
    """
    if document.status == DocumentState.PURGED.value:
        raise StateTransitionError("Cannot transition a PURGED document.")

    now = datetime.now(timezone.utc)

    if new_state == DocumentState.ARCHIVED:
        document.status = DocumentState.ARCHIVED.value
        document.archived_at = now
        document.archived_by = user_id
    elif new_state == DocumentState.PURGED:
        document.status = DocumentState.PURGED.value
        document.purged_at = now
        document.purged_by = user_id
    elif new_state == DocumentState.ACTIVE:
        document.status = DocumentState.ACTIVE.value
        document.archived_at = None
        document.archived_by = None
    else:
        raise StateTransitionError(f"Unknown state: {new_state}")
