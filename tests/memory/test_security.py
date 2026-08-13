"""
Tests for Memory Security Policy Engine & RBAC Enforcement
"""

import pytest
from app.memory.memory_policies import MemoryPolicyEngine
from app.memory.exceptions import TenantMemoryIsolationError, MemoryRBACPermissionDeniedError


def test_memory_policy_engine_validation():
    # Valid tenant access
    MemoryPolicyEngine.validate_tenant_access("org_1", "org_1", "ws_1", "ws_1")

    # Cross-tenant access -> Exception
    with pytest.raises(TenantMemoryIsolationError):
        MemoryPolicyEngine.validate_tenant_access("org_1", "org_2")

    # Cross-workspace access -> Exception
    with pytest.raises(TenantMemoryIsolationError):
        MemoryPolicyEngine.validate_tenant_access("org_1", "org_1", "ws_1", "ws_2")

    # RBAC checks
    MemoryPolicyEngine.validate_rbac(["admin"], "write")
    MemoryPolicyEngine.validate_rbac(["developer"], "write")

    with pytest.raises(MemoryRBACPermissionDeniedError):
        MemoryPolicyEngine.validate_rbac(["viewer"], "write")
