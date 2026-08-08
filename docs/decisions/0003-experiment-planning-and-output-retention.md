# ADR 0003 — Experiment planning, amendments, and output retention

- Status: Accepted
- Date: 2026-08-06
- Decision owners: Project lead and repository maintainers
- Origin: Experiment `20260806_145124`, Plan 01

## Context

Approved plans often diverge from implementation after results reveal a
situational need. Rewriting the baseline loses the original approval, while
putting every state transition into the plan makes it hard for humans to read.
At the same time, unrestricted raw/derived outputs make experiments difficult to
navigate and can exceed Git hosting limits.

## Decision

### Planning surfaces

- The human authorization surface is one concise Markdown baseline plan.
- Implementation is allowed only when the baseline status line explicitly says
  `APPROVED`; machine status cannot grant authority by itself.
- After approval, keep the baseline stable. Record situational changes in one
  append-only chronological amendment log using IDs assigned as needed:
  `PNN-A001`, `PNN-A002`, and so on.
- Store current lifecycle state and optional relationships in
  `plans/NN-status.yaml`. Humans normally need only roadmap order and timeline.
- Close a plan with one final report comparing evidence with the baseline and
  one handoff describing the next human gate.

The lifecycle vocabulary is intentionally small: `draft`, `approved`,
`in_progress`, `blocked`, `completed`, `cancelled`, and `superseded`.

### Artifact budget and retention

Each plan normally has at most one baseline, status file, amendment log,
runbook, final report, and handoff, plus up to three machine outputs that are
actually consumed. Exceptions require a reason in machine-readable status.

Outputs are classified as canonical shared artifacts, reproducibility
manifests, human reports, large raw/provider outputs, rebuildable derived data,
ephemeral files, or unique historical evidence. Large raw/provider outputs are
externalized or ignored by targeted directory rules when practical; a broad
`*.jsonl` ignore rule is prohibited because JSONL can be source/test data.

Deletion, destructive overwrite, and Git history rewriting always require a
separate target-specific approval, even when a retention plan is approved.

## Consequences

- Reviewers follow chronological decisions without learning a baseline-to-
  amendment graph.
- Automation can validate authorization, gates, links, and artifact budgets.
- Historical experiments remain valid provenance and are not rewritten solely
  to match the new templates.
- Repository cleanup becomes a verified migration rather than ad-hoc deletion.

## Enforcement

New experiments use `experiments/_templates/` and the governance validator.
Existing experiments migrate only when an approved plan needs them to change.

