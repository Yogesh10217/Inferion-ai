"""Provider-Agnostic Connector Framework Interface & Registry."""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from app.data_fabric.data_source import DataSource
from app.data_fabric.exceptions import ConnectorNotFoundException

logger = logging.getLogger(__name__)


class ConnectorCapabilities(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    SCHEMA_DISCOVERY = "SCHEMA_DISCOVERY"
    INCREMENTAL_SYNC = "INCREMENTAL_SYNC"
    CHANGE_DATA_CAPTURE = "CHANGE_DATA_CAPTURE"
    WEBHOOKS = "WEBHOOKS"
    FILE_STREAMING = "FILE_STREAMING"
    PAGINATION = "PAGINATION"


class ConnectorMetadata(BaseModel):
    """Metadata describing connector implementation capabilities."""

    connector_type: str
    display_name: str
    description: str = ""
    capabilities: List[ConnectorCapabilities] = Field(default_factory=list)
    version: str = "1.0.0"


class DataConnector(ABC):
    """Abstract Base Interface for all Enterprise Data Connectors."""

    def __init__(self, data_source: DataSource, secret_data: Optional[Dict[str, Any]] = None) -> None:
        self.data_source = data_source
        self.secret_data = secret_data or {}
        self.is_connected = False

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to external data source."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close external connection."""

    @abstractmethod
    async def validate(self) -> bool:
        """Test credentials and connection health."""

    @abstractmethod
    async def discover_schema(self) -> Dict[str, Any]:
        """Inspect and return schema structure."""

    @abstractmethod
    async def fetch(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Fetch records from data source."""

    @abstractmethod
    async def fetch_incremental(self, cursor: Optional[str] = None, limit: int = 100) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Fetch records updated since cursor."""

    @abstractmethod
    async def get_changes(self, last_checkpoint: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract CDC event stream."""

    @abstractmethod
    async def checkpoint(self) -> str:
        """Generate state checkpoint cursor."""

    @abstractmethod
    async def restore_checkpoint(self, checkpoint_id: str) -> None:
        """Restore cursor position from checkpoint."""


class ConnectorRegistry:
    """Central registry of available data connector classes."""

    def __init__(self) -> None:
        self._connectors: Dict[str, type] = {}
        self._metadata: Dict[str, ConnectorMetadata] = {}

    def register_connector(self, connector_type: str, connector_cls: type, metadata: ConnectorMetadata) -> None:
        self._connectors[connector_type] = connector_cls
        self._metadata[connector_type] = metadata
        logger.info(f"[CONNECTOR REGISTRY] Registered connector type '{connector_type}' ({metadata.display_name})")

    def get_connector_class(self, connector_type: str) -> type:
        cls = self._connectors.get(connector_type)
        if not cls:
            raise ConnectorNotFoundException(connector_type)
        return cls

    def get_metadata(self, connector_type: str) -> ConnectorMetadata:
        meta = self._metadata.get(connector_type)
        if not meta:
            raise ConnectorNotFoundException(connector_type)
        return meta

    def list_connectors(self) -> List[ConnectorMetadata]:
        return list(self._metadata.values())


class ConnectorFactory:
    """Factory instantiating DataConnector implementations bound with secrets."""

    def __init__(self, registry: Optional[ConnectorRegistry] = None) -> None:
        self.registry = registry or ConnectorRegistry()

    def create_connector(self, data_source: DataSource, secret_data: Optional[Dict[str, Any]] = None) -> DataConnector:
        cls = self.registry.get_connector_class(data_source.connector_type)
        return cls(data_source=data_source, secret_data=secret_data)
