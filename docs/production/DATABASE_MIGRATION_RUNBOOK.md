# DATABASE MIGRATION RUNBOOK

**Target System:** Enterprise AI Platform  
**Execution Boundary Notice:** Advisory procedures for database schema migrations. `MIGRATION_RUNTIME_NOT_EXECUTED` is maintained until migrations are explicitly run.

---

## 1. PREPARATION
1. Confirm Alembic migration scripts exist in `/alembic/versions`.
2. Inspect target database schema and create pre-migration backup (`DATABASE_BACKUP_READY`).

## 2. VALIDATION
1. Run schema compatibility analysis against the proposed release candidate.
2. Confirm zero non-nullable column additions without default values.

## 3. EXECUTION
1. Execute migration dry-run script.
2. Apply schema migration to target PostgreSQL instance.

## 4. ROLLBACK
1. If migration fails, execute Alembic downgrade script (`alembic downgrade -1`).
2. Verify table indexes and constraints match previous schema state.
