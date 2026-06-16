# FIRMA v2.0 — Core specification

## 1. Overview

FIRMA (from Latin: *firm, steadfast, unalterable*) is a cryptographic audit trail format for recording and verifying coherence in multi-agent decision systems.

A FIRMA ledger is an append-only sequence of records, each cryptographically linked to its predecessor, forming a tamper-evident chain. Every record captures a decision event — who decided what, under which context, with what coherence score — and seals it with the actor's digital signature.

## 2. Design principles

1. **Immutability** — What is written in FIRMA endures. No record may be altered or deleted after commitment.
2. **Automatic execution** — Approved rules execute without human intervention at runtime. Human judgment is deferred to rule design time.
3. **Reciprocity** — Every action has an accountability trace. FIRMA records both sides of every interaction.
4. **Selective sharing** — Transparency is a virtue; confidentiality is a right. Access is governed by attribute-based encryption.

## 3. Record format

Every FIRMA record contains the following fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `firma_id` | UUID v4 | Yes | Unique identifier for this record |
| `record_type` | String (2-3 chars) | Yes | Record type code (see [record-types.md](./record-types.md)) |
| `version` | SemVer string | Yes | FIRMA spec version (e.g. `"2.0.0"`) |
| `actor_id` | UUID v4 | Yes | The agent or human producing this record |
| `counterpart_id` | UUID v4 | No | The other party in the interaction (if applicable) |
| `content` | JSON object | Yes | Record-type-specific payload |
| `coherence_score` | Float [0.0, 1.0] | No | Coherence between declared intent and observed behaviour |
| `timestamp_utc` | ISO 8601 | Yes | UTC timestamp of record creation |
| `predecessor_hash` | Hex string (128 chars) | Yes* | SHA3-512 hash of the preceding record. Null for genesis. |
| `record_hash` | Hex string (128 chars) | Yes | SHA3-512 hash of this record (see [hash-chain.md](./hash-chain.md)) |
| `signature` | Base64 string | Yes | Ed25519 signature over `record_hash` |
| `anchor_ref` | String | No | RFC 3161 timestamp authority reference |

*`predecessor_hash` is `null` only for the genesis record (first record in the chain).

## 4. Hash computation

The `record_hash` is computed as:

```
record_hash = SHA3-512(
    firma_id || record_type || version || actor_id ||
    JSON_canonical(content) || timestamp_utc || predecessor_hash
)
```

Where `||` denotes concatenation and `JSON_canonical` produces a deterministic JSON serialisation (keys sorted, no whitespace).

The `predecessor_hash` of record N is the `record_hash` of record N-1. This forms the chain.

## 5. Signature

Every record must be signed by the producing actor using Ed25519:

```
signature = Ed25519_sign(private_key, record_hash)
```

Verification:

```
Ed25519_verify(public_key, record_hash, signature) == true
```

## 6. Genesis record

The first record in a FIRMA chain is the genesis record. It has:
- `predecessor_hash`: `null`
- `record_type`: `"CR"` (Constitutional Record)
- `content`: contains the initial governance rules and actor registrations

The genesis record anchors the entire chain. Its `record_hash` serves as the chain identifier.

## 7. Coherence score

The coherence score quantifies alignment between declared intent and observed behaviour:

- `1.0` = perfect coherence (intent matches reality)
- `0.0` = complete contradiction (intent fully diverges from reality)

The score is computed from weighted sub-signals specific to the record type. For decision records, the default formula is:

```
coherence = 1.0 - contradiction_score

contradiction_score = weighted_average(
    w1 * temporal_contradiction,
    w2 * behavioural_contradiction,
    w3 * quantitative_contradiction,
    w4 * semantic_contradiction
)
```

Default weights: `w1=0.20, w2=0.30, w3=0.25, w4=0.25`.

## 8. Chain verification

A FIRMA chain is valid if and only if:

1. The genesis record has `predecessor_hash == null`
2. For every subsequent record N: `record.predecessor_hash == records[N-1].record_hash`
3. Every `record_hash` can be independently recomputed from the record fields
4. Every `signature` validates against the `actor_id`'s registered public key

See [hash-chain.md](./hash-chain.md) for the verification algorithm.

## 9. Constitutional rules

Rules inscribed in FIRMA govern automated behaviour. See [record-types.md](./record-types.md) for the Constitutional Record (CR) format.

Absolute Rules (priority 1-10) cannot be suspended or overridden. They require the chain owner's signature to amend.

## 10. Versioning

This specification follows semantic versioning. Breaking changes increment the major version. The current version is **2.0.0**.

Implementations must include `version` in every record and must reject records with an unsupported major version.
