import crypto from 'crypto';

export const config = {
  runtime: 'nodejs',
  maxDuration: 30,
};

const TASKS = new Map([
  ['ipfs-resolver', resolveIpfs],
  ['runtime-capsule', runtimeCapsule],
  ['proof-receipt', proofReceipt],
  ['telemetry-tunnel', telemetryTunnel],
  ['gpu-router', gpuRouter],
  ['llm-gateway-test', llmGatewayTest],
  ['network-health', networkHealth],
  ['cid-registry', cidRegistry],
  ['prompt-hasher', promptHasher],
  ['session-fork', sessionFork],
  ['pool-signal', poolSignal],
  ['telegram-payload', telegramPayload],
]);

const corsHeaders = {
  'access-control-allow-origin': process.env.CORS_ALLOW_ORIGIN || '*',
  'access-control-allow-methods': 'POST,OPTIONS',
  'access-control-allow-headers': 'content-type,authorization,x-api-key',
};

export default async function handler(req, res) {
  setHeaders(res, corsHeaders);

  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'method_not_allowed' });

  if (process.env.GATEWAY_API_KEY && req.headers['x-api-key'] !== process.env.GATEWAY_API_KEY) {
    return res.status(401).json({ error: 'unauthorized' });
  }

  const body = req.body || {};
  const task = String(body.task || '').trim();
  const run = TASKS.get(task);

  if (!run) {
    return res.status(400).json({
      error: 'unknown_task',
      supported_tasks: [...TASKS.keys()],
    });
  }

  try {
    const result = await run(body);
    return res.status(200).json({
      ok: true,
      task,
      timestamp: new Date().toISOString(),
      result,
    });
  } catch (err) {
    return res.status(err.statusCode || 500).json({
      ok: false,
      task,
      error: err.code || 'task_failed',
      detail: err.message,
    });
  }
}

async function resolveIpfs(body) {
  const cid = requiredCid(body.cid || process.env.GGUF_MODEL_CID);
  const gateway = normalizeBaseUrl(body.gateway || process.env.IPFS_GATEWAY_URL || 'https://ipfs.io/ipfs');
  const url = `${gateway}/${cid}`;

  if (body.check === false) {
    return { cid, gateway, url, checked: false };
  }

  const head = await fetch(url, { method: 'HEAD' });
  return {
    cid,
    gateway,
    url,
    checked: true,
    reachable: head.ok,
    status: head.status,
    content_type: head.headers.get('content-type'),
    content_length: head.headers.get('content-length'),
  };
}

function runtimeCapsule(body) {
  const modelCid = requiredCid(body.modelCid || body.cid || process.env.GGUF_MODEL_CID);
  const runtimeCid = optionalCid(body.runtimeCid || process.env.RUNTIME_CAPSULE_CID);
  const capsule = {
    capsule_version: '0.1.0',
    runtime: body.runtime || 'llama.cpp',
    runtime_cid: runtimeCid,
    model_format: 'gguf',
    model_cid: modelCid,
    tokenizer_cid: optionalCid(body.tokenizerCid || process.env.TOKENIZER_CID),
    launch: {
      ctx_size: clampInteger(body.ctx_size, 512, 262144, 8192),
      gpu_layers: clampInteger(body.gpu_layers, -1, 200, -1),
      batch_size: clampInteger(body.batch_size, 1, 4096, 512),
    },
    proof: {
      receipts: body.receipts !== false,
      token_hashing: true,
      telemetry_tunnel: true,
    },
  };

  return {
    capsule,
    capsule_hash: sha256(canonicalJson(capsule)),
  };
}

function proofReceipt(body) {
  const modelCid = requiredCid(body.modelCid || body.cid || process.env.GGUF_MODEL_CID);
  const prompt = String(body.prompt || '');
  const output = String(body.output || '');
  const receipt = {
    schema: 'poi.receipt.v0',
    model_cid: modelCid,
    prompt_hash: sha256(prompt),
    output_hash: sha256(output),
    token_sequence_hash: sha256(JSON.stringify(body.tokens || [])),
    sampler_state: {
      temperature: clampNumber(body.temperature, 0, 2, 0.7),
      top_p: clampNumber(body.top_p, 0, 1, 0.95),
    },
    runtime_fingerprint: body.runtime_fingerprint || process.env.RUNTIME_FINGERPRINT || 'unattested',
    worker: process.env.VERCEL_REGION || 'vercel',
    timestamp: new Date().toISOString(),
  };

  return {
    receipt,
    receipt_hash: sha256(canonicalJson(receipt)),
  };
}

