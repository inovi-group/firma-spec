# Contributing to FIRMA

FIRMA is an open specification. We welcome contributions that strengthen the protocol and expand its ecosystem.

## How to contribute

### Spec feedback
Open an issue describing the gap, ambiguity, or improvement. Reference the specific section of the spec.

### Implementations in other languages
We actively seek reference validators in JavaScript/TypeScript, Go, and Rust. See `validators/python/` for the reference behaviour to match.

### Test vectors
Additional test vectors (valid and invalid chains, edge cases, adversarial inputs) are valuable. Place them in `examples/` with a descriptive filename.

### Bug reports
If you find a discrepancy between the spec and the reference implementation, open an issue with:
- The spec section that defines the expected behaviour
- The actual behaviour observed
- A minimal reproduction

## Pull request process

1. Fork the repository
2. Create a feature branch (`feat/your-feature` or `fix/your-fix`)
3. Ensure all existing tests pass (`pytest tests/ -v`)
4. Add tests for new functionality
5. Submit a PR with a clear description

## Code style

- Python: follow PEP 8, type hints required
- Markdown: one sentence per line for clean diffs
- JSON schemas: use draft-07

## Scope

FIRMA is a **specification** repository. Product-level implementation code (backends, UIs, integrations) belongs in separate repositories. This repo contains:
- The formal spec
- JSON schemas for validation
- Reference implementations (minimal, correct, readable)
- Test vectors and examples

## Code of conduct

Be respectful. Be constructive. Focus on the work.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
