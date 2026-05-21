"""도윤 P-6 3박스 AI 단위 테스트 — profile + meeting + pattern."""

from __future__ import annotations

import pytest

from app.domains.ai.application.usecase.generate_p6_meeting_usecase import (
    GenerateP6MeetingUseCase,
)
from app.domains.ai.application.usecase.generate_p6_pattern_usecase import (
    GenerateP6PatternUseCase,
)
from app.domains.ai.application.usecase.generate_p6_profile_usecase import (
    GenerateP6ProfileUseCase,
)
from app.domains.ai.domain.port.ai_client_port import AIClientError, AIClientPort
from app.domains.ai.domain.service.doyoon_p6_meeting_prompt import validate_p6_meeting
from app.domains.ai.domain.service.doyoon_p6_pattern_prompt import validate_p6_pattern
from app.domains.ai.domain.service.doyoon_p6_profile_prompt import validate_p6_profile
from app.domains.ai.domain.templates.doyoon_p6_destined import (
    compose_doyoon_p6_meeting,
    compose_doyoon_p6_pattern,
    compose_doyoon_p6_profile,
    get_doyoon_p6_meeting_facts,
    get_doyoon_p6_pattern_facts,
    get_doyoon_p6_profile_facts,
)
from app.domains.ai.domain.value_object.doyoon_p6_data import (
    DOYOON_INYON_BY_SLOT,
    DOYOON_P6_DATA,
    VALID_DOYOON_P6_ILGAN,
)


class _FakeAIClient(AIClientPort):
    def __init__(self, *, response_text=None, raise_exc=None):
        self.response_text = response_text
        self.raise_exc = raise_exc

    async def generate_chapter(self, *, system_prompt, user_prompt, max_tokens=1024, temperature=0.85, model=None):
        if self.raise_exc:
            raise self.raise_exc
        return self.response_text


# ── 데이터 완전성 ────────────────────────────────────────────────


def test_all_22_slots_inyon_data() -> None:
    assert len(DOYOON_INYON_BY_SLOT) == 22


def test_all_10_ilgan_p6_data() -> None:
    assert len(DOYOON_P6_DATA) == 10
    for ilgan in VALID_DOYOON_P6_ILGAN:
        d = DOYOON_P6_DATA[ilgan]
        assert len(d.behavior_cards) == 2


def test_compose_profile_all_slots() -> None:
    for slot in DOYOON_INYON_BY_SLOT:
        text = compose_doyoon_p6_profile(
            user_name="홍길동", ilgan="임수", match_slot_id=slot,
            pct_value=8, ohang_lack="화",
        )
        assert "홍길동님" in text


def test_compose_unknown_slot_fallback() -> None:
    text = compose_doyoon_p6_profile(
        user_name="홍길동", ilgan="임수", match_slot_id="m-unknown-yang",
        pct_value=8, ohang_lack="화",
    )
    assert "71%" in text  # f-water-yang fallback


# ── PROFILE ─────────────────────────────────────────────────────


def test_profile_facts_imsu() -> None:
    f = get_doyoon_p6_profile_facts(
        user_name="홍길동", ilgan="임수", match_slot_id="f-water-yang",
        pct_value=8, ohang_lack="화",
    )
    assert f["pct_value"] == "8%"
    assert f["compatibility_pct"] == "82%"
    assert f["height_distribution_pct"] == "71%"
    assert f["ohang_lack_hanja"] == "火"


def _profile_valid(facts):
    return (
        f"궁합 지수 상위 {facts['pct_value']} 케이스로 측정됐어요. "
        "이 구간은 통계적으로 흔하지 않은 분포예요. 최적 인연 프로파일 데이터를 차례대로 보여드릴게요.\n\n"
        f"외형 데이터 — 키 분포 ±5cm 범위가 {facts['height_distribution_pct']}, 균형 잡힌 체형이 다수. "
        "얼굴은 부드러운 둥근형이 우세하고 이마가 넓은 비율이 상위. "
        f"눈매와 입꼬리 패턴은 동일 호환 사례의 {facts['profile_signal_pct']}를 차지합니다. "
        "손가락 길이와 자세 데이터도 일관된 신호로 잡혀요.\n\n"
        f"성격 변수는 감정 변동성 평균 대비 {facts['emotional_stability_multiplier']}로 측정. "
        f"안정성이 {facts['stability_high_multiplier']} 높다는 의미예요. "
        "직업군은 기획·교육·창작 계열이 매칭 강세이고, 데이터 분포 상위에서 일관됩니다.\n\n"
        f"{facts['ohang_lack']}({facts['ohang_lack_hanja']}) 보완 효율이 결정적이에요. "
        f"{facts['ilgan_full']}({facts['ilgan_hanja']}) 일간 궁합이 {facts['compatibility_pct']}로 측정. "
        f"평균 {facts['avg_compatibility_baseline']} 대비 {facts['compatibility_lift']} 상승치예요. "
        f"{facts['user_name']}님 사주에서 비어 있던 변수를 정확히 채워주는 케이스로 분류돼요."
    )


