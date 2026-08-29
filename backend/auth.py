"""Authentication helpers for UCEK-JNTUK CCTV Camera Health Monitoring System.

Default login credentials:
Username: admin
Password: Admin@1234
"""

import base64
import hashlib
import hmac
import json
import os
import sys
import time

from config import JWT_SECRET


def _b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value):
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def _json_response(handler, payload, status=401):
    module = sys.modules.get("app") or sys.modules.get("__main__")
    responder = getattr(module, "json_response", None)
    if responder:
        responder(handler, payload, status)
        return
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def hash_password(plain_text):
    """Hash a plaintext password using PBKDF2-HMAC-SHA256."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", plain_text.encode("utf-8"), salt, 100000)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(plain_text, stored):
    """Verify a plaintext password against a stored salt:hash string."""
    try:
        salt_hex, hash_hex = stored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        actual = hashlib.pbkdf2_hmac("sha256", plain_text.encode("utf-8"), salt, 100000)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def create_token(user_id, username, role, expires_hours=8):
    """Create a compact HMAC-SHA256 signed JWT string."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"user_id": user_id, "username": username, "role": role, "exp": int(time.time() + expires_hours * 3600)}
    encoded_header = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_b64url_encode(signature)}"


def decode_token(token):
    """Decode and validate a JWT string, returning its payload."""
    try:
        header_part, payload_part, signature_part = token.split(".")
    except ValueError as exc:
        raise ValueError("Invalid token format") from exc
    signing_input = f"{header_part}.{payload_part}".encode("ascii")
    expected = _b64url_encode(hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest())
    if not hmac.compare_digest(signature_part, expected):
        raise ValueError("Invalid token signature")
    try:
        payload = json.loads(_b64url_decode(payload_part).decode("utf-8"))
    except Exception as exc:
        raise ValueError("Invalid token payload") from exc
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("Token expired")
    return payload


def require_auth(handler, allowed_roles=None):
    """Validate a Bearer token and optionally enforce role membership."""
    header = handler.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        _json_response(handler, {"error": "Authorization token required"}, 401)
        return None
    try:
        user = decode_token(header.split(" ", 1)[1].strip())
    except ValueError as exc:
        _json_response(handler, {"error": str(exc)}, 401)
        return None
    if allowed_roles and user.get("role") not in allowed_roles:
        _json_response(handler, {"error": "Permission denied"}, 403)
        return None
    return user
