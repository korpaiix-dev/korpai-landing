// Hybrid LLM router: prefer self-hosted local model, fail over to cloud API.
// Pattern for the "start with API, move some traffic to self-host" architecture.
// - Sensitive/PDPA traffic is PINNED to local (never leaves your server).
// - Bulk/simple traffic tries local first (cheap), falls back to API on error/timeout.
// - Hard/complex traffic goes straight to a flagship API model.
// No external deps. Node 18+ (global fetch).

const CONFIG = {
  local:  { url: process.env.LOCAL_LLM_URL  || "http://127.0.0.1:8000/v1/chat/completions",
            model: process.env.LOCAL_MODEL  || "typhoon2", timeoutMs: 6000 },
  cloud:  { url: process.env.CLOUD_LLM_URL  || "https://api.example-llm.com/v1/chat/completions",
            model: process.env.CLOUD_MODEL  || "flagship", key: process.env.CLOUD_API_KEY || "",
            timeoutMs: 20000 },
};

async function callEndpoint(ep, messages, extraHeaders = {}) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), ep.timeoutMs);
  try {
    const res = await fetch(ep.url, {
      method: "POST",
      signal: ctrl.signal,
      headers: { "content-type": "application/json", ...extraHeaders },
      body: JSON.stringify({ model: ep.model, messages, max_tokens: 512 }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.choices?.[0]?.message?.content ?? "";
  } finally {
    clearTimeout(t);
  }
}

// route: 'sensitive' -> local only | 'complex' -> cloud only | else -> local then cloud
export async function route(messages, { sensitive = false, complex = false } = {}) {
  if (sensitive) {
    return { via: "local-pinned", text: await callEndpoint(CONFIG.local, messages) };
  }
  if (complex) {
    return { via: "cloud", text: await callEndpoint(CONFIG.cloud, messages,
      { authorization: `Bearer ${CONFIG.cloud.key}` }) };
  }
  try {
    return { via: "local", text: await callEndpoint(CONFIG.local, messages) };
  } catch (e) {
    return { via: "cloud-fallback", error: String(e),
      text: await callEndpoint(CONFIG.cloud, messages,
        { authorization: `Bearer ${CONFIG.cloud.key}` }) };
  }
}

// demo
if (import.meta.url === `file://${process.argv[1]}`) {
  route([{ role: "user", content: "ราคาคอร์สเท่าไหร่" }])
    .then(r => console.log(r.via, "=>", r.text.slice(0, 80)))
    .catch(err => console.error("both failed:", err));
}
