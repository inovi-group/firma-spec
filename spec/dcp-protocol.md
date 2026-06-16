# Decision Context Packet (DCP) protocol v2.2

## Overview

The DCP protocol defines how an intelligence source (e.g. an AI agent, a decision engine, or a human operator) communicates decision context to a FIRMA ledger for constitutional evaluation and recording.

A DCP is a structured data packet that carries everything FIRMA needs to evaluate, record, and audit a decision.

## DCP fields

| Field | Type | Required | Description |
|---|---|---|---|
| `dcp_id` | UUID v4 | Yes | Unique identifier for this context packet |
| `source_version` | SemVer | Yes | Version of the producing system |
| `firma_id_ref` | UUID v4 | Yes | Reference to prior FIRMA record (chain link) |
| `context_vector` | Float[512] | No | Embedded context representation (for ML-enabled systems) |
| `declared_intent` | JSON object | Yes | What the actor declares they will do |
| `observed_reality` | JSON object | Yes | What the data actually shows |
| `confidence_score` | Float [0, 1] | Yes | Source system confidence in this context |
| `actor_ids` | UUID[] | Yes | Actors referenced in this context |
| `timestamp_utc` | ISO 8601 | Yes | UTC timestamp of context capture |
| `signature` | Ed25519 | Yes | Source system cryptographic signature |
| `metadata` | JSON object | No | Auxiliary metadata (extensible) |

## Protocol flow

```
[Intelligence Source] -- DCP --> [FIRMA]
                                   |
                                   ├── Validate schema
                                   ├── Verify signature
                                   ├── Check temporal coherence (±5s drift)
                                   ├── Evaluate constitutional rules
                                   ├── Compute contradiction score
                                   |
                                   └── Write Decision Record (DR) to ledger
```

## Validation rules

A DCP is accepted if and only if:

1. All required fields are present and correctly typed
2. `signature` validates against the source system's registered public key
3. `timestamp_utc` is within ±5 seconds of FIRMA server time
4. `firma_id_ref` references an existing record in the chain
5. `dcp_id` has not been previously submitted (replay protection)

## Rejection codes

| Code | Meaning |
|---|---|
| `DCP-001` | Schema validation failure |
| `DCP-002` | Signature verification failure |
| `DCP-003` | Temporal coherence violation |
| `DCP-004` | Unknown FIRMA reference |
| `DCP-005` | Duplicate DCP (replay detected) |

Rejected DCPs generate an Alert Record (AR) in the FIRMA ledger.

## Example DCP

```json
{
  "dcp_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "source_version": "1.0.0",
  "firma_id_ref": "00000000-0000-0000-0000-000000000001",
  "declared_intent": {
    "action": "approve_deal",
    "parameters": { "deal_value": 50000, "discount": 10 }
  },
  "observed_reality": {
    "action": "approve_deal",
    "parameters": { "deal_value": 50000, "discount": 35, "payment_history": "late" }
  },
  "confidence_score": 0.85,
  "actor_ids": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"],
  "timestamp_utc": "2026-06-16T10:30:00Z",
  "signature": "base64-encoded-ed25519-signature",
  "metadata": { "crm_source": "hubspot", "deal_stage": "negotiation" }
}
```
