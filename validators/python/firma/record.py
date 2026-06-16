"""FIRMA record creation and serialisation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Any

from .crypto import compute_record_hash, sign_hash, SigningKey


VALID_RECORD_TYPES = {"DR", "ER", "AR", "KR", "CPR", "CR", "AUD", "RR"}
SPEC_VERSION = "2.0.0"


@dataclass
class FirmaRecord:
    """A single record in a FIRMA append-only ledger chain."""

    firma_id: str
    record_type: str
    version: str
    actor_id: str
    content: dict
    timestamp_utc: str
    predecessor_hash: str | None
    record_hash: str
    signature: str
    counterpart_id: str | None = None
    coherence_score: float | None = None
    anchor_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a dictionary, omitting None optional fields."""
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None or k in ("predecessor_hash",)}

    @classmethod
    def from_dict(cls, data: dict) -> "FirmaRecord":
        """Deserialise from a dictionary."""
        return cls(
            firma_id=data["firma_id"],
            record_type=data["record_type"],
            version=data["version"],
            actor_id=data["actor_id"],
            content=data["content"],
            timestamp_utc=data["timestamp_utc"],
            predecessor_hash=data.get("predecessor_hash"),
            record_hash=data["record_hash"],
            signature=data["signature"],
            counterpart_id=data.get("counterpart_id"),
            coherence_score=data.get("coherence_score"),
            anchor_ref=data.get("anchor_ref"),
        )


def create_record(
    record_type: str,
    actor_id: str,
    content: dict,
    signing_key: SigningKey,
    predecessor_hash: str | None = None,
    counterpart_id: str | None = None,
    coherence_score: float | None = None,
) -> FirmaRecord:
    """Create a new FIRMA record with computed hash and signature.

    Args:
        record_type: One of the valid record type codes (DR, ER, AR, etc.)
        actor_id: UUID of the producing actor
        content: Record-type-specific payload
        signing_key: Ed25519 signing key for the actor
        predecessor_hash: Hash of the previous record (None for genesis)
        counterpart_id: UUID of the other party (optional)
        coherence_score: Coherence metric (optional)

    Returns:
        A fully populated FirmaRecord with hash and signature.

    Raises:
        ValueError: If record_type is not valid.
    """
    if record_type not in VALID_RECORD_TYPES:
        raise ValueError(f"Invalid record type: {record_type}. Must be one of {VALID_RECORD_TYPES}")

    firma_id = str(uuid.uuid4())
    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    record_hash = compute_record_hash(
        firma_id=firma_id,
        record_type=record_type,
        version=SPEC_VERSION,
        actor_id=actor_id,
        content=content,
        timestamp_utc=timestamp_utc,
        predecessor_hash=predecessor_hash,
    )

    signature = sign_hash(signing_key, record_hash)

    return FirmaRecord(
        firma_id=firma_id,
        record_type=record_type,
        version=SPEC_VERSION,
        actor_id=actor_id,
        content=content,
        timestamp_utc=timestamp_utc,
        predecessor_hash=predecessor_hash,
        record_hash=record_hash,
        signature=signature,
        counterpart_id=counterpart_id,
        coherence_score=coherence_score,
    )
