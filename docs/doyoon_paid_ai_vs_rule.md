# 도윤 유료 결과지 — AI vs 룰 분별표

작성일: 2026-05-22
대상: 한도윤 캐릭터 paid report 12페이지 (P-0 ~ P-11)

도윤 결제 1건당 AI 호출 슬롯 총 **22개**, 룰 합성 영역 별도. AI 실패 시 모든 슬롯은 **룰 fallback** 자동 적용.
사용 모델: `claude-sonnet-4-6` (전 슬롯).

---

## 한 눈에 보기

| 페이지 | 챕터 | AI 슬롯 수 | 룰 영역 | 합산 |
|---|---|---|---|---|
| P-0 (프롤로그) | 사주 진단 + 일간 + 챕터 인트로 | **1** | 사주 카드, 일간 카드, 오행 차트, 챕터 가이드 | 1 AI + 多 룰 |
| P-1 (一 1/2) | 너라는 사람 | **3** | 챕터 헤더, 일주 카드 | 3 AI |
| P-2 (一 2/2) | 상처와 회복 | **2** | 상처 카드 4종, 회복 메트릭 4종 | 2 AI |
| P-3 (二 1/2) | 연애 막는 것 (구조/패턴) | **2** | BlockadeBigCard, PatternCard×3, ControlStrategy×2, SD spotlight | 2 AI |
| P-4 (二 2/2) | 비호환·착각 인연 | **2** | KeywordTags×5, InfoGrid×10, LineChart SVG, IllusionSign×3, GoodCard | 2 AI |
| P-5 (三) | 매력 분석 | **3** | RadarChart SVG (6축), FlowSteps (4단계), MeterBar×4 | 3 AI |
| P-6 (四 1/2) | 운명의 짝 — 인연 | **3** | PersonFrame, KeywordTags×5, InfoGrid×9, MeterBar(궁합), MeterBar×3(심리), CardDy×2 | 3 AI |
| P-7 (四 2/2) | 결말 시나리오 | **1** | ScenarioCard×3 (자산 frame) | 1 AI |
| P-8 (五) | 인연이 오는 시간 | **1** | 12개월 Timeline (룰 합성, hearts/state/desc), 두루마리 자산 | 1 AI |
| P-9 (六) | 변수 최적화 가이드 | **3** | CardGood×3, CardWarn/Amber×3, MeterBar×2 | 3 AI |
| P-10 (七) | 도윤의 편지 | **3** | 헤더, 사용자 선택 칩, 인용, 강조구, 꼬리 | 3 AI |
| P-11 (終) | 에필로그 | **0** | SD + bubble + 인장 (전부 고정) | 0 AI |
| **합계** | — | **22** | — | 22 AI |

---

## P-0 (프롤로그) · 大門前 — 사주 진단

### AI 박스 1개

| 슬롯 | 내용 | 입력 변수 | 출력 분량 |
|---|---|---|---|
| `ai_intro` | 사주 분석 도입 멘트 (도윤 톤) | `user_name`, `ilgan_full`, `ohang_excess`, `ohang_lack`, `birth_summary` | ~150~250자, 3단락 |

### 룰 영역

- 사주 8자 카드 (year/month/day/hour pillar)
- 일간 카드 (한자 + 십신 + 오행)
- 오행 5축 도넛 차트
- 챕터 가이드 6 (one/two/three/.../seven 한자 + 부제)

---

## P-1 (一 1/2) — 너라는 사람

### AI 박스 3개

| 슬롯 | 내용 | 입력 변수 |
|---|---|---|
| `ai_opening` | 1-1 챕터 오프닝 (감정 도입) | user_name, ilgan, ilju |
| `ai_trigger` | 1-2 트리거 분석 (사주 변수 → 감정 활성도) | user_name, ilgan, ohang_excess, ohang_lack |
| `ai_emotion` | 1-3 감정 폭발 패턴 | user_name, ilgan, charm_score |

### 룰 영역

- 챕터 헤더 (一 / CH-1 / "너라는 사람")
- 일주 카드 (한자 + 십신 5종)

---

## P-2 (一 2/2) — 상처와 회복

### AI 박스 2개

| 슬롯 | 내용 |
|---|---|
| `ai_hurt` | 2-1 상처 진단 (4 키워드 + 위험률 % 기반 종합) |
| `ai_recovery` | 2-2 회복 전략 (4 회복 메트릭 진단) |

### 룰 영역

- HurtType × 4 (키워드 + risk_pct + desc) — 일간 매트릭스
- RecoveryMeter × 4 (4단계 회복) — 일간 매트릭스
- SD avatar dy_03 + 한도윤 bubble

