// pii-output-redactor.js
// Layer 4 — last line of defense BEFORE a reply reaches the customer's screen.
// Catches Thai PII the bot may have accidentally pulled (especially another customer's data).
// Maps to OWASP LLM02:2025 (Sensitive Information Disclosure) + PDPA security measures.

function isThaiId(s) {
  const d = s.replace(/\D/g, '');
  if (d.length !== 13) return false;
  let sum = 0;
  for (let i = 0; i < 12; i++) sum += parseInt(d[i], 10) * (13 - i);
  return (11 - (sum % 11)) % 10 === parseInt(d[12], 10);
}

function luhn(s) {
  const d = s.replace(/\D/g, '');
  if (d.length < 13) return false;
  let sum = 0, alt = false;
  for (let i = d.length - 1; i >= 0; i--) {
    let n = parseInt(d[i], 10);
    if (alt) { n *= 2; if (n > 9) n -= 9; }
    sum += n; alt = !alt;
  }
  return sum % 10 === 0;
}

const RULES = [
  { name: 'thai_id', re: /\b\d[\d -]{11,16}\d\b/g, mask: m => isThaiId(m) ? 'x-xxxx-xxxxx-xx-x' : m },
  { name: 'card',    re: /\b\d[\d -]{11,17}\d\b/g, mask: m => luhn(m) ? '**** **** **** ' + m.replace(/\D/g, '').slice(-4) : m },
  { name: 'phone',   re: /\b0\d{1,2}[- ]?\d{3}[- ]?\d{3,4}\b/g, mask: () => '0xx-xxx-xxxx' },
  { name: 'email',   re: /\b[\w.+-]+@[\w-]+\.[\w.-]+\b/g, mask: m => m.replace(/^(.).*(@.*)$/, '$1***$2') },
];

// Run order matters: ID/card (longest digit runs) first, then phone, then email.
function redact(text) {
  let out = String(text);
  const redacted = [];
  for (const r of RULES) {
    out = out.replace(r.re, m => {
      const masked = r.mask(m);
      if (masked !== m) redacted.push(r.name);
      return masked;
    });
  }
  return { text: out, redacted: [...new Set(redacted)] };
}

module.exports = { redact, isThaiId, luhn };

if (require.main === module) {
  const r = redact('ลูกค้าเบอร์ 081-234-5678 บัตรเครดิต 4111 1111 1111 1111 อีเมล somchai@example.com');
  console.log(r.text);
  console.log('redacted:', r.redacted);
}
