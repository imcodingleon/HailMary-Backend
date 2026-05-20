# HailMary-Backend — DA Amplitude 연동 작업 메모

작성일: 2026-05-19
대상 스펙: `HailMary/docs/DA-Amplitude/260519(화)/yeonwoo_eventlog.md`
프론트 측 메모: `HailMary-Frontend/docs/amplitude/작업계획.md`

---

## 목적

프론트가 Amplitude `identify()` 로 user property 를 set 할 수 있도록, 백엔드가 **PII 가공 완료된 사용자 속성**을 유료 결과 응답에 포함하여 내려준다.

원본 PII (이메일·이름·생년월일·태어난 시각) 는 절대 프론트로 흘려보내지 않는다 — 백엔드에서만 가공·소비된다.

---

## 변경 요약

### 1. 신규: PII 가공 도메인 서비스

`app/domains/user/domain/service/pii_redaction.py`

순수 함수 모음. CLAUDE.md "개인정보 로그 출력 금지 — 마스킹 처리" 원칙과 정합.

| 함수 | 입력 | 출력 |
|---|---|---|
| `email_hash(email)` | str | SHA-256 hex (64자) |
| `email_domain(email)` | str | `@` 뒷부분 |
| `name_initial(name)` | str | "강○○" 형태 |
| `birth_year(birth_date)` | date | int |
| `age_group(birth_date, reference=)` | date | "20s", "30s", "under_10", "90s_plus", "unknown" |
| `birth_branch(birth_time)` | time \| None | 12지 시진 ("자", "축", ...) \| None |
| `gender_code(Gender)` | enum | "M" \| "F" \| "other" |

12지 시진 매핑: 야자시 관행, 23:00 시작 = 자(子), 2시간 구간. 분석용 coarse-graining (실제 사주 계산은 FortuneTeller 가 별도 수행).

### 2. 응답 모델 확장

`app/domains/ai/application/response/paid_report_response.py`

- 신규: `PaidUserPropertiesResponse` — 가공 user property 전용 DTO
- 변경: `PaidReportResponse` 에 `user: PaidUserPropertiesResponse | None` 필드 추가

### 3. UseCase 시그니처 확장

`app/domains/ai/application/usecase/get_paid_report_usecase.py`

- 의존성 추가: `user_repo: UserRepositoryPort`
- 반환 타입 변경: `tuple[PaidReport, Payment]` → `tuple[PaidReport, Payment, User | None]`
- User 조회 실패는 결과지 응답을 막지 않음 (분석 메타에 그치므로 None 허용).

### 4. 라우터 응답 조립

`app/domains/ai/adapter/inbound/api/paid_report_router.py`

- `_build_user_properties(user, customer_email)` 헬퍼 — usecase 결과를 pii_redaction 서비스로 변환.
- `GET /api/saju/paid/{order_id}` 응답 본문에 `user` 필드 포함.
- `/status` 엔드포인트는 `_user` 무시 (status 만 필요).

라우터에 비즈니스 로직 X. 헬퍼는 순수 DTO 매핑 (2~3줄 분기 미만).

### 5. DI 와이어링

`app/main.py`

- `_make_get_paid_report_usecase` 에 `user_repo=UserRepository(session)` 추가.

---

## CLAUDE.md 원칙 준수 체크

- ✅ Domain (pii_redaction) — 순수 Python, 외부 라이브러리 import 없음 (hashlib 는 표준 라이브러리)
- ✅ Application UseCase — Port 인터페이스만 의존, ORM 직접 호출 X
- ✅ Router — 비즈니스 로직 X, UseCase + DTO 매핑만
- ✅ 환경변수 직접 접근 없음
- ✅ 결제 검증 후에만 user property 산출 (Payment 만료 체크 통과 후 진입)

---

## 응답 예시 (200 OK)

```json
{
  "order_id": "ord_abc123",
  "status": "ready",
  "chapters": { "p0": { ... }, "p1": { ... }, ... },
  "expires_at": "2026-06-18T05:23:00Z",
  "user": {
    "user_id": "42",
    "user_nickname": null,
    "user_name_initial": "강○○",
    "user_email_domain": "gmail.com",
    "user_email_hash": "3f2b9a...64자",
    "birth_year": 1995,
    "age_group": "30s",
    "birth_branch": "인",
    "gender": "F"
  }
}
```

