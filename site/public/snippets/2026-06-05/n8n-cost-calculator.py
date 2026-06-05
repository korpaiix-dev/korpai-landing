#!/usr/bin/env python3
"""KORP AI — เครื่องคิดจุดคุ้มทุน n8n: self-host VPS vs n8n Cloud
ใส่จำนวน execution/เดือน แล้วบอกว่าทางไหนถูกกว่า (ข้อมูลราคา มิ.ย. 2026).
ใช้: python3 n8n-cost-calculator.py 6000
"""
import sys

EUR_THB = 38.0   # อัตราโดยประมาณ มิ.ย. 2026
USD_THB = 35.0

# n8n Cloud (คิดตาม execution/เดือน)
CLOUD = [
    ("Starter",  24 * EUR_THB,  2_500),
    ("Pro",      60 * EUR_THB,  10_000),
    ("Business", 800 * EUR_THB, 40_000),
]
# Self-host VPS 2vCPU/4GB (execution ไม่จำกัด)
VPS_TH       = 400          # VPS ไทย ~บาท/เดือน
VPS_HETZNER  = 9 * USD_THB  # ~315 บาท
MAINT_HOURS  = 1.5          # ชม.ดูแล/เดือน

def best_cloud(execs):
    for name, price, cap in CLOUD:
        if execs <= cap:
            return name, price, cap
    name, price, cap = CLOUD[-1]
    return f"{name}+ (เกินลิมิต ต้องคุย enterprise)", price, cap

def main():
    execs = int(sys.argv[1]) if len(sys.argv) > 1 else 6000
    name, cprice, cap = best_cloud(execs)
    print(f"\nปริมาณ: {execs:,} execution/เดือน (~{execs/30:.0f}/วัน)\n")
    print(f"  n8n Cloud {name:<28} ≈ {cprice:>8,.0f} บาท/เดือน (ลิมิต {cap:,})")
    print(f"  Self-host VPS ไทย (ไม่จำกัด)          ≈ {VPS_TH:>8,.0f} บาท/เดือน + ดูแล ~{MAINT_HOURS} ชม.")
    print(f"  Self-host Hetzner (ไม่จำกัด)           ≈ {VPS_HETZNER:>8,.0f} บาท/เดือน + ดูแล ~{MAINT_HOURS} ชม.")
    saving = cprice - VPS_TH
    print()
    if saving > 0:
        print(f"➡️  Self-host (ไทย) ประหยัดกว่า ~{saving:,.0f} บาท/เดือน "
              f"(~{saving*12:,.0f} บาท/ปี) — คุ้มถ้ารับงานดูแล server ไหว")
    else:
        print("➡️  Volume ยังต่ำ — n8n Cloud คุ้มกว่าในแง่เวลา (ไม่ต้องดูแล server)")
    print("หมายเหตุ: ตัวเลขประมาณการ มิ.ย. 2026 — เช็คราคาจริงจากผู้ให้บริการก่อนตัดสินใจ\n")

if __name__ == "__main__":
    main()
