"""Cryptographic primitives for FIRMA: SHA3-512 hashing and Ed25519 signing."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError
from nacl.encoding import Base64Encoder


def canonical_json(obj: Any) -> str:
    """Produce a deterministic JSON string: sorted keys, no whitespace."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha3_512_hex(data: str) -> str:
    """Compute SHA3-512 and return the lowercase hex digest (128 chars)."""
    return hashlib.sha3_512(data.encode("utf-8")).hexdigest()


def compute_record_hash(
    firma_id: str,
    record_type: str,
    version: str,
    actor_id: str,
    content: dict,
    timestamp_utc: str,
    predecessor_hash: str | None,
) -> str:
    """Compute the FIRMA record hash per spec §4.

    record_hash = SHA3-512(
        firma_id || record_type || version || actor_id ||
        JSON_canonical(content) || timestamp_utc || predecessor_hash
    )
    """
    predecessor = predecessor_hash if predecessor_hash is not None else ""
    payload = (
        firma_id
        + record_type
        + version
        + actor_id
        + canonical_json(content)
        + timestamp_utc
        + predecessor
    )
    return sha3_512_hex(payload)


def generate_keypair() -> tuple[SigningKey, VerifyKey]:
    """Generate a new Ed25519 signing/verification key pair."""
    signing_key = SigningKey.generate()
    return signing_key, signing_key.verify_key


def sign_hash(signing_key: SigningKey, record_hash: str) -> str:
    """Sign a record hash with Ed25519, returning base64-encoded signature."""
    signed = signing_key.sign(record_hash.encode("utf-8"), encoder=Base64Encoder)
    return signed.signature.decode("ascii")


def verify_signature(verify_key_bytes: bytes, record_hash: str, signature_b64: str) -> bool:
    """Verify an Ed25519 signature. Returns True if valid, False otherwise."""
    try:
        vk = VerifyKey(verify_key_bytes)
        import base64
        sig_bytes = base64.b64decode(signature_b64)
        vk.verify(record_hash.encode("utf-8"), sig_bytes)
        return True
    except (BadSignatureError, Exception):
        return False
