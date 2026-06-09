#!/usr/bin/env python3
"""
judge_calibration.py — prove your LLM judge agrees with humans BEFORE you trust it.
Feed a CSV of human-labeled scores + the judge's scores; get the agreement rate.
Rule of thumb (2026): >= 0.75 agreement within tolerance -> ready to scale the judge;
below that -> fix your rubric before relying on it. (c) KORP AI 2026 MIT

CSV columns: id, human_score, judge_score   (scores in 0..1)
"""
import csv, sys

def calibrate(path: str, tol: float = 0.2, threshold: float = 0.75):
    pairs = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            pairs.append((r["id"], float(r["human_score"]), float(r["judge_score"])))
    if not pairs:
        print("no rows"); return
    agree = [pid for pid, h, j in pairs if abs(h - j) <= tol]
    disagree = [(pid, h, j) for pid, h, j in pairs if abs(h - j) > tol]
    rate = len(agree) / len(pairs)
    bias = sum(j - h for _, h, j in pairs) / len(pairs)  # +ve = judge too lenient
    print(f"agreement (|h-j|<={tol}): {rate:.0%}  on n={len(pairs)}")
    print(f"mean bias (judge - human): {bias:+.3f}  ({'judge too lenient' if bias>0 else 'judge too strict'})")
    print("VERDICT:", "READY — scale the judge" if rate >= threshold
          else "NOT READY — revise rubric / lower judge temperature")
    if disagree:
        print("worst disagreements:", sorted(disagree, key=lambda x: -abs(x[1]-x[2]))[:5])
    return rate

if __name__ == "__main__":
    calibrate(sys.argv[1] if len(sys.argv) > 1 else "calibration.csv")
