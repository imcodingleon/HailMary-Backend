/**
 * 신살 + v2 매력 신호 단위 테스트.
 *
 * 검증 포인트:
 * - 홍염살 / 자좌홍염 / 금여록 신규 판정
 * - computeCharmFlags (도화일주, 자좌홍염, 시너지, 목욕 위치)
 * - computeDohwaInteractions (도화 합/충/형)
 * - 회귀 가드: 기존 7개 신살 판정 비파괴
 */

import {
  findSinSals,
  computeCharmFlags,
  computeDohwaInteractions,
} from '../src/lib/sin_sal.js';
import type {
  SajuData,
  HeavenlyStem,
  EarthlyBranch,
  WuXing,
  CalendarType,
  Gender,
  TenGod,
} from '../src/types/index.js';

// ── fixture builder ────────────────────────────────────────────────────────

function makePillar(stem: HeavenlyStem, branch: EarthlyBranch) {
  // Pillar 필수 필드를 최소만 채움 (테스트 대상 함수는 stem/branch 만 사용)
  return {
    stem,
    branch,
    stemElement: '목' as WuXing,
    branchElement: '목' as WuXing,
    yinYang: '양' as const,
  };
}

function makeSaju(
  year: [HeavenlyStem, EarthlyBranch],
  month: [HeavenlyStem, EarthlyBranch],
  day: [HeavenlyStem, EarthlyBranch],
  hour: [HeavenlyStem, EarthlyBranch],
  overrides: Partial<SajuData> = {},
): SajuData {
  return {
    birthDate: '1992-11-14',
    birthTime: '12:00',
    birthCity: '서울특별시',
    calendar: 'solar' as CalendarType,
    isLeapMonth: false,
    gender: 'male' as Gender,
    year: makePillar(...year),
    month: makePillar(...month),
    day: makePillar(...day),
    hour: makePillar(...hour),
    wuxingCount: { 목: 0, 화: 0, 토: 0, 금: 0, 수: 0 },
    tenGods: [] as TenGod[],
    ...overrides,
  };
}

// ── findSinSals: 신규 신살 판정 ────────────────────────────────────────────

describe('findSinSals — v2 신규 신살', () => {
  test('홍염살: 갑오 일주 (갑→오)', () => {
    const saju = makeSaju(['임', '신'], ['신', '해'], ['갑', '오'], ['경', '오']);
    const sinSals = findSinSals(saju);
    expect(sinSals).toContain('hong_yeom_sal');
  });

  test('홍염살: 을→오 또는 신 (이중 매칭)', () => {
    const sajuO = makeSaju(
      ['갑', '자'], ['갑', '자'], ['을', '묘'], ['갑', '오'],
    );
    const sajuShin = makeSaju(
      ['갑', '자'], ['갑', '자'], ['을', '묘'], ['갑', '신'],
    );
    const sajuMiss = makeSaju(
      ['갑', '자'], ['갑', '자'], ['을', '묘'], ['갑', '축'],
    );
    expect(findSinSals(sajuO)).toContain('hong_yeom_sal');
    expect(findSinSals(sajuShin)).toContain('hong_yeom_sal');
    expect(findSinSals(sajuMiss)).not.toContain('hong_yeom_sal');
  });

  test('금여록: 갑→진', () => {
    const sajuHit = makeSaju(
      ['갑', '진'], ['갑', '자'], ['갑', '오'], ['갑', '자'],
    );
    const sajuMiss = makeSaju(
      ['갑', '사'], ['갑', '자'], ['갑', '오'], ['갑', '자'],
    );
    expect(findSinSals(sajuHit)).toContain('geum_yeo_rok');
    expect(findSinSals(sajuMiss)).not.toContain('geum_yeo_rok');
  });

  test.each([
    ['갑', '오'], ['정', '미'], ['무', '진'], ['기', '진'],
    ['경', '술'], ['신', '유'], ['임', '자'],
  ] as Array<[HeavenlyStem, EarthlyBranch]>)(
    '자좌홍염 7개 일주: %s%s',
    (stem, branch) => {
      const saju = makeSaju(
        ['갑', '자'], ['갑', '자'], [stem, branch], ['갑', '자'],
      );
      expect(findSinSals(saju)).toContain('ja_jwa_hong_yeom');
    },
  );

  test('자좌홍염 미스: 갑자 일주', () => {
    const saju = makeSaju(
      ['갑', '자'], ['갑', '자'], ['갑', '자'], ['갑', '자'],
    );
    expect(findSinSals(saju)).not.toContain('ja_jwa_hong_yeom');
  });
});

// ── 회귀 가드: 기존 7개 신살 판정 비파괴 ──────────────────────────────────

