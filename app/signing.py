"""HMAC-SHA256 signature verification for OpenAI ACP requests."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time


ALLOWED_SKEW_SECONDS = 300


def verify_openai_signature(api_key: str, body: bytes, signature: str | None, timestamp: str | None) -> bool:
    if not signature or not timestamp:
        return False
    try:
        ts = time.mktime(time.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ"))
    except ValueError:
        return False
    if abs(time.time() - ts) > ALLOWED_SKEW_SECONDS:
        return False
    secret = os.environ.get(f"VEYRA_MERCHANT_SECRET_{api_key}", "")
    if not secret:
        return False
    mac = hmac.new(secret.encode(), body + timestamp.encode(), hashlib.sha256)
    expected = base64.b64encode(mac.digest()).decode()
    return hmac.compare_digest(expected, signature)
