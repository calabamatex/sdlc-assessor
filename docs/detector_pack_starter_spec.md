# Language Detector Pack Starter Specification

## Purpose

Detector packs translate language-specific repository patterns into the common evidence schema.

## Common detector responsibilities

Every detector pack should attempt to emit evidence for:

- type and contract rigor
- error handling discipline
- logging and observability
- external boundary validation
- unsafe command execution
- unsafe file and path handling
- dependency and packaging hygiene
- test patterns
- CI alignment
- documentation consistency signals

## Output rules

Each detector must emit:
- normalized category
- subcategory
- severity
- statement
- evidence refs
- confidence
- score impact suggestion
- detector source name

## TypeScript and JavaScript starter rules

Key signals:
- `any`, `as any`, non-null assertions in critical paths
- `strict` mode in tsconfig
- zod, io-ts, valibot, class-validator
- `exec`, `execSync`, shell interpolation
- JSON parsing without validation
- unsafe fs writes
- console leakage outside CLI boundaries
- package publish hygiene
- GitHub Actions usage

## Python starter rules

Key signals:
- `Any`, `type: ignore`, mypy or pyright strictness
- pydantic, attrs, dataclasses plus validation
- bare `except`
- subprocess shell execution
- unvalidated path or URL handling
- pytest, unittest, coverage, tox, nox
- pyproject metadata, build backend, pinned dependencies

## Go starter rules

Key signals:
- ignored errors
- panic-heavy behavior
- `exec.Command` safety
- context usage
- `go test`, benchmark files, race detector
- `go.mod`, `go.sum`, govulncheck
- structured logging conventions

## Rust starter rules

Key signals:
- `unwrap` and `expect` density in non-test code
- `unsafe` blocks
- serde validation boundaries
- clippy config
- cargo-audit, cargo-deny
- feature flag hygiene
- integration tests and doc tests

## Confidence guidance

- high when exact parser or config evidence is found
- medium when regex-based approximation is used
- low when signal is inferred indirectly

## Calibration note

Detector packs should be benchmarked independently because false-positive rates vary sharply by language and repo archetype.
