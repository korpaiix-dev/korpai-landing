#!/usr/bin/env python3
"""qdrant_upsert_kb.py — push kb.jsonl into a Qdrant collection (idempotent re-runs).

- Embeddings via any OpenAI-compatible /v1/embeddings endpoint (set EMBED_API_BASE,
  EMBED_API_KEY, EMBED_MODEL). Works with OpenAI, Voyage (compat mode), LiteLLM proxy, Ollama.
- Point IDs = UUID5 of doc id → re-running updates instead of duplicating.
- Payload keeps category/updated_at/expires_at so you can filter stale promos at query time.

Usage: QDRANT_URL=http://localhost:6333 EMBED_API_BASE=https://api.openai.com/v1 \
       EMBED_API_KEY=sk-... EMBED_MODEL=text-embedding-3-small \
       python3 qdrant_upsert_kb.py kb.jsonl my_shop_kb
Requires: pip install requests
Companion to: https://korpai.co/blog/knowledge-base-ai-chatbot-เตรียมข้อมูล-sme-ไทย-2026
MIT license — KORP AI (korpai.co)
"""
import json, os, sys, uuid
import requests

QDRANT = os.environ.get("QDRANT_URL", "http://localhost:6333")
BASE = os.environ["EMBED_API_BASE"].rstrip("/")
KEY = os.environ.get("EMBED_API_KEY", "")
MODEL = os.environ.get("EMBED_MODEL", "text-embedding-3-small")
BATCH = 64

def embed(texts):
    r = requests.post(f"{BASE}/embeddings",
                      headers={"Authorization": f"Bearer {KEY}"},
                      json={"model": MODEL, "input": texts}, timeout=60)
    r.raise_for_status()
    return [d["embedding"] for d in r.json()["data"]]

def ensure_collection(name, dim):
    r = requests.get(f"{QDRANT}/collections/{name}", timeout=10)
    if r.status_code == 200: return
    requests.put(f"{QDRANT}/collections/{name}",
                 json={"vectors": {"size": dim, "distance": "Cosine"}}, timeout=30).raise_for_status()

def main(jsonl_path, collection):
    docs = [json.loads(l) for l in open(jsonl_path, encoding="utf-8") if l.strip()]
    print(f"{len(docs)} docs → collection '{collection}'")
    dim = None
    for i in range(0, len(docs), BATCH):
        batch = docs[i:i + BATCH]
        vecs = embed([d["text"] for d in batch])
        dim = dim or len(vecs[0])
        if i == 0: ensure_collection(collection, dim)
        points = [{
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"kb/{d['id']}")),
            "vector": v,
            "payload": {"text": d["text"], **d.get("metadata", {})},
        } for d, v in zip(batch, vecs)]
        requests.put(f"{QDRANT}/collections/{collection}/points?wait=true",
                     json={"points": points}, timeout=60).raise_for_status()
        print(f"  upserted {i + len(batch)}/{len(docs)}")
    print("[done] tip: filter expires_at < today OUT at query time — or better, run kb_freshness_audit.py monthly")

if __name__ == "__main__":
    if len(sys.argv) != 3: sys.exit("usage: qdrant_upsert_kb.py kb.jsonl collection_name")
    main(sys.argv[1], sys.argv[2])
