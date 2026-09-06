"""Tenant-scoped repositories for Data Intelligence Platform (Phase 5.43)."""

from typing import Dict, Any, Optional, List
from app.data_intelligence.exceptions import (
    CrossTenantDataIntelligenceException,
    DatasetNotFoundException,
    DataSourceNotFoundException,
    DataAnomalyNotFoundException,
    DataIncidentNotFoundException,
    ImmutableDataRecordException,
)
from app.data_intelligence.datasets import DatasetReference
from app.data_intelligence.sources import DataSource
from app.data_intelligence.anomalies import DataAnomaly
from app.data_intelligence.incidents import DataIncident
from app.data_intelligence.evidence import DataEvidenceBundle
from app.platform_contracts.redaction import SensitiveDataSanitizer


class DatasetRepository:
    """Tenant-isolated repository for dataset references."""

    def __init__(self) -> None:
        self._datasets: Dict[str, DatasetReference] = {}
        self._sanitizer = SensitiveDataSanitizer()

    def save(self, dataset: DatasetReference) -> DatasetReference:
        self._datasets[dataset.dataset_id] = dataset
        return dataset

    def get(self, dataset_id: str, tenant_id: str) -> DatasetReference:
        ds = self._datasets.get(dataset_id)
        if not ds:
            raise DatasetNotFoundException(dataset_id)
        if ds.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return ds

    def list(self, tenant_id: str) -> List[DatasetReference]:
        return [ds for ds in self._datasets.values() if ds.tenant_id == tenant_id]


class DataSourceRepository:
    """Tenant-isolated repository for data sources."""

    def __init__(self) -> None:
        self._sources: Dict[str, DataSource] = {}

    def save(self, source: DataSource) -> DataSource:
        self._sources[source.source_id] = source
        return source

    def get(self, source_id: str, tenant_id: str) -> DataSource:
        src = self._sources.get(source_id)
        if not src:
            raise DataSourceNotFoundException(source_id)
        if src.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return src

    def list(self, tenant_id: str) -> List[DataSource]:
        return [s for s in self._sources.values() if s.tenant_id == tenant_id]


class DataAnomalyRepository:
    """Tenant-isolated repository for data anomalies."""

    def __init__(self) -> None:
        self._anomalies: Dict[str, DataAnomaly] = {}

    def save(self, anomaly: DataAnomaly) -> DataAnomaly:
        self._anomalies[anomaly.anomaly_id] = anomaly
        return anomaly

    def get(self, anomaly_id: str, tenant_id: str) -> DataAnomaly:
        a = self._anomalies.get(anomaly_id)
        if not a:
            raise DataAnomalyNotFoundException(anomaly_id)
        if a.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return a

    def list(self, tenant_id: str) -> List[DataAnomaly]:
        return [a for a in self._anomalies.values() if a.tenant_id == tenant_id]


class DataIncidentRepository:
    """Tenant-isolated repository for data incidents."""

    def __init__(self) -> None:
        self._incidents: Dict[str, DataIncident] = {}

    def save(self, incident: DataIncident) -> DataIncident:
        self._incidents[incident.incident_id] = incident
        return incident

    def get(self, incident_id: str, tenant_id: str) -> DataIncident:
        inc = self._incidents.get(incident_id)
        if not inc:
            raise DataIncidentNotFoundException(incident_id)
        if inc.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return inc

    def list(self, tenant_id: str) -> List[DataIncident]:
        return [i for i in self._incidents.values() if i.tenant_id == tenant_id]


class DataEvidenceRepository:
    """Tenant-isolated repository for immutable evidence bundles."""

    def __init__(self) -> None:
        self._bundles: Dict[str, DataEvidenceBundle] = {}

    def save(self, bundle: DataEvidenceBundle) -> DataEvidenceBundle:
        if bundle.bundle_id in self._bundles:
            raise ImmutableDataRecordException(bundle.bundle_id)
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def get(self, bundle_id: str, tenant_id: str) -> DataEvidenceBundle:
        b = self._bundles.get(bundle_id)
        if not b:
            raise Exception(f"Evidence bundle '{bundle_id}' not found.")
        if b.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return b

    def list(self, tenant_id: str) -> List[DataEvidenceBundle]:
        return [b for b in self._bundles.values() if b.tenant_id == tenant_id]
