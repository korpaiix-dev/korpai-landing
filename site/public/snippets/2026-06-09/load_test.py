#!/usr/bin/env python3
"""
load_test.py — concurrency / stress harness for a chatbot HTTP endpoint.
Under load, LLMs degrade: shorter answers, dropped context, more hallucination.
This fires N concurrent requests, reports p50/p95 latency + error rate, and FLAGS
answers that shrank vs a low-load baseline (a degradation smell). stdlib only.
Usage: python3 load_test.py https://your-bot/endpoint 50    (c) KORP AI 2026 MIT
"""
import sys, json, time, statistics, urllib.request
from concurrent.futures import ThreadPoolExecutor

PROMPT = "ร้านเปิดกี่โมง มีที่จอดรถไหม และมีโปรโมชันอะไรบ้างตอนนี้"

def hit(url):
    body = json.dumps({"message": PROMPT}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            txt = r.read().decode("utf-8", "replace")
        return {"ok": True, "latency": time.time() - t0, "len": len(txt)}
    except Exception as e:
        return {"ok": False, "latency": time.time() - t0, "len": 0, "err": str(e)}

def run(url, n=50, baseline_len=None):
    with ThreadPoolExecutor(max_workers=n) as ex:
        res = list(ex.map(lambda _: hit(url), range(n)))
    lat = sorted(r["latency"] for r in res)
    ok = [r for r in res if r["ok"]]
    err_rate = 1 - len(ok) / n
    p50 = statistics.median(lat)
    p95 = lat[int(0.95 * (len(lat) - 1))]
    avg_len = statistics.mean([r["len"] for r in ok]) if ok else 0
    print(f"n={n}  err_rate={err_rate:.0%}  p50={p50:.2f}s  p95={p95:.2f}s  avg_len={avg_len:.0f}")
    if baseline_len and avg_len < 0.6 * baseline_len:
        print("WARN: responses ~40% shorter under load -> possible degradation/truncation")
    print("VERDICT:", "OK" if err_rate <= 0.02 and p95 <= 8 else "INVESTIGATE before peak season")
    return res

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/chat"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    run(url, n)
