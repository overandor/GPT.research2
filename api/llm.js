export const config = {
  runtime: 'nodejs',
  maxDuration: 30,
};

const DEFAULT_MODEL_CID = process.env.GGUF_MODEL_CID;
const DEFAULT_BACKEND = normalizeBaseUrl(process.env.LLAMA_CPP_SERVER_URL);
const DEFAULT_MAX_TOKENS = Number(process.env.LLM_DEFAULT_MAX_TOKENS || 256);
const HARD_MAX_TOKENS = Number(process.env.LLM_HARD_MAX_TOKENS || 1024);
const REQUEST_TIMEOUT_MS = Number(process.env.LLM_REQUEST_TIMEOUT_MS || 25000);

const corsHeaders = {
  'access-control-allow-origin': process.env.CORS_ALLOW_ORIGIN || '*',
  'access-control-allow-methods': 'POST,OPTIONS',
  'access-control-allow-headers': 'content-type,authorization,x-api-key',
};

export default async function handler(req, res) {
  setHeaders(res, corsHeaders);

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'method_not_allowed' });
  }

  if (process.env.GATEWAY_API_KEY && req.headers['x-api-key'] !== process.env.GATEWAY_API_KEY) {
    return res.status(401).json({ error: 'unauthorized' });
  }

  if (!DEFAULT_BACKEND) {
    return res.status(500).json({
      error: 'missing_backend',
      detail: 'Set LLAMA_CPP_SERVER_URL in Vercel environment variables.',
    });
  }

  const body = req.body || {};
  const prompt = typeof body.prompt === 'string' ? body.prompt.trim() : '';
  const stream = body.stream === true;
  const modelCid = normalizeCid(body.modelCid || body.model_cid || DEFAULT_MODEL_CID);

  if (!prompt) {
    return res.status(400).json({ error: 'missing_prompt' });
  }

  if (!modelCid) {
    return res.status(400).json({
      error: 'missing_model_cid',
      detail: 'Provide modelCid in the request body or set GGUF_MODEL_CID.',
    });
  }

  const payload = buildLlamaCppPayload({
    prompt,
    modelCid,
    temperature: body.temperature,
    top_p: body.top_p,
    max_tokens: body.max_tokens,
    stop: body.stop,
    stream,
  });

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const upstream = await fetch(`${DEFAULT_BACKEND}/completion`, {
      method: 'POST',
      signal: controller.signal,
      headers: {
        'content-type': 'application/json',
        ...(process.env.LLAMA_CPP_API_KEY
          ? { authorization: `Bearer ${process.env.LLAMA_CPP_API_KEY}` }
          : {}),
      },
      body: JSON.stringify(payload),
    });

    if (stream) {
      setHeaders(res, {
        'content-type': upstream.headers.get('content-type') || 'text/event-stream; charset=utf-8',
        'cache-control': 'no-cache, no-transform',
        'x-model-cid': modelCid,
      });

      res.status(upstream.status);

      if (!upstream.body) {
        return res.end();
      }

      const reader = upstream.body.getReader();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        res.write(Buffer.from(value));
      }

      return res.end();
    }

    const text = await upstream.text();
    const data = safeJson(text);

    return res.status(upstream.status).json({
      ok: upstream.ok,
      model_cid: modelCid,
      backend: redactBackend(DEFAULT_BACKEND),
      response: data ?? text,
    });
  } catch (err) {
    const aborted = err?.name === 'AbortError';
    return res.status(aborted ? 504 : 500).json({
      error: aborted ? 'upstream_timeout' : 'llm_gateway_failure',
      detail: err.message,
      model_cid: modelCid,
    });
  } finally {
    clearTimeout(timeout);
  }
}

function buildLlamaCppPayload({ prompt, modelCid, temperature, top_p, max_tokens, stop, stream }) {
  const boundedMaxTokens = clampInteger(max_tokens, 1, HARD_MAX_TOKENS, DEFAULT_MAX_TOKENS);

  return {
    prompt,
    temperature: clampNumber(temperature, 0, 2, 0.7),
    top_p: clampNumber(top_p, 0, 1, 0.95),
    n_predict: boundedMaxTokens,
    stop: Array.isArray(stop) ? stop.map(String).slice(0, 8) : undefined,
    stream,
    cache_prompt: true,
    metadata: {
      model_format: 'gguf',
      model_distribution: 'ipfs',
      ipfs_cid: modelCid,
    },
  };
}

function normalizeBaseUrl(value) {
  if (!value) return '';
  return String(value).replace(/\/+$/, '');
}

function normalizeCid(value) {
  if (!value) return '';
  const cid = String(value).trim();
  return /^[a-zA-Z0-9]+$/.test(cid) ? cid : '';
}

function clampInteger(value, min, max, fallback) {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.min(Math.max(parsed, min), max);
}

function clampNumber(value, min, max, fallback) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.min(Math.max(parsed, min), max);
}

function safeJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function redactBackend(url) {
  try {
    const parsed = new URL(url);
    return parsed.host;
  } catch {
    return 'configured';
  }
}

function setHeaders(res, headers) {
  for (const [key, value] of Object.entries(headers)) {
    if (value !== undefined && value !== null) {
      res.setHeader(key, value);
    }
  }
}