---

## 후속 작업

- `User` 엔티티에 `nickname` 필드 도입 시 `_build_user_properties` 에서 `user_nickname` 채움 (현재 항상 null).
- doyoon 유료 흐름 도입 시 응답 모델/라우터는 동일, `character` 필드만 다름.

---

## 검증

- `ruff check`: 우리 변경분 0 errors (`All checks passed!`)
- `mypy`: 4 source files clean (pre-existing `# type: ignore[arg-type]` 2개만 unused 경고 — 본 작업과 무관, 별도 정리 대상)
- `python -c "from app.main import app"` OK, `uvicorn app.main:app --reload` 부팅 정상 (`Application startup complete.`)
- 응답 본문에 `user` 필드 포함 확인 (`PaidReportResponse.user: PaidUserPropertiesResponse | None`)

---

## 2026-05-20 복구 작업 메모

GitHub re-clone 시 5/19 코드 변경분이 누락되어 위 §변경 요약 전 구간을 재구현. 스펙은 그대로 유지.

| 항목 | 상태 |
|---|---|
| `app/domains/user/domain/service/pii_redaction.py` | ✅ 재생성 (순수 함수 7종, hashlib 만 import) |
| `PaidUserPropertiesResponse` DTO + `PaidReportResponse.user` | ✅ 재추가 |
| `GetPaidReportUseCase` `user_repo` 의존 + `(report, payment, user)` 반환 | ✅ 재적용 (`execute`, `execute_by_share_code` 양쪽) |
| `paid_report_router._build_user_properties` 헬퍼 | ✅ 재추가, `/{order_id}`, `/{share_code}` 양쪽 응답 본문에 user 동봉 |
| `main.py` DI 와이어링 (`user_repo=UserRepository(session)`) | ✅ |
| `expires_at` timezone 비교 | **이미 수정되어 있음** (`expires_at.replace(tzinfo=UTC)`) → 후속 작업 항목에서 제거 |
| `Payment.customer_email`, `Payment.user_id` 활용 | 변동 없음 (User 엔티티에 email 없음 → email 출처는 Payment) |
| `Gender` enum 값 = `male/female` (other 없음) | `pii_redaction.gender_code` 에서 default `"other"` 처리 |

---

## 2026-05-20 오후 후속 — user_id prefix 적용

검증 e2e 단계에서 Amplitude Logger 가 `Invalid id length for user_id or device_id` 노출. Amplitude 는 `user_id` 최소 5자를 요구하는데, `User.id` 가 작은 정수면 `str(user.id)` 가 1~2자라 identify 자체가 서버에서 거부됨.

### 변경

`paid_report_router._build_user_properties`:

```diff
-    return PaidUserPropertiesResponse(
-        user_id=str(user.id),
+    # Amplitude 는 user_id 최소 5자 요구 → "usr_" prefix 로 패딩.
+    return PaidUserPropertiesResponse(
+        user_id=f"usr_{user.id}",
```

스펙(`yeonwoo_eventlog.md` §5-1) 예시 `"usr_8c2f..."` 와도 형식 일치. doyoon 도입 시에도 동일 prefix 적용.

### 영향 범위

- 응답 본문 `user.user_id` 형식만 변경. 다른 필드/엔드포인트 무영향.
- 프론트는 받은 값 그대로 `setUserId()` 에 전달 → 프론트 변경 없음.
- DB `User.id` 자체는 그대로(정수). 가공은 라우터에서만.

### 별도 인프라 발견 (본 문서 범위 외 — 정사 문서 참조)

| 항목 | 처리 |
|---|---|
| `paid_reports.share_code` 컬럼 미존재 (1054 OperationalError) | `alembic upgrade head` 적용 (`4dda5005e680` → `f3b6ba2f1b8e`) |
| Backend `.env.local` `TOSS_SECRET_KEY` placeholder | 토스 문서용 테스트 시크릿 `test_gsk_docs_...` 로 교체 |

> 시간순 흐름·결정 사유 전체: `Hailmary-docs/DA-Amplitude/260520(수)/recovery-and-refactor.md`
