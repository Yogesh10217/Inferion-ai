import pytest
from app.knowledge.permissions import DocumentPermissions, Visibility

def test_document_permissions_model():
    perms = DocumentPermissions(organization_id="org1", workspace_id="ws1", owner_id="owner1", visibility=Visibility.PUBLIC)
    assert perms.visibility == "public"
