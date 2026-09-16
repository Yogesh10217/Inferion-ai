"""Repository Interfaces & Persistence Implementations for Data Governance."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.data_governance.assets import DataAsset
from app.data_governance.consent import DataConsent
from app.data_governance.contracts import DataContract


class DataAssetRepository(ABC):
    @abstractmethod
    def save(self, asset: DataAsset) -> DataAsset:
        pass

    @abstractmethod
    def get_by_id(self, asset_id: str, tenant_id: str) -> Optional[DataAsset]:
        pass

    @abstractmethod
    def list(self, tenant_id: str) -> List[DataAsset]:
        pass


class InMemoryDataAssetRepository(DataAssetRepository):
    def __init__(self) -> None:
        self._store: Dict[str, DataAsset] = {}

    def save(self, asset: DataAsset) -> DataAsset:
        self._store[asset.asset_id] = asset
        return asset

    def get_by_id(self, asset_id: str, tenant_id: str) -> Optional[DataAsset]:
        a = self._store.get(asset_id)
        if a and a.tenant_id == tenant_id:
            return a
        return None

    def list(self, tenant_id: str) -> List[DataAsset]:
        return [a for a in self._store.values() if a.tenant_id == tenant_id]


class DataContractRepository(ABC):
    @abstractmethod
    def save(self, contract: DataContract) -> DataContract:
        pass

    @abstractmethod
    def get_by_asset(self, asset_id: str, tenant_id: str) -> Optional[DataContract]:
        pass


class InMemoryDataContractRepository(DataContractRepository):
    def __init__(self) -> None:
        self._store: Dict[str, DataContract] = {}

    def save(self, contract: DataContract) -> DataContract:
        self._store[contract.contract_id] = contract
        return contract

    def get_by_asset(self, asset_id: str, tenant_id: str) -> Optional[DataContract]:
        for c in self._store.values():
            if c.asset_id == asset_id and c.tenant_id == tenant_id:
                return c
        return None


class DataConsentRepository(ABC):
    @abstractmethod
    def save(self, consent: DataConsent) -> DataConsent:
        pass

    @abstractmethod
    def get_by_subject(self, subject_id: str, tenant_id: str) -> Optional[DataConsent]:
        pass


class InMemoryDataConsentRepository(DataConsentRepository):
    def __init__(self) -> None:
        self._store: Dict[str, DataConsent] = {}

    def save(self, consent: DataConsent) -> DataConsent:
        self._store[f"{consent.tenant_id}:{consent.subject_id}"] = consent
        return consent

    def get_by_subject(self, subject_id: str, tenant_id: str) -> Optional[DataConsent]:
        return self._store.get(f"{tenant_id}:{subject_id}")


class DataGovernanceRepository:
    """Production Repository coordinator managing database & memory persistence abstractions."""

    def __init__(self, use_memory: bool = True) -> None:
        self.use_memory = use_memory
        self.asset_repo: DataAssetRepository = InMemoryDataAssetRepository()
        self.contract_repo: DataContractRepository = InMemoryDataContractRepository()
        self.consent_repo: DataConsentRepository = InMemoryDataConsentRepository()
