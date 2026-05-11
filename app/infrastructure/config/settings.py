from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    fortuneteller_url: str
    payapp_base_url: str | None = None
    payapp_api_key: str | None = None
    claude_api_key: str | None = None
    claude_model: str = "claude-sonnet-4-6"
    app_env: str = "local"
    debug: bool = False
    # 토스페이먼츠 결제 승인 (백엔드 전용)
    toss_secret_key: str | None = None
    toss_base_url: str = "https://api.tosspayments.com"
    # Amplitude HTTP API V2 (백엔드 결제 이벤트 발화용)
    amplitude_api_key: str | None = None
    amplitude_base_url: str = "https://api2.amplitude.com"

    model_config = SettingsConfigDict(
        env_file=".env.local", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
