# Changelog

All notable changes to the FIRMA specification and reference implementation.

## [2.0.0] — 2026-05-25

### Added
- Core specification v2.0 with four pillars (Immutability, Automatic Execution, Reciprocity, Selective Sharing)
- Eight record types: DR, ER, AR, KR, CPR, CR, AUD, RR
- Hash chain integrity model (SHA3-512)
- Ed25519 digital signatures for non-repudiation
- Decision Context Packet (DCP) protocol v2.2
- JSON schemas for record validation
- Python reference implementation with chain generation and verification
- 16 unit tests covering hash computation, record creation, chain integrity, and tamper detection
- Example records: genesis, decision, and 5-record verifiable chain

### Changed
- Upgraded from SHA-256 (v1.x) to SHA3-512 for hash chain
- Replaced placeholder signatures with Ed25519 cryptographic signatures

## [1.0.0] — 2026-04-01

### Added
- Initial FIRMA concept: JSON lines + SHA-256 hash chain
- Basic contradiction scoring
- Prototype trace generation
