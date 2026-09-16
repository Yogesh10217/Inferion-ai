"""Tenant-Scoped Repositories for FinOps Intelligence (Phase 5.42)."""

from typing import Dict, List

from app.finops_intelligence.allocation import CostAllocation
from app.finops_intelligence.budgets import Budget
from app.finops_intelligence.cost_intelligence import CostIntelligenceRecord
from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException
from app.finops_intelligence.investigations import FinOpsInvestigation
from app.finops_intelligence.optimization import OptimizationRecommendation


class BaseTenantRepository:
    """Base repository enforcing strict tenant scoping with zero metadata leakage."""

    def _check_tenant(self, item_tenant_id: str, requested_tenant_id: str) -> None:
        if item_tenant_id != requested_tenant_id:
            raise CrossTenantFinOpsIntelligenceException()


class CostRepository(BaseTenantRepository):
    def __init__(self) -> None:
        self._store: Dict[str, CostIntelligenceRecord] = {}

    def save(self, record: CostIntelligenceRecord) -> None:
        self._store[record.record_id] = record

    def get(self, tenant_id: str, record_id: str) -> CostIntelligenceRecord:
        rec = self._store.get(record_id)
        if not rec:
            raise CrossTenantFinOpsIntelligenceException()
        self._check_tenant(rec.tenant_id, tenant_id)
        return rec

    def list(self, tenant_id: str) -> List[CostIntelligenceRecord]:
        return [r for r in self._store.values() if r.tenant_id == tenant_id]


class BudgetRepository(BaseTenantRepository):
    def __init__(self) -> None:
        self._store: Dict[str, Budget] = {}

    def save(self, budget: Budget) -> None:
        self._store[budget.budget_id] = budget

    def get(self, tenant_id: str, budget_id: str) -> Budget:
        bdg = self._store.get(budget_id)
        if not bdg:
            raise CrossTenantFinOpsIntelligenceException()
        self._check_tenant(bdg.tenant_id, tenant_id)
        return bdg

    def list(self, tenant_id: str) -> List[Budget]:
        return [b for b in self._store.values() if b.tenant_id == tenant_id]


class AllocationRepository(BaseTenantRepository):
    def __init__(self) -> None:
        self._store: Dict[str, CostAllocation] = {}

    def save(self, allocation: CostAllocation) -> None:
        self._store[allocation.allocation_id] = allocation

    def get(self, tenant_id: str, allocation_id: str) -> CostAllocation:
        alloc = self._store.get(allocation_id)
        if not alloc:
            raise CrossTenantFinOpsIntelligenceException()
        self._check_tenant(alloc.tenant_id, tenant_id)
        return alloc

    def list(self, tenant_id: str) -> List[CostAllocation]:
        return [a for a in self._store.values() if a.tenant_id == tenant_id]


class OptimizationRepository(BaseTenantRepository):
    def __init__(self) -> None:
        self._store: Dict[str, OptimizationRecommendation] = {}

    def save(self, recommendation: OptimizationRecommendation) -> None:
        self._store[recommendation.optimization_id] = recommendation

    def get(self, tenant_id: str, optimization_id: str) -> OptimizationRecommendation:
        rec = self._store.get(optimization_id)
        if not rec:
            raise CrossTenantFinOpsIntelligenceException()
        self._check_tenant(rec.tenant_id, tenant_id)
        return rec

    def list(self, tenant_id: str) -> List[OptimizationRecommendation]:
        return [r for r in self._store.values() if r.tenant_id == tenant_id]


class InvestigationRepository(BaseTenantRepository):
    def __init__(self) -> None:
        self._store: Dict[str, FinOpsInvestigation] = {}

    def save(self, investigation: FinOpsInvestigation) -> None:
        self._store[investigation.investigation_id] = investigation

    def get(self, tenant_id: str, investigation_id: str) -> FinOpsInvestigation:
        inv = self._store.get(investigation_id)
        if not inv:
            raise CrossTenantFinOpsIntelligenceException()
        self._check_tenant(inv.tenant_id, tenant_id)
        return inv

    def list(self, tenant_id: str) -> List[FinOpsInvestigation]:
        return [i for i in self._store.values() if i.tenant_id == tenant_id]
