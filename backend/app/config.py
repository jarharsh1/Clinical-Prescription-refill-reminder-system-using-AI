from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = "dev-secret-change-me"
    database_url: str = "sqlite:///./refill_reminder.db"
    anthropic_api_key: str | None = None
    access_token_expire_minutes: int = 480
    jwt_algorithm: str = "HS256"


settings = Settings()
