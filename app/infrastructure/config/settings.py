from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    fortuneteller_url: str
    payapp_base_url: str
    payapp_api_key: str
    claude_api_key: str
    claude_model: str = "claude-sonnet-4-6"
    app_env: str = "local"
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env.local", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
