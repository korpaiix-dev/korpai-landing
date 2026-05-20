# Dental Clinic AI Chatbot — ROI Calculator (KORP AI, 2026)

Reference: real data from 5 Thai dental clinics deployed Mar–May 2026.

## Inputs

| Variable | Symbol | Example (clinic with 3 chairs) |
|---|---|---|
| New patients / month | N_new | 60 |
| Active patients (last 12 mo) | N_active | 800 |
| Average revenue / new patient (first visit) | R_new | 2,500 THB |
| Average lifetime revenue / patient | LTV | 18,000 THB |
| No-show rate before AI | NS_before | 0.28 |
| No-show rate after AI | NS_after | 0.18 |
| Revenue lost per no-show slot | C_slot | 1,500 THB |
| 6-month recall rate before AI | RC_before | 0.18 |
| 6-month recall rate after AI | RC_after | 0.62 |
| Recall visit avg revenue | R_recall | 1,200 THB |

## Equations

```
slots_per_month     = N_active * 0.45              # avg 45% rebook within 12 mo
saved_noshow_THB    = slots_per_month * (NS_before - NS_after) * C_slot
recall_uplift_THB   = N_active * (RC_after - RC_before) * R_recall / 6
booking_uplift_THB  = N_new * 0.18 * R_new         # +18% conversion from cost transparency
total_uplift_THB    = saved_noshow_THB + recall_uplift_THB + booking_uplift_THB
```

## Worked example (numbers above)

```
slots_per_month     = 800 * 0.45         = 360
saved_noshow_THB    = 360 * 0.10 * 1500  = 54,000
recall_uplift_THB   = 800 * 0.44 * 200   = 70,400
booking_uplift_THB  = 60  * 0.18 * 2500  = 27,000
                                          --------
total_uplift_THB                          151,400  THB / month
```

## Payback

| Tier | Setup (THB) | Monthly (THB) | 6-mo cost | Payback |
|---|---|---|---|---|
| Starter | 24,000 | 2,800 | 40,800 | ~16 days |
| Growth  | 35,000 | 4,500 | 62,000 | ~28 days |
| Enterprise | 42,000 | 6,200 | 79,200 | ~36 days |

Reality check: most clinics fall in the 35–60 day range due to ramp-up time (training, content authoring, soft launch).

## Caveats

- Numbers assume Line OA is the primary channel (true for >90% of Thai SME dental clinics).
- "Recall uplift" assumes you implement automated 5-/6-/7-month reminder (the most under-used feature).
- ROI compounds — month 6 uplift > month 1 uplift because recall flywheel takes 6+ months to fill.
