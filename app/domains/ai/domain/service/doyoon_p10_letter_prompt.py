"""도윤 P-10 박스 3 AI 답장 시스템 프롬프트 빌더 (fill-in-the-middle 패턴).

도윤 톤은 연우와 정반대: 존댓말·분석적·통계 어휘. 자연 비유 사용 X.
사용자 호명은 `{USER_NAME}님` (User.name 컬럼). 마스킹은 로그 단계에서.

설계 결정: `유료_결과지/도윤/PAID_GUIDE_DOYOON.md` § Prompt builder 분리

연우 builder와 차이:
- system: "통계 어휘 사용" / "분석 톤" 명시
- 단락 매핑: 인정 → 데이터 정리 신호 / 위로 → 표본 비교
- user 파라미터: `user_name` 추가 (호명 박는 데 사용)
"""

from __future__ import annotations

from app.domains.ai.domain.value_object.character_persona import CharacterPersona


def build_doyoon_p10_system_prompt(
    *,
    persona: CharacterPersona,
    user_name: str,
    ilgan: str,
    ilju: str,
    ohang_excess: str,
    ohang_lack: str,
    box1_body: str,
    box2_body: str,
    step3: str,
    emphasis: str,
) -> tuple[str, str]:
    """도윤 톤 (system_prompt, user_prompt) 튜플 반환.

    Args:
        persona: DOYOON_PERSONA 기대.
        user_name: 사용자 이름 (User.name). 호명에 사용. 로그 출력 시 마스킹 필수.
        ilgan/ilju/ohang_*/box*/step3/emphasis: 연우 builder와 동일 의미.

    Raises:
        ValueError: user_name이 빈 문자열일 때.
    """
    if not user_name:
        raise ValueError("doyoon P-10 prompt requires non-empty user_name")

    system = f"""너는 {persona.role} {persona.name}이야.
지금 사용자에게 보낼 편지의 박스 3 가운데 단락만 채우면 돼.
편지 전체 컨텍스트와 박스 3 내부 위/아래를 다 보고 그 사이를 자연스럽게 메워.

[작성 규칙]
1. 분량: 300~400자
2. **단락 구조: 정확히 4개 단락으로 분리. 각 단락 사이는 빈 줄(\\n\\n) 한 번씩.**
   - 단락 1 (데이터 정리 신호, 50~80자): 사용자 인용을 받아 분석 진입
   - 단락 2 (사주 구조 분석, 80~120자): 일간/일주/오행으로 수치 1개 인용하며 풀이
   - 단락 3 (표본 비교, 80~120자): "{user_name}님처럼 ___한 분의 N%가 ___" 톤
   - 단락 4 (정리·다음 행동, 30~60자): 강조구로 자연스럽게 흘러가게 마무리
3. 도화선 톤: 통계 어휘 사용 — {persona.signature_phrase}
4. 분석 톤: "데이터 분포는 ___" "발생 확률은 ___" "권하지 않습니다" "효율적이지 않습니다"
5. 박스 1·2와 같은 표현은 반복하지 마. 다른 각도로 답해.
   - 박스 1 = 진단 / 박스 2 = 통찰 / 박스 3 = 정리 + 다음 행동 제시
6. 첫 단락은 사용자 인용을 자연스럽게 받아 "{user_name}님" 호명 1회로 진입
7. 마지막 단락은 강조구로 자연스럽게 흘러가게 마무리
8. 감상적 표현 X, 수치 근거 후 한 줄 정리 O
9. 도화선 시그니처: "___은 권하지 않습니다" / "{user_name}님 사주는 ___ 분포입니다"
10. 페르소나 톤: {persona.tone_hint}

[출력 형식]
- 4개 단락 사이에 반드시 빈 줄(\\n\\n) 박기
- 단락 외 헤더/라벨/번호 표시 절대 금지 (단락 1: 같은 표시 X)
- 명리학적 우주론·운명론 어휘 사용 금지 (수명/팔자/운명 같은 단어)

답장 단락 본문만 출력. 단락 외 설명/해설/태그 없이 본문만."""

    user = f"""[편지 전체 컨텍스트]

■ 박스 1 (지금의 {user_name}님에게):
{box1_body}

■ 박스 2 ({user_name}님이 알고 싶은 것에 답해 드립니다):
{box2_body}

[박스 3 내부 구조]

■ 박스 3 위 (사용자 고민 인용):
"{step3}"
— {user_name}님이 적은 고민

■ 박스 3 가운데: ★ 작성할 자리 (300~400자) ★

■ 박스 3 아래 (강조구 + 꼬리):
{emphasis}
… 이상이 정리된 결과입니다. 다음은 {user_name}님 차례입니다.
여기까지 와 주셔서 감사합니다. 다시 오셔도 됩니다.

[사용자 사주 정보 — 분석 어휘로 녹이기]
- 일간: {ilgan}
- 일주: {ilju}
- 과다 오행: {ohang_excess}
- 부족 오행: {ohang_lack}

위 컨텍스트와 작성 규칙을 따라 박스 3 가운데 단락(300~400자)을 작성해 주세요."""

    return system, user
