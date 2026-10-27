// OpenChat 1.4.2 (AI Chatbot Assistant, dialgptapi.com) local mock server
// LOOPBACK ONLY — never proxies to api.dialgptapi.com
// Usage: node mock-server.cjs [port=8942]
const http = require('http');
const crypto = require('crypto');
const PORT = Number(process.argv[2] || 8942);

const refreshTokens = new Map(); // refreshToken -> { appName, userId }
const accessTokens = new Map();  // accessToken -> { userId, exp }

function issueTokens(userId) {
  const access = crypto.randomBytes(24).toString('hex');
  const refresh = crypto.randomBytes(24).toString('hex');
  accessTokens.set(access, { userId, exp: Date.now() + 3600e3 });
  refreshTokens.set(refresh, { userId });
  return {
    access_token: access,
    access_token_expires_in: 3600,
    refresh_token: refresh,
    refresh_token_expires_in: 86400,
    token_type: 'Bearer',
  };
}

const SYSTEM_PROMPT = 'You are a helpful AI assistant running on OpenChat 1.4.2 mock.';

function buildGptBody(parsed) {
  // StreamGPTRequest: {model, messages:[{role, content:[{type,text}|{type,image_url,image_url:{url}}]}], max_completion_tokens, stream}
  const sys = (parsed.messages || []).filter(m => m.role === 'system').map(m => (m.content || []).map(c => c.text || '').join('\n')).join('\n');
  const lastUser = [...(parsed.messages || [])].reverse().find(m => m.role === 'user');
  const text = lastUser ? (lastUser.content || []).map(c => c.text || '[image]').join(' ') : '';
  return { sys: sys || SYSTEM_PROMPT, text, model: parsed.model };
}

function sseChunks(res, text, model) {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive',
  });
  const words = text.split(/(\s+)/);
  let i = 0;
  const id = 'chatcmpl-' + crypto.randomUUID();
  const timer = setInterval(() => {
    if (i >= words.length) {
      res.write(`data: {"id":"${id}","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}\n\n`);
      res.write('data: [DONE]\n\n');
      res.end();
      clearInterval(timer);
      return;
    }
    const delta = { id, choices: [{ index: 0, delta: { content: words[i] }, finish_reason: null }] };
    res.write(`data: ${JSON.stringify(delta)}\n\n`);
    i++;
  }, 5);
}

let requestCount = 0;

const server = http.createServer((req, res) => {
  const url = req.url.split('?')[0];
  let body = '';
  req.on('data', c => { body += c; if (body.length > 5e6) req.destroy(); });
  req.on('end', () => {
    requestCount++;
    const auth = req.headers['authorization'] || '';

    // ---- auth/login : TokenRequest {timezone, token, app_name, revenue_cat_app_user_id, one_link_params}
    if (req.method === 'POST' && url === '/v1/auth/login') {
      let p = {}; try { p = JSON.parse(body || '{}'); } catch {}
      if (!p.token) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ error: 'missing firebase token' }));
      }
      const userId = 'mock-user-' + crypto.createHash('md5').update(String(p.token)).digest('hex').slice(0, 10);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify(issueTokens(userId)));
    }

    // ---- auth/token/refresh
    if (req.method === 'POST' && url === '/v1/auth/token/refresh') {
      let p = {}; try { p = JSON.parse(body || '{}'); } catch {}
      if (!p.refresh_token || !refreshTokens.has(p.refresh_token)) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ error: 'invalid refresh token' }));
      }
      res.writeHead(200, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify(issueTokens(refreshTokens.get(p.refresh_token).userId)));
    }

    // ---- users/me
    if (req.method === 'GET' && url === '/v1/users/me') {
      if (!auth.startsWith('Bearer ') || !accessTokens.has(auth.slice(7))) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ error: 'unauthorized' }));
      }
      res.writeHead(200, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify({ id: 'mock-user', name: 'Mock User', is_pro: false, requests_left: 999 }));
    }

    // ---- ai/services/{gpt|gemini|grok|deepseek}  (SSE stream)
    const svcMatch = url.match(/^\/v1\/ai\/services\/(\w+)$/);
    if (req.method === 'POST' && svcMatch) {
      if (!auth.startsWith('Bearer ') || !accessTokens.has(auth.slice(7))) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ error: 'unauthorized' }));
      }
      let parsed = {}; try { parsed = JSON.parse(body || '{}'); } catch {}
      const service = svcMatch[1];
      const info = buildGptBody(parsed);
      const text = `[mock:${service}] You said: ${info.text}`;
      if (service === 'gemini') {
        // Gemini-style SSE: candidates[].content.parts[].text
        res.writeHead(200, { 'Content-Type': 'text/event-stream' });
        const chunks = text.match(/.{1,20}/gs) || [];
        let i = 0;
        const timer = setInterval(() => {
          if (i >= chunks.length) {
            res.write(`data: ${JSON.stringify({ candidates: [{ content: { parts: [{ text: '' }], role: 'model' }, finishReason: 'STOP' }] })}\n\n`);
            res.end(); clearInterval(timer); return;
          }
          res.write(`data: ${JSON.stringify({ candidates: [{ content: { parts: [{ text: chunks[i] }], role: 'model' } }] })}\n\n`);
          i++;
        }, 5);
        return;
      }
      return sseChunks(res, text, parsed.model);
    }

    // ---- ai/fal (image gen) + polling
    if (req.method === 'POST' && url === '/v1/ai/fal') {
      if (!auth.startsWith('Bearer ')) { res.writeHead(401); return res.end('{}'); }
      const taskId = crypto.randomUUID();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify({ task_id: taskId, status: 'IN_QUEUE' }));
    }
    const falMatch = url.match(/^\/v1\/ai\/fal\/([\w-]+)$/);
    if (req.method === 'GET' && falMatch) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify({
        status: 'COMPLETED',
        images: [{ url: 'https://mock.local/1x1.png', width: 1024, height: 1024 }],
      }));
    }

    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'not found', path: url }));
  });
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[openchat142-mock] listening on http://127.0.0.1:${PORT} (loopback only)`);
});
