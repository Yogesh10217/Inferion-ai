"""Automatic & Deterministic Data Classification with Strict Monotonicity."""

import re
import uuid
from datetime import datetime, timezone
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.data_governance.exceptions import DataClassificationViolationException


class ClassificationLevel(IntEnum):
    PUBLIC = 1
    INTERNAL = 2
    CONFIDENTIAL = 3
    RESTRICTED = 4
    HIGHLY_RESTRICTED = 5

    @classmethod
    def from_str(cls, val: str) -> "ClassificationLevel":

        v = val.upper()
        if v in cls.__members__:
            return cls[v]
        return cls.CONFIDENTIAL


class SensitiveDataType(str, Enum):
    PII = "PII"
    FINANCIAL = "FINANCIAL"
    CREDENTIAL = "CREDENTIAL"
    AUTHENTICATION_DATA = "AUTHENTICATION_DATA"
    HEALTH_RELATED_DATA = "HEALTH_RELATED_DATA"
    LEGAL = "LEGAL"
    SOURCE_CODE = "SOURCE_CODE"
    PROPRIETARY_DATA = "PROPRIETARY_DATA"
    CUSTOMER_DATA = "CUSTOMER_DATA"
    REGULATED_DATA = "REGULATED_DATA"


class ClassificationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    pattern: str
    sensitive_type: SensitiveDataType
    target_level: ClassificationLevel
    description: str = ""


class ClassificationResult(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    assigned_level: ClassificationLevel
    detected_sensitive_types: List[SensitiveDataType] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    classified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    classification_version: str = "1.0.0"


class ReclassificationRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    current_level: ClassificationLevel
    requested_level: ClassificationLevel
    reason: str
    approved: bool = False
    approved_by: Optional[str] = None


class DataClassificationEngine:
    """Engine enforcing deterministic classification and strict monotonicity."""

    def __init__(self) -> None:
        self.rules: List[ClassificationRule] = [
            ClassificationRule(
                name="PII Email/SSN",
                pattern=r"(?i)(email|ssn|social_security|passport|phone)",
                sensitive_type=SensitiveDataType.PII,
                target_level=ClassificationLevel.RESTRICTED,
            ),
            ClassificationRule(
                name="Financial Credit Card/Bank",
                pattern=r"(?i)(card_number|credit_card|iban|bank_account|routing_number)",
                sensitive_type=SensitiveDataType.FINANCIAL,
                target_level=ClassificationLevel.HIGHLY_RESTRICTED,
            ),
            ClassificationRule(
                name="Credentials API Keys/Passwords",
                pattern=r"(?i)(password|secret|api_key|token|private_key)",
                sensitive_type=SensitiveDataType.CREDENTIAL,
                target_level=ClassificationLevel.HIGHLY_RESTRICTED,
            ),
            ClassificationRule(
                name="Health Data HIPAA",
                pattern=r"(?i)(diagnosis|patient|medical_record|prescription|health_condition)",
                sensitive_type=SensitiveDataType.HEALTH_RELATED_DATA,
                target_level=ClassificationLevel.RESTRICTED,
            ),
        ]
        self._reclassification_requests: Dict[str, ReclassificationRequest] = {}

    def classify_asset(
        self,
        tenant_id: str,
        asset_id: str,
        content_sample: Optional[str] = None,
        schema_fields: Optional[List[str]] = None,
        existing_level: Optional[ClassificationLevel] = None,
    ) -> ClassificationResult:
        highest_level = existing_level or ClassificationLevel.PUBLIC
        detected_types: List[SensitiveDataType] = []
        evidence: List[Dict[str, Any]] = []

        text_to_check = f"{content_sample or ''} {' '.join(schema_fields or [])}"

        for rule in self.rules:
            if re.search(rule.pattern, text_to_check):
                detected_types.append(rule.sensitive_type)
                evidence.append({
                    "rule": rule.name,
                    "pattern": rule.pattern,
                    "sensitive_type": rule.sensitive_type.value,
                    "recommended_level": rule.target_level.name,
                })
                if rule.target_level > highest_level:
                    highest_level = rule.target_level

        # Monotonicity rule check if existing level is higher than evaluated level
        if existing_level and existing_level > highest_level:
            highest_level = existing_level
            evidence.append({
                "note": "Monotonicity invariant preserved: classification was not downgraded.",
                "retained_level": existing_level.name,
            })

        return ClassificationResult(
            tenant_id=tenant_id,
            asset_id=asset_id,
            assigned_level=highest_level,
            detected_sensitive_types=detected_types,
            evidence=evidence,
        )

    def enforce_monotonicity(
        self,
        current_level: ClassificationLevel,
        new_level: ClassificationLevel,
        approved: bool = False,
    ) -> ClassificationLevel:
        """Ensure upward movement is automatic, but downward movement requires explicit approval."""
        if new_level >= current_level:
            return new_level

        if not approved:
            raise DataClassificationViolationException(
                f"Classification monotonicity violation: Cannot silently downgrade from '{current_level.name}' to '{new_level.name}' without explicit approval."
            )
        return new_level

    def request_reclassification_downgrade(
        self,
        tenant_id: str,
        asset_id: str,
        current_level: ClassificationLevel,
        requested_level: ClassificationLevel,
        reason: str,
    ) -> ReclassificationRequest:
        if requested_level >= current_level:
            req = ReclassificationRequest(
                tenant_id=tenant_id,
                asset_id=asset_id,
                current_level=current_level,
                requested_level=requested_level,
                reason=reason,
                approved=True,
                approved_by="auto-system",
            )
        else:
            req = ReclassificationRequest(
                tenant_id=tenant_id,
                asset_id=asset_id,
                current_level=current_level,
                requested_level=requested_level,
                reason=reason,
                approved=False,
            )
        self._reclassification_requests[req.request_id] = req
        return req

    def approve_reclassification_downgrade(self, request_id: str, approver_id: str) -> ReclassificationRequest:
        req = self._reclassification_requests.get(request_id)
        if not req:
            raise DataClassificationViolationException(f"Reclassification request '{request_id}' not found.")
        req.approved = True
        req.approved_by = approver_id
        return req
