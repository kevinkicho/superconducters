"""Authentication dependencies for the HTTP surface."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from collections import deque
from threading import Lock

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class LoginRateLimiter:
    def __init__(
        self,
        *,
        attempts: int = 5,
        window_seconds: int = 60,
        max_identities: int = 10_000,
    ):
        self.attempts = attempts
        self.window_seconds = window_seconds
        self.max_identities = max_identities
        self._attempts: dict[str, deque[float]] = {}
        self._lock = Lock()

    def is_blocked(self, identity: str) -> bool:
        now = time.monotonic()
        with self._lock:
            values = self._attempts.get(identity)
            if values is None:
                return False
            self._discard_expired(values, now)
            return len(values) >= self.attempts

    def record_failure(self, identity: str) -> None:
        now = time.monotonic()
        with self._lock:
            if identity not in self._attempts and len(self._attempts) >= self.max_identities:
                self._attempts.pop(next(iter(self._attempts)))
            values = self._attempts.setdefault(identity, deque())
            self._discard_expired(values, now)
            values.append(now)

    def reset(self, identity: str) -> None:
        with self._lock:
            self._attempts.pop(identity, None)

    def _discard_expired(self, values: deque[float], now: float) -> None:
        while values and now - values[0] >= self.window_seconds:
            values.popleft()


def require_api_key(request: Request, provided: str | None = Depends(api_key_header)) -> str:
    expected = request.app.state.settings.api_key
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication is not configured",
        )
    if provided is None or not (
        secrets.compare_digest(provided, expected) or verify_access_token(provided, expected)
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return provided


def issue_access_token(secret: str, *, lifetime_seconds: int = 3600) -> str:
    payload = json.dumps(
        {"role": "admin", "exp": int(time.time()) + lifetime_seconds},
        separators=(",", ":"),
    ).encode()
    encoded = base64.urlsafe_b64encode(payload).rstrip(b"=")
    signature = hmac.new(secret.encode(), encoded, hashlib.sha256).digest()
    return f"{encoded.decode()}.{base64.urlsafe_b64encode(signature).rstrip(b'=').decode()}"


def verify_access_token(token: str, secret: str) -> bool:
    try:
        encoded, supplied_signature = token.split(".", 1)
        expected = hmac.new(secret.encode(), encoded.encode(), hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(
            supplied_signature + "=" * (-len(supplied_signature) % 4)
        )
        if not hmac.compare_digest(supplied, expected):
            return False
        payload = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        return int(json.loads(payload)["exp"]) > int(time.time())
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False
