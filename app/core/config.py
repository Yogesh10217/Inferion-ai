from functools import lru_cache

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="LLM Inference Engine", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    api_prefix: str = Field(default="/v1", alias="API_PREFIX")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    cohere_api_key: str | None = Field(default=None, alias="COHERE_API_KEY")
    mistral_api_key: str | None = Field(default=None, alias="MISTRAL_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"], alias="CORS_ORIGINS")

    # Batching Config
    batch_enabled: bool = Field(default=True, alias="BATCH_ENABLED")
    batch_max_size: int = Field(default=10, alias="BATCH_MAX_SIZE")
    batch_max_wait_ms: int = Field(default=50, alias="BATCH_MAX_WAIT_MS")
    batch_max_queue_tokens: int = Field(default=10000, alias="BATCH_MAX_QUEUE_TOKENS")

    # Load Balancing Configuration
    load_balancing_policy: str = Field(default="round_robin", alias="LOAD_BALANCING_POLICY")
    provider_health_check_interval_s: float = Field(default=10.0, alias="PROVIDER_HEALTH_CHECK_INTERVAL_S")
    provider_failure_threshold: int = Field(default=3, alias="PROVIDER_FAILURE_THRESHOLD")
    provider_recovery_time_s: float = Field(default=30.0, alias="PROVIDER_RECOVERY_TIME_S")
    default_provider_weight: int = Field(default=1, alias="DEFAULT_PROVIDER_WEIGHT")

    # Caching Configuration
    cache_enabled: bool = Field(default=True, alias="CACHE_ENABLED")
    cache_backend: str = Field(default="memory", alias="CACHE_BACKEND")  # 'memory' or 'redis'
    cache_ttl_seconds: int = Field(default=3600, alias="CACHE_TTL_SECONDS")
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")

    # Observability Configuration
    prometheus_enabled: bool = Field(default=True, alias="PROMETHEUS_ENABLED")
    prometheus_namespace: str = Field(default="llm_engine", alias="PROMETHEUS_NAMESPACE")
    prometheus_subsystem: str = Field(default="inference", alias="PROMETHEUS_SUBSYSTEM")

    # Authentication & Database Configuration
    auth_enabled: bool = Field(default=True, alias="AUTH_ENABLED")
    database_url: str = Field(default="sqlite+aiosqlite:///./data/engine.db", alias="DATABASE_URL")
    jwt_secret: str = Field(default="super-secret-key-change-in-production", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    api_key_length: int = Field(default=32, alias="API_KEY_LENGTH")
    allow_anonymous: bool = Field(default=False, alias="ALLOW_ANONYMOUS")

    # Rate Limiting & Quotas Configuration
    rate_limiting_enabled: bool = Field(default=True, alias="RATE_LIMITING_ENABLED")
    rate_limit_backend: str = Field(default="memory", alias="RATE_LIMIT_BACKEND")  # 'memory' or 'redis'
    default_rate_limit_strategy: str = Field(default="sliding_window", alias="DEFAULT_RATE_LIMIT_STRATEGY")
    default_requests_per_minute: int = Field(default=60, alias="DEFAULT_REQUESTS_PER_MINUTE")
    default_tokens_per_day: int = Field(default=100000, alias="DEFAULT_TOKENS_PER_DAY")
    default_concurrent_requests: int = Field(default=5, alias="DEFAULT_CONCURRENT_REQUESTS")

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, value: str, info: ValidationInfo) -> str:
        env = info.data.get("environment", "development")
        if env.lower() == "production" and value == "super-secret-key-change-in-production":
            raise ValueError("JWT_SECRET must be changed from default in production environment!")
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object, info: ValidationInfo) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
