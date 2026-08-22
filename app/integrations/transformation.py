"""Data Transformation, Field Mapping & Redaction Subsystem."""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.security.secrets import SecretManager

logger = logging.getLogger(__name__)


class FieldMapping(BaseModel):
    source_field: str
    target_field: str
    redact_sensitive: bool = False


class TransformationPipeline:
    """Transforms, maps, renames, and redacts external payloads before passing to internal subsystems."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.secret_manager = secret_manager or SecretManager()

    def transform(self, payload: Dict[str, Any], mappings: List[FieldMapping]) -> Dict[str, Any]:
        transformed = {}
        for m in mappings:
            val = payload.get(m.source_field)
            if val is not None:
                if m.redact_sensitive:
                    val = "[REDACTED]"
                transformed[m.target_field] = val
            else:
                transformed[m.target_field] = payload.get(m.target_field)

        # Copy unmapped fields while sanitizing strings
        for k, v in payload.items():
            if k not in transformed:
                if isinstance(v, str):
                    transformed[k] = self.secret_manager.sanitize_text(v)
                else:
                    transformed[k] = v

        logger.info(f"[TRANSFORMATION PIPELINE] Transformed payload with {len(mappings)} field mappings")
        return transformed