---

## P-3 (二 1/2) — 연애 막는 것 (구조/패턴)

### AI 박스 2개

| 슬롯 | 내용 |
|---|---|
| `ai_blockade` | 2-1 구조적 원인 (오행 매트릭스 5종 × 일간 10) |
| `ai_pattern` | 2-2 반복 패턴 (PatternEntry × 3) |

### 룰 영역

- BlockadeBigCard (위험률 % + 구조 정리)
- PatternCard × 3 (시점 / 발생률 / 한 줄)
- ControlStrategyCard × 2 (전략 키워드 + 효과 %)
- SD spotlight dy_10

---

## P-4 (二 2/2) — 비호환·착각 인연

### AI 박스 2개

| 슬롯 | 내용 |
|---|---|
| `ai_akyon` | 2-3 통계적 비호환 유형 (akyon_slot_id 20 매트릭스) |
| `ai_illusion` | 2-4 착각 인연 (3 오인 신호 + 결정 분기점) |

### 룰 영역

- KeywordTags × 5 (비호환 인상 태그)
- InfoGrid × 10 row (키 분포 / 체형 / 얼굴상 등)
- **LineChart SVG** (4시점 진짜/착각 곡선 — 인라인 SVG 그대로)
- IllusionSign × 3 (오인 신호 + 발생률)
- GoodDecisionCard (결정 분기점, 녹색)
- SpouseImage (character=doyoon, type=avoid)

---

## P-5 (三) — 매력 분석

### AI 박스 3개

| 슬롯 | 내용 |
|---|---|
| `ai_charm_index` | 3-1 매력 지수 (Radar 6축 + 강점 2축) |
| `ai_conversion` | 3-2 끌림 메커니즘 (4단계 전환율) |
| `ai_appeal` | 3-3 호감 유발 (4 변수 점수) |

### 룰 영역

- **RadarChart SVG** (200×200, 6축: 존재감/매력살/목소리/깊이감/분위기/눈빛)
- 6각형 grid 3겹 + 데이터 폴리곤
- 핑크 알약 뱃지 ("궁합/매력 지수 상위 N%")
- FlowSteps 4단계 (첫인상 → 끌림, 마지막 핑크 강조)
- MeterBar × 4 (호감 유발 변수)

---

## P-6 (四 1/2) — 운명의 짝 (인연 프로파일 + 행동 패턴)

### AI 박스 3개

| 슬롯 | 내용 |
|---|---|
| `ai_profile` | 4-1 인연 프로파일 (match_slot_id 20 매트릭스 + 오행 보완) |
| `ai_meeting` | 4-1 만남 시나리오 (기존 동선 + 두 번째 접촉) |
| `ai_pattern` | 4-2 행동 패턴 분석 (심리 추정값) |

### 룰 영역

- PersonFrame (인연 사진 — SpouseImage match)
- KeywordTags × 5 (인연 인상 태그)
- InfoGrid × 9 row (키 / 체형 / 직업군 / 궁합 핑크)
- 궁합 MeterBar (핑크)
- NoticeBox 📊 (행동 패턴 안내)
- SD spotlight dy_07 (200×264 sz-xxl)
- MeterBar × 3 (관심도 / 표현 의지 / 지속 가능성)
- CardDy × 2 (행동 → 심리)

---

## P-7 (四 2/2) — 결말 시나리오

### AI 박스 1개

| 슬롯 | 내용 |
|---|---|
| `ai_ending` | 4-3 결말 시나리오 (3 분기 + 기대값 비교) |

### 룰 영역

- NoticeBox 📊 (3가지 결말 안내)
- **ScenarioCard × 3** (자산 frame: `scenario_card_frame.png` / `scenario_card_frame_recommend_dy.png`)
- prob 뱃지 색 토큰 (sc-low 빨강 / sc-high 골드 / sc-best 녹색)
- SD + bubble (dy_05, right flow)

---

## P-8 (五) — 인연이 오는 시간

### AI 박스 1개

| 슬롯 | 내용 |
|---|---|
| `ai_intro` | 5-1 12개월 접촉 확률 도입 (피크 2개 + 일간 흐름) |

### 룰 영역 (큰 비중)

**연우 P-8 인프라 100% 재사용** — `MonthlyRomanceFlowService.compute_full_months` + 헬퍼:
- `_pct_to_hearts_p8` (점수 → ♥/♡ 1~5)
- `_pick_top_two_peaks` (12개월 score 상위 2 → 피크)
- `_classify_state` (상태 10종 분류)
- `_format_month_label` (롤링 라벨: "5월 (이번달)" / "'27. 1월")
- `_peak_label_for_ai`

