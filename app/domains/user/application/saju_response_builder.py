"""FortuneTeller 응답 dict + 분석 서비스 결과를 묶어 FreeResultResponse 로 변환.

영업비밀 차단:
  - yongSin.reasoning 제거
  - dayMasterStrength.score / analysis 제거
  - gyeokGuk 세부, jiJangGan 세부, branchRelations 세부, wolRyeong, specialMarks
    는 응답에서 제거 (프론트에 노출되지 않도록)
"""

from __future__ import annotations

from typing import Any

from app.domains.user.application.response.free_result_response import (
    BlockingView,
    CharmView,
    FreeResultResponse,
    MonthlyRomanceFlowView,
    SpouseAvoidView,
    SpouseMatchView,
)

_SECRET_TOP_LEVEL_KEYS: tuple[str, ...] = (
    "gyeokGuk",
    "jiJangGan",
    "branchRelations",
    "wolRyeong",
    "specialMarks",
)


def _strip_business_secrets(saju_data: dict[str, Any]) -> dict[str, Any]:
    """원본 dict 를 변경하지 않고 영업비밀 필드를 제거한 사본을 반환."""
    sanitized = dict(saju_data)

    for key in _SECRET_TOP_LEVEL_KEYS:
        sanitized.pop(key, None)

    yong_sin = sanitized.get("yongSin")
    if isinstance(yong_sin, dict):
        clean_yong_sin = dict(yong_sin)
        clean_yong_sin.pop("reasoning", None)
        sanitized["yongSin"] = clean_yong_sin

    day_master_strength = sanitized.get("dayMasterStrength")
    if isinstance(day_master_strength, dict):
        clean_dms = dict(day_master_strength)
        clean_dms.pop("score", None)
        clean_dms.pop("analysis", None)
        sanitized["dayMasterStrength"] = clean_dms

    return sanitized


def build_free_result_response(
    *,
    saju_request_id: int,
    saju_data: dict[str, Any],
    charm: dict[str, Any],
    blocking: dict[str, Any],
    spouse_avoid: dict[str, Any],
    spouse_match: dict[str, Any],
    monthly_romance_flow: dict[str, Any],
) -> FreeResultResponse:
    return FreeResultResponse(
        sajuRequestId=saju_request_id,
        sajuData=_strip_business_secrets(saju_data),
        charm=CharmView.model_validate(charm),
        blocking=BlockingView.model_validate(blocking),
        spouseAvoid=SpouseAvoidView.model_validate(spouse_avoid),
        spouseMatch=SpouseMatchView.model_validate(spouse_match),
        monthlyRomanceFlow=MonthlyRomanceFlowView.model_validate(monthly_romance_flow),
    )
