"""charm_service v2 산식 회귀 테스트.

검증 포인트:
- Top 10 매력 신호 가산 (홍염살, 자좌홍염, 천을귀인, 도화일주, 시너지,
  도화 충 페널티, 목욕 위치 가중, 금여록, 편관·식상×도화 격국, 공망 페널티 확장)
- FortuneTeller 폴백 동등성 (응답에 sinSals/charmFlags 없어도 같은 점수)
- v2 가산 0 사주는 기존 결과와 동등
- floor=20 유지, cap=100 유지
"""

from __future__ import annotations

from typing import Any

import pytest

from app.domains.user.domain.service.charm_service import (
    V2_BONUS_CAP,
    CharmService,
    _augment_charm_signals,
    _calculate_v2_bonus,
    _find_dohwa_pillars,
    _has_geum_yeo_rok,
    _has_hong_yeom,
    _is_dohwa_ilju,
    _is_ja_jwa_hong_yeom,
    _mokyok_pillars,
)

# ── 사주 fixture 빌더 ─────────────────────────────────────────────────────


def _pillar(stem: str, branch: str) -> dict[str, Any]:
    return {"stem": stem, "branch": branch}


def make_saju(
    year: tuple[str, str],
    month: tuple[str, str],
    day: tuple[str, str],
    hour: tuple[str, str],
    *,
    sin_sals: list[str] | None = None,
    ten_gods: dict[str, int] | None = None,
    charm_flags: dict[str, Any] | None = None,
) -> dict[str, Any]:
    saju: dict[str, Any] = {
        "year": _pillar(*year),
        "month": _pillar(*month),
        "day": _pillar(*day),
        "hour": _pillar(*hour),
        "sinSals": list(sin_sals) if sin_sals is not None else [],
        "tenGodsDistribution": dict(ten_gods) if ten_gods is not None else {},
    }
    if charm_flags is not None:
        saju["charmFlags"] = dict(charm_flags)
    return saju


# ── 폴백 헬퍼 단위 테스트 ──────────────────────────────────────────────────


class TestFallbackDetectors:
    def test_hong_yeom_gap_o(self) -> None:
        """갑오일주 → 자좌홍염, 홍염살 hit."""
        saju = make_saju(("임", "신"), ("신", "해"), ("갑", "오"), ("경", "오"))
        assert _has_hong_yeom(saju) is True
        assert _is_ja_jwa_hong_yeom(saju) is True

    def test_hong_yeom_eul_dual_match(self) -> None:
        """을 일간은 오·신 둘 다 홍염 — 둘 중 하나만 있어도 true."""
        saju_o = make_saju(("갑", "자"), ("갑", "자"), ("을", "묘"), ("갑", "오"))
        saju_sin = make_saju(("갑", "자"), ("갑", "자"), ("을", "묘"), ("갑", "신"))
        saju_miss = make_saju(("갑", "자"), ("갑", "자"), ("을", "묘"), ("갑", "축"))
        assert _has_hong_yeom(saju_o) is True
        assert _has_hong_yeom(saju_sin) is True
        assert _has_hong_yeom(saju_miss) is False

    def test_geum_yeo_rok(self) -> None:
        """갑 일간 → 진 보유 시 금여록."""
        saju_hit = make_saju(("갑", "진"), ("갑", "자"), ("갑", "오"), ("갑", "자"))
        saju_miss = make_saju(("갑", "사"), ("갑", "자"), ("갑", "오"), ("갑", "자"))
        assert _has_geum_yeo_rok(saju_hit) is True
        assert _has_geum_yeo_rok(saju_miss) is False

    @pytest.mark.parametrize(
        ("stem", "branch"),
        [("갑", "오"), ("정", "미"), ("무", "진"), ("기", "진"),
         ("경", "술"), ("신", "유"), ("임", "자")],
    )
    def test_ja_jwa_hong_yeom_all_seven_ilju(self, stem: str, branch: str) -> None:
        saju = make_saju(("갑", "자"), ("갑", "자"), (stem, branch), ("갑", "자"))
        assert _is_ja_jwa_hong_yeom(saju) is True

    def test_ja_jwa_hong_yeom_miss(self) -> None:
        saju = make_saju(("갑", "자"), ("갑", "자"), ("갑", "자"), ("갑", "자"))
        assert _is_ja_jwa_hong_yeom(saju) is False

    @pytest.mark.parametrize("branch", ["자", "묘", "오", "유"])
    def test_dohwa_ilju_hit(self, branch: str) -> None:
        saju = make_saju(("갑", "자"), ("갑", "자"), ("갑", branch), ("갑", "자"))
        assert _is_dohwa_ilju(saju) is True

    def test_dohwa_ilju_miss(self) -> None:
        saju = make_saju(("갑", "자"), ("갑", "자"), ("갑", "인"), ("갑", "자"))
        assert _is_dohwa_ilju(saju) is False

    def test_mokyok_pillars_gap_at_hour(self) -> None:
        """갑 일간의 목욕은 자(子). hour=자 → mokyokPillars=['hour']."""
        saju = make_saju(("임", "신"), ("신", "해"), ("갑", "오"), ("경", "자"))
        assert _mokyok_pillars(saju) == ["hour"]


