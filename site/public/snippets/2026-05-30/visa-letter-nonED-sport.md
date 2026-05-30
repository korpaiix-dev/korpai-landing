# Non-ED (Sport) Visa Support Letter — Generator Template

Used by KORP AI Muay Thai gym chatbots to auto-generate visa invitation letters
for foreign fighters training 4+ weeks. Letter is built from chatbot intake +
gym registration, then emailed/Line-filed to the customer.

Letter requires: gym Tax ID, owner's Thai ID, sport-promotion license number
(กกท. / กกพ.), foreign student's passport details, training start/end dates,
emergency contact, and a brief training-plan paragraph.

---

```jinja
{{ gym_name }}
{{ gym_address }}
ใบอนุญาตกีฬา: {{ sport_license_no }}
เลขประจำตัวผู้เสียภาษี: {{ tax_id }}

วันที่ {{ date_thai }}

To: The Royal Thai Embassy / Consulate, {{ embassy_country }}
Re: Sport-related Long-Stay Visa (Non-Immigrant ED) — supporting letter for
    {{ student_full_name }} (Passport {{ passport_no }})

Dear Consular Officer,

We confirm that {{ student_full_name }}, holder of {{ nationality }} passport
{{ passport_no }} (issued {{ passport_issue }}, expires {{ passport_expiry }}),
has been accepted into our authorized Muay Thai training program at
{{ gym_name }}, located at {{ gym_address }}, Thailand.

Program duration:  {{ training_start }} to {{ training_end }} ({{ weeks }} weeks)
Training intensity: {{ sessions_per_week }} sessions/week, {{ hours_per_session }}
                    hours/session, supervised by certified trainers.
Total fee paid: THB {{ fee_thb }} (received {{ receipt_no }}, {{ receipt_date }}).

We respectfully request a Non-Immigrant ED (sport) entry visa appropriate to the
above training period. Accommodation arrangements: {{ accommodation }}.
Medical clearance and waiver are on file (ref. {{ waiver_id }}).

Sincerely,

{{ owner_name }}
{{ owner_title }}
Contact: {{ owner_phone }}  |  Email: {{ owner_email }}

[Stamp + signature]
```

## Variable mapping (from chatbot intake)

| Template var          | Source                                      |
|-----------------------|---------------------------------------------|
| student_full_name     | Intake form Q3 (passport-spelling required) |
| passport_no           | OCR from uploaded passport photo            |
| nationality           | OCR + customer confirm                      |
| training_start/end    | Booking calendar                            |
| sessions_per_week     | Package selection                           |
| fee_thb               | Payment record (Omise/Stripe webhook)       |
| receipt_no            | E-Tax invoice system                        |
| waiver_id             | e-waiver signature payload (see snippet 3)  |
| accommodation         | Bundle selection (gym dorm / partner hotel) |

## Compliance notes

- Owner must sign physically — DocuSign mobile signature acceptable in practice
  but consulates increasingly prefer wet signature for Non-ED sport.
- Gym must hold a current sport-promotion license (กกท. / กกพ.) — letter must
  reference license number on letterhead.
- Keep PDF + audit log of letter issuance for 5 years (Thai tax law).
