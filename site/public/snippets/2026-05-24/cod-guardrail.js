/**
 * cod-guardrail.js
 * Middleware that blocks COD financial info from leaking via chatbot
 * unless the requester passed verification.
 *
 * Why: many logistics chatbots happily answer "COD ของร้าน X วันนี้เท่าไหร่?"
 * with no auth → financial data leak. This middleware enforces the negative prompt
 * *outside* the LLM (defense-in-depth — LLM can be prompt-injected).
 *
 * Released by KORP AI Automation (https://korpai.co) under MIT.
 * Companion to: https://korpai.co/blog/ai-chatbot-ขนส่ง-โลจิสติกส์-logistics-sme-2026
 */

const VERIFY_WINDOW_MS = 4 * 60 * 60 * 1000; // 4h session
const OTP_WINDOW_MS = 5 * 60 * 1000;          // 5 min OTP validity

// Patterns that count as "asking for COD financial data".
// Tune for your locale; this is Thai + English.
const COD_INTENT_PATTERNS = [
  /ยอด\s*COD/i,
  /COD\s*(วันนี้|วัน\s*ที่|ของ\s*ร้าน|ยอด)/i,
  /\b(cod|cash on delivery)\b.*(total|amount|balance|yesterday|today)/i,
  /รวม.*COD/i,
  /COD.*รวม/i,
];

function looksCodFinancial(text) {
  if (!text) return false;
  return COD_INTENT_PATTERNS.some(p => p.test(text));
}

/**
 * verifyStore — call after merchant provides ID + phone last-4 + OTP.
 * Stores a session entry; later requests within 4h pass automatically
 * from the same device fingerprint.
 */
async function verifyStore({ merchantId, phoneLast4, otpEntered, deviceFp }, store) {
  const expected = await store.getOtp(merchantId);
  if (!expected || expected.code !== otpEntered) return { ok: false, reason: 'otp_mismatch' };
  if (Date.now() - expected.at > OTP_WINDOW_MS)  return { ok: false, reason: 'otp_expired' };
  const reg = await store.getMerchant(merchantId);
  if (!reg)                                       return { ok: false, reason: 'no_merchant' };
  if (!reg.phone.endsWith(phoneLast4))            return { ok: false, reason: 'phone_mismatch' };
  await store.setSession({ merchantId, deviceFp, at: Date.now() });
  await store.clearOtp(merchantId);
  return { ok: true };
}

async function isVerified(merchantId, deviceFp, store) {
  const s = await store.getSession({ merchantId, deviceFp });
  if (!s) return false;
  return Date.now() - s.at < VERIFY_WINDOW_MS;
}

/**
 * codGuardrail — Express/Koa-style middleware factory.
 * Pass it the chat message + sender context; returns either { allow: true }
 * or { allow: false, reply: "..." } that the chatbot must use verbatim.
 */
function makeCodGuardrail(store) {
  return async function ({ message, merchantId, deviceFp }) {
    if (!looksCodFinancial(message)) return { allow: true };
    if (!merchantId || !deviceFp) {
      return {
        allow: false,
        reply: 'ขอ verify ตัวตนก่อนแสดงข้อมูล COD นะคะ '
             + 'กรุณาแจ้งเลขร้านค้า + เบอร์โทรที่ลงทะเบียน เพื่อรับ OTP ค่ะ',
      };
    }
    const ok = await isVerified(merchantId, deviceFp, store);
    if (!ok) {
      return {
        allow: false,
        reply: 'session หมดอายุค่ะ ขอ OTP ใหม่นะคะ '
             + '— กด /verify เพื่อรับรหัสในเบอร์โทรที่ลงทะเบียน',
      };
    }
    return { allow: true };
  };
}

module.exports = { makeCodGuardrail, verifyStore, isVerified, looksCodFinancial };
