# ADR 0002 — Promotion of experiment artifacts into `shared/`

- Status: Accepted
- Date: 2026-08-06
- Decision owners: Project lead, UET, and HNMU according to artifact authority
- Origin: Experiment `20260806_145124`, Plan 01

## Context

Experiments correctly preserve run history, but stable inputs such as audit
checklists, filtered dialogue sets, candidate pools, selections, and provisional
specifications are difficult to discover when every consumer follows historical
snapshot paths. Copying an artifact into `shared/` without provenance would
create the opposite problem: an easy-to-find file with unclear authority.

## Decision

An artifact may be promoted from `experiments/<id>/` into `shared/` only when a
promotion record establishes:

- a stable artifact ID, type, version, status, and canonical path;
- source experiment/path, schema version, checksum, and count invariants;
- transformation code/command when the canonical form is derived;
- approval authority and the exact review state;
- access/licensing policy and an external locator when payload cannot be in Git;
- supersession/deprecation information for consumers.

Experiments remain immutable provenance. Promotion does not erase the source and
does not upgrade `provisional`, `needs_review`, or `awaiting_hnmu_review` into an
approved benchmark state.

Canonical selections should store IDs, dispositions, reasons, and provenance
when the full materialized table can be rebuilt by a validated join.

This ADR defines the promotion contract. The Plan 03 migration remains subject
to separate approval and checksum/equivalence validation.

## Consequences

- Humans and agents can discover stable artifacts through one registry.
- Consumers stop depending on arbitrary inherited snapshot paths.
- Promotion requires more metadata, but avoids silent ground-truth claims.
- Large or restricted payloads can remain external while manifests stay tracked.

## Enforcement

No consumer should call an experiment output canonical solely because it is the
newest file. Plan 03 will implement the registry and idempotent promotion tool.

