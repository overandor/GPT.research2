export const config = {
  runtime: 'nodejs',
  maxDuration: 30,
};

const DEFAULT_MODEL = process.env.GGUF_MODEL_CID;
const DEFAULT_BACKEND = process.env.LLAMA_CPP_SERVER_URL;

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'method_not_allowed' });
  }

  try {
    const {
      prompt,
      modelCid = DEFAULT_MODEL,
      temperature = 0.7,
      max_tokens = 256
    } = req.body || {};

    if (!prompt) {
      return res.status(400).json({ error: 'missing_prompt' });
    }

    if (!DEFAULT_BACKEND) {
      return res.status(500).json({
        error: 'missing_backend',
        detail: 'Set LLAMA_CPP_SERVER_URL in Vercel environment variables'
      });
    }

    const upstream = await fetch(`${DEFAULT_BACKEND}/completion`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        ...(process.env.LLAMA_CPP_API_KEY
          ? { authorization: `Bearer ${process.env.LLAMA_CPP_API_KEY}` }
          : {})
      },
      body: JSON.stringify({
        prompt,
        temperature,
        n_predict: max_tokens,
        cache_prompt: true,
        metadata: {
          ipfs_cid: modelCid
        }
      })
    });

    const data = await upstream.json();

    return res.status(upstream.status).json({
      ok: upstream.ok,
      model_cid: modelCid,
      response: data
    });
  } catch (err) {
    return res.status(500).json({
      error: 'llm_gateway_failure',
      detail: err.message
    });
  }
}
