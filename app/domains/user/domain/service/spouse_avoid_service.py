"""피해야 할 인연(spouseAvoid) 지표 산출 서비스.

dohwa-backend src/lib/spouseAvoid.ts + transformers/spouseAvoidView.ts 포팅.
"""

from __future__ import annotations

from typing import Any, cast

from app.domains.user.domain.value_object.saju_constants import (
    WUXING_DESTRUCTION,
    WuXing,
    YinYang,
)

ELEMENT_PREFIX: dict[WuXing, str] = {
    "목": "wood", "화": "fire", "토": "earth", "금": "metal", "수": "water",
}

YIN_YANG_SLUG: dict[YinYang, str] = {
    "양": "yang", "음": "yin",
}


def _resolve_avoid_element(saju: dict[str, Any]) -> WuXing | None:
    yong_sin = saju.get("yongSin") or {}
    primary = yong_sin.get("primaryYongSin")
    if primary:
        return WUXING_DESTRUCTION.get(cast(WuXing, primary))

    day_stem_element = saju["day"].get("stemElement")
    if day_stem_element:
        return WUXING_DESTRUCTION.get(cast(WuXing, day_stem_element))
    return None


class SpouseAvoidService:
    """SajuData(dict) → SpouseAvoidView(dict, camelCase)."""

    def calculate(self, saju: dict[str, Any]) -> dict[str, Any]:
        avoid_element = _resolve_avoid_element(saju)
        if not avoid_element:
            return {"slotId": "neutral", "avoidElement": None, "avoidYinYang": None}

        avoid_yin_yang = cast(YinYang, saju["day"]["yinYang"])
        gender = saju.get("gender", "female")
        opposite_gender = "f" if gender == "male" else "m"
        slot_id = (
            f"{opposite_gender}-{ELEMENT_PREFIX[avoid_element]}-"
            f"{YIN_YANG_SLUG[avoid_yin_yang]}"
        )
        return {
            "slotId": slot_id,
            "avoidElement": avoid_element,
            "avoidYinYang": avoid_yin_yang,
        }
