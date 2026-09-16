"""Business Value Measurement Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field


class ValueDimension(str, Enum):
    REVENUE = "REVENUE"
    COST_SAVINGS = "COST_SAVINGS"
    PRODUCTIVITY = "PRODUCTIVITY"
    CUSTOMER_EXPERIENCE = "CUSTOMER_EXPERIENCE"
    RISK_REDUCTION = "RISK_REDUCTION"
    COMPLIANCE_IMPROVEMENT = "COMPLIANCE_IMPROVEMENT"
    RELIABILITY = "RELIABILITY"
    TIME_SAVED = "TIME_SAVED"
    CARBON_REDUCTION = "CARBON_REDUCTION"
    STRATEGIC_VALUE = "STRATEGIC_VALUE"


class ValueStage(str, Enum):
    EXPECTED_VALUE = "EXPECTED_VALUE"
    REALIZED_VALUE = "REALIZED_VALUE"


class ValueMeasurement(BaseModel):
    measurement_id: str = Field(default_factory=lambda: f"val_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    initiative_id: str
    dimension: ValueDimension
    stage: ValueStage = ValueStage.EXPECTED_VALUE
    target_value_usd: float
    actual_value_usd: float = 0.0
    measured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ValueManager:
    """Tracks expected vs realized business value across dimensions."""

    def __init__(self) -> None:
        self._measurements: Dict[str, ValueMeasurement] = {}

    def record_expected_value(
        self,
        tenant_id: str,
        initiative_id: str,
        dimension: ValueDimension,
        target_value_usd: float,
    ) -> ValueMeasurement:
        vm = ValueMeasurement(
            tenant_id=tenant_id,
            initiative_id=initiative_id,
            dimension=dimension,
            stage=ValueStage.EXPECTED_VALUE,
            target_value_usd=target_value_usd,
        )
        self._measurements[vm.measurement_id] = vm
        return vm

    def record_realized_value(
        self,
        tenant_id: str,
        initiative_id: str,
        dimension: ValueDimension,
        actual_value_usd: float,
    ) -> ValueMeasurement:
        vm = ValueMeasurement(
            tenant_id=tenant_id,
            initiative_id=initiative_id,
            dimension=dimension,
            stage=ValueStage.REALIZED_VALUE,
            target_value_usd=0.0,
            actual_value_usd=actual_value_usd,
        )
        self._measurements[vm.measurement_id] = vm
        return vm

    def list_measurements_for_initiative(self, tenant_id: str, initiative_id: str) -> List[ValueMeasurement]:
        return [m for m in self._measurements.values() if m.tenant_id == tenant_id and m.initiative_id == initiative_id]
