#!/usr/bin/env python3
"""Generate FIRMA trace records with real cryptographic hashes and signatures.

Usage:
    python generate_trace.py                    # Generate a single decision record
    python generate_trace.py --chain 5          # Generate a chain of 5 records
    python generate_trace.py --chain 5 -o out.json  # Save chain to file
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid

from firma.crypto import generate_keypair
from firma.record import create_record


def make_genesis(actor_id: str, signing_key) -> dict:
    """Create a genesis Constitutional Record."""
    content = {
        "rule_id": str(uuid.uuid4()),
        "rule_version": "1.0.0",
        "rule_type": "ABSOLUTE",
        "priority": 1,
        "trigger": {"type": "event", "conditions": [{"field": "record_hash", "operator": "modified"}]},
        "action": {"type": "block_and_alert", "parameters": {"alert_class": "CONSTITUTIONAL_BREACH"}},
        "description": "AR-003: Ledger immutability enforcement.",
        "created_by": actor_id,
        "created_at": "2026-05-25T00:00:00Z",
        "supersedes": None,
    }
    record = create_record(
        record_type="CR",
        actor_id=actor_id,
        content=content,
        signing_key=signing_key,
        predecessor_hash=None,
        coherence_score=1.0,
    )
    return record


def make_decision_record(actor_id: str, signing_key, predecessor_hash: str, index: int) -> dict:
    """Create a sample Decision Record with contradiction scoring."""
    import random

    random.seed(42 + index)

    declared_discount = random.randint(5, 15)
    actual_discount = random.randint(10, 45)
    deal_value = random.choice([25000, 50000, 75000, 100000])

    temporal = round(random.uniform(0.0, 0.3), 2)
    behavioural = round(random.uniform(0.1, 0.8), 2)
    quantitative = round(abs(actual_discount - declared_discount) / max(actual_discount, 1), 2)
    semantic = round(random.uniform(0.0, 0.5), 2)

    contradiction_score = round(
        0.20 * temporal + 0.30 * behavioural + 0.25 * quantitative + 0.25 * semantic, 3
    )
    coherence = round(1.0 - contradiction_score, 3)

    content = {
        "decision_id": str(uuid.uuid4()),
        "declared_intent": {
            "action": "approve_deal",
            "parameters": {"deal_value": deal_value, "discount_percent": declared_discount},
        },
        "observed_reality": {
            "action": "approve_deal",
            "parameters": {
                "deal_value": deal_value,
                "discount_percent": actual_discount,
                "payment_history": random.choice(["on_time", "late_1x", "late_3x"]),
            },
        },
        "contradiction_signals": {
            "temporal": temporal,
            "behavioural": behavioural,
            "quantitative": quantitative,
            "semantic": semantic,
        },
        "contradiction_score": contradiction_score,
        "confidence": round(random.uniform(0.7, 0.95), 2),
        "narrative": f"Deal #{index}: discount divergence detected ({declared_discount}% declared vs {actual_discount}% actual).",
    }

    record = create_record(
        record_type="DR",
        actor_id=actor_id,
        content=content,
        signing_key=signing_key,
        predecessor_hash=predecessor_hash,
        coherence_score=coherence,
    )
    return record


def generate_chain(length: int) -> list[dict]:
    """Generate a valid FIRMA chain of the specified length."""
    signing_key, _verify_key = generate_keypair()
    actor_id = str(uuid.uuid4())

    chain = []

    genesis = make_genesis(actor_id, signing_key)
    chain.append(genesis.to_dict())

    for i in range(1, length):
        predecessor_hash = chain[-1]["record_hash"]
        record = make_decision_record(actor_id, signing_key, predecessor_hash, i)
        chain.append(record.to_dict())

    return chain


def main():
    parser = argparse.ArgumentParser(description="Generate FIRMA trace records.")
    parser.add_argument("--chain", type=int, default=1, help="Number of records to generate (default: 1)")
    parser.add_argument("-o", "--output", type=str, help="Output file path (default: stdout)")
    args = parser.parse_args()

    chain = generate_chain(max(1, args.chain))

    output = json.dumps(chain, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output + "\n")
        print(f"Wrote {len(chain)} records to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
