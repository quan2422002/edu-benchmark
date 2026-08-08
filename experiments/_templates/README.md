# Experiment governance templates

These templates define the repository governance contract for experiments
created after experiment `20260806_145124` Plan 01.

## Human and machine surfaces

- Humans follow `roadmap.md`, the approved baseline plan, chronological
  amendments, the final report, and the handoff.
- Automation reads `metadata.yaml`, `plans/NN-status.yaml`, and append-only
  coordination events.
- Machine-readable relationships are optional. Do not require reviewers to
  reconstruct a dependency graph between baseline sections and amendments.

## Authorization rule

The Markdown baseline plan is the authorization surface. Implementation is
allowed only when its status line explicitly contains `APPROVED`. A status
YAML file cannot grant implementation authority by itself.

After approval, keep the baseline stable. Record situational decisions as
chronological amendments named `PNN-A001`, `PNN-A002`, and so on. Update the
status YAML as execution advances, then compare the result with the baseline
in one final report.

## Default artifact budget

Each plan normally has at most one baseline, status file, amendment log,
runbook, final report, and handoff, plus up to three machine outputs that are
actually consumed by code or review. Record and justify exceptions in the
status file.

## Validation

From the repository root, run:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/governance/validate_experiment.py experiments/<YYYYMMDD_HHMMSS>
```

Historical experiments are not required to be rewritten into this contract.

