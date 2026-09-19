"""Central Marketplace Item Registry & Catalog."""

import logging
from typing import Dict, List, Optional

from app.marketplace.exceptions import MarketplaceItemNotFoundException
from app.marketplace.marketplace_item import ItemLifecycle, MarketplaceCategory, MarketplaceItem

logger = logging.getLogger(__name__)


class MarketplaceRegistry:
    """Manages publishing catalog, category indexes, search, and metadata."""

    def __init__(self) -> None:
        self._items: Dict[str, MarketplaceItem] = {}

    def register_item(self, item: MarketplaceItem) -> MarketplaceItem:
        """Add or update an item in the marketplace catalog."""
        self._items[item.item_id] = item
        logger.info(
            f"[MARKETPLACE REGISTRY] Registered item '{item.title}' (ID: {item.item_id}, Status: {item.status.value})"
        )
        return item

    def get_item(self, item_id: str) -> MarketplaceItem:
        item = self._items.get(item_id)
        if not item:
            raise MarketplaceItemNotFoundException(item_id)
        return item

    def list_items(
        self,
        category: Optional[MarketplaceCategory] = None,
        published_only: bool = True,
    ) -> List[MarketplaceItem]:
        """List catalog items matching filters."""
        res = list(self._items.values())
        if published_only:
            res = [i for i in res if i.status == ItemLifecycle.PUBLISHED]
        if category:
            res = [i for i in res if i.category == category]
        return res

    def search_items(self, query: str) -> List[MarketplaceItem]:
        """Search published marketplace items by title or summary."""
        q_norm = query.lower()
        published = self.list_items(published_only=True)
        return [i for i in published if q_norm in i.title.lower() or q_norm in i.summary.lower()]
