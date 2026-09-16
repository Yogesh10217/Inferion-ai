"""
HIPAA & Privacy Compliance PHI/PII Detector Module.

Scans text prompts and outputs for Protected Health Information (PHI) and PII
such as SSNs, Credit Cards, Medical Record Numbers (MRN), and Email addresses.
"""

import re
from typing import Dict, List

from pydantic import BaseModel


class PHIMatch(BaseModel):
    category: str  # SSN, CREDIT_CARD, EMAIL, PHONE, MRN
    matched_text: str
    start_char: int
    end_char: int


class PHIDetectorResult(BaseModel):
    contains_phi: bool
    matches: List[PHIMatch]
    sanitized_text: str


class PHIDetector:
    """Regex + Heuristic PHI / PII Scanner and Sanitizer."""

    PATTERNS: Dict[str, str] = {
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "PHONE": r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b",
        "MRN": r"\bMRN[-\s]?\d{6,9}\b",
    }

    def scan(self, text: str) -> PHIDetectorResult:
        matches: List[PHIMatch] = []
        sanitized = text

        for cat, pattern in self.PATTERNS.items():
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(
                    PHIMatch(
                        category=cat,
                        matched_text=m.group(0),
                        start_char=m.start(),
                        end_char=m.end(),
                    )
                )
                sanitized = sanitized.replace(m.group(0), f"[REDACTED_{cat}]")

        return PHIDetectorResult(
            contains_phi=len(matches) > 0,
            matches=matches,
            sanitized_text=sanitized,
        )
