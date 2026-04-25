# CLAUDE.md

이 문서는 Claude Code가 HailMary-Backend 코드를 작성할 때 반드시 준수해야 하는 아키텍처 규칙을 정의한다.

## 프로젝트 개요

HailMary-Backend — 사주 기반 연애운 유료 리포트 서비스 백엔드

## 기술 스택

| 항목 | 선택 |
|------|------|
| 언어 | Python 3.12+ |
| 프레임워크 | FastAPI |
| DB | MySQL (Docker, EC2 동일 서버) |
| ORM | SQLAlchemy (async) |
| 검증 | Pydantic v2 |
| 사주 엔진 | FortuneTeller Lambda (TypeScript, 외부 서비스) |
| 결제 | PayApp |
| AI | Claude API (claude-sonnet-4-6) |
| 서버 | AWS EC2 |

## 커맨드

- **개발 서버 실행**: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- **직접 실행**: `python -m app.main`
- **DB 마이그레이션**: `alembic upgrade head`
- **린트**: `ruff check .`
- **타입 체크**: `mypy app/`
- **테스트**: `pytest`

## 로컬 개발 환경 포트

| 서비스 | 포트 | 비고 |
|--------|------|------|
| 프론트엔드 | 3000 | |
| FastAPI (백엔드) | 8000 | |
| FortuneTeller (로컬) | 4000 | 테스트 시 직접 실행 |
| MySQL (Docker) | 3306 | |

**FortuneTeller 로컬 실행 방법:**
FortuneTeller 레포에서 포트 4000으로 서버 실행 후, `.env.local` 의 URL을 아래와 같이 설정한다.

```
# .env.local
FORTUNETELLER_URL=http://localhost:4000

# .env.prod
FORTUNETELLER_URL=https://xxxxxx.lambda-url.ap-northeast-2.on.aws
```

환경변수 URL만 바꾸면 코드 변경 없이 로컬 ↔ 프로덕션 전환이 가능하다.

## 제품 플로

### 무료 플로

```
1. 사용자가 개인정보 + 설문(객관식/주관식) 입력
         ↓
2. DB 저장 (user 도메인)
         ↓
3. 사주 분석에 필요한 정보 추출 → FortuneTeller Lambda 호출 → 사주 분석 결과
         ↓
4. 사주 결과 DB 저장
         ↓
5. 무료 결과 API → 프론트엔드 출력
```

**FortuneTeller 호출은 이 시점 단 1회. 결과는 DB에 저장해 유료 플로에서 재사용한다.**
**Claude API 호출 없음.**

---

### 유료 플로

```
1. 고객이 "유료 결과 보기" 클릭
         ↓
2. 결제 (payment 도메인 — PayApp)
         ↓
3. 결제 완료 확인
         ↓
4. DB에서 조회:
     - 고객 설문 내용 (객관식 + 주관식)
     - FortuneTeller 사주 분석 결과 (무료 플로에서 저장된 것)
         ↓
5. AI 도메인: 사전 작성 프롬프트 + 고객 정보 결합 → Claude API 호출
         ↓
6. 유료 결과 DB 저장
         ↓
7. 유료 결과 API → 프론트엔드 출력
```

**결제 완료 전 Claude API 호출 절대 금지.**

---

# 프로젝트 구조

