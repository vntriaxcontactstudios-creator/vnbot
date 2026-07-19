"""VNBOT API — Crypto helpers for export/import encryption.

Per docs/08 §6:
- AES-256-GCM for at-rest encryption (authenticated)
- Key derivation: PBKDF2 250k iter (Argon2id in 0.3+ for server-side)
- IV: random 12 bytes per encryption, never reused
- HMAC-SHA256 for dedup hash (keyed by workspace)
"""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
from dataclasses import dataclass
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Constants
PBKDF2_ITERATIONS = 250_000  # OWASP 2024 minimum for PBKDF2-SHA256
SALT_BYTES = 16
IV_BYTES = 12  # GCM standard
KEY_BYTES = 32  # AES-256


@dataclass
class EncryptedPayload:
    """AES-256-GCM encrypted payload with metadata for portable export."""

    ciphertext: bytes
    iv: bytes
    salt: bytes
    iterations: int
    version: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict for export."""
        return {
            "version": self.version,
            "iterations": self.iterations,
            "salt": base64.b64encode(self.salt).decode("ascii"),
            "iv": base64.b64encode(self.iv).decode("ascii"),
            "ciphertext": base64.b64encode(self.ciphertext).decode("ascii"),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EncryptedPayload:
        """Deserialize from JSON dict."""
        return cls(
            ciphertext=base64.b64decode(data["ciphertext"]),
            iv=base64.b64decode(data["iv"]),
            salt=base64.b64decode(data["salt"]),
            iterations=data.get("iterations", PBKDF2_ITERATIONS),
            version=data.get("version", 1),
        )


def derive_key(passphrase: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    """Derive a 256-bit AES key from a passphrase using PBKDF2-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_BYTES,
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(passphrase.encode("utf-8"))


def encrypt_json(data: Any, passphrase: str) -> EncryptedPayload:
    """Encrypt a JSON-serializable object with AES-256-GCM."""
    salt = secrets.token_bytes(SALT_BYTES)
    iv = secrets.token_bytes(IV_BYTES)
    key = derive_key(passphrase, salt)

    plaintext = json.dumps(data, default=str, ensure_ascii=False).encode("utf-8")
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext, associated_data=None)

    return EncryptedPayload(
        ciphertext=ciphertext,
        iv=iv,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )


def decrypt_json(payload: EncryptedPayload, passphrase: str) -> Any:
    """Decrypt an AES-256-GCM payload and return the original JSON object.

    Raises cryptography.exceptions.InvalidTag if passphrase is wrong.
    """
    key = derive_key(passphrase, payload.salt, payload.iterations)
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(payload.iv, payload.ciphertext, associated_data=None)
    return json.loads(plaintext.decode("utf-8"))


def compute_dedup_hash(content: str, workspace_salt: str = "") -> str:
    """Compute HMAC-SHA256 dedup hash for content (without exposing plaintext)."""
    h = hashlib.sha256()
    h.update(workspace_salt.encode("utf-8"))
    h.update(b":")
    h.update(content.encode("utf-8"))
    return h.hexdigest()


def compute_input_hash(text: str) -> str:
    """SHA-256 hash of user input for audit log (without storing plaintext)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
