"""Tenant-Scoped Repositories for Operations Intelligence (Phase 5.41)."""

from typing import Dict, Any, Optional, List
from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException
from app.operations_intelligence.services import OperationalService
from app.operations_intelligence.incidents import OperationalIncident
from app.operations_intelligence.major_incidents import MajorIncident
from app.operations_intelligence.alerts import OperationalAlert
from app.operations_intelligence.problems import OperationalProblem
from app.operations_intelligence.known_errors import KnownError
from app.operations_intelligence.investigations import OperationalInvestigation


class BaseTenantRepository:
    """Base repository enforcing strict tenant scoping with zero metadata leakage."""

    def _check_tenant(self, item_tenant_id: str, requested_tenant_id: str) -> None:
        if item_tenant_id != requested_tenant_id:
            raise CrossTenantOperationsAccessException()


class ServiceRepository(BaseTenantRepository):
    def __init__(self) -> None:
        self._store: Dict[str, OperationalService] = {}

    def save(self, service: OperationalService) -> None:
        self._store[service.service_id] = service

    def get(self, tenant_id: str, service_id: str) -> OperationalService:
        svc = self._store.get(service_id)
        if not svc:
            raise CrossTenantOperationsAccessException()
        self._check_tenant(svc.tenant_id, tenant_id)
        return svc

    def list(self, tenant_id: str) -> List[OperationalService]:
        return [s for s in self._store.values() if s.tenant_id == tenant_id]


class IncidentRepository(BaseTenantRepository):
    def __init__(self) -> None:
        self._store: Dict[str, OperationalIncident] = {}

    def save(self, incident: OperationalIncident) -> None:
        self._store[incident.incident_id] = incident

    def get(self, tenant_id: str, incident_id: str) -> OperationalIncident:
        inc = self._store.get(incident_id)
        if not inc:
            raise CrossTenantOperationsAccessException()
        self._check_tenant(inc.tenant_id, tenant_id)
        return inc

    def list(self, tenant_id: str) -> List[OperationalIncident]:
        return [i for i in self._store.values() if i.tenant_id == tenant_id]


class MajorIncidentRepository(BaseTenantRepository):
    def __init__(self) -> None:
        self._store: Dict[str, MajorIncident] = {}

    def save(self, major_incident: MajorIncident) -> None:
        self._store[major_incident.major_incident_id] = major_incident

    def get(self, tenant_id: str, major_incident_id: str) -> MajorIncident:
        maj = self._store.get(major_incident_id)
        if not maj:
            raise CrossTenantOperationsAccessException()
        self._check_tenant(maj.tenant_id, tenant_id)
        return maj

    def list(self, tenant_id: str) -> List[MajorIncident]:
        return [m for m in self._store.values() if m.tenant_id == tenant_id]


class AlertRepository(BaseTenantRepository):
    def __init__(self) -> None:
        self._store: Dict[str, OperationalAlert] = {}

    def save(self, alert: OperationalAlert) -> None:
        self._store[alert.alert_id] = alert

    def get(self, tenant_id: str, alert_id: str) -> OperationalAlert:
        alt = self._store.get(alert_id)
        if not alt:
            raise CrossTenantOperationsAccessException()
        self._check_tenant(alt.tenant_id, tenant_id)
        return alt

    def list(self, tenant_id: str) -> List[OperationalAlert]:
        return [a for a in self._store.values() if a.tenant_id == tenant_id]


class ProblemRepository(BaseTenantRepository):
    def __init__(self) -> None:
        self._store: Dict[str, OperationalProblem] = {}

    def save(self, problem: OperationalProblem) -> None:
        self._store[problem.problem_id] = problem

    def get(self, tenant_id: str, problem_id: str) -> OperationalProblem:
        prob = self._store.get(problem_id)
        if not prob:
            raise CrossTenantOperationsAccessException()
        self._check_tenant(prob.tenant_id, tenant_id)
        return prob

    def list(self, tenant_id: str) -> List[OperationalProblem]:
        return [p for p in self._store.values() if p.tenant_id == tenant_id]


class KnownErrorRepository(BaseTenantRepository):
    def __init__(self) -> None:
        self._store: Dict[str, KnownError] = {}

    def save(self, known_error: KnownError) -> None:
        self._store[known_error.known_error_id] = known_error

    def get(self, tenant_id: str, known_error_id: str) -> KnownError:
        ke = self._store.get(known_error_id)
        if not ke:
            raise CrossTenantOperationsAccessException()
        self._check_tenant(ke.tenant_id, tenant_id)
        return ke

    def list(self, tenant_id: str) -> List[KnownError]:
        return [k for k in self._store.values() if k.tenant_id == tenant_id]


class InvestigationRepository(BaseTenantRepository):
    def __init__(self) -> None:
        self._store: Dict[str, OperationalInvestigation] = {}

    def save(self, investigation: OperationalInvestigation) -> None:
        self._store[investigation.investigation_id] = investigation

    def get(self, tenant_id: str, investigation_id: str) -> OperationalInvestigation:
        inv = self._store.get(investigation_id)
        if not inv:
            raise CrossTenantOperationsAccessException()
        self._check_tenant(inv.tenant_id, tenant_id)
        return inv

    def list(self, tenant_id: str) -> List[OperationalInvestigation]:
        return [i for i in self._store.values() if i.tenant_id == tenant_id]
