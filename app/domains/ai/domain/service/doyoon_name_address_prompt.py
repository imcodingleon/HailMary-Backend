"""도윤 호명용 이름 분류 — AI 1회 호출.

회원 정보 user.name (실명 또는 닉네임)을 받아 *AI 박스에서 호명할 이름* 결정.
- 한국 실명 (성+이름) → given name 추출 ("배성현" → "성현")
- 복성 (남궁/황보/제갈 등) → given name 추출 ("남궁성현" → "성현")
- 외래어/닉네임/모호 → 풀네임 그대로 ("곰돌이푸" → "곰돌이푸", "John" → "John")

이 결정값은 모든 도윤 AI 박스 prompt + 룰 fallback의 호명에 사용.
데이터 헤더 (InfoGrid 등 카드 라벨)는 별도 처리 (영향 없음).
"""

from __future__ import annotations

import json

_SYSTEM_PROMPT = """\
당신은 한국 이름 분류 분석가입니다.

입력된 이름이 한국 실명인지, 닉네임/외래어인지 판단하고
호명에 자연스러운 이름 형태를 결정합니다.

[분류 규칙]
1. 한국 실명 (성 1자 + 이름 1~2자, 예: "배성현", "민지")
   → given name만 추출 (예: "배성현" → "성현", "민지" → "민지")
   → 단, 외자 이름(2자 전체)이면 그대로 사용
2. 한국 복성 (남궁, 황보, 사공, 제갈, 서문, 선우, 독고, 동방,
              어금, 장곡, 강전, 묵태, 갈천, 망절, 단야 등)
   → 복성 2자 떼고 given name 추출 (예: "남궁성현" → "성현")
3. 닉네임/별명 ("곰돌이푸", "토끼", "치즈케이크" 등 일반명사 결합)
   → 풀네임 그대로 사용
4. 외래어/영문 이름 ("John", "Sarah", "이쁜이" 등)
   → 그대로 사용
5. 판단 모호 → 안전하게 풀네임 그대로 사용

[출력 형식 — 반드시 JSON]
{
  "name_for_address": "...",
  "is_korean_real_name": true/false,
  "reasoning": "분류 근거 한 줄"
}

[예시]
입력: "배성현"
출력: {"name_for_address": "성현", "is_korean_real_name": true, "reasoning": "한국 실명: 성(배) + 이름(성현)"}

입력: "남궁성현"
출력: {"name_for_address": "성현", "is_korean_real_name": true, "reasoning": "복성 남궁 + 이름(성현)"}

입력: "곰돌이푸"
출력: {"name_for_address": "곰돌이푸", "is_korean_real_name": false, "reasoning": "캐릭터/닉네임"}

입력: "John"
출력: {"name_for_address": "John", "is_korean_real_name": false, "reasoning": "영문 이름"}

입력: "민지"
출력: {"name_for_address": "민지", "is_korean_real_name": true, "reasoning": "외자 이름 — 분리 불가, 그대로"}

JSON 외 다른 텍스트 출력 금지.
"""


def build_name_address_prompt(full_name: str) -> tuple[str, str]:
    if not full_name:
        raise ValueError("full_name required")
    user = f'입력: "{full_name}"\n출력:'
    return _SYSTEM_PROMPT, user


def parse_name_address_response(response_text: str, full_name: str) -> str:
    """JSON 응답 파싱 + 안전 validate. 실패 시 풀네임 fallback.

    Returns:
        호명용 이름 (검증 통과 시 AI 결정값, 실패 시 풀네임).
    """
    try:
        # JSON 추출 — 응답에 다른 텍스트 섞여있을 수 있음
        start = response_text.find("{")
        end = response_text.rfind("}")
        if start == -1 or end == -1:
            return full_name
        data = json.loads(response_text[start : end + 1])
        candidate = data.get("name_for_address", "").strip()
        if not candidate:
            return full_name
        # 안전 validate: 출력이 입력의 부분 문자열인지 (변형/생성 차단)
        if candidate not in full_name:
            return full_name
        return candidate
    except (json.JSONDecodeError, ValueError, AttributeError):
        return full_name
