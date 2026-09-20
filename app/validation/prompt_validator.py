import logging
from app.core.exceptions import ValidationError
from app.schemas.request import ChatMessage

logger = logging.getLogger(__name__)


class PromptValidator:
    """Validates prompt text and chat messages before inference execution."""

    def __init__(self, max_total_chars: int = 128000, max_single_message_chars: int = 64000) -> None:
        self.max_total_chars = max_total_chars
        self.max_single_message_chars = max_single_message_chars

    def validate_messages(self, messages: list[ChatMessage]) -> None:
        """Validate a list of ChatMessage objects."""
        if not messages:
            raise ValidationError("Chat completion payload must contain at least one message.")

        total_chars = 0
        valid_roles = {"system", "user", "assistant", "tool"}

        for idx, msg in enumerate(messages):
            if msg.role not in valid_roles:
                raise ValidationError(f"Invalid message role '{msg.role}' at index {idx}.")

            content_len = len(msg.content or "")
            if content_len > self.max_single_message_chars:
                raise ValidationError(
                    f"Message at index {idx} exceeds maximum allowed character length of {self.max_single_message_chars}."
                )

            total_chars += content_len

        if total_chars > self.max_total_chars:
            raise ValidationError(
                f"Total request prompt length ({total_chars} chars) exceeds maximum limit of {self.max_total_chars}."
            )