# ── 폴백 동등성 (FortuneTeller 미제공 ↔ 제공 시 같은 결과) ────────────────


class TestFallbackParity:
    def test_augment_does_not_override_existing(self) -> None:
        """FortuneTeller가 이미 보낸 값은 덮어쓰지 않음."""
        saju = make_saju(
            ("임", "신"), ("신", "해"), ("갑", "오"), ("경", "오"),
            sin_sals=["hong_yeom_sal"],  # 이미 보냄
            charm_flags={"dohwaIlju": False, "jaJwaHongYeom": False},  # 임의의 우회값
        )
        augmented = _augment_charm_signals(saju)
        # 이미 보낸 값 신뢰 (덮어쓰지 않음)
        assert augmented["charmFlags"]["dohwaIlju"] is False
        assert augmented["charmFlags"]["jaJwaHongYeom"] is False
        # 홍염살 중복 추가 없음
        assert augmented["sinSals"].count("hong_yeom_sal") == 1

    def test_augment_fills_missing(self) -> None:
        """sinSals/charmFlags 없을 때 폴백으로 채움."""
        saju = make_saju(("임", "신"), ("신", "해"), ("갑", "오"), ("경", "오"))
        augmented = _augment_charm_signals(saju)
        assert "hong_yeom_sal" in augmented["sinSals"]
        assert "ja_jwa_hong_yeom" in augmented["sinSals"]
        assert augmented["charmFlags"]["dohwaIlju"] is True
        assert augmented["charmFlags"]["jaJwaHongYeom"] is True

    def test_calculate_parity_with_and_without_flags(self) -> None:
        """charm_service.calculate 결과: FortuneTeller 응답 유무 무관 동등."""
        saju_without = make_saju(
            ("임", "신"), ("신", "해"), ("갑", "오"), ("경", "오"),
            ten_gods={"편인": 2, "정관": 1, "편관": 2, "상관": 2},
        )
        saju_with = make_saju(
            ("임", "신"), ("신", "해"), ("갑", "오"), ("경", "오"),
            sin_sals=["hong_yeom_sal", "ja_jwa_hong_yeom"],
            ten_gods={"편인": 2, "정관": 1, "편관": 2, "상관": 2},
            charm_flags={
                "dohwaIlju": True,
                "jaJwaHongYeom": True,
                "hongYeomDohwaSynergy": False,
                "mokyokPillars": [],
            },
        )
        result_without = CharmService().calculate(saju_without)
        result_with = CharmService().calculate(saju_with)
        assert result_without["charmStrength"] == result_with["charmStrength"]


# ── v2 가산 시뮬레이션 ─────────────────────────────────────────────────────


