---
description: HailMary 백엔드(Docker MySQL + uvicorn) 한 번에 기동
---

HailMary 백엔드를 처음부터 끝까지 띄운다. 과거에 겪은 누락 패키지/마이그레이션 문제가 재발하지 않도록 모든 단계를 idempotent 하게 수행한다.

다음 단계를 **순서대로** 수행한다. 각 단계가 끝나면 짧게 결과를 보고하고 다음으로 넘어간다.

## 1. Docker Desktop 기동

- `docker info` 로 daemon 살아있는지 확인.
- 죽어있으면 `open -a Docker` 로 띄우고, Monitor 도구로 `until docker info >/dev/null 2>&1; do sleep 2; done; echo ready` 를 timeout 120000ms 로 돌려 daemon 준비될 때까지 대기.

## 2. MySQL 컨테이너 기동

```bash
docker compose up -d
```

이미 떠있으면 그대로 둔다.

## 3. Python 의존성 설치 (누락 방지)

시스템 Python(`python3`) 기준으로 다음 패키지가 모두 import 가능한지 확인하고, 빠진 게 있으면 설치한다. 한 번에 묶어 실행:

```bash
python3 -m pip install --quiet \
  'fastapi[standard]' \
  'sqlalchemy[asyncio]' \
  asyncmy \
  greenlet \
  'pydantic[email]' \
  pydantic-settings \
  alembic \
  anthropic \
  httpx \
  aiohttp
```

> 과거 사고 이력: `email-validator`, `asyncmy`, `greenlet`, `alembic` 누락으로 `neutral` 오행 fallback 버그 + 마이그레이션 미적용이 발생했다. 위 명령은 그 재발을 방지한다.

## 4. DB 마이그레이션 적용

```bash
python3 -c "from alembic.config import CommandLine; CommandLine().main(['upgrade','head'])"
```

(작업 디렉토리는 프로젝트 루트 `/Users/benjaminsoohwan/Desktop/SVP/HailMary/HailMary-Backend` 여야 한다.)

## 5. FortuneTeller 로컬 서버 확인 (필수, 수정 금지)

`curl -s -o /dev/null -w "%{http_code}" http://localhost:4000 -m 3` 로 200 확인.
- 안 떠있으면 사용자에게 **별도 터미널에서 FortuneTeller 레포를 4000 포트로 직접 띄워달라고** 안내한다. 이 백엔드 레포에서 띄우는 게 아니다(CLAUDE.md 규칙 — 외부 서비스).
- 떠있으면 통과.

## 6. 포트 8000 정리 후 uvicorn 기동

```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null; true
```

이어서 background 로:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

(`run_in_background: true` 로 실행)

## 7. 헬스체크

3~5초 대기 후 background 로그 tail 해서 `Application startup complete` 확인. 그리고:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/docs -m 5
```

200 이면 성공 보고. 그 외면 로그 그대로 보여주고 원인 추적.

## 보고 형식

마지막에 한 블록으로 정리:
- Docker: ✅/❌
- MySQL 컨테이너: 컨테이너명 + 상태
- 의존성: 설치된 추가 패키지 (있으면)
- 마이그레이션: 현재 head revision
- FortuneTeller: ✅/❌
- uvicorn: background task ID + URL

## 금지

- `docker compose down` 같은 파괴적 명령 금지.
- FortuneTeller 레포/코드 수정 금지.
- `.env` 수정 금지(사용자가 직접 수정).
- 기존 alembic 리비전 파일 변경 금지.
