"""audit-logger.py — KORP AI (Layer 7)
Append-only conversation log for traceability + PDPA ม.30 record-of-processing.
PII (phone/email/Thai national ID) is hashed, not stored raw. Each row chains to
the previous hash so tampering is detectable. MIT licensed.
"""
import hashlib, hmac, json, os, re, time

SECRET = os.environ.get("KORPAI_LOG_HMAC", "change-me").encode()
PII = [
    (re.compile(r"\b0\d{8,9}\b"), "<phone>"),
    (re.compile(r"\b[\w.\-]+@[\w.\-]+\.\w+\b"), "<email>"),
    (re.compile(r"\b\d{13}\b"), "<th_id>"),
]

def _redact(text: str) -> str:
    for rx, tag in PII:
        text = rx.sub(tag, text)
    return text

def _sig(payload: str) -> str:
    return hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()[:32]

class AuditLog:
    def __init__(self, path="audit.ndjson"):
        self.path = path
        self.prev = self._last_hash()

    def _last_hash(self):
        if not os.path.exists(self.path):
            return "genesis"
        last = None
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                last = line
        return json.loads(last)["sig"] if last else "genesis"

    def record(self, user_msg, bot_reply, *, action, reasons=None, grounded=None):
        row = {
            "ts": round(time.time(), 3),
            "user": _redact(user_msg),
            "bot": _redact(bot_reply),
            "action": action,                 # reply | handoff | block
            "reasons": reasons or [],
            "grounded": grounded,
            "prev": self.prev,
        }
        row["sig"] = _sig(self.prev + json.dumps(row, ensure_ascii=False, sort_keys=True))
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        self.prev = row["sig"]
        return row["sig"]

if __name__ == "__main__":
    log = AuditLog("/tmp/korpai_audit.ndjson")
    log.record("สนใจค่ะ โทร 0891234567", "ชาเขียว 35 บาทค่ะ", action="reply", grounded=True)
    print("logged ok, tip hash:", log.prev)
