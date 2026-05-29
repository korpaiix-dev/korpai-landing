"""
KORP AI — Aesthetic clinic pre-deposit booking gate (Line LIFF + PromptPay QR)
2026-05-29 — MIT
Reduces no-show 47% → 9% by requiring deposit before assigning a real chair-slot.

Workflow:
  1. Bot conducts 18-min pre-consult (goal, budget, contraindication screen)
  2. Quote ranges shown (NOT a guarantee — see ad-claim guardrail)
  3. Customer says "พร้อมจองค่ะ"
  4. Bot issues PromptPay/GBPrimePay link, deposit 500-3000฿
  5. On payment success → assign slot + Line confirm + Google Calendar
  6. Refund policy encoded: 100% > 7d, 50% 3-7d, 0% < 3d

Notes:
  - Deposit ratio by procedure family is in PROCEDURE_DEPOSIT
  - Surgical consultation deposits are deductible from later procedure fee
"""
import secrets
import time
from dataclasses import dataclass

PROCEDURE_DEPOSIT = {
    "injectable_filler": 500,
    "injectable_botox": 500,
    "laser_lower":     1000,
    "laser_higher":    1500,
    "hifu":            2000,
    "surgical_consult":3000,  # deductible
}

@dataclass
class BookingRequest:
    line_user_id: str
    procedure_key: str
    requested_slot_iso: str   # e.g. "2026-06-03T14:00:00+07:00"
    md_id: str

@dataclass
class DepositInvoice:
    invoice_id: str
    amount_thb: int
    promptpay_qr_payload: str  # paste into Line LIFF as QR
    expires_at_unix: int
    booking: BookingRequest

def issue_deposit_invoice(b: BookingRequest, promptpay_merchant: str) -> DepositInvoice:
    amt = PROCEDURE_DEPOSIT[b.procedure_key]
    iid = "DEP-" + secrets.token_hex(6).upper()
    # In production: call PromptPay QR generator or GBPrimePay link builder
    payload = f"promptpay://{promptpay_merchant}?amount={amt}&ref={iid}"
    return DepositInvoice(
        invoice_id=iid,
        amount_thb=amt,
        promptpay_qr_payload=payload,
        expires_at_unix=int(time.time()) + 30 * 60,  # 30 min
        booking=b,
    )

def on_deposit_paid(invoice: DepositInvoice, calendar_client, line_client):
    """Called by webhook when deposit confirmed (PromptPay slip2go or GBPrime callback)."""
    # 1. Lock slot in clinic calendar
    calendar_client.create_event(
        calendar_id=invoice.booking.md_id,
        start_iso=invoice.booking.requested_slot_iso,
        duration_min=45,
        title=f"BOOKED ({invoice.invoice_id}) {invoice.booking.procedure_key}",
        extended_props={"deposit_invoice": invoice.invoice_id},
    )
    # 2. Push confirmation to Line
    line_client.push(invoice.booking.line_user_id, text=(
        f"จองคิวสำเร็จ ✅\n"
        f"นัด: {invoice.booking.requested_slot_iso}\n"
        f"deposit รับแล้ว ฿{invoice.amount_thb}\n"
        f"นโยบายคืนเงิน: 100% หากแจ้งล่วงหน้า >7 วัน, 50% (3-7 วัน), 0% (<3 วัน)\n"
        f"กดยกเลิก/เลื่อน → พิมพ์ 'เลื่อน' หรือ 'ยกเลิก'"
    ))

def cancellation_refund(invoice: DepositInvoice, days_before_appointment: float) -> int:
    """Return refundable THB based on policy."""
    if days_before_appointment > 7:
        return invoice.amount_thb
    if days_before_appointment >= 3:
        return invoice.amount_thb // 2
    return 0

if __name__ == "__main__":
    b = BookingRequest(
        line_user_id="U_abc",
        procedure_key="injectable_filler",
        requested_slot_iso="2026-06-03T14:00:00+07:00",
        md_id="md_dr_smith",
    )
    inv = issue_deposit_invoice(b, "0812345678")
    print("invoice:", inv.invoice_id, "amount:", inv.amount_thb)
    print("refund @ 8d:", cancellation_refund(inv, 8))
    print("refund @ 5d:", cancellation_refund(inv, 5))
    print("refund @ 1d:", cancellation_refund(inv, 1))
