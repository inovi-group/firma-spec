#!/usr/bin/env python3
"""Verify the integrity of a FIRMA chain from a JSON file.

Usage:
    python verify_chain.py chain.json
    python verify_chain.py examples/chain-sample.json
"""

from __future__ import annotations

import json
import sys

from firma.chain import load_chain_from_json, verify_chain


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_chain.py <chain.json>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print("Error: expected a JSON array of records.", file=sys.stderr)
        sys.exit(1)

    records = load_chain_from_json(data)
    result = verify_chain(records)

    print(result)

    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