```
app/
 ├── domains/
 │   ├── user/                    사용자 정보 도메인
 │   │   ├── domain/
 │   │   │   ├── entity/
 │   │   │   ├── value_object/
 │   │   │   └── service/
 │   │   ├── application/
 │   │   │   ├── usecase/
 │   │   │   ├── request/
 │   │   │   └── response/
 │   │   ├── adapter/
 │   │   │   ├── inbound/api/
 │   │   │   └── outbound/persistence/
 │   │   └── infrastructure/
 │   │       ├── orm/
 │   │       └── mapper/
 │   │
 │   ├── payment/                 결제 도메인 (PayApp)
 │   │   ├── domain/
 │   │   │   ├── entity/
 │   │   │   ├── value_object/
 │   │   │   └── service/
 │   │   ├── application/
 │   │   │   ├── usecase/
 │   │   │   ├── request/
 │   │   │   └── response/
 │   │   ├── adapter/
 │   │   │   ├── inbound/api/
 │   │   │   └── outbound/external/   ← PayApp HTTP 클라이언트
 │   │   └── infrastructure/
 │   │       ├── orm/
 │   │       └── mapper/
 │   │
 │   └── ai/                      유료 리포트 AI 도메인
 │       ├── domain/
 │       │   ├── entity/
 │       │   ├── value_object/
 │       │   └── service/
 │       ├── application/
 │       │   ├── usecase/
 │       │   ├── request/
 │       │   └── response/
 │       ├── adapter/
 │       │   ├── inbound/api/
 │       │   └── outbound/external/   ← Claude API 클라이언트
 │       └── infrastructure/
 │           ├── orm/
 │           └── mapper/
 │
 ├── infrastructure/              전역 인프라
 │   ├── config/                  환경변수 (Pydantic BaseSettings)
 │   ├── database/                SQLAlchemy 세션
 │   ├── cache/                   Redis (추후 필요 시)
 │   └── external/
 │       └── fortuneteller/       FortuneTeller Lambda 클라이언트
 │
 └── main.py                      FastAPI 진입점, DI 와이어링
```

---

# 아키텍처 원칙

이 프로젝트는 **Hexagonal Architecture (Ports and Adapters) + Domain-Driven Design** 을 따른다.

레이어 의존성 방향:

```
Adapter → Application → Domain
Infrastructure → Adapter / Application
```

의존성은 항상 **안쪽(Domain) 방향으로만 흐른다.**

---

# Domain Layer 규칙

Domain은 비즈니스 로직의 핵심이다. 다음만 포함할 수 있다.

- Entity
- Value Object
- Domain Service
- Business Rule

## MUST 규칙

Domain 레이어는 다음을 **절대 import하면 안 된다.**

- FastAPI
- SQLAlchemy
- Redis
- Pydantic
- HTTP Client (httpx, requests)
- External API (Claude, PayApp, FortuneTeller)
- `process.env` / `os.environ` 직접 접근
- ORM Model

Domain 코드는 **순수 Python** 이어야 한다.

---

# Application Layer 규칙

Application 레이어는 UseCase를 정의한다.

역할:
- UseCase 실행
- Domain Entity 조합
- Port 인터페이스 호출
- Request / Response DTO 정의

## MUST 규칙

Application 레이어는 다음을 **직접 사용하면 안 된다.**

- FastAPI
- SQLAlchemy ORM 직접 호출
- `httpx.get(...)` 등 HTTP 클라이언트 직접 사용
- Claude API / PayApp / FortuneTeller 직접 호출

외부 시스템 접근은 **Port 인터페이스를 통해서만** 한다.

---

# Request / Response DTO 규칙

- DTO는 Application Layer에 위치한다 (`application/request/`, `application/response/`)
- Domain Entity를 API Response로 직접 반환하면 안 된다
- 항상 DTO를 통해 변환한다

---

# Adapter Layer 규칙

## Inbound Adapter (FastAPI Router)

위치: `adapter/inbound/api/`

역할: Request DTO 수신 → UseCase 호출 → Response DTO 반환

**Router에 비즈니스 로직을 작성하면 안 된다.** 2줄 초과 분기 로직은 UseCase로 추출한다.

## Outbound Adapter

위치: `adapter/outbound/`

역할: Repository 구현, 외부 API 클라이언트 구현

- `persistence/` — SQLAlchemy Repository 구현
- `external/` — PayApp, Claude API 클라이언트 구현

---

# FortuneTeller Lambda 연동 규칙

FortuneTeller는 TypeScript로 작성된 **외부 서비스**다. 수정하거나 내부 구조를 건드리면 안 된다.

클라이언트 위치: `app/infrastructure/external/fortuneteller/client.py`

