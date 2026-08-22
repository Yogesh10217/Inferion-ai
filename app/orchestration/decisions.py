"""Deterministic Decision Automation & Decision Table Subsystem."""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.orchestration.exceptions import DecisionEvaluationException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DecisionRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: f"rule_{uuid.uuid4().hex[:8]}")
    condition_key: str  # e.g., "amount", "credit_score"
    operator: str  # ">", "<", "==", ">=", "<=", "in"
    threshold: Any
    output_decision: str  # "APPROVE", "REJECT", "REQUIRE_REVIEW"


class DecisionTable(BaseModel):
    table_id: str = Field(default_factory=lambda: f"dtab_{uuid.uuid4().hex[:10]}")
    name: str
    tenant_id: str = "global"
    rules: List[DecisionRule] = Field(default_factory=list)
    default_decision: str = "REQUIRE_REVIEW"


class DecisionResult(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: f"deval_{uuid.uuid4().hex[:10]}")
    table_id: str
    tenant_id: str = "global"

    decision: str
    matched_rule_id: Optional[str] = None
    explanation: str = ""
    evidence_references: List[str] = Field(default_factory=list)
    is_deterministic: bool = True
    evaluated_at: datetime = Field(default_factory=_now)


class DecisionEngine:
    """Evaluates deterministic decision tables and rules for policy & threshold decisions without LLM hallucination."""

    def __init__(self) -> None:
        self._tables: Dict[str, DecisionTable] = {}

    def register_table(self, name: str, rules: List[DecisionRule], tenant_id: str = "global", default_decision: str = "REQUIRE_REVIEW") -> DecisionTable:
        dtab = DecisionTable(name=name, rules=rules, tenant_id=tenant_id, default_decision=default_decision)
        self._tables[dtab.table_id] = dtab
        logger.info(f"[DECISION ENGINE] Registered decision table '{dtab.table_id}' ({name}) with {len(rules)} rules")
        return dtab

    def evaluate(self, table_id: str, inputs: Dict[str, Any], tenant_id: str = "global") -> DecisionResult:
        table = self.get_table(table_id)

        for rule in table.rules:
            val = inputs.get(rule.condition_key)
            if val is not None:
                matched = False
                if rule.operator == ">" and float(val) > float(rule.threshold):
                    matched = True
                elif rule.operator == "<" and float(val) < float(rule.threshold):
                    matched = True
                elif rule.operator == ">=" and float(val) >= float(rule.threshold):
                    matched = True
                elif rule.operator == "<=" and float(val) <= float(rule.threshold):
                    matched = True
                elif rule.operator == "==" and str(val) == str(rule.threshold):
                    matched = True

                if matched:
                    res = DecisionResult(
                        table_id=table_id,
                        tenant_id=tenant_id,
                        decision=rule.output_decision,
                        matched_rule_id=rule.rule_id,
                        explanation=f"Matched rule '{rule.rule_id}': {rule.condition_key} {rule.operator} {rule.threshold}",
                        evidence_references=[f"rule_id:{rule.rule_id}"],
                    )
                    logger.info(f"[DECISION ENGINE] Table '{table_id}' evaluated -> Decision '{rule.output_decision}'")
                    return res

        # Default fallback
        res_def = DecisionResult(
            table_id=table_id,
            tenant_id=tenant_id,
            decision=table.default_decision,
            explanation=f"No rules matched. Default decision applied: {table.default_decision}",
        )
        return res_def

    def get_table(self, table_id: str) -> DecisionTable:
        tbl = self._tables.get(table_id)
        if not tbl:
            raise DecisionEvaluationException(table_id, "Decision table not found")
        return tbl
