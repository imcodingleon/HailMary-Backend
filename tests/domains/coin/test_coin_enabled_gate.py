"""coin_enabled 플래그 게이트 회귀 테스트 (Task 2 리뷰 후속, HMDA-PG P4 Unit B).

app/main.py는 `if _settings.coin_enabled:` 블록 안에서만 coin_router /
coin_unlock_router를 등록한다 — "1.0 무영향" 안전장치의 핵심 분기(PG_SSOT.md).
이 게이트에 대한 자동화 테스트가 없다는 리뷰 지적에 따라 추가한다.

app/main.py는 별도 create_app() 팩토리 없이 모듈 로드 시 app 인스턴스를
구성하는 하드 싱글톤(app = FastAPI(...)가 import-time에 실행되고,
include_router 호출도 import-time에 끝남)이라, 테스트 안에서 코인 라우터
등록 여부를 바꿔볼 유일한 방법은 monkeypatch(COIN_ENABLED) + get_settings
캐시 초기화 + importlib.reload(app.main) 조합뿐이다. main.py를 팩토리
패턴으로 바꾸는 건 프로덕션 코드 변경이라 이 테스트 범위 밖.

리로드는 OAuth 클라이언트/Redis 캐시 등 다른 모듈 전역도 재생성하지만
전부 lazy 생성자(네트워크 I/O 없음)라 부작용 없음. 그래도 다른 테스트에
남는 상태를 주지 않도록 매 테스트 종료 후 기본값(coin_enabled=False)으로
한 번 더 리로드해 복원한다.
"""

from __future__ import annotations

import importlib
from collections.abc import Generator

import pytest

from app.infrastructure.config.settings import get_settings

_COIN_PATHS = {"/api/coins/balance", "/api/coins/spend/love-report"}


def _reload_main_with(monkeypatch: pytest.MonkeyPatch, *, coin_enabled: bool) -> set[str]:
    """COIN_ENABLED 환경변수를 지정한 값으로 바꾸고 app.main을 리로드해
    최종 라우트 경로 집합을 반환한다."""
    monkeypatch.setenv("COIN_ENABLED", "true" if coin_enabled else "false")
    get_settings.cache_clear()
    import app.main as main_module

    importlib.reload(main_module)
    return {route.path for route in main_module.app.routes}  # type: ignore[attr-defined]


@pytest.fixture(autouse=True)
def _restore_main_module_after_test(monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    """모듈 싱글톤 상태를 다음 테스트를 위해 기본값(coin_enabled=False)으로 복원."""
    yield
    monkeypatch.setenv("COIN_ENABLED", "false")
    get_settings.cache_clear()
    import app.main as main_module

    importlib.reload(main_module)
    get_settings.cache_clear()


def test_coin_enabled_false_does_not_mount_coin_routes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """coin_enabled=False면 balance/spend 라우트 둘 다 라우트 테이블에 없어야 한다."""
    paths = _reload_main_with(monkeypatch, coin_enabled=False)

    assert not (_COIN_PATHS & paths), (
        f"coin_enabled=False인데 코인 라우터가 등록됨: {_COIN_PATHS & paths}"
    )


def test_coin_enabled_true_mounts_coin_routes(monkeypatch: pytest.MonkeyPatch) -> None:
    """coin_enabled=True면 balance/spend 라우트 둘 다 라우트 테이블에 있어야 한다."""
    paths = _reload_main_with(monkeypatch, coin_enabled=True)

    assert paths >= _COIN_PATHS, f"coin_enabled=True인데 미등록: {_COIN_PATHS - paths}"
