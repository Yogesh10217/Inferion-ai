"""Master Marketplace Manager unifying publishing, review, and installation pipelines."""

import logging
from typing import Any, Dict

from app.marketplace.marketplace_installation import MarketplaceInstallationManager
from app.marketplace.marketplace_registry import MarketplaceRegistry
from app.marketplace.marketplace_review import MarketplaceReviewEngine
from app.marketplace.metrics import MarketplaceMetricsCollector
from app.marketplace.publisher import PublisherManager

logger = logging.getLogger(__name__)


class MarketplaceManager:
    """Master Manager orchestrating Marketplace Publishers, Items, Security Scans, Approvals, and Tenant Installations."""

    def __init__(self) -> None:
        self.publisher_manager = PublisherManager()
        self.registry = MarketplaceRegistry()
        self.review_engine = MarketplaceReviewEngine()
        self.installation_manager = MarketplaceInstallationManager()
        self.metrics_collector = MarketplaceMetricsCollector()

        logger.info("[MARKETPLACE MASTER] MarketplaceManager initialized cleanly")

    def get_summary(self) -> Dict[str, Any]:
        """Aggregate marketplace summary."""
        items = self.registry.list_items(published_only=False)
        published = self.registry.list_items(published_only=True)

        return {
            "total_items": len(items),
            "published_items": len(published),
            "metrics": self.metrics_collector.get_metrics_summary(),
        }
