# ADR 0001 — Boundary between `src/` and `scripts/`

- Status: Accepted
- Date: 2026-08-06
- Decision owners: Project lead and repository maintainers
- Origin: Experiment `20260806_145124`, Plan 01

## Context

Reusable processing logic and command orchestration are currently distributed
across both `src/` and `scripts/`. Some scripts contain business rules, while
some source modules carry experiment-specific defaults. This makes ownership,
testing, reuse, and path portability harder to reason about.

## Decision

- `src/edu_benchmark/` owns reusable domain types, validation, transformations,
  provider adapters, persistence policies, and analysis logic.
- `scripts/` owns thin command-line entry points: argument parsing, configuration
  loading, library dispatch, progress reporting, and exit-code mapping.
- Reusable source code must not embed an experiment ID, developer-machine path,
  secret, or a mutable copy of a versioned prompt/configuration.
- Experiment-specific configuration and operational commands belong under the
  relevant experiment's `configs/` and `runbooks/` directories.
- Historical commands may keep compatibility wrappers during an explicit
  migration window. They must not become a second implementation of the logic.

This ADR defines the durable boundary. It does not authorize the Plan 05 code
move; that move still requires its own approved plan and compatibility audit.

## Consequences

- Unit tests can call library functions without spawning subprocesses.
- CLI behavior remains inspectable and replaceable without duplicating policy.
- Packaging must eventually make `edu_benchmark` importable without path
  injection; that work belongs to Plan 02.
- Existing large scripts require incremental migration rather than a blind move.

## Enforcement

New code should follow this boundary immediately. Existing code is migrated only
through approved plans, with call-graph inventory and equivalence tests.

