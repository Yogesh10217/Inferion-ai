"""Schema Discovery & Metadata Engine."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.data_fabric.connector import ConnectorFactory
from app.data_fabric.data_source import DataSource

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SchemaField(BaseModel):
    """Schema field definition."""

    field_name: str
    field_type: str
    nullable: bool = True
    sensitive: bool = False
    classification: str = "INTERNAL"  # PII, FINANCIAL, HEALTH, SECRET, PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    description: str = ""


class SchemaDefinition(BaseModel):
    """Container holding schema definition."""

    schema_id: str
    source_id: str
    tenant_id: str = "global"
    version: int = 1
    tables_or_resources: List[Dict[str, Any]] = Field(default_factory=list)
    fields: List[SchemaField] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


class SchemaVersion(BaseModel):
    """Tracks schema evolution history."""

    version_number: int
    schema_id: str
    diff_summary: str = ""
    discovered_at: datetime = Field(default_factory=_now)


class SchemaDiscoveryEngine:
    """Discovers, infers, version-tracks, and classifies schemas across enterprise data sources."""

    def __init__(self, connector_factory: Optional[ConnectorFactory] = None) -> None:
        self.connector_factory = connector_factory or ConnectorFactory()
        self._schemas: Dict[str, SchemaDefinition] = {}
        self._history: Dict[str, List[SchemaVersion]] = {}

    async def discover_schema(
        self, data_source: DataSource, secret_data: Optional[Dict[str, Any]] = None
    ) -> SchemaDefinition:
        """Connect to source, infer schema, detect sensitive fields, and record version."""
        connector = self.connector_factory.create_connector(data_source, secret_data=secret_data)
        await connector.connect()
        raw_schema = await connector.discover_schema()
        await connector.disconnect()

        fields: List[SchemaField] = []
        tables = raw_schema.get("tables", [])
        for t in tables:
            for f in t.get("fields", []):
                fields.append(
                    SchemaField(
                        field_name=f"{t['name']}.{f['name']}",
                        field_type=f.get("type", "VARCHAR"),
                        sensitive=f.get("sensitive", False),
                        classification=f.get("classification", "INTERNAL"),
                    )
                )

        schema_id = f"sch_{data_source.id}"
        prev_schema = self._schemas.get(schema_id)
        new_version = (prev_schema.version + 1) if prev_schema else 1

        schema_def = SchemaDefinition(
            schema_id=schema_id,
            source_id=data_source.id,
            tenant_id=data_source.tenant_id,
            version=new_version,
            tables_or_resources=tables,
            fields=fields,
        )

        self._schemas[schema_id] = schema_def

        v_record = SchemaVersion(
            version_number=new_version,
            schema_id=schema_id,
            diff_summary="Initial schema discovery" if new_version == 1 else "Schema updated",
        )
        self._history.setdefault(schema_id, []).append(v_record)

        logger.info(
            f"[SCHEMA DISCOVERY] Discovered schema for source '{data_source.name}' (Version: {new_version}, Fields: {len(fields)})"
        )
        return schema_def

    def get_schema(self, source_id: str) -> SchemaDefinition:
        schema_id = f"sch_{source_id}"
        sch = self._schemas.get(schema_id)
        if not sch:
            return SchemaDefinition(schema_id=schema_id, source_id=source_id)
        return sch