- **두루마리 자산** (`scroll_full_dy.png`, aspect 724/2536, padding 53% 19%)
- TimelineRow × 12 (라벨 + ♥/♡ 5 + % + state별 코멘트)
- 피크 2개 핑크 강조
- 도윤 톤 STATE_DESC × 10 (시작/상승/진입/피크/심화/안정/정체/충전/2차 피크/마무리)
- SD spotlight dy_04 (260×260)

---

## P-9 (六) — 변수 최적화 가이드

### AI 박스 3개

| 슬롯 | 내용 |
|---|---|
| `ai_ohang` | 6-1 오행 보완 (반응성 분석) |
| `ai_risk` | 6-2 리스크 제거 (우선순위 임팩트) |
| `ai_optimize` | 6-3 매력 최적화 (현재 → 목표 격차) |

### 룰 영역

- **CardGood × 3** (오행 보완 방법 — 5 오행 매트릭스, 색채/공간/행동)
- **CardWarn × 2 + CardAmber × 1** (즉시/단기/중기 리스크 — 공통)
- MeterBar × 2 (현재 활성화 / 목표)
- SD + bubble (dy_06)

---

## P-10 (七) — 도윤의 편지

### AI 박스 3개

| 슬롯 | 내용 | 입력 변수 |
|---|---|---|
| `ai_box1` | 박스 1 — 지금 입력하신 상황 (step1 답변) | step1 슬러그 (1~4: crushing/in_relationship/missing_ex/waiting_new), 일간 |
| `ai_box2` | 박스 2 — 알고 싶다 하신 영역 (step2 답변) | step2 슬러그 (1~4: soulmate/timing/compatibility/patterns), 일간, 오행 보완 |
| `ai_box3` (`ai_letter`) | 박스 3 — 당신의 한 줄에 답합니다 (step3 자유서술) | step3 자유서술, 모든 사주 변수 + persona (DOYOON_PERSONA) |

### 룰 영역

- 편지 헤더 ("한 도 윤 의 편 지" + 일주)
- 사용자 선택 칩 (step1/step2 라벨)
- step3 quote (사용자가 적은 고민 그대로 인용)
- emphasis 강조구 (일간 10셀 매트릭스)
- tail 꼬리 (고정)
- 시그니처 "— 도윤 드림"
- SD dy_03 sz-xxxl + thread_corner × 2

---

## P-11 (終) — 에필로그

### AI 박스 0개

### 룰 영역 (전체 고정)

- SD spotlight dy_09 (창가 노을, 260×260)
- thread_corner × 2 (tl/br)
- 한도윤 클로징 bubble 4줄 (사용자명 치환만)
- 緣 인장 (motif_seal_yeon) + "당신의 인연은 여기에"

---

## 비용 정리

| 슬롯 | 분량 | 토큰당 비용 |
|---|---|---|
| P-0 ai_intro | ~250자 | ~7원 |
| P-1 × 3 | 250~350자 | ~24원 |
| P-2 × 2 | 200~350자 | ~16원 |
| P-3 × 2 | 280~400자 | ~16원 |
| P-4 × 2 | 350~450자 | ~20원 |
| P-5 × 3 | 200~400자 | ~24원 |
| P-6 × 3 | 300~500자 | ~30원 |
| P-7 × 1 | 400~450자 | ~10원 |
| P-8 × 1 | 200~300자 | ~7원 |
| P-9 × 3 | 220~340자 | ~24원 |
| P-10 × 3 | 250~720자 (편지 길음) | ~43원 |
| **합계** | — | **~221원/결제** |

**fallback**: AI 실패 시 룰 합성 자동 적용 — 비용 0원이지만 톤 다양성 ↓.

---

## 룰 vs AI 선택 기준

### AI 적용 영역 (총 22 슬롯)
- 사용자 호명이 필요한 본문
- 사주 데이터 + 사용자 입력 결합 분석
- 톤 다양성·자연스러움 중요한 정서 텍스트
- 사용자 자유서술(step3) 응답

### 룰 적용 영역
- 수치 데이터 (점수 / %)
- 그래프 자산 (Radar / LineChart / Meter / Timeline)
- 고정 카드 (한자 / 일주 / 챕터 가이드)
- SD avatar / bubble (캐릭터 시그니처)
- 사용자 선택 칩 (step1/step2 라벨 표시)
- 결말 시나리오 카드 prob 라벨 (78%, 91% 고정)
- 인장·footer

### Hybrid
- P-8 Timeline — 룰로 12개월 데이터 합성 + AI 1박스로 도입 멘트만
- P-10 편지 — box1/box2/box3 모두 AI, 인용·강조구는 룰
