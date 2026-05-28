/**
 * KORP AI — สก./สภาวิศวกร engineer license verifier (Thai contractor chatbot)
 * Checks the Council of Engineers (สก. — สภาวิศวกร) registry before any chatbot
 * accepts a quote signed by an engineer. Prevents accepting work signed by a PE
 * whose ก.ว. / ภ.ว. has expired or been revoked (พรบ. วิศวกร 2542 ม.45).
 *
 * USAGE:
 *   const result = await verifyCoELicense('ก.ว.โยธา-12345');
 *   if (!result.valid) { ... block sign / warn owner ... }
 *
 * NOTE: Replace `COE_REGISTRY_API` with the actual endpoint your integration uses
 *       (either direct from coe.or.th or a curated registry mirror that you maintain).
 */

const COE_REGISTRY_API = process.env.COE_REGISTRY_API ?? 'https://api.example/coe/lookup';
const CACHE = new Map(); // license → { result, expiresAt }
const CACHE_TTL_MS = 24 * 60 * 60 * 1000; // 24h

const LICENSE_RE = /^(ก\.ว\.|ภ\.ว\.|พ\.ว\.|วฒ\.|สย\.)\s?(โยธา|ไฟฟ้า|เครื่องกล|สิ่งแวดล้อม|เคมี|อุตสาหการ|เหมืองแร่)\s?-?\s?(\d{3,7})$/;

export async function verifyCoELicense(rawLicenseId) {
  const license = String(rawLicenseId || '').trim();

  // 1) format check
  if (!LICENSE_RE.test(license)) {
    return { valid: false, code: 'INVALID_FORMAT', message: 'รูปแบบเลขใบประกอบวิชาชีพไม่ถูกต้อง — ตัวอย่าง: ก.ว.โยธา-12345' };
  }

  // 2) cache
  const cached = CACHE.get(license);
  if (cached && cached.expiresAt > Date.now()) return cached.result;

  // 3) registry lookup
  let res;
  try {
    res = await fetch(`${COE_REGISTRY_API}?id=${encodeURIComponent(license)}`, {
      headers: { 'accept': 'application/json' },
      signal: AbortSignal.timeout(5000),
    });
  } catch (e) {
    return { valid: false, code: 'LOOKUP_FAILED', message: 'ไม่สามารถตรวจสอบกับสภาวิศวกรได้ในตอนนี้ — กรุณาให้ทีมงานยืนยันด้วยใบสำเนา' };
  }
  if (!res.ok) {
    return { valid: false, code: 'REGISTRY_ERROR', message: `Registry HTTP ${res.status}` };
  }

  const data = await res.json();
  const now = new Date();
  const expires = data.expires_at ? new Date(data.expires_at) : null;
  const expired = expires && expires < now;
  const complaints3y = (data.complaints || []).filter(c => new Date(c.date) > new Date(Date.now() - 3 * 365 * 86400_000)).length;

  const result = {
    valid: !expired && data.status === 'active',
    code: !expired && data.status === 'active' ? 'OK' : (expired ? 'EXPIRED' : 'NOT_ACTIVE'),
    name: data.name,
    branch: data.branch,          // โยธา / ไฟฟ้า / เครื่องกล …
    issued_at: data.issued_at,
    expires_at: data.expires_at,
    complaints_last_3y: complaints3y,
    warning: complaints3y > 2 ? 'มี complaint สาธารณะ > 2 ครั้งใน 3 ปี — แนะนำ owner ทบทวนก่อนเซ็น' : null,
    raw: data,
  };

  CACHE.set(license, { result, expiresAt: Date.now() + CACHE_TTL_MS });
  return result;
}

// CLI smoke test
if (import.meta.url === `file://${process.argv[1]}`) {
  verifyCoELicense(process.argv[2] || 'ก.ว.โยธา-12345').then(r => console.log(JSON.stringify(r, null, 2)));
}
