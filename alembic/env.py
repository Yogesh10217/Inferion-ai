import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config, create_async_engine

from alembic import context

# ---------------------------------------------------------------------------
# Load application settings so we get the real DATABASE_URL from .env
# ---------------------------------------------------------------------------
from app.core.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Alembic Config object — gives access to values within alembic.ini
# ---------------------------------------------------------------------------
config = context.config

# Override sqlalchemy.url from the app's settings (reads from .env)
db_url = settings.database_url
# Alembic needs a *synchronous* URL for the config key even though we use
# async engines below.  We swap the async driver prefix for the sync one.
sync_url = (
    db_url
    .replace("sqlite+aiosqlite", "sqlite")
    .replace("postgresql+asyncpg", "postgresql+psycopg2")
)
config.set_main_option("sqlalchemy.url", sync_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import all models so Alembic can detect schema changes automatically
# ---------------------------------------------------------------------------
from app.core.database import Base  # noqa: E402  — must be after settings load

import app.auth.models          # noqa: F401
import app.tenant.models        # noqa: F401
import app.limits.models        # noqa: F401
import app.billing.models       # noqa: F401
import app.admin.models         # noqa: F401
import app.events.event_models  # noqa: F401
import app.knowledge.models     # noqa: F401
import app.observability.models # noqa: F401
import app.registry.models      # noqa: F401
import app.mlops.models         # noqa: F401
import app.access_intelligence.orm_models # noqa: F401
import app.agent_orchestration.orm_models # noqa: F401
import app.ai_lifecycle_platform.orm_models # noqa: F401
import app.application_platform.models # noqa: F401
import app.architecture_platform.models # noqa: F401
import app.capacity_intelligence.models # noqa: F401
import app.compliance_platform.models # noqa: F401
import app.continuous_assurance.models # noqa: F401
import app.control_assurance.models # noqa: F401
import app.data_fabric.models # noqa: F401
import app.data_governance.models # noqa: F401
import app.data_intelligence.models # noqa: F401
import app.decision_governance.models # noqa: F401
import app.decision_intelligence.models # noqa: F401
import app.developer_platform.models # noqa: F401
import app.extensions.models # noqa: F401
import app.finops.models # noqa: F401
import app.governance_platform.models # noqa: F401
import app.identity.models # noqa: F401
import app.identity_assurance.models # noqa: F401
import app.integration_intelligence.models # noqa: F401
import app.integrations.models # noqa: F401
import app.intelligence_platform.models # noqa: F401
import app.jobs.models # noqa: F401
import app.knowledge_assurance.models # noqa: F401
import app.knowledge_intelligence.models # noqa: F401
import app.knowledge_platform.models # noqa: F401
import app.marketplace.models # noqa: F401
import app.model_intelligence.models # noqa: F401
import app.operations.models # noqa: F401
import app.operations_assurance.models # noqa: F401
import app.operations_intelligence.models # noqa: F401
import app.orchestration.models # noqa: F401
import app.planning.models # noqa: F401
import app.platform_hardening.models # noqa: F401
import app.platform_integration.models # noqa: F401
import app.platform_operations.models # noqa: F401
import app.platform_resilience.models # noqa: F401
import app.portfolio_platform.models # noqa: F401
import app.reliability.models # noqa: F401
import app.reliability_intelligence.models # noqa: F401
import app.runtime_intelligence.models # noqa: F401
import app.security.models # noqa: F401
import app.security_assurance.models # noqa: F401
import app.security_intelligence.models # noqa: F401
import app.unified_intelligence.models # noqa: F401

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline migration (generates SQL without a live DB connection)
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migration (async — requires a live DB connection)
# ---------------------------------------------------------------------------
def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations."""
    # asyncpg does not accept `sslmode` as a URL query param — pass ssl via connect_args
    import ssl as ssl_module
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed = urlparse(db_url)
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    needs_ssl = "sslmode" in query_params or "ssl" in query_params
    # Strip SSL params from URL — we'll pass them via connect_args instead
    clean_params = {k: v for k, v in query_params.items() if k not in ("sslmode", "ssl", "channel_binding")}
    clean_query = urlencode(clean_params, doseq=True)
    clean_url = urlunparse(parsed._replace(query=clean_query))

    connect_args = {}
    if needs_ssl:
        ssl_ctx = ssl_module.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl_module.CERT_NONE
        connect_args["ssl"] = ssl_ctx

    connectable = create_async_engine(
        clean_url,
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()



def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
