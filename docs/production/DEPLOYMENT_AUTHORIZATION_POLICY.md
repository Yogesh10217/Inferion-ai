# Deployment Authorization Policy

## 1. Governance Categories
Authorization requires 100% signoff across 6 distinct categories:
1. `TECHNICAL`: Platform lead signoff on code & test coverage.
2. `SECURITY`: CISO/SecOps signoff on canary checks & vulnerability scans.
3. `DATABASE`: DBA signoff on migration safety and rollback scripts.
4. `OPERATIONS`: SRE signoff on observability and monitoring SLAs.
5. `RELEASE`: Release manager signoff on manifest & artifact identity.
6. `DEPLOYMENT_EXECUTOR`: Explicit authorization to trigger deployment execution.

## 2. Invalidation & Binding Rules
- **Digest Binding**: Modifying the SHA-256 artifact digest immediately invalidates all active authorizations (`DEPLOYMENT_ARTIFACT_MISMATCH`).
- **Git Revision Binding**: Changing the git commit SHA invalidates active authorizations.
- **TTL Expiration**: Authorizations expire automatically after configured TTL (default: 3600 seconds). Expired authorizations return `AUTHORIZATION_EXPIRED`.
