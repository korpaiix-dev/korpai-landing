"""pdpa-access-log.py — append-only, hash-chained audit log for every read of
customer personal data (supports PDPA มาตรา 30 record-keeping). One JSON line per
access; each entry hashes the previous one so tampering is detectable."""
import json, time, hashlib, io


class PdpaAuditLog:
    def __init__(self, path):
        self.path = path
        self.prev = self._last_hash()

    def _last_hash(self):
        try:
            last = None
            for line in io.open(self.path, encoding="utf-8"):
                line = line.strip()
                if line:
                    last = line
            return json.loads(last)["hash"] if last else "GENESIS"
        except FileNotFoundError:
            return "GENESIS"

    def record(self, actor, subject_id, purpose, fields):
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "actor": actor,            # e.g. "chatbot:line"
            "subject": subject_id,     # customer id (pseudonymous where possible)
            "purpose": purpose,        # why the data was accessed
            "fields": fields,          # which PII fields were read
            "prev": self.prev,
        }
        payload = json.dumps(entry, ensure_ascii=False, sort_keys=True)
        entry["hash"] = hashlib.sha256((self.prev + payload).encode("utf-8")).hexdigest()
        with io.open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self.prev = entry["hash"]
        return entry["hash"]
