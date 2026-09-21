import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


@pytest.fixture(autouse=True)
def reset_settings():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_production_http_security_headers(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("ENVIRONMENT", "LOCAL")
    monkeypatch.setenv("DEBUG", "false")
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "Content-Security-Policy" in response.headers


def test_production_wildcard_cors_rejected(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("CORS_ORIGINS", '["*"]')
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://prod_user:prod_pass@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("JWT_SECRET", "secure_prod_secret_key_88492048")

    with pytest.raises(ValueError) as exc_info:
        create_app()
    assert "CORS_POLICY_VIOLATION" in str(exc_info.value)


def test_production_docs_disabled_by_default(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("CORS_ORIGINS", '["https://app.enterprise-ai.internal"]')
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://prod_user:prod_pass@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("JWT_SECRET", "secure_prod_secret_key_88492048")
    monkeypatch.setenv("ALLOW_DOCS_IN_PROD", "false")

    app = create_app()
    client = TestClient(app)

    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_production_cors_edge_cases(monkeypatch):
    # A. Wildcard origin
    get_settings.cache_clear()
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://prod_user:prod_pass@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("JWT_SECRET", "secure_prod_secret_key_88492048")

    monkeypatch.setenv("CORS_ORIGINS", '["*"]')
    with pytest.raises(ValueError) as exc:
        create_app()
    assert "CORS_POLICY_VIOLATION" in str(exc.value)

    # C. Empty origin list
    get_settings.cache_clear()
    monkeypatch.setenv("CORS_ORIGINS", "[]")
    with pytest.raises(ValueError) as exc:
        create_app()
    assert "CORS_POLICY_VIOLATION" in str(exc.value)

    # D. Invalid origin
    get_settings.cache_clear()
    monkeypatch.setenv("CORS_ORIGINS", '[""]')
    with pytest.raises(ValueError) as exc:
        create_app()
    assert "CORS_POLICY_VIOLATION" in str(exc.value)

    # E. Unsafe HTTP scheme
    get_settings.cache_clear()
    monkeypatch.setenv("CORS_ORIGINS", '["http://remote-unsafe-domain.com"]')
    with pytest.raises(ValueError) as exc:
        create_app()
    assert "CORS_POLICY_VIOLATION" in str(exc.value)


def test_untrusted_proxy_header_safety(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.core.middleware import SecurityHeadersMiddleware

    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware, enable_hsts=True, trust_proxies=False)

    @app.get("/test")
    def test_endpoint():
        return {"status": "ok"}

    client = TestClient(app)
    response = client.get("/test", headers={"X-Forwarded-Proto": "http"})
    assert response.status_code == 200
    assert response.headers.get("Strict-Transport-Security") == "max-age=31536000; includeSubDomains"
