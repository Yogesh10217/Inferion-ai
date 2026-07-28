import pytest
from app.auth.rbac import RBACService
from app.auth.permissions import SystemPermissions

def test_has_permission():
    user_permissions = {SystemPermissions.INFERENCE_GENERATE, SystemPermissions.MODELS_READ}
    
    assert RBACService.has_permission(user_permissions, SystemPermissions.INFERENCE_GENERATE) is True
    assert RBACService.has_permission(user_permissions, SystemPermissions.MODELS_READ) is True
    assert RBACService.has_permission(user_permissions, SystemPermissions.API_KEYS_MANAGE) is False

def test_developer_permissions_set():
    dev_perms = SystemPermissions.developer_permissions()
    assert SystemPermissions.INFERENCE_GENERATE in dev_perms
    assert SystemPermissions.MODELS_READ in dev_perms
    assert SystemPermissions.USERS_MANAGE not in dev_perms

def test_viewer_permissions_set():
    viewer_perms = SystemPermissions.viewer_permissions()
    assert SystemPermissions.MODELS_READ in viewer_perms
    assert SystemPermissions.INFERENCE_GENERATE not in viewer_perms
