"""
Car loan affordability calculator — Thailand 2026.
Used in KORP AI dealer chatbot to pre-screen customers BEFORE calling
the bank sandbox APIs (which are rate-limited per dealer partner).

Bank rule of thumb for car loan approval (used cars):
  - DSR (Debt Service Ratio) <= 45% of monthly income
  - Monthly installment <= 35% of income for owner-driven
  - Min income 15,000 THB/month
  - Loan term: 12 / 24 / 36 / 48 / 60 / 72 months
  - Used car interest rate range 2026: 3.5% - 8% effective
"""
from dataclasses import dataclass


@dataclass
class LoanPlan:
    months: int
    monthly_pay: float
    total_interest: float
    dsr: float
    pre_qual: bool


def car_loan_quote(
    car_price: float,
    down_payment: float,
    monthly_income: float,
    existing_debt_monthly: float = 0,
    eff_rate_annual: float = 0.0485,  # 4.85% — KBank used car typical 2026
    terms_months=(36, 48, 60, 72),
) -> list[LoanPlan]:
    principal = car_price - down_payment
    if principal <= 0:
        return []

    monthly_rate = eff_rate_annual / 12
    plans: list[LoanPlan] = []
    for n in terms_months:
        # Amortized monthly payment
        if monthly_rate > 0:
            m = principal * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
        else:
            m = principal / n
        total_interest = m * n - principal
        dsr = (m + existing_debt_monthly) / max(monthly_income, 1)
        plans.append(LoanPlan(
            months=n,
            monthly_pay=round(m, 0),
            total_interest=round(total_interest, 0),
            dsr=round(dsr, 3),
            pre_qual=dsr <= 0.45 and monthly_income >= 15_000,
        ))
    return plans


def best_plan(plans: list[LoanPlan]) -> LoanPlan | None:
    eligible = [p for p in plans if p.pre_qual]
    if not eligible:
        return None
    # Prefer shortest term that keeps DSR < 40%
    eligible.sort(key=lambda p: (p.dsr > 0.40, p.months))
    return eligible[0]


if __name__ == "__main__":
    plans = car_loan_quote(
        car_price=685_000,
        down_payment=100_000,
        monthly_income=42_000,
        existing_debt_monthly=4_500,
    )
    for p in plans:
        flag = "✓" if p.pre_qual else "✗"
        print(f"{flag} {p.months}m  pay={p.monthly_pay:>8.0f}/mo  DSR={p.dsr:.0%}  interest={p.total_interest:,.0f}")
    print("→ best:", best_plan(plans))
