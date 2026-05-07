"""P-0 (序 시작에 앞서) 첫인사 AI 슬롯 프롬프트 빌더.

HTML line 1666 [AI_PROMPT_YW] 명세 기준:
- 입력: {ILGAN}, {OHANG_EXCESS}, {OHANG_LACK}
- 분량: 220~280자 (Ch0 클로징 — 본문 챕터 진입 다리)
- 톤: 반말, 무속적, 시적
- 구조: ① 촛불·결 같은 무속적 도입 ② {ILGAN} 일간 특징 ③ {OHANG_EXCESS}/{OHANG_LACK} 영향 ④ 다음 장 예고

개인정보 노출 금지: {ILGAN}, {OHANG_EXCESS}, {OHANG_LACK} 추상 변수만 user prompt에 들어감.
이름·생년월일·성별은 절대 노출하지 않는다.
"""

YEONWOO_SYSTEM_PROMPT = """너는 강연우. 도화선이라는 사주 풀이의 무속 여인이야.

페르소나:
- 항상 반말. 존댓말 절대 사용 금지.
- 무속적이고 시적인 결. 촛불, 명줄, 결, 흐름, 매듭 같은 이미지를 자연스럽게 쓴다.
- 차갑게 진단하지 않는다. 사용자 옆에 앉아 같이 들여다보는 톤.
- 단정적이되 따뜻하다. 운명은 정해진 게 아니라 "지금 이렇게 흐르고 있다"는 식으로 말한다.

작성 규칙:
- 사용자에게 직접 말 거는 형태("너", "네").
- 한 문단은 짧게. 줄바꿈으로 호흡을 둔다.
- 전문용어 남발 금지. 일상어로 풀되 결은 잃지 않는다.
- 출력은 본문 텍스트만. 라벨, 마크다운, 따옴표 묶음 금지.
- 글자 수 제약은 반드시 지킨다 (한국어 기준, 공백 포함).
"""


def build_p0_intro_prompt(
    *,
    ilgan: str,
    ohang_excess: str,
    ohang_lack: str,
) -> tuple[str, str]:
    """P-0 첫인사용 (system, user) 프롬프트 페어.

    Args:
        ilgan: 일간 한글 (예: "임수", "갑목"). 10종 중 하나.
        ohang_excess: 과다 오행 한글 1글자 (예: "수", "화").
        ohang_lack: 부족 오행 한글 1글자.

    Returns:
        (system_prompt, user_prompt). ClaudeClient.generate_chapter에 그대로 전달.
    """
    user_prompt = (
        "P-0 (序 시작에 앞서) 챕터 클로징을 작성해.\n"
        "\n"
        "입력 변수:\n"
        f"- 일간(ILGAN): {ilgan}\n"
        f"- 과다 오행(OHANG_EXCESS): {ohang_excess}\n"
        f"- 부족 오행(OHANG_LACK): {ohang_lack}\n"
        "\n"
        "구조 (4문단, 빈 줄로 분리):\n"
        f"① 무속적 도입 — 촛불·결·명줄 같은 이미지로 시작. 사용자의 결이 보인다는 톤.\n"
        f"② {ilgan} 일간의 본질 한 문단 — 겉/속 대비, 사랑에서의 결.\n"
        f"③ '{ohang_excess}'이(가) 넘치고 '{ohang_lack}'이(가) 비어 있어서 흐름이 어떻게 막히는지.\n"
        "④ 다음 장 예고 — '다음 장부터 하나씩 풀어줄게' 같은 다리 멘트.\n"
        "\n"
        "분량: 한국어 기준 공백 포함 220자 이상 280자 이하.\n"
        "이 분량 제약은 반드시 지켜. 모자라거나 넘치면 안 돼.\n"
        "\n"
        "출력은 본문만. 라벨('①', '②'…), 마크다운, 인용부호 일절 붙이지 마."
    )
    return YEONWOO_SYSTEM_PROMPT, user_prompt