def test_profile_validate() -> None:
    f = get_doyoon_p6_profile_facts(
        user_name="홍길동", ilgan="임수", match_slot_id="f-water-yang",
        pct_value=8, ohang_lack="화",
    )
    ok, reason = validate_p6_profile(_profile_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_profile_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP6ProfileUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수", match_slot_id="f-water-yang",
        pct_value=8, ohang_lack="화",
    )
    assert "82%" in out


# ── MEETING ─────────────────────────────────────────────────────


def test_meeting_facts_imsu() -> None:
    f = get_doyoon_p6_meeting_facts(
        user_name="홍길동", ilgan="임수", match_slot_id="f-water-yang"
    )
    assert f["existing_path_multiplier"] == "2.3배"
    assert f["low_impact_pct"] == "73%"
    assert f["second_contact_multiplier"] == "2.4배"


def _meeting_valid(facts):
    return (
        f"만남 환경 데이터부터 보여드릴게요. 기존 동선 내 재접촉 확률이 "
        f"{facts['existing_path_multiplier']} 높게 측정됩니다. "
        "새로운 환경 매칭률은 상대적으로 낮은 분포예요.\n\n"
        f"첫 접촉 패턴 — 짧고 평이한 대화로 시작. "
        f"인상에 강하게 남지 않는 케이스가 {facts['low_impact_pct']}로 다수입니다. "
        "데이터 자체가 그렇게 분포돼요.\n\n"
        f"결정적인 건 두 번째 접촉이에요. 호감 전환율이 첫 번째 대비 {facts['second_contact_multiplier']}로 급상승. "
        f"{facts['user_name']}님, 첫 만남에서 두 번째 약속을 자연스럽게 잡아두시는 게 효율적이에요."
    )


def test_meeting_validate() -> None:
    f = get_doyoon_p6_meeting_facts(
        user_name="홍길동", ilgan="임수", match_slot_id="f-water-yang"
    )
    ok, reason = validate_p6_meeting(_meeting_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_meeting_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP6MeetingUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수", match_slot_id="f-water-yang"
    )
    assert "2.3배" in out
    assert "2.4배" in out


# ── PATTERN ─────────────────────────────────────────────────────


def test_pattern_facts_imsu() -> None:
    f = get_doyoon_p6_pattern_facts(user_name="홍길동", ilgan="임수")
    assert f["hesitation_pct"] == "78%"
    assert f["cut_intent_pct"] == "12%"
    assert f["resolution_pct"] == "87%"
    assert f["initiative_multiplier"] == "1.4배"


def _pattern_valid(facts):
    return (
        "상대의 행동 데이터 분석부터 정리합니다.\n\n"
        f"연락 빈도 — 답장은 길게 받지만 먼저 연락은 적은 패턴. "
        f"관심 없는 케이스 평균 답장 길이는 {facts['answer_length_multiplier']} 짧아요. "
        "그러니 답장이 길다는 건 시간을 들이고 있다는 신호입니다.\n\n"
        f"심리 추정값 — 망설임 {facts['hesitation_pct']}, 단절 의지 {facts['cut_intent_pct']}. "
        "끊을 마음은 거의 없어요. 시작 결정도 안 내린 상태입니다.\n\n"
        f"교착 상태는 한 명이 작은 신호 보내면 {facts['resolution_pct']} 확률로 해소돼요. "
        f"통계적으로 {facts['user_name']}님 쪽 먼저 보낼 때 매칭 성공률이 {facts['initiative_multiplier']} 높게 측정됩니다."
    )


def test_pattern_validate() -> None:
    f = get_doyoon_p6_pattern_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p6_pattern(_pattern_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_pattern_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP6PatternUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert "78%" in out
    assert "1.4배" in out
