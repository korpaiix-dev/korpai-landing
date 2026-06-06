#!/usr/bin/env python3
"""
vLLM concurrency / VRAM sizing helper for self-hosting an open-weight chatbot model.
Answers: "Given my peak chats-per-minute, how many concurrent requests must the
server hold, and is my GPU VRAM enough?" Rough planning math — load-test before prod.
"""
import argparse

# very rough VRAM rule-of-thumb (GB) for weights at common quantizations
WEIGHT_GB = {  # (params_billion, quant) -> GB
    (7, "fp16"): 14, (7, "int8"): 8, (7, "int4"): 5,
    (14, "fp16"): 28, (14, "int8"): 15, (14, "int4"): 9,
    (70, "fp16"): 140, (70, "int8"): 75, (70, "int4"): 40,
}


def little_law_concurrency(peak_per_min: float, avg_seconds: float) -> float:
    # L = lambda * W  (requests in system = arrival rate * service time)
    arrivals_per_sec = peak_per_min / 60.0
    return arrivals_per_sec * avg_seconds


def kv_cache_gb(concurrency: float, ctx_tokens: int, params_b: int) -> float:
    # crude KV-cache estimate: ~ a few hundred KB per token scaled by model size
    per_token_mb = 0.20 * (params_b / 7.0)
    return concurrency * ctx_tokens * per_token_mb / 1024.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--peak-per-min", type=float, default=120)
    ap.add_argument("--avg-seconds", type=float, default=4.0,
                    help="avg end-to-end generation time per request")
    ap.add_argument("--params-b", type=int, default=7, choices=[7, 14, 70])
    ap.add_argument("--quant", default="int8", choices=["fp16", "int8", "int4"])
    ap.add_argument("--ctx-tokens", type=int, default=2048)
    ap.add_argument("--gpu-vram-gb", type=float, default=24)
    a = ap.parse_args()

    conc = little_law_concurrency(a.peak_per_min, a.avg_seconds)
    weights = WEIGHT_GB.get((a.params_b, a.quant), 0)
    kv = kv_cache_gb(conc, a.ctx_tokens, a.params_b)
    total = weights + kv
    headroom = a.gpu_vram_gb - total

    print(f"Peak load            : {a.peak_per_min:.0f}/min, {a.avg_seconds:.1f}s each")
    print(f"Required concurrency : {conc:.1f} in-flight requests (Little's Law)")
    print(f"Model {a.params_b}B {a.quant:5} : ~{weights} GB weights")
    print(f"KV cache (est)       : ~{kv:.1f} GB at ctx={a.ctx_tokens}")
    print(f"Total VRAM (est)     : ~{total:.1f} GB / available {a.gpu_vram_gb:.0f} GB")
    print("-" * 44)
    if headroom < 0:
        print(f"INSUFFICIENT: short ~{-headroom:.1f} GB. Use smaller/quantized model, "
              "lower ctx, or add GPU / use API for peaks.")
    else:
        print(f"FITS with ~{headroom:.1f} GB headroom. Still load-test before prod.")


if __name__ == "__main__":
    main()
