"""token-refresh.py — auto-refresh an OAuth access token (Shopee/Lazada-style)
BEFORE it expires, so the chatbot never goes silent at 3am on a dead token.
Refreshes when <10% of lifetime (or <60s) remains."""
import time, threading, requests


class TokenStore:
    def __init__(self, refresh_url, client_id, client_secret, refresh_token, skew=0.10):
        self.url, self.cid, self.secret = refresh_url, client_id, client_secret
        self.refresh_token = refresh_token
        self.skew = skew                 # refresh when this fraction of life remains
        self.access_token = None
        self.expires_at = 0.0
        self.lifetime = 0.0
        self._lock = threading.Lock()

    def _refresh(self):
        r = requests.post(self.url, data={
            "grant_type": "refresh_token",
            "client_id": self.cid,
            "client_secret": self.secret,
            "refresh_token": self.refresh_token,
        }, timeout=15)
        r.raise_for_status()
        j = r.json()
        self.access_token = j["access_token"]
        self.refresh_token = j.get("refresh_token", self.refresh_token)
        self.lifetime = float(j["expires_in"])
        self.expires_at = time.time() + self.lifetime

    def get(self):
        with self._lock:
            life_left = self.expires_at - time.time()
            if (not self.access_token) or life_left < max(60.0, self.skew * self.lifetime):
                self._refresh()
            return self.access_token
