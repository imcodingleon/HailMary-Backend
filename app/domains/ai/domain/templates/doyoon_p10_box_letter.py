"""도윤 P-10 box1/box2 — facts 빌더 + 룰 fallback.

원본 도윤_final.html data-page-idx=10 편지 박스.
연우는 BOX1/BOX2 매트릭스 룰 합성 — 도윤은 AI 호출 (도윤 톤).
AI 실패 시 룰 fallback (이 모듈의 compose_* 함수).
"""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import (
    ILGAN_HANJA,
    OHANG_HANJA,
)


STEP1_LABEL: dict[str, str] = {
    "waiting_new": "새로운 인연을 기다리는 상태",
    "crushing": "썸 진행 중",
    "in_relationship": "연애 중",
    "missing_ex": "헤어진 연인을 그리워하는 상태",
}

STEP2_LABEL: dict[str, str] = {
    "soulmate": "운명의 상대",
    "timing": "다음 인연의 시기",
    "compatibility": "현재 인연과의 궁합",
    "patterns": "연애 패턴의 본질",
}


# ── 룰 fallback (AI 실패 시) ──────────────────────────────────────


def compose_doyoon_box1_body(*, user_name: str, ilgan: str, step1: tuple[str, ...]) -> str:
    """도윤 box1 룰 합성 — 입력 상황 + 일간 분석."""
    if not step1:
        raise ValueError("step1 required")
    labels = [STEP1_LABEL.get(s, s) for s in step1]
    labels_text = " · ".join(labels)
    ilgan_hanja = ILGAN_HANJA[ilgan]
    return (
        f"{user_name}님이 선택해주신 상황 변수, 정리해드릴게요.\n\n"
        f"입력값: {labels_text}. {ilgan}({ilgan_hanja}) 일간 표본에서 이 조합은 "
        "일관된 패턴으로 분류돼요. 변수가 한 곳으로 쏠려 있어서 감정 활성도가 평균보다 1.4배 높은 상태예요.\n\n"
        "당장 결정 내리지 않으셔도 돼요. 데이터부터 보고 그다음에 움직이시면 됩니다."
    )


def compose_doyoon_box2_body(*, user_name: str, ilgan: str, step2: tuple[str, ...]) -> str:
    """도윤 box2 룰 합성 — 알고싶은 영역 분석."""
    if not step2:
        raise ValueError("step2 required")
    labels = [STEP2_LABEL.get(s, s) for s in step2]
    labels_text = " · ".join(labels)
    ilgan_hanja = ILGAN_HANJA[ilgan]
    return (
        f"{user_name}님이 알고 싶다고 표시하신 영역, 데이터로 정리해드릴게요.\n\n"
        f"질문 영역: {labels_text}. {ilgan}({ilgan_hanja}) 일간 표본에서 가장 자주 "
        "잡히는 질문 셋이에요. 답변 가능한 변수는 이미 측정돼 있고, 다음 장에서 풀어드려요.\n\n"
        "데이터가 답할 수 있는 영역과 그렇지 않은 영역이 명확하게 나뉘어요. 측정값이 닿는 곳까지는 정확하게 보여드릴게요."
    )


# ── facts ─────────────────────────────────────────────────────────


def get_doyoon_box1_facts(
    *,
    user_name: str,
    ilgan: str,
    step1: tuple[str, ...],
) -> dict[str, str]:
    if not user_name:
        raise ValueError("user_name required")
    if not step1:
        raise ValueError("step1 required")
    rule_text = compose_doyoon_box1_body(user_name=user_name, ilgan=ilgan, step1=step1)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "step1_labels": " · ".join(STEP1_LABEL.get(s, s) for s in step1),
        "rule_text": rule_text,
    }


def get_doyoon_box2_facts(
    *,
    user_name: str,
    ilgan: str,
    step2: tuple[str, ...],
    ohang_lack: str,
) -> dict[str, str]:
    if not user_name:
        raise ValueError("user_name required")
    if not step2:
        raise ValueError("step2 required")
    rule_text = compose_doyoon_box2_body(user_name=user_name, ilgan=ilgan, step2=step2)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "step2_labels": " · ".join(STEP2_LABEL.get(s, s) for s in step2),
        "ohang_lack": ohang_lack,
        "ohang_lack_hanja": OHANG_HANJA.get(ohang_lack, ohang_lack),
        "rule_text": rule_text,
    }
