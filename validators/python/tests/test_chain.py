"""Tests for FIRMA chain creation and verification."""

from __future__ import annotations

import json
import copy
import uuid

import pytest

from firma.crypto import generate_keypair, compute_record_hash, sign_hash, sha3_512_hex
from firma.record import create_record, FirmaRecord
from firma.chain import verify_chain, verify_record_hash, load_chain_from_json


@pytest.fixture
def keypair():
    """Generate a fresh Ed25519 keypair for testing."""
    return generate_keypair()


@pytest.fixture
def actor_id():
    return str(uuid.uuid4())


@pytest.fixture
def genesis(keypair, actor_id):
    """Create a genesis record."""
    signing_key, _ = keypair
    return create_record(
        record_type="CR",
        actor_id=actor_id,
        content={"rule_id": str(uuid.uuid4()), "description": "Genesis rule"},
        signing_key=signing_key,
        predecessor_hash=None,
        coherence_score=1.0,
    )


@pytest.fixture
def valid_chain(keypair, actor_id, genesis):
    """Create a valid chain of 5 records."""
    signing_key, _ = keypair
    chain = [genesis]
    for i in range(4):
        record = create_record(
            record_type="DR",
            actor_id=actor_id,
            content={"decision_id": str(uuid.uuid4()), "index": i},
            signing_key=signing_key,
            predecessor_hash=chain[-1].record_hash,
            coherence_score=0.8,
        )
        chain.append(record)
    return chain


class TestHashComputation:
    """Tests for SHA3-512 hash computation."""

    def test_deterministic(self):
        """Same inputs always produce the same hash."""
        h1 = sha3_512_hex("hello")
        h2 = sha3_512_hex("hello")
        assert h1 == h2

    def test_different_inputs(self):
        """Different inputs produce different hashes."""
        h1 = sha3_512_hex("hello")
        h2 = sha3_512_hex("world")
        assert h1 != h2

    def test_hash_length(self):
        """SHA3-512 hex digest is 128 characters."""
        h = sha3_512_hex("test")
        assert len(h) == 128

    def test_record_hash_reproducible(self):
        """Record hash can be recomputed from fields."""
        h1 = compute_record_hash("id1", "DR", "2.0.0", "actor1", {"key": "val"}, "2026-01-01T00:00:00Z", None)
        h2 = compute_record_hash("id1", "DR", "2.0.0", "actor1", {"key": "val"}, "2026-01-01T00:00:00Z", None)
        assert h1 == h2


class TestRecordCreation:
    """Tests for FIRMA record creation."""

    def test_creates_valid_record(self, keypair, actor_id):
        signing_key, _ = keypair
        record = create_record(
            record_type="DR",
            actor_id=actor_id,
            content={"test": True},
            signing_key=signing_key,
        )
        assert record.record_type == "DR"
        assert record.version == "2.0.0"
        assert len(record.record_hash) == 128
        assert record.signature is not None

    def test_hash_matches_fields(self, keypair, actor_id):
        signing_key, _ = keypair
        record = create_record(
            record_type="DR",
            actor_id=actor_id,
            content={"test": True},
            signing_key=signing_key,
        )
        assert verify_record_hash(record)

    def test_invalid_record_type_raises(self, keypair, actor_id):
        signing_key, _ = keypair
        with pytest.raises(ValueError, match="Invalid record type"):
            create_record(
                record_type="INVALID",
                actor_id=actor_id,
                content={},
                signing_key=signing_key,
            )

    def test_genesis_has_null_predecessor(self, genesis):
        assert genesis.predecessor_hash is None

    def test_serialisation_roundtrip(self, genesis):
        d = genesis.to_dict()
        restored = FirmaRecord.from_dict(d)
        assert restored.firma_id == genesis.firma_id
        assert restored.record_hash == genesis.record_hash


class TestChainVerification:
    """Tests for FIRMA chain integrity verification."""

    def test_valid_chain_passes(self, valid_chain):
        result = verify_chain(valid_chain)
        assert result.valid
        assert result.record_count == 5
        assert len(result.errors) == 0

    def test_empty_chain_fails(self):
        result = verify_chain([])
        assert not result.valid
        assert "Empty chain" in result.errors[0]

    def test_tampered_content_detected(self, valid_chain):
        """Modifying a record's content should break hash verification."""
        tampered = copy.deepcopy(valid_chain)
        tampered[2].content["tampered"] = True
        result = verify_chain(tampered)
        assert not result.valid
        assert any("hash mismatch" in e for e in result.errors)

    def test_broken_chain_link_detected(self, valid_chain):
        """Changing a predecessor_hash should break chain link verification."""
        broken = copy.deepcopy(valid_chain)
        broken[3].predecessor_hash = "0" * 128
        result = verify_chain(broken)
        assert not result.valid
        assert any("chain break" in e for e in result.errors)

    def test_genesis_with_predecessor_fails(self, keypair, actor_id):
        """Genesis record must have null predecessor."""
        signing_key, _ = keypair
        bad_genesis = create_record(
            record_type="CR",
            actor_id=actor_id,
            content={"test": True},
            signing_key=signing_key,
            predecessor_hash="a" * 128,
        )
        result = verify_chain([bad_genesis])
        assert not result.valid
        assert any("genesis" in e for e in result.errors)

    def test_single_genesis_is_valid(self, genesis):
        result = verify_chain([genesis])
        assert result.valid
        assert result.record_count == 1


class TestJsonLoading:
    """Tests for loading chains from JSON."""

    def test_load_from_dict_list(self, valid_chain):
        dicts = [r.to_dict() for r in valid_chain]
        loaded = load_chain_from_json(dicts)
        assert len(loaded) == len(valid_chain)
        result = verify_chain(loaded)
        assert result.valid
