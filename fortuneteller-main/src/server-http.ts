/**
 * Railway 배포용 HTTP 서버 엔트리포인트
 * SSE(Server-Sent Events) 트랜스포트를 사용한 MCP 서버
 */

import http from 'node:http';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import { z } from 'zod';
import { createMCPServer } from './core/server.js';
import { handleAnalyzeSaju } from './tools/analyze_saju.js';

const ISO_DATE = /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/;
const HHMM = /^([01]\d|2[0-3]):([0-5]\d)$/;

const freeSajuRestSchema = z.object({
  birth: z.string().regex(ISO_DATE, 'birth는 YYYY-MM-DD 형식이어야 합니다'),
  calendar: z.enum(['solar', 'lunar']),
  time: z.union([z.string().regex(HHMM, 'time은 HH:MM 형식이어야 합니다'), z.literal('unknown')]),
  gender: z.enum(['male', 'female']),
});

function readBody(req: http.IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on('data', (chunk: Buffer) => chunks.push(chunk));
    req.on('end', () => resolve(Buffer.concat(chunks).toString()));
    req.on('error', reject);
  });
}

const PORT = parseInt(process.env.PORT || '3000', 10);

// 활성 트랜스포트 추적
const transports = new Map<string, SSEServerTransport>();

const httpServer = http.createServer(async (req, res) => {
  // CORS 헤더
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // 헬스 체크
  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', service: 'saju-mcp-server' }));
    return;
  }

  // SSE 연결 (GET /sse)
  if (req.method === 'GET' && req.url === '/sse') {
    const server = createMCPServer();
    const transport = new SSEServerTransport('/messages', res);
    transports.set(transport.sessionId, transport);

    res.on('close', () => {
      transports.delete(transport.sessionId);
    });

    await server.connect(transport);
    return;
  }

  // 메시지 수신 (POST /messages)
  if (req.method === 'POST' && req.url?.startsWith('/messages')) {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const sessionId = url.searchParams.get('sessionId');

    if (!sessionId || !transports.has(sessionId)) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: '유효하지 않은 세션입니다' }));
      return;
    }

    const transport = transports.get(sessionId)!;
    await transport.handlePostMessage(req, res);
    return;
  }

  // 루트 경로 안내
  if (req.method === 'GET' && (req.url === '/' || req.url === '')) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      name: 'saju-mcp-server',
      description: '한국 전통 사주팔자 운세 분석 MCP 서버',
      endpoints: {
        sse: '/sse',
        messages: '/messages',
        health: '/health',
      },
    }));
    return;
  }

  // REST 엔드포인트: POST /api/saju/free
  if (req.method === 'POST' && req.url === '/api/saju/free') {
    let body: unknown;
    try {
      const raw = await readBody(req);
      body = JSON.parse(raw) as unknown;
    } catch {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: '유효하지 않은 JSON 요청입니다' }));
      return;
    }

    const parsed = freeSajuRestSchema.safeParse(body);
    if (!parsed.success) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: '입력값이 올바르지 않습니다', issues: parsed.error.issues }));
      return;
    }

    const { birth, time, calendar, gender } = parsed.data;
    const birthTime = time === 'unknown' ? '12:00' : time;

    try {
      const result = await handleAnalyzeSaju({
        birthDate: birth,
        birthTime,
        gender,
        analysisType: 'basic',
        calendar,
      });
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(result);
    } catch (err) {
      console.error('[/api/saju/free] 사주 계산 오류', err);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: '사주 계산 중 오류가 발생했습니다' }));
    }
    return;
  }

  res.writeHead(404);
  res.end('Not Found');
});

httpServer.listen(PORT, '0.0.0.0', () => {
  console.log(`사주 MCP 서버가 포트 ${PORT}에서 실행 중입니다`);
  console.log(`SSE 엔드포인트: http://0.0.0.0:${PORT}/sse`);
});

process.on('SIGINT', () => {
  httpServer.close();
  process.exit(0);
});

process.on('SIGTERM', () => {
  httpServer.close();
  process.exit(0);
});
