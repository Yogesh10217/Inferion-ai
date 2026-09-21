"""Unit tests for MarketplaceInstallationManager."""

from app.extensions.extension import ExtensionManifest, ExtensionType
from app.marketplace.marketplace_installation import MarketplaceInstallationManager
from app.marketplace.marketplace_item import MarketplaceCategory, MarketplaceItem


def test_marketplace_item_installation():
    install_mgr = MarketplaceInstallationManager()

    m = ExtensionManifest(
        identifier="ext.install", name="Install Ext", publisher_id="pub_1", extension_type=ExtensionType.TOOL
    )
    item = MarketplaceItem(
        title="Installable Extension", category=MarketplaceCategory.TOOLS, publisher_id="pub_1", manifest=m
    )

    ext = install_mgr.install_marketplace_item(item, tenant_id="tenant_inst", enable_immediately=True)
    assert ext.tenant_id == "tenant_inst"
    assert ext.is_enabled is True
    assert item.download_count == 1
