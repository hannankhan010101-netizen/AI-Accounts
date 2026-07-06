"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for FastAPI and Prisma."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    database_url: str = "postgresql://user:pass@localhost:5432/fast_accounts"
    """Optional read replica / analytics URL — report queries use this when set (P5)."""
    database_read_url: str = ""
    # FBR / PRAL digital invoicing (P5)
    fbr_pral_enabled: bool = False
    fbr_pral_api_url: str = ""
    fbr_pral_api_key: str = ""
    # PayPro online payments (P5)
    paypro_enabled: bool = False
    paypro_merchant_id: str = ""
    paypro_api_url: str = ""
    paypro_api_key: str = ""
    paypro_webhook_secret: str = ""
    # ClickHouse analytics export (P6)
    clickhouse_url: str = ""
    clickhouse_database: str = "default"
    clickhouse_table: str = "report_runs"
    # Kuickpay (P7)
    kuickpay_enabled: bool = False
    kuickpay_merchant_id: str = ""
    kuickpay_api_url: str = ""
    kuickpay_api_key: str = ""
    kuickpay_webhook_secret: str = ""
    paypro_webhook_allowed_ips: str = ""
    kuickpay_webhook_allowed_ips: str = ""
    # Background jobs (P8)
    clickhouse_sync_interval_seconds: int = 3600
    fbr_retry_enabled: bool = True
    fbr_max_retry_count: int = 5
    fbr_retry_base_minutes: int = 15
    outbox_max_attempts: int = 5
    outbox_retry_base_minutes: int = 15
    # Phase 2 — scale-out (optional Redis; local/S3 report blobs)
    redis_url: str = ""
    report_storage_dir: str = "report_exports"
    report_cache_ttl_seconds: int = 900
    """``api`` = HTTP only; ``worker`` = background jobs only; ``all`` = both (default)."""
    app_mode: str = "all"
    rate_limit_reports_per_minute: int = 60
    # Optional S3-compatible storage (MinIO/AWS); falls back to ``report_storage_dir``.
    report_s3_bucket: str = ""
    report_s3_endpoint: str = ""
    report_s3_access_key: str = ""
    report_s3_secret_key: str = ""
    report_s3_region: str = "us-east-1"
    # Phase 3 — MV refresh, retention, maintenance
    mv_refresh_interval_seconds: int = 3600
    maintenance_interval_seconds: int = 86400
    maintenance_enabled: bool = True
    outbox_retention_days: int = 7
    audit_log_retention_days: int = 365
    # Phase 4 — observability, cache warming, ops thresholds
    log_level: str = "INFO"
    metrics_enabled: bool = True
    slow_request_ms: int = 500
    outbox_backlog_max: int = 10_000
    """Comma-separated company UUIDs to warm dashboard + TB cache on startup."""
    cache_warm_company_ids: str = ""
    cache_warm_on_startup: bool = False
    # Phase 5 — baselines (Phase 0 retroactive) + optional pg_stat in health
    perf_expose_pg_stat: bool = True
    otel_service_name: str = "fast-accounts-api"
    secrets_vault_file: str = ""
    secrets_aws_secret_arn: str = ""
    secrets_aws_region: str = "us-east-1"
    vault_addr: str = ""
    vault_secret_path: str = ""
    billing_webhook_secret: str = ""
    stripe_webhook_secret: str = ""
    stripe_secret_key: str = ""
    stripe_price_starter: str = ""
    stripe_price_pro: str = ""
    app_public_url: str = "http://localhost:3000"
    attachment_upload_dir: str = "uploads"
    attachment_s3_bucket: str = ""
    attachment_s3_endpoint: str = ""
    attachment_s3_access_key: str = ""
    attachment_s3_secret_key: str = ""
    attachment_s3_region: str = "us-east-1"
    financial_report_ids_file: str = ""
    rate_limit_webhooks_per_minute: int = 120
    rate_limit_auth_per_minute: int = 30
    jwt_secret_key: str = "dev-secret-change-me-min-32-characters-long"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: str = "http://localhost:3000"
    otp_ttl_minutes: int = 15
    # When true, sign-up / forgot-password responses include plaintext devOtp (local dev only).
    auth_expose_otp_in_response: bool = False
    # When true, new registrations skip email OTP verification: the account is
    # activated immediately at sign-up and tokens are returned. Set to false to
    # re-enable the OTP step. (Temporarily disabled per product request.)
    auth_skip_email_verification: bool = True
    # Learning assistant LLM (P52) — OpenAI-compatible chat completions API
    onboarding_llm_enabled: bool = False
    onboarding_llm_api_key: str = ""
    onboarding_llm_base_url: str = "https://api.openai.com/v1"
    onboarding_llm_model: str = "gpt-4o-mini"
    onboarding_llm_timeout_seconds: float = 12.0
    # Enterprise AI assistant (Groq) — server-side only
    groq_api_key: str = ""
    groq_enabled: bool = True
    groq_model: str = "llama-3.3-70b-versatile"
    groq_max_tokens: int = 2048
    groq_timeout_seconds: float = 60.0
    assistant_rate_limit_per_minute: int = 30
    assistant_max_message_chars: int = 4000
    assistant_memory_turns: int = 20
    # AI intelligence layer — Anthropic Claude (primary provider) + task-tier routing.
    # Key flows through secrets_resolver: ANTHROPIC_API_KEY -> env -> settings.
    anthropic_api_key: str = ""
    anthropic_enabled: bool = True
    anthropic_model: str = "claude-sonnet-5"
    anthropic_max_tokens: int = 2048
    anthropic_timeout_seconds: float = 60.0
    # Provider routing: preferred provider per task tier ("claude" | "groq" | "openai").
    # Router falls back to whichever provider is actually configured, so a Groq-only
    # deploy is unchanged until an Anthropic key is added.
    ai_provider_primary: str = "claude"
    ai_provider_fast: str = "groq"
    # Brevo (https://app.brevo.com) — preferred for OTP emails
    brevo_api_key: str = ""
    brevo_sender_email: str = "hannan.khan010101@gmail.com"
    brevo_sender_name: str = "Delta tech"
    # Optional SMTP fallback (e.g. Brevo relay: smtp-relay.brevo.com)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "hannan.khan010101@gmail.com"
    smtp_use_tls: bool = True


@lru_cache
def get_settings() -> Settings:
    """Return cached settings singleton."""

    return Settings()