```
Python FastAPI → HTTP → FortuneTeller Lambda (AWS, TS)
```

## MUST 규칙

- FortuneTeller 호출은 반드시 `infrastructure/external/fortuneteller/client.py` 에서만 한다
- Domain / Application / Router에서 FortuneTeller를 직접 호출하면 안 된다
- **무료 플로에서 Claude API 호출 금지** — FortuneTeller 결과만 반환한다
- FortuneTeller Lambda URL은 `infrastructure/config/settings.py` 환경변수로만 관리한다

---

# AI 도메인 규칙

AI 도메인은 결제 완료 후에만 진입한다.

흐름:

```
결제 검증 완료
     ↓
AI UseCase
  1. DB에서 사용자 정보 조회 (user 도메인 Repository Port)
  2. FortuneTeller Lambda 호출 (fortuneteller client)
  3. 프롬프트 조립
  4. Claude API 호출 (outbound/external/claude_client.py)
  5. 리포트 DB 저장
```

## MUST 규칙

- 결제 검증 전 Claude API 호출 절대 금지
- 프롬프트는 `ai/domain/service/` 에 위치한다 (비즈니스 로직)
- Claude API 키는 `infrastructure/config/settings.py` 에서만 읽는다
- 사용 모델: `claude-sonnet-4-6`

---

# Infrastructure Layer 규칙

포함되는 요소:
- Database Session (`infrastructure/database/`)
- ORM Model (`domains/<name>/infrastructure/orm/`)
- 환경변수 설정 (`infrastructure/config/settings.py`)
- FortuneTeller Lambda 클라이언트 (`infrastructure/external/fortuneteller/`)
- 공통 외부 클라이언트

## 환경변수 규칙

환경변수는 **Pydantic BaseSettings** 로만 관리한다.

위치: `infrastructure/config/settings.py`

Domain / Application 레이어에서 `os.environ` 직접 접근 금지.

## ORM / Mapper 규칙

- ORM Model은 Domain Entity와 분리한다
- ORM Model 위치: `domains/<name>/infrastructure/orm/`
- 변환은 반드시 Mapper를 통한다: `domains/<name>/infrastructure/mapper/`
- Domain Entity에서 SQLAlchemy Model import 금지

---

# Dependency Injection 규칙

의존성 흐름:

```
Router → UseCase → Repository Port → Infrastructure
```

의존성 연결은 **`main.py` 에서만** 수행한다.

---

# 금지 사항

다음 코드는 **절대 작성하면 안 된다.**

```python
# Domain에서 SQLAlchemy 사용
from sqlalchemy import Column

# Domain에서 FastAPI 사용
from fastapi import APIRouter

# Domain에서 외부 API 직접 호출
import httpx
httpx.get("https://...")

# UseCase에서 환경변수 직접 접근
import os
os.environ["CLAUDE_API_KEY"]

# Router에서 비즈니스 로직 작성 (2줄 초과)
@router.post("/report")
async def create_report(body: ReportRequest):
    user = db.query(User).filter(...).first()   # 금지
    saju = calculate_saju(user.birth_date)       # 금지
    ...

# 결제 검증 전 Claude API 호출
claude_client.generate(prompt)  # payment 검증 없이 호출 금지
```

---

# Core Rules (절대 불변)

1. **무료 플로에서 Claude API 호출 금지** — 결제 검증 이후에만 진입
2. **FortuneTeller 코드 수정 금지** — 외부 서비스로 취급, 클라이언트만 작성
3. **환경변수는 `infrastructure/config/settings.py` 에서만** — Domain/Application에서 직접 읽기 금지
4. **Domain은 순수 Python** — 외부 라이브러리 import 금지
5. **ORM Model ↔ Domain Entity 반드시 Mapper 경유**
6. **Router에 비즈니스 로직 금지** — UseCase로 추출
7. **코드 수정 후 반드시 `ruff check . && mypy app/` 실행, 에러 0건 확인**
8. **개인정보(생년월일·출생시각·성별) 로그 출력 금지** — 마스킹 처리