function telemetryTunnel(body) {
  const event = {
    schema: 'telemetry.tunnel.v0',
    trace_id: body.trace_id || crypto.randomUUID(),
    session_id: body.session_id || crypto.randomUUID(),
    model_cid: optionalCid(body.modelCid || body.cid || process.env.GGUF_MODEL_CID),
    runtime_cid: optionalCid(body.runtimeCid || process.env.RUNTIME_CAPSULE_CID),
    prompt_hash: body.prompt ? sha256(String(body.prompt)) : null,
    token_count: clampInteger(body.token_count, 0, 10000000, 0),
    latency_ms: clampInteger(body.latency_ms, 0, 3600000, 0),
    entropy: clampNumber(body.entropy, 0, 64, 0),
    kv_commitment: body.kv_commitment || null,
    worker_signature: body.worker_signature || null,
    emitted_at: new Date().toISOString(),
  };

  return {
    event,
    event_hash: sha256(canonicalJson(event)),
  };
}

function gpuRouter(body) {
  const workers = parseJsonEnv('GPU_WORKERS', []);
  const modelCid = optionalCid(body.modelCid || body.cid || process.env.GGUF_MODEL_CID);
  const requiredCapability = body.capability || 'gguf';
  const candidates = workers.filter((worker) => {
    if (!worker || typeof worker !== 'object') return false;
    const caps = Array.isArray(worker.capabilities) ? worker.capabilities : [];
    const models = Array.isArray(worker.models) ? worker.models : [];
    return caps.includes(requiredCapability) && (!modelCid || models.includes(modelCid) || models.includes('*'));
  });

  if (candidates.length === 0) {
    throw httpError(503, 'no_gpu_worker', 'No configured GPU worker can serve this model/capability. Set GPU_WORKERS JSON in Vercel.');
  }

  candidates.sort((a, b) => Number(a.priority || 100) - Number(b.priority || 100));
  return {
    selected: safeWorker(candidates[0]),
    candidates: candidates.map(safeWorker),
  };
}

async function llmGatewayTest(body) {
  const backend = normalizeBaseUrl(body.backend || process.env.LLAMA_CPP_SERVER_URL);
  if (!backend) throw httpError(500, 'missing_backend', 'Set LLAMA_CPP_SERVER_URL or provide backend.');

  const response = await fetch(`${backend}/health`, {
    method: 'GET',
    headers: process.env.LLAMA_CPP_API_KEY ? { authorization: `Bearer ${process.env.LLAMA_CPP_API_KEY}` } : {},
  });

  return {
    backend: redactUrl(backend),
    health_endpoint: '/health',
    reachable: response.ok,
    status: response.status,
  };
}

async function networkHealth(body) {
  const checks = [];
  checks.push({ name: 'vercel_api', ok: true, region: process.env.VERCEL_REGION || null });

  if (process.env.LLAMA_CPP_SERVER_URL || body.backend) {
    try {
      checks.push({ name: 'llm_backend', ...(await llmGatewayTest(body)) });
    } catch (err) {
      checks.push({ name: 'llm_backend', ok: false, error: err.message });
    }
  }

  if (process.env.GGUF_MODEL_CID || body.cid) {
    try {
      const ipfs = await resolveIpfs({ cid: body.cid, gateway: body.gateway, check: body.checkIpfs !== false });
      checks.push({ name: 'ipfs_model', ok: ipfs.reachable ?? true, ...ipfs });
    } catch (err) {
      checks.push({ name: 'ipfs_model', ok: false, error: err.message });
    }
  }

  return { healthy: checks.every((check) => check.ok !== false && check.reachable !== false), checks };
}

