"""PII 가공 도메인 서비스 (순수 함수).

원본 PII는 절대 프론트로 흘려보내지 않는다. 이 모듈은 Amplitude user property로
내보낼 가공값만을 산출한다. 외부 라이브러리 import 금지 — hashlib는 표준 라이브러리.

12지 시진 매핑: 야자시 관행, 23:00 시작 = 자(子), 2시간 구간. 분석용 coarse-graining.
"""

from __future__ import annotations

import hashlib
from datetime import date, time

from app.domains.user.domain.value_object.gender import Gender


def email_hash(email: str) -> str:
    """원본 이메일 SHA-256 hex (64자)."""
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()


def email_domain(email: str) -> str:
    """이메일에서 `@` 뒷부분만."""
    _, _, domain = email.strip().partition("@")
    return domain.lower()


def name_initial(name: str) -> str:
    """이름 첫 글자 + `○○`. 빈 문자열이면 빈 문자열."""
    if not name:
        return ""
    return f"{name[0]}○○"


def birth_year(birth_date: date) -> int:
    return birth_date.year


def age_group(birth_date: date, reference: date | None = None) -> str:
    """10년 단위 연령대. under_10 / 10s / 20s / ... / 90s_plus / unknown."""
    ref = reference or date.today()
    age = ref.year - birth_date.year - ((ref.month, ref.day) < (birth_date.month, birth_date.day))
    if age < 0:
        return "unknown"
    if age < 10:
        return "under_10"
    if age >= 90:
        return "90s_plus"
    return f"{(age // 10) * 10}s"


# 12지 시진: (시작시, 종료시-exclusive, 지지). 자시 = 23:00~01:00 (야자시).
_BRANCH_RANGES: list[tuple[int, int, str]] = [
    (23, 1, "자"),
    (1, 3, "축"),
    (3, 5, "인"),
    (5, 7, "묘"),
    (7, 9, "진"),
    (9, 11, "사"),
    (11, 13, "오"),
    (13, 15, "미"),
    (15, 17, "신"),
    (17, 19, "유"),
    (19, 21, "술"),
    (21, 23, "해"),
]


def birth_branch(birth_time: time | None) -> str | None:
    """태어난 시각 → 12지 시진. None이면 None."""
    if birth_time is None:
        return None
    h = birth_time.hour
    for start, end, branch in _BRANCH_RANGES:
        if start < end:
            if start <= h < end:
                return branch
        else:  # 자시 (23~01)
            if h >= start or h < end:
                return branch
    return None


def gender_code(gender: Gender | None) -> str:
    """Gender enum → 'M' | 'F' | 'other'."""
    if gender is None:
        return "other"
    if gender == Gender.MALE:
        return "M"
    if gender == Gender.FEMALE:
        return "F"
    return "other"
