"""FIRMA chain verification — validates integrity of an ordered sequence of records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .crypto import compute_record_hash
from .record import FirmaRecord


@dataclass
class VerificationResult:
    """Result of a chain verification."""

    valid: bool
    record_count: int
    errors: list[str]

    def __str__(self) -> str:
        status = "VALID" if self.valid else "INVALID"
        lines = [f"Chain verification: {status} ({self.record_count} records)"]
        for err in self.errors:
            lines.append(f"  ERROR: {err}")
        return "\n".join(lines)


def verify_record_hash(record: FirmaRecord) -> bool:
    """Recompute the record hash and compare to the stored value."""
    expected = compute_record_hash(
        firma_id=record.firma_id,
        record_type=record.record_type,
        version=record.version,
        actor_id=record.actor_id,
        content=record.content,
        timestamp_utc=record.timestamp_utc,
        predecessor_hash=record.predecessor_hash,
    )
    return record.record_hash == expected


def verify_chain(records: list[FirmaRecord]) -> VerificationResult:
    """Verify the integrity of a FIRMA chain.

    Checks:
    1. Genesis record has predecessor_hash == None
    2. Each subsequent record's predecessor_hash matches the previous record_hash
    3. Each record_hash can be independently recomputed from fields

    Note: Signature verification requires the actor public key registry,
    which is outside the scope of this reference implementation.

    Args:
        records: Ordered list of FirmaRecord objects.

    Returns:
        VerificationResult with validity status and any errors found.
    """
    errors: list[str] = []

    if len(records) == 0:
        return VerificationResult(valid=False, record_count=0, errors=["Empty chain"])

    # Check genesis
    genesis = records[0]
    if genesis.predecessor_hash is not None:
        errors.append(
            f"Record 0 ({genesis.firma_id}): genesis record must have "
            f"predecessor_hash=null, got '{genesis.predecessor_hash}'"
        )

    for i, record in enumerate(records):
        # Verify hash integrity
        if not verify_record_hash(record):
            expected = compute_record_hash(
                firma_id=record.firma_id,
                record_type=record.record_type,
                version=record.version,
                actor_id=record.actor_id,
                content=record.content,
                timestamp_utc=record.timestamp_utc,
                predecessor_hash=record.predecessor_hash,
            )
            errors.append(
                f"Record {i} ({record.firma_id}): hash mismatch. "
                f"Stored: {record.record_hash[:16]}... "
                f"Computed: {expected[:16]}..."
            )

        # Verify chain link (skip genesis)
        if i > 0:
            expected_predecessor = records[i - 1].record_hash
            if record.predecessor_hash != expected_predecessor:
                errors.append(
                    f"Record {i} ({record.firma_id}): chain break. "
                    f"predecessor_hash does not match record {i-1}'s hash."
                )

    return VerificationResult(
        valid=len(errors) == 0,
        record_count=len(records),
        errors=errors,
    )


def load_chain_from_json(data: list[dict[str, Any]]) -> list[FirmaRecord]:
    """Parse a JSON array into a list of FirmaRecord objects."""
    return [FirmaRecord.from_dict(entry) for entry in data]
