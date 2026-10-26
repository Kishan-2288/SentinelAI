from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./sentinelai.db"
    supabase_url: str = "https://pkkqopmwlfarbbzomsvf.supabase.co"
    supabase_jwt_secret: str = ""
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    external_api_base_url: str = "https://api.openai.com/v1"
    external_api_key: str = ""
    external_api_model: str = ""
    secret_encryption_key: str = ""
    request_timeout_seconds: float = 60.0
    llm_max_attempts: int = 3
    llm_retry_backoff_seconds: float = 1.0
    max_concurrent_runs: int = 2
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    dev_user_id: str = "local-dev"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def sqlalchemy_url(self) -> str:
        """Normalise Supabase/Heroku-style URLs to the psycopg3 SQLAlchemy driver."""
        url = self.database_url
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url[len(prefix):]
        return url

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
