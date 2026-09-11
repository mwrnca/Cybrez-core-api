from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str
    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_COOKIE_NAME: str = "cybrez_refresh_token"
    REFRESH_COOKIE_SECURE: bool = True

    API_V1_PREFIX: str

    DEBUG: bool = False

    # Used to build links (e.g. invitation accept links) inside
    # server-generated content like notifications and emails.
    # Set this to the real production frontend URL in prod .env.
    FRONTEND_URL: str = "http://localhost:5173"

    # ---------------------------------------------------------------------------
    # Rate limiting (requests per minute, per key)
    # These are in-memory limits suitable for single-instance deployments.
    # For multi-instance / distributed deployments, migrate to shared storage
    # (e.g. Redis) and update app/core/rate_limit.py accordingly.
    # ---------------------------------------------------------------------------
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 10
    RATE_LIMIT_REGISTER_PER_MINUTE: int = 5
    RATE_LIMIT_REFRESH_PER_MINUTE: int = 20
    RATE_LIMIT_LOGOUT_PER_MINUTE: int = 20
    RATE_LIMIT_INVITE_CREATE_PER_MINUTE: int = 10
    RATE_LIMIT_INVITE_RESEND_PER_MINUTE: int = 5
    RATE_LIMIT_SEARCH_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()