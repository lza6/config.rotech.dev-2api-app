// OpenChat 1.4.2 protocol load test — LOOPBACK ONLY (hits local mock, never api.dialgptapi.com)
// Usage: node stress_test.cjs [concurrency] [totalRequests]
const http = require('http');
const crypto = require('crypto');

const PORT = Number(process.argv[2] || 8942);
const CONC = Number(process.argv[3] || 20);
const TOTAL = Number(process.argv[4] || 200);
const BASE = `http://127.0.0.1:${PORT}`;

function post(path, body, headers = {}) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const req = http.request(BASE + path, { method: 'POST', headers: { 'Content-Type': 'application/json', ...headers, 'Content-Length': Buffer.byteLength(data) } }, res => {
      let b = ''; res.on('data', c => b += c); res.on('end', () => resolve({ status: res.statusCode, body: b }));
    });
    req.on('error', reject); req.end(data);
  });
}

function sse(path, body, token) {
  return new Promise((resolve, reject) => {
    const t0 = Date.now();
    const data = JSON.stringify(body);
    const req = http.request(BASE + path, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token, 'Content-Length': Buffer.byteLength(data) } }, res => {
      let b = '', firstChunk = null;
      res.on('data', c => { if (firstChunk === null) firstChunk = Date.now() - t0; b += c; });
      res.on('end', () => resolve({ status: res.statusCode, ms: Date.now() - t0, ttfc: firstChunk, chunks: (b.match(/data:/g) || []).length }));
    });
    req.on('error', reject); req.end(data);
  });
}

const pct = (arr, p) => { const s = [...arr].sort((a, b) => a - b); return s[Math.min(s.length - 1, Math.floor(s.length * p))] ?? 0; };

(async () => {
  console.log(`=== OpenChat 1.4.2 mock 压测  conc=${CONC} total=${TOTAL} (loopback only) ===`);

  // 1) login
  const logins = [];
  let okLogin = 0;
  const t0 = Date.now();
  for (let i = 0; i < CONC; i++) {
    logins.push(post('/v1/auth/login', { timezone: 'GMT+08:00', token: 'stress-' + i, app_name: 'chat_gpt_android', revenue_cat_app_user_id: '', one_link_params: null }).then(r => { if (r.status === 200) okLogin++; return r; }));
  }
  const loginResults = await Promise.all(logins);
  const loginMs = Date.now() - t0;
  console.log(`login: ${okLogin}/${CONC} ok in ${loginMs}ms`);

  // 2) chat SSE burst — each worker reuses its own token, sequential requests
  const tokens = loginResults.map(r => { try { return JSON.parse(r.body).access_token; } catch { return null; } }).filter(Boolean);
  const results = [];
  const perWorker = Math.ceil(TOTAL / tokens.length);
  const t1 = Date.now();
  await Promise.all(tokens.map(async (tk, w) => {
    for (let i = 0; i < perWorker && w * perWorker + i < TOTAL; i++) {
      const svc = ['gpt', 'gemini', 'grok', 'deepseek'][i % 4];
      const body = svc === 'gemini'
        ? { contents: [{ role: 'user', parts: [{ text: 'ping ' + i }] }] }
        : { model: 'gpt-4o-mini', messages: [{ role: 'user', content: [{ type: 'text', text: 'ping ' + i }] }], max_completion_tokens: 1000, stream: true };
      results.push(await sse(`/v1/ai/services/${svc}`, body, tk));
    }
  }));
  const wall = Date.now() - t1;

  const okRes = results.filter(r => r.status === 200);
  const msArr = okRes.map(r => r.ms);
  const ttfcArr = okRes.map(r => r.ttfc).filter(x => x !== null);
  console.log(`chat: ${okRes.length}/${results.length} ok | wall=${wall}ms rps=${(results.length / (wall / 1000)).toFixed(1)}`);
  if (msArr.length) {
    console.log(`latency  p50=${pct(msArr, .5)}ms p90=${pct(msArr, .9)}ms p99=${pct(msArr, .99)}ms`);
    console.log(`ttfc     p50=${pct(ttfcArr, .5)}ms p90=${pct(ttfcArr, .9)}ms`);
  }
  const errs = {};
  results.filter(r => r.status !== 200).forEach(r => { errs[r.status] = (errs[r.status] || 0) + 1; });
  if (Object.keys(errs).length) console.log('errors:', errs);

  // 3) unauthorized path
  const un = await sse('/v1/ai/services/gpt', { model: 'gpt-4o-mini', messages: [] }, 'bad-token');
  console.log(`unauthorized check: status=${un.status} (expect 401)`);
})().catch(e => { console.error(e); process.exit(1); });
