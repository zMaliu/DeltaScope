import base64
import hashlib
import hmac
import json
import time
from typing import Dict, Optional

from app.config import TOKEN_CONFIG


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64_decode(data: str) -> bytes:
    pad = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode((data + pad).encode("utf-8"))


def create_token(payload: Dict, expires_in: Optional[int] = None) -> str:
    ttl = TOKEN_CONFIG["expires_in"] if expires_in is None else int(expires_in)
    if ttl <= 0:
        raise ValueError("Token expiry must be positive")
    body = {**payload, "exp": int(time.time()) + int(ttl)}
    body_raw = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    body_b64 = _b64_encode(body_raw)
    sign = hmac.new(
        TOKEN_CONFIG["secret"].encode("utf-8"),
        body_b64.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return body_b64 + "." + sign


def verify_token(token: str) -> Optional[Dict]:
    if not token or "." not in token:
        return None
    body_b64, sign = token.split(".", 1)
    expect = hmac.new(
        TOKEN_CONFIG["secret"].encode("utf-8"),
        body_b64.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(sign, expect):
        return None
    try:
        payload = json.loads(_b64_decode(body_b64).decode("utf-8"))
        if not isinstance(payload, dict):
            return None
        expires_at = int(payload.get("exp", 0))
    except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if expires_at <= int(time.time()):
        return None
    return payload
