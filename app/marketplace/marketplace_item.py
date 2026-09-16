"""Marketplace Item entities and item lifecycle states."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from app.extensions.extension import ExtensionManifest

logger = logging.getLogger(__name__)


class MarketplaceCategory(str, Enum):
    AGENTS = "AGENTS"
    TOOLS = "TOOLS"
    WORKFLOWS = "WORKFLOWS"
    MCP_SERVERS = "MCP_SERVERS"
    MODEL_PROVIDERS = "MODEL_PROVIDERS"
    MEMORY_PROVIDERS = "MEMORY_PROVIDERS"
    KNOWLEDGE_CONNECTORS = "KNOWLEDGE_CONNECTORS"
    OBSERVABILITY_EXPORTERS = "OBSERVABILITY_EXPORTERS"
    AUTOMATION_TEMPLATES = "AUTOMATION_TEMPLATES"


class ItemLifecycle(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"
    DEPRECATED = "DEPRECATED"


class MarketplaceItem(BaseModel):
    """Publishable Marketplace Item container."""

    item_id: str = Field(default_factory=lambda: f"mkt_{uuid.uuid4().hex[:10]}")
    title: str
    summary: str = ""
    category: MarketplaceCategory
    publisher_id: str
    manifest: ExtensionManifest
    status: ItemLifecycle = ItemLifecycle.DRAFT
    rating: float = 5.0
    download_count: int = 0
    price_dollars: float = 0.0
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
