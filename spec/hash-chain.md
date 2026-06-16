# FIRMA hash chain integrity model

## Chain structure

A FIRMA chain is an ordered sequence of records `[R₀, R₁, R₂, ..., Rₙ]` where:

- `R₀` is the genesis record (`predecessor_hash = null`)
- For all `i > 0`: `Rᵢ.predecessor_hash = Rᵢ₋₁.record_hash`

This forms a singly-linked hash chain. Any modification to any record breaks all subsequent links.

## Hash computation

```
record_hash = SHA3-512(
    firma_id ||
    record_type ||
    version ||
    actor_id ||
    JSON_canonical(content) ||
    timestamp_utc ||
    predecessor_hash
)
```

### Canonical JSON

`JSON_canonical(obj)` produces a deterministic string:
- Keys sorted alphabetically (recursive)
- No whitespace between tokens
- Numbers without trailing zeros
- Strings with minimal escaping (UTF-8)
- `null` values preserved (not omitted)

This ensures the same logical content always produces the same hash regardless of serialisation order.

## Verification algorithm

```python
def verify_chain(records: list[FirmaRecord]) -> bool:
    if len(records) == 0:
        return False

    # Genesis must have null predecessor
    if records[0].predecessor_hash is not None:
        return False

    for i, record in enumerate(records):
        # Recompute hash from fields
        expected_hash = compute_hash(record)
        if record.record_hash != expected_hash:
            return False  # record tampered

        # Verify chain link (skip genesis)
        if i > 0:
            if record.predecessor_hash != records[i - 1].record_hash:
                return False  # chain broken

        # Verify signature
        if not verify_signature(record):
            return False  # signature invalid

    return True
```

## Threat model

| Threat | Detection |
|---|---|
| Record content modified | `record_hash` recomputation fails |
| Record inserted into chain | `predecessor_hash` mismatch with neighbours |
| Record deleted from chain | `predecessor_hash` of next record has no match |
| Record reordered | `predecessor_hash` chain breaks |
| Timestamp forged | RFC 3161 anchor mismatch (if anchored) |
| Signature forged | Ed25519 verification fails |

## External anchoring (optional)

Records can be anchored to an RFC 3161 Timestamp Authority at configurable intervals. The `anchor_ref` field stores the TSA response reference. This provides independent temporal proof that a record existed at a specific time, even if the FIRMA operator is untrusted.

Default anchoring interval: every 100 records or 15 minutes, whichever occurs first.