describe('findSinSals — 기존 7개 신살 회귀 가드', () => {
  test('천을귀인: 갑→축미', () => {
    const saju = makeSaju(
      ['갑', '축'], ['갑', '인'], ['갑', '인'], ['갑', '인'],
    );
    expect(findSinSals(saju)).toContain('cheon_eul_gwi_in');
  });

  test('도화살: 인오술 그룹 → 묘', () => {
    const saju = makeSaju(
      ['갑', '인'], ['갑', '인'], ['갑', '묘'], ['갑', '술'],
    );
    expect(findSinSals(saju)).toContain('do_hwa_sal');
  });

  test('역마살: 인오술 그룹 → 신', () => {
    const saju = makeSaju(
      ['갑', '인'], ['갑', '신'], ['갑', '인'], ['갑', '인'],
    );
    expect(findSinSals(saju)).toContain('yeok_ma_sal');
  });

  test('화개살: 인오술 그룹 → 술', () => {
    const saju = makeSaju(
      ['갑', '인'], ['갑', '술'], ['갑', '인'], ['갑', '인'],
    );
    expect(findSinSals(saju)).toContain('hwa_gae_sal');
  });

  test('공망: 갑오 일주 → 진·사', () => {
    // 갑오순(甲午→癸卯) 의 공망은 진·사. 사주에 진 포함.
    const saju = makeSaju(
      ['갑', '진'], ['갑', '인'], ['갑', '오'], ['갑', '인'],
    );
    expect(findSinSals(saju)).toContain('gong_mang');
  });
});

// ── computeCharmFlags ────────────────────────────────────────────────────

describe('computeCharmFlags', () => {
  test('도화일주: day=오 → dohwaIlju true', () => {
    const saju = makeSaju(
      ['임', '신'], ['신', '해'], ['갑', '오'], ['경', '오'],
    );
    const flags = computeCharmFlags(saju);
    expect(flags?.dohwaIlju).toBe(true);
  });

  test('도화일주 미스: day=인', () => {
    const saju = makeSaju(
      ['갑', '인'], ['갑', '인'], ['갑', '인'], ['갑', '인'],
    );
    const flags = computeCharmFlags(saju);
    // dohwaIlju 가 false 일 때는 키 자체가 생략될 수 있음
    expect(flags?.dohwaIlju).not.toBe(true);
  });

  test('자좌홍염 flag: 갑오 일주', () => {
    const saju = makeSaju(
      ['임', '신'], ['신', '해'], ['갑', '오'], ['경', '오'],
    );
    expect(computeCharmFlags(saju)?.jaJwaHongYeom).toBe(true);
  });

  test('홍염×도화 시너지: 둘 다 보유', () => {
    // 갑인일주, hour=오 → 홍염살(갑→오). 도화살(인오술→묘): day=인+hour=오, 묘 필요. 묘 없음.
    // 다른 조합: 도화살 인오술→묘 + 홍염 갑→오.
    // 갑묘일주 + 오 → 도화살: 인오술 그룹 멤버(오) + 도화 묘(day) → hit.
    // 갑일간 홍염 오 → year/month/hour 중 오 있어야.
    const saju = makeSaju(
      ['갑', '오'], ['갑', '인'], ['갑', '묘'], ['갑', '인'],
    );
    const flags = computeCharmFlags(saju);
    expect(flags?.hongYeomDohwaSynergy).toBe(true);
  });

  test('목욕 위치: 갑 일간 + hour=자 → mokyokPillars=[hour]', () => {
    const saju = makeSaju(
      ['임', '신'], ['신', '해'], ['갑', '오'], ['경', '자'],
    );
    expect(computeCharmFlags(saju)?.mokyokPillars).toEqual(['hour']);
  });
});

// ── computeDohwaInteractions ─────────────────────────────────────────────

describe('computeDohwaInteractions', () => {
  test('도화 충: day=오 (사유축그룹 도화) + hour=자 → 자오충', () => {
    const saju = makeSaju(
      ['을', '축'], ['정', '유'], ['갑', '오'], ['병', '자'],
    );
    const interactions = computeDohwaInteractions(saju);
    expect(interactions?.chung).toBeDefined();
    expect(interactions?.chung?.length).toBeGreaterThan(0);
    // day=오 가 충에 걸렸어야 함
    const dayChung = interactions?.chung?.find((c) =>
      c.pillars.includes('day'),
    );
    expect(dayChung).toBeDefined();
  });

  test('도화 미보유 시 undefined', () => {
    const saju = makeSaju(
      ['갑', '인'], ['갑', '인'], ['갑', '인'], ['갑', '인'],
    );
    const interactions = computeDohwaInteractions(saju);
    expect(interactions).toBeUndefined();
  });
});
