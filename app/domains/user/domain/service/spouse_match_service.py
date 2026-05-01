"""곧 다가올 인연(spouseMatch) 지표 산출 서비스.

dohwa-backend src/lib/spouseMatch.ts + transformers/spouseMatchView.ts 포팅.
"""

from __future__ import annotations

from typing import Any, cast

from app.domains.user.domain.value_object.saju_constants import WuXing, YinYang

ELEMENT_PREFIX: dict[WuXing, str] = {
    "목": "wood", "화": "fire", "토": "earth", "금": "metal", "수": "water",
}

YIN_YANG_SLUG: dict[YinYang, str] = {"양": "yang", "음": "yin"}

# 일간 오행을 생(生)하는 오행 (역방향 생 관계)
WUXING_GENERATING_ME: dict[WuXing, WuXing] = {
    "목": "수", "화": "목", "토": "화", "금": "토", "수": "금",
}


def _resolve_match_element(saju: dict[str, Any]) -> WuXing | None:
    yong_sin = saju.get("yongSin") or {}
    primary = yong_sin.get("primaryYongSin")
    if primary:
        return cast(WuXing, primary)
    secondary = yong_sin.get("secondaryYongSin")
    if secondary:
        return cast(WuXing, secondary)
    day_stem_element = saju["day"].get("stemElement")
    if day_stem_element:
        return WUXING_GENERATING_ME.get(cast(WuXing, day_stem_element))
    return None


class SpouseMatchService:
    """SajuData(dict) → SpouseMatchView(dict, camelCase)."""

    def calculate(self, saju: dict[str, Any]) -> dict[str, Any]:
        gender = saju.get("gender", "female")
        opposite_gender = "f" if gender == "male" else "m"

        match_element = _resolve_match_element(saju)
        if not match_element:
            return {
                "slotId": f"{opposite_gender}-neutral",
                "matchElement": None,
                "matchYinYang": None,
            }

        day_yin_yang = cast(YinYang, saju["day"]["yinYang"])
        match_yin_yang: YinYang = "음" if day_yin_yang == "양" else "양"
        slot_id = (
            f"{opposite_gender}-{ELEMENT_PREFIX[match_element]}-"
            f"{YIN_YANG_SLUG[match_yin_yang]}"
        )
        return {
            "slotId": slot_id,
            "matchElement": match_element,
            "matchYinYang": match_yin_yang,
        }