function cidRegistry(body) {
  const registry = parseJsonEnv('CID_REGISTRY', {});
  const alias = String(body.alias || '').trim();

  if (alias) {
    const entry = registry[alias];
    if (!entry) throw httpError(404, 'alias_not_found', `No CID registry entry for alias: ${alias}`);
    return { alias, entry };
  }

  return { aliases: Object.keys(registry), registry };
}

function promptHasher(body) {
  const prompt = String(body.prompt || '');
  if (!prompt) throw httpError(400, 'missing_prompt', 'Provide prompt to hash.');

  return {
    prompt_hash: sha256(prompt),
    bytes: Buffer.byteLength(prompt, 'utf8'),
    chars: prompt.length,
  };
}

function sessionFork(body) {
  const parent = String(body.parent_session || body.parent || '').trim();
  if (!parent) throw httpError(400, 'missing_parent_session', 'Provide parent_session.');

  const fork = {
    schema: 'cais.fork.v0',
    parent_session: parent,
    model_cid: optionalCid(body.modelCid || body.cid || process.env.GGUF_MODEL_CID),
    branch_label: body.branch_label || 'default',
    sampler_delta: {
      temperature: body.temperature ?? null,
      top_p: body.top_p ?? null,
    },
    created_at: new Date().toISOString(),
  };

  return { fork, fork_hash: sha256(canonicalJson(fork)) };
}

function poolSignal(body) {
  const signal = {
    schema: 'clp.signal.v0',
    semantic_domain: body.semantic_domain || 'general',
    model_cid: optionalCid(body.modelCid || body.cid || process.env.GGUF_MODEL_CID),
    prompt_hash: body.prompt ? sha256(String(body.prompt)) : null,
    contribution_score: clampNumber(body.contribution_score, 0, 1, 0),
    reuse_score: clampNumber(body.reuse_score, 0, 1, 0),
    entropy_reduction: clampNumber(body.entropy_reduction, 0, 64, 0),
    emitted_at: new Date().toISOString(),
  };

  return { signal, signal_hash: sha256(canonicalJson(signal)) };
}

function telegramPayload(body) {
  const text = String(body.text || body.prompt || '').trim();
  if (!text) throw httpError(400, 'missing_text', 'Provide text or prompt.');

  return {
    method: 'sendMessage',
    payload: {
      chat_id: body.chat_id || '<chat_id>',
      text,
      parse_mode: body.parse_mode || 'Markdown',
      disable_web_page_preview: true,
    },
    telegram_api_configured: Boolean(process.env.TELEGRAM_BOT_TOKEN),
  };
}

function requiredCid(value) {
  const cid = optionalCid(value);
  if (!cid) throw httpError(400, 'missing_or_invalid_cid', 'A valid CID-like alphanumeric value is required.');
  return cid;
}

function optionalCid(value) {
  if (!value) return null;
  const cid = String(value).trim();
  return /^[a-zA-Z0-9]+$/.test(cid) ? cid : null;
}

function sha256(value) {
  return crypto.createHash('sha256').update(String(value)).digest('hex');
}

function canonicalJson(value) {
  return JSON.stringify(sortKeys(value));
}

function sortKeys(value) {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (!value || typeof value !== 'object') return value;
  return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => [k, sortKeys(v)]));
}

function normalizeBaseUrl(value) {
  if (!value) return '';
  return String(value).replace(/\/+$/, '');
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

function parseJsonEnv(name, fallback) {
  const raw = process.env[name];
  if (!raw) return fallback;
  try {
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function redactUrl(url) {
  try {
    return new URL(url).host;
  } catch {
    return 'configured';
  }
}

function safeWorker(worker) {
  return {
    id: worker.id,
    endpoint: worker.endpoint ? redactUrl(worker.endpoint) : undefined,
    capabilities: worker.capabilities || [],
    models: worker.models || [],
    priority: worker.priority || 100,
  };
}

function httpError(statusCode, code, message) {
  const err = new Error(message);
  err.statusCode = statusCode;
  err.code = code;
  return err;
}

function setHeaders(res, headers) {
  for (const [key, value] of Object.entries(headers)) {
    if (value !== undefined && value !== null) res.setHeader(key, value);
  }
}
