import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# ── APP_ENV에 따라 env_file 분기 ──
# local → .env.local (개발)
# test  → .env.test (QA 분리 DB, 포트 3308)
# prod  → .env.prod (운영)
_ENV_FILE_MAP: dict[str, str] = {
    "local": ".env.local",
    "test": ".env.test",
    "prod": ".env.prod",
}
_CURRENT_ENV: str = os.environ.get("APP_ENV", "local")
_ENV_FILE: str = _ENV_FILE_MAP.get(_CURRENT_ENV, ".env.local")


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
    # AWS SES (이메일 발송, Phase 4 추가 예정)
    aws_region: str = "ap-northeast-2"
    aws_ses_sender: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    # QA 로그인 게이트 (APP_ENV=test 일 때만 활성, 운영에선 무시)
    qa_username: str | None = None
    qa_password: str | None = None
    qa_access_token: str | None = None

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
