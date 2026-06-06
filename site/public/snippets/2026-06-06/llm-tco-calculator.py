#!/usr/bin/env python3
"""
LLM Total-Cost-of-Ownership calculator — API (pay-as-you-go) vs self-host (fixed).
Helps a Thai SME decide whether self-hosting an open-weight model (Typhoon/Llama)
actually beats calling Claude/GPT/Gemini at THEIR real chat volume.

Honest model: self-host has a fixed monthly floor you pay even at 0 traffic
(amortized GPU + power + ops). API scales to zero. Break-even = where the two cross.

Usage:
    python3 llm-tco-calculator.py --conversations 6000 --api-thb-per-conv 1.0 \
        --selfhost-fixed-thb 4000
"""
import argparse


def monthly_api_cost(conversations: int, thb_per_conv: float) -> float:
    return conversations * thb_per_conv


def monthly_selfhost_cost(fixed_thb: float, conversations: int,
                          marginal_thb_per_conv: float = 0.0) -> float:
    # Self-host marginal cost ~ electricity only; the dominant term is the fixed floor.
    return fixed_thb + conversations * marginal_thb_per_conv


def break_even_conversations(fixed_thb: float, api_thb_per_conv: float,
                             selfhost_marginal: float = 0.0):
    delta = api_thb_per_conv - selfhost_marginal
    if delta <= 0:
        return None  # API per-conv cheaper than even self-host electricity -> never breaks even
    return fixed_thb / delta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conversations", type=int, required=True,
                    help="conversations per month")
    ap.add_argument("--api-thb-per-conv", type=float, default=1.0,
                    help="API cost per conversation in THB (see token-cost article)")
    ap.add_argument("--selfhost-fixed-thb", type=float, default=4000.0,
                    help="amortized GPU + power + ops floor per month, THB")
    ap.add_argument("--selfhost-marginal-thb", type=float, default=0.02,
                    help="electricity per conversation on self-host, THB")
    a = ap.parse_args()

    api = monthly_api_cost(a.conversations, a.api_thb_per_conv)
    sh = monthly_selfhost_cost(a.selfhost_fixed_thb, a.conversations,
                               a.selfhost_marginal_thb)
    be = break_even_conversations(a.selfhost_fixed_thb, a.api_thb_per_conv,
                                  a.selfhost_marginal_thb)

    print(f"Conversations/month : {a.conversations:,}")
    print(f"API monthly cost     : {api:,.0f} THB")
    print(f"Self-host monthly    : {sh:,.0f} THB (fixed {a.selfhost_fixed_thb:,.0f} + usage)")
    print("-" * 44)
    if be is None:
        print("Break-even: never — API per-conversation is cheaper than self-host "
              "electricity. Stay on API.")
    else:
        print(f"Break-even at        : {be:,.0f} conversations/month")
        verdict = "SELF-HOST may win" if a.conversations > be else "API WINS"
        print(f"At your volume       : {verdict}")
    print("\nNote: estimates only. Add ops risk + idle cost before committing to GPU.")


if __name__ == "__main__":
    main()
