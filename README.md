# FIRMA — Coherence Telemetry for Multi-Agent Trust Infrastructure

**FIRMA** (*from Latin: firm, steadfast, unalterable*) is an open specification for cryptographic audit trails that measure coherence between declared intent and observed behaviour in multi-agent systems.

Where TLS secures the *transport* of data, FIRMA secures the *coherence* of decisions — detecting when what an agent says it will do diverges from what it actually does.

---

## The problem

AI agents are increasingly autonomous — writing code, managing workflows, executing transactions. But there is no standard mechanism to:

- **Detect** when an agent's declared intent contradicts its actual behaviour
- **Record** decisions immutably so they can be audited after the fact
- **Verify** that a chain of agent interactions remained coherent over time

Without coherence telemetry, multi-agent coordination operates on blind trust. FIRMA provides the missing verification layer.

## What FIRMA does

FIRMA defines a minimal, auditable record format for agent decisions:

1. **Append-only ledger** — Every decision is written once and cannot be altered. Records are hash-chained (SHA3-512) to form a tamper-evident sequence.
2. **Contradiction detection** — Each record captures declared intent vs. observed reality, producing a coherence score that quantifies drift.
3. **Cryptographic signatures** — Every record is signed (Ed25519) by the producing agent, ensuring non-repudiation.
4. **Timestamp anchoring** — Records can be anchored to external timestamp authorities (RFC 3161) for independent temporal proof.

## Live demo

An interactive demo of the Trust Sensor is available at:

**[https://SAMTHP.github.io/firma-spec/demo/](https://SAMTHP.github.io/firma-spec/demo/)**

The demo runs entirely client-side (no server required). Adjust deal parameters and see real-time contradiction scoring, ACT analysis, and FIRMA trace generation. You can also open `demo/index.html` locally in any browser.

## Specification

The full specification is in [`spec/`](./spec/):

| Document | Description |
|---|---|
| [firma-v2.0.md](./spec/firma-v2.0.md) | Core specification — record format, hash chain, governance model |
| [record-types.md](./spec/record-types.md) | Eight record types and their semantics |
| [hash-chain.md](./spec/hash-chain.md) | Hash chain integrity model and verification algorithm |
| [dcp-protocol.md](./spec/dcp-protocol.md) | Decision Context Packet protocol for agent-to-FIRMA communication |

## Schemas

JSON Schemas for validation are in [`schemas/`](./schemas/):

- [`firma-record.schema.json`](./schemas/firma-record.schema.json) — Core record schema
- [`constitutional-rule.schema.json`](./schemas/constitutional-rule.schema.json) — Governance rule schema
- [`dcp.schema.json`](./schemas/dcp.schema.json) — Decision Context Packet schema

## Examples

Concrete examples are in [`examples/`](./examples/):

- [`genesis-record.json`](./examples/genesis-record.json) — First record in a FIRMA chain (anchor)
- [`decision-record.json`](./examples/decision-record.json) — A standard decision with contradiction scoring
- [`chain-sample.json`](./examples/chain-sample.json) — Five chained records demonstrating full integrity

## Reference implementation

A Python reference implementation is in [`validators/python/`](./validators/python/):

```bash
cd validators/python
pip install -r requirements.txt

# Generate a signed trace
python generate_trace.py

# Verify chain integrity
python verify_chain.py examples/chain-sample.json

# Run tests
pytest tests/ -v
```

## Metrics (validated)

| Metric | Value | Methodology |
|---|---|---|
| Drift detection precision | **72%** (95% CI: [60%, 82%]) | 100-deal synthetic benchmark, MEDIUM+ detection threshold |
| Recall | 93% | Same benchmark |
| F1 score | 82% | Same benchmark |
| Cohen's kappa | 0.58 | Same benchmark — target κ > 0.8 |
| End-to-end latency (p99) | < 200 ms | Measured on prototype deployment |

Precision is defined as: of all deals the engine flags as at-risk (MEDIUM or HIGH), what fraction truly exhibit drift. Evaluated on a labeled synthetic dataset with explicit ground truth criteria. Full methodology: see `METHODOLOGY.md` in the evaluation repository.

## Alignment with ARIA Scaling Trust

FIRMA is designed as open-source coordination infrastructure for the [ARIA Scaling Trust](https://aria.org.uk/opportunity-spaces/trust-everything-everywhere/scaling-trust) programme (Track 2: Tooling).

| ARIA principle | FIRMA implementation |
|---|---|
| Secure agent coordination | Cryptographic audit trail for every agent interaction |
| Verifiable trust | Hash-chained records with Ed25519 signatures |
| Open-source tooling | MIT-licensed spec + reference implementation |
| Adversarial resilience | Contradiction detection surfaces intent-behaviour divergence |

FIRMA does not replace authentication or encryption. It operates at a higher level: *given that agents can already identify and communicate securely, are they doing what they said they would?*

## Project status

FIRMA is developed by [INOVI Group Ltd](https://github.com/SAMTHP) (London, UK) as the governance ledger of the IDA 2.0 (Intelligent Decision Architecture) ecosystem.

- **Spec**: v2.0 (stable)
- **Reference implementation**: Python (functional)
- **Production deployment**: Active — contradiction detection on commercial CRM data
- **Open-source**: This repository (MIT)

## License

[MIT](./LICENSE)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). We welcome implementations in other languages, test vectors, and spec feedback.

## Contact

INOVI Group Ltd — London, UK
[contact.inovigroup@gmail.com](mailto:contact.inovigroup@gmail.com)

*"What is written in FIRMA endures. No hand may erase it."*
