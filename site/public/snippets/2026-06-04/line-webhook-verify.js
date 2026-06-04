// line-webhook-verify.js — verify LINE webhook signature before trusting events.
// Why: the X-Line-Signature header proves a request really came from LINE, not a
// forger. Always verify BEFORE parsing/acting on webhook events. Node 18+.
import crypto from 'node:crypto';

export function verifyLineSignature(channelSecret, rawBody, signatureHeader) {
  // rawBody MUST be the exact raw bytes/string of the request body — not a
  // re-serialized JSON object, or the HMAC will not match.
  const expected = crypto.createHmac('sha256', channelSecret).update(rawBody).digest('base64');
  const a = Buffer.from(expected);
  const b = Buffer.from(signatureHeader || '');
  // constant-time compare to avoid leaking info via timing
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

// Express usage — note express.raw so we keep the raw body:
//   app.post('/line/webhook', express.raw({ type: '*/*' }), (req, res) => {
//     const ok = verifyLineSignature(process.env.LINE_CHANNEL_SECRET, req.body, req.get('x-line-signature'));
//     if (!ok) return res.sendStatus(401);
//     res.sendStatus(200);                 // ACK fast...
//     enqueue(JSON.parse(req.body));       // ...then process events asynchronously
//   });
