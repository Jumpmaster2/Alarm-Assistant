"""Alarm code: salted hash, check and format.

New codes are stored as ``pbkdf2_sha256$<iterations>$<salt>$<hash>``. Codes of
version 0.4 and older are a plain SHA-256 hex digest; they are still accepted
and replaced by the new format after the next correct entry.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

PREFIX = "pbkdf2_sha256"
ITERATIONS = 100_000
MIN_DIGITS = 4
MAX_DIGITS = 10


def valid_code(code: str) -> bool:
    """A new code has 4 to 10 digits (the panel shows a number pad)."""
    return code.isdigit() and MIN_DIGITS <= len(code) <= MAX_DIGITS


def hash_code(code: str, salt: str | None = None, iterations: int = ITERATIONS) -> str:
    """Salted hash of the code (CPU bound: run it in the executor)."""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", code.encode(), bytes.fromhex(salt), iterations)
    return f"{PREFIX}${iterations}${salt}${digest.hex()}"


def legacy_hash(code: str) -> str:
    """Hash of version 0.4 and older (unsalted SHA-256)."""
    return hashlib.sha256(code.encode()).hexdigest()


def is_legacy(stored: str) -> bool:
    return not stored.startswith(f"{PREFIX}$")


def verify_code(code: str, stored: str) -> bool:
    """True if ``code`` matches the stored hash (both formats)."""
    if is_legacy(stored):
        return hmac.compare_digest(legacy_hash(code), stored)
    try:
        _, iterations, salt, _digest = stored.split("$")
        expected = hash_code(code, salt, int(iterations))
    except ValueError:
        return False
    return hmac.compare_digest(expected, stored)
