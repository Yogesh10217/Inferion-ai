"""Data Contracts & Breaking Change Management Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine


class ContractStatus(str, Enum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"


class ContractRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    field_name: str
    expected_type: str
    required: bool = True
    nullable: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    regex_pattern: Optional[str] = None


class ContractSchema(BaseModel):
    schema_version: str = "1.0.0"
    fields: Dict[str, ContractRule] = Field(default_factory=dict)
    max_freshness_seconds: Optional[int] = 3600
    min_quality_score: float = 80.0
    required_classification: str = "CONFIDENTIAL"


class DataContract(BaseModel):
    contract_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    version: str = "1.0.0"
    status: ContractStatus = ContractStatus.DRAFT
    schema_spec: ContractSchema
    owner_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContractValidationResult(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contract_id: str
    asset_id: str
    tenant_id: str
    is_valid: bool
    is_breaking_change: bool = False
    violations: List[str] = Field(default_factory=list)
    requires_approval: bool = False
    approval_request_id: Optional[str] = None
    validated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataContractManager:
    """Manages Data Contracts, schema compatibility, and breaking change workflows."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._contracts: Dict[str, DataContract] = {}

    def create_contract(
        self,
        tenant_id: str,
        asset_id: str,
        schema_spec: ContractSchema,
        owner_id: str,
        version: str = "1.0.0",
    ) -> DataContract:
        contract = DataContract(
            tenant_id=tenant_id,
            asset_id=asset_id,
            version=version,
            status=ContractStatus.ACTIVE,
            schema_spec=schema_spec,
            owner_id=owner_id,
        )
        self._contracts[contract.contract_id] = contract
        return contract

    def get_contract_for_asset(self, asset_id: str, tenant_id: str) -> Optional[DataContract]:
        for c in self._contracts.values():
            if c.asset_id == asset_id and c.tenant_id == tenant_id and c.status == ContractStatus.ACTIVE:
                return c
        return None

    def validate_producer_schema(
        self,
        tenant_id: str,
        asset_id: str,
        incoming_schema: Dict[str, str],
        data_sample: Optional[List[Dict[str, Any]]] = None,
    ) -> ContractValidationResult:
        contract = self.get_contract_for_asset(asset_id, tenant_id)
        if not contract:
            return ContractValidationResult(
                contract_id="none",
                asset_id=asset_id,
                tenant_id=tenant_id,
                is_valid=True,
                violations=[],
            )

        violations = []
        is_breaking = False
        spec = contract.schema_spec

        # Check missing required fields
        for field_name, rule in spec.fields.items():
            if rule.required and field_name not in incoming_schema:
                violations.append(f"Breaking Change: Required field '{field_name}' is missing in incoming schema.")
                is_breaking = True
            elif field_name in incoming_schema:
                inc_type = incoming_schema[field_name]
                if inc_type != rule.expected_type:
                    violations.append(f"Breaking Change: Type mismatch for field '{field_name}'. Expected '{rule.expected_type}', got '{inc_type}'.")
                    is_breaking = True

        requires_approval = False
        approval_id = None

        if is_breaking:
            requires_approval = True
            # Request approval from ApprovalEngine for breaking schema change
            app_req = self.approval_engine.request_approval(
                execution_id=asset_id,
                action_type="DATA_CONTRACT_BREAKING_CHANGE",
                requester="producer_pipeline",
                tenant_id=tenant_id,
                payload={
                    "contract_id": contract.contract_id,
                    "violations": violations,
                },
            )

            approval_id = app_req.request_id

        return ContractValidationResult(
            contract_id=contract.contract_id,
            asset_id=asset_id,
            tenant_id=tenant_id,
            is_valid=not bool(violations),
            is_breaking_change=is_breaking,
            violations=violations,
            requires_approval=requires_approval,
            approval_request_id=approval_id,
        )
