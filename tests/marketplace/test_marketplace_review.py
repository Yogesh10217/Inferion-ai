"""Unit tests for MarketplaceReviewEngine and security scan integration."""

import pytest
from app.marketplace.marketplace_item import MarketplaceItem, MarketplaceCategory, ItemLifecycle
from app.marketplace.marketplace_review import MarketplaceReviewEngine
from app.extensions.extension import ExtensionManifest, ExtensionType


def test_marketplace_review_pipeline():
    review_engine = MarketplaceReviewEngine()

    m = ExtensionManifest(identifier="ext.clean", name="Clean Ext", publisher_id="pub_1", extension_type=ExtensionType.TOOL)
    item = MarketplaceItem(title="Clean Extension", summary="Safe tool", category=MarketplaceCategory.TOOLS, publisher_id="pub_1", manifest=m)

    res = review_engine.review_item_submission(item)
    assert res.passed_review is True
    assert item.status == ItemLifecycle.APPROVED
