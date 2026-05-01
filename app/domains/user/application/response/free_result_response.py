from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def _camel_config() -> ConfigDict:
    return ConfigDict(populate_by_name=True)


class CharmDohwaView(BaseModel):
    model_config = _camel_config()

    present: bool
    pillar: Literal["year", "month", "day", "hour"] | None
    hanja: str | None


class CharmView(BaseModel):
    model_config = _camel_config()

    type_key: str = Field(alias="typeKey")
    manifestation_key: str = Field(alias="manifestationKey")
    variant_tags: list[str] = Field(alias="variantTags")
    charm_strength: int = Field(alias="charmStrength")
    charm_percentile: int = Field(alias="charmPercentile")
    show_percent: bool = Field(alias="showPercent")
    label: str
    dohwa: CharmDohwaView


class BlockingView(BaseModel):
    model_config = _camel_config()

    element_overload_key: str | None = Field(alias="elementOverloadKey")
    ten_god_pattern_key: str | None = Field(alias="tenGodPatternKey")


class SpouseAvoidView(BaseModel):
    model_config = _camel_config()

    slot_id: str = Field(alias="slotId")
    avoid_element: str | None = Field(alias="avoidElement")
    avoid_yin_yang: str | None = Field(alias="avoidYinYang")


class SpouseMatchView(BaseModel):
    model_config = _camel_config()

    slot_id: str = Field(alias="slotId")
    match_element: str | None = Field(alias="matchElement")
    match_yin_yang: str | None = Field(alias="matchYinYang")


class VisibleMonthView(BaseModel):
    model_config = _camel_config()

    month_label: str = Field(alias="monthLabel")
    percentage: int
    hearts: int
    is_peak: bool = Field(alias="isPeak")


class LockedSlotsView(BaseModel):
    model_config = _camel_config()

    total_count: int = Field(alias="totalCount")
    peak_offset_from_visible: int = Field(alias="peakOffsetFromVisible")


class MonthlyRomanceFlowView(BaseModel):
    model_config = _camel_config()

    visible_months: list[VisibleMonthView] = Field(alias="visibleMonths")
    locked_slots: LockedSlotsView = Field(alias="lockedSlots")


class FreeResultResponse(BaseModel):
    """무료 사주 결과 응답.

    sajuData: FortuneTeller가 반환하는 분석 dict (pillars/highlight/wuxing/yongSin/
    dayMaster/daeUn 등 기존 필드). 영업비밀 필드(yongSin.reasoning,
    dayMasterStrength.score/analysis 등)는 UseCase에서 제거된 상태로 들어온다.

    charm/blocking/spouseAvoid/spouseMatch/monthlyRomanceFlow: hailmary 백엔드가
    추가로 산출한 5종 분석 결과.
    """

    model_config = _camel_config()

    sajuRequestId: int
    sajuData: dict[str, Any]
    charm: CharmView
    blocking: BlockingView
    spouseAvoid: SpouseAvoidView
    spouseMatch: SpouseMatchView
    monthlyRomanceFlow: MonthlyRomanceFlowView