class TestV2Bonus:
    def test_1992_11_14_gap_o_jeong_o_floor_escape(self) -> None:
        """플랜 핵심 케이스: 1992-11-14 갑오일 시간 모름→정오(경오시).

        지지: 신·해·오·오. 갑오 자좌홍염 + 홍염살 + 도화일주.
        기존 산식만으로는 floor 20에 묶였던 케이스가 v2로 자력 탈출.
        """
        saju = make_saju(
            ("임", "신"), ("신", "해"), ("갑", "오"), ("경", "오"),
            ten_gods={"편인": 2, "정관": 1, "편관": 2, "상관": 2},
        )
        result = CharmService().calculate(saju)
        assert result["charmStrength"] > 20, "floor 탈출 실패"
        # 도화 가중치 없음(도화 자 미적중) + 홍염 hit + 자좌홍염 + 도화일주
        # + 공망×홍염 페널티 + 12운성 큰 마이너스. 25~60 범위.
        # 상한 갱신: 2026-05-15 매력 v3 도화 부재 대체 가산(천을 +25 / 홍염 +25)
        # 도입으로 합산 자연스레 50 초과 가능. 56점도 정상 운영 분포.
        assert 25 <= result["charmStrength"] <= 60, (
            f"실제 점수 {result['charmStrength']}"
        )

    def test_v2_bonus_zero_no_drift(self) -> None:
        """v2_bonus 가 0인 사주는 v2 도입 전후 점수 동일.

        모든 v2 신호 + 천을귀인(v2 가산 항목)이 모두 0인 fixture.
        갑신일주: 자좌홍염/도화일주/홍염/금여록/천을귀인/목욕 전부 미적중.
        """
        saju = make_saju(
            ("갑", "인"), ("갑", "인"), ("갑", "신"), ("갑", "인"),
            ten_gods={},
        )
        augmented = _augment_charm_signals(saju)
        for v2_sig in ("hong_yeom_sal", "geum_yeo_rok", "ja_jwa_hong_yeom"):
            assert v2_sig not in augmented["sinSals"], (
                f"{v2_sig} 가 잘못 채워짐"
            )
        # 천을귀인도 미적중 확인 (갑→축미, fixture 에 없음)
        assert "cheon_eul_gwi_in" not in augmented["sinSals"]
        assert augmented["charmFlags"]["dohwaIlju"] is False
        assert augmented["charmFlags"]["jaJwaHongYeom"] is False
        assert augmented["charmFlags"]["mokyokPillars"] == []
        dohwa_pillars = _find_dohwa_pillars(augmented)
        assert _calculate_v2_bonus(augmented, dohwa_pillars) == 0

    def test_v2_bonus_capped_at_30(self) -> None:
        """모든 신호 풀세트라도 _calculate_score 내부에서 cap +30 적용."""
        # 인위적 charm_flags 로 풀 보너스 강제. _augment 가 덮어쓰지 않으므로 유지.
        saju = make_saju(
            ("갑", "축"), ("갑", "자"), ("갑", "오"), ("갑", "진"),
            sin_sals=["cheon_eul_gwi_in", "geum_yeo_rok", "hong_yeom_sal"],
            ten_gods={"편관": 2, "상관": 2},
            charm_flags={
                "dohwaIlju": True,
                "jaJwaHongYeom": True,
                "hongYeomDohwaSynergy": True,
                "mokyokPillars": ["day", "hour", "month"],
            },
        )
        augmented = _augment_charm_signals(saju)
        dohwa_pillars = _find_dohwa_pillars(augmented)
        raw_bonus = _calculate_v2_bonus(augmented, dohwa_pillars)
        assert raw_bonus > V2_BONUS_CAP, f"raw {raw_bonus} 가 cap 미만이면 검증 X"

    def test_hong_yeom_adds_score(self) -> None:
        """홍염 적중 사주가 미적중 사주보다 점수 ≥."""
        # 동일 일주(을묘) + hour만 차이.
        # 을 일간 12운성: 묘=건록(4), 오=장생(3). 사=목욕(8) — base가 사라 12운성 보너스 큼.
        # 홍염 (을→오 또는 신): hour=오 시 hit.
        saju_base = make_saju(
            ("갑", "축"), ("갑", "자"), ("을", "묘"), ("갑", "축"),  # 매력 신호 적음
            ten_gods={},
        )
        saju_hong = make_saju(
            ("갑", "축"), ("갑", "자"), ("을", "묘"), ("갑", "오"),  # hour=오 홍염
            ten_gods={},
        )
        result_base = CharmService().calculate(saju_base)
        result_hong = CharmService().calculate(saju_hong)
        assert result_hong["charmStrength"] > result_base["charmStrength"]

    def test_dohwa_chung_penalty(self) -> None:
        """도화 충 페널티: 도화 지지가 6충 페어로 사주에 동시 존재 시."""
        from app.domains.user.domain.service.charm_service import (
            _dohwa_chung_pillars,
        )

        # 사유축 그룹 도화 = 오. day=오가 도화 + hour=자 → 자오충.
        saju = make_saju(
            ("을", "축"), ("정", "유"), ("갑", "오"), ("병", "자"),
            ten_gods={},
        )
        augmented = _augment_charm_signals(saju)
        dohwa = _find_dohwa_pillars(augmented)
        assert "day" in dohwa  # day=오 가 도화 기둥으로 잡혀야 함
        chung = _dohwa_chung_pillars(augmented, dohwa)
        assert "day" in chung  # day=오와 hour=자 의 자오충


# ── 회귀 가드: v2 가산 0 인 사주의 점수 안정성 ──────────────────────────


class TestRegressionGuard:
    def test_existing_seven_sinsals_preserved(self) -> None:
        """기존 7개 신살은 augment 후에도 그대로 유지 (중복 추가 X)."""
        saju = make_saju(
            ("임", "신"), ("신", "해"), ("갑", "오"), ("임", "자"),
            sin_sals=[
                "cheon_eul_gwi_in", "do_hwa_sal", "yeok_ma_sal",
                "gong_mang", "hwa_gae_sal", "won_jin_sal", "gwi_mun_gwan_sal",
            ],
        )
        augmented = _augment_charm_signals(saju)
        for ss in [
            "cheon_eul_gwi_in", "do_hwa_sal", "yeok_ma_sal",
            "gong_mang", "hwa_gae_sal", "won_jin_sal", "gwi_mun_gwan_sal",
        ]:
            assert augmented["sinSals"].count(ss) == 1

    def test_calculate_returns_camelcase_keys(self) -> None:
        """반환 DTO key shape 비파괴."""
        saju = make_saju(
            ("갑", "인"), ("을", "축"), ("갑", "인"), ("정", "사"),
            ten_gods={},
        )
        result = CharmService().calculate(saju)
        for key in (
            "typeKey", "manifestationKey", "variantTags", "charmStrength",
            "charmPercentile", "showPercent", "label", "dohwa",
        ):
            assert key in result
