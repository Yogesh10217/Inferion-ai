"""Sensitive Data Detection, Masking, and Redaction Subsystem."""

import re
import logging
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SensitiveDataAction(str, Enum):
    ALLOW = "ALLOW"
    MASK = "MASK"
    REDACT = "REDACT"
    BLOCK = "BLOCK"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class DetectedSensitivity(BaseModel):
    pattern_name: str
    match_count: int
    sample_masked: str


class SensitiveDataDetector:
    """Detects API keys, passwords, bearer tokens, SSNs, credit cards, emails, and phone numbers."""

    PATTERNS = {
        "API_KEY": re.compile(r"(?:api[_-]?key|sk[_-]live|secret[_-]?key)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{16,})['\"]?", re.IGNORECASE),
        "BEARER_TOKEN": re.compile(r"Bearer\s+([A-Za-z0-9\-._~+/]+=*)", re.IGNORECASE),
        "CREDIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
        "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "PHONE": re.compile(r"\b\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b"),
    }

    def detect_sensitive_data(self, text_or_dict: Any) -> List[DetectedSensitivity]:
        text = str(text_or_dict)
        detections: List[DetectedSensitivity] = []

        for name, pattern in self.PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                sample = str(matches[0])
                masked_sample = sample[:2] + "*" * (len(sample) - 4) + sample[-2:] if len(sample) > 4 else "****"
                detections.append(DetectedSensitivity(pattern_name=name, match_count=len(matches), sample_masked=masked_sample))

        return detections


class RedactionEngine:
    """Sanitizes sensitive patterns in strings, dictionaries, or log payloads."""

    def __init__(self, detector: Optional[SensitiveDataDetector] = None) -> None:
        self.detector = detector or SensitiveDataDetector()

    def sanitize(self, content: Any, action: SensitiveDataAction = SensitiveDataAction.MASK) -> Any:
        if action == SensitiveDataAction.ALLOW:
            return content

        if isinstance(content, dict):
            sanitized_dict = {}
            for k, v in content.items():
                if any(kw in k.lower() for kw in ("password", "secret", "token", "api_key", "auth")):
                    sanitized_dict[k] = "[REDACTED_SECRET]" if action == SensitiveDataAction.REDACT else "********"
                else:
                    sanitized_dict[k] = self.sanitize(v, action=action)
            return sanitized_dict

        text = str(content)
        if action == SensitiveDataAction.REDACT:
            for name, pattern in self.detector.PATTERNS.items():
                text = pattern.sub(f"[{name}_REDACTED]", text)
        elif action == SensitiveDataAction.MASK:
            for name, pattern in self.detector.PATTERNS.items():
                text = pattern.sub(lambda m: m.group(0)[:2] + "*" * max(0, len(m.group(0)) - 4) + m.group(0)[-2:] if len(m.group(0)) > 4 else "****", text)

        return text
