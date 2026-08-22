"""Master Developer Platform Manager unifying developer identities, projects, APIs, and webhooks."""

import logging
from typing import Dict, Any, Optional

from app.developer_platform.developer import DeveloperManager
from app.developer_platform.project import ProjectManager
from app.developer_platform.api_management import DeveloperAPIManager
from app.developer_platform.events import DeveloperEventEngine
from app.developer_platform.sdk_validation import SDKConsistencyValidator
from app.developer_platform.billing import DeveloperBillingTracker
from app.developer_platform.metrics import DeveloperPlatformMetricsCollector

logger = logging.getLogger(__name__)


class DeveloperPlatformManager:
    """Master Manager orchestrating Developer accounts, Projects, Webhooks, API management, and SDK validation."""

    def __init__(self) -> None:
        self.developer_manager = DeveloperManager()
        self.project_manager = ProjectManager()
        self.api_manager = DeveloperAPIManager()
        self.event_engine = DeveloperEventEngine()
        self.sdk_validator = SDKConsistencyValidator()
        self.billing_tracker = DeveloperBillingTracker()
        self.metrics_collector = DeveloperPlatformMetricsCollector()

        logger.info("[DEVELOPER PLATFORM MASTER] DeveloperPlatformManager initialized cleanly")

    def get_summary(self) -> Dict[str, Any]:
        """Aggregate developer platform summary."""
        devs = self.developer_manager.list_developers()
        projs = self.project_manager.list_projects()
        subs = self.event_engine.list_subscriptions()

        return {
            "total_developers": len(devs),
            "active_developers": len([d for d in devs if d.status.value == "ACTIVE"]),
            "total_projects": len(projs),
            "total_webhook_subscriptions": len(subs),
            "metrics": self.metrics_collector.get_metrics_summary(),
        }
