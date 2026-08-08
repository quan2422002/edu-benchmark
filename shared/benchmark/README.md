# Shared benchmark artifacts

This directory is the canonical discovery surface for stable benchmark inputs.
Historical experiments remain immutable provenance and are not deleted.

## What is here

- `artifact_registry.csv`: one row per versioned bundle, including status,
  source, checksum, counts, authority, access policy, and limitations.
- `checklists/raw_dialogue/v1/`: the 18-criterion raw-dialogue audit checklist.
- `datasets/phase1_pass_dialogues/v1/`: 665 dialogue families that passed the
  operational Phase-1 audit; this is not final HNMU approval.
- `datasets/candidate_pool/v1/`: 2,028 validated conversion candidates from the
  665 families, with one-to-one trace and family dispositions.
- `selections/provisional_evaluation_pool/v1/`: a minimal 1,400-ID provisional
  selection plus compact scores/status for all 2,028 candidates. The remaining
  628 require UET review; zero are structurally blocked.
- `specifications/`: the current capability, pedagogical-principle, and rubric
  bundles. Their source status remains `needs_hnmu_review`.

## Status and authority

`shared` means canonical for discovery and consumption, not scientifically
final. The 1,400 selection is a `provisional_evaluation_pool`, never benchmark
v1 or ground truth. Model-derived requirement scores are operational evidence,
not expert labels. Read each manifest before use.

## Access and large/local sources

Tracked payloads were already tracked in their source experiments or are compact
projections of tracked analysis tables. Raw HNMU XLSX, raw model JSONL, provider
responses, and large evaluation outputs are not copied here. Manifests retain
their locators and hashes when they are part of upstream provenance.

## Consumer migration and rollback

The representative migrated consumer is
`scripts/benchmark_specification/build_principle_grounding_pool.py`, whose
default candidate input is now
`shared/benchmark/datasets/candidate_pool/v1/candidates.csv`.

Deprecated source-to-canonical mapping:

| Historical source | Canonical path |
|---|---|
| `.../checklists/raw-dialogue-audit-criteria-v0.csv` | `checklists/raw_dialogue/v1/criteria.csv` |
| `.../benchmark_conversion/conversion_input_pass_samples.csv` | `datasets/phase1_pass_dialogues/v1/dialogues.csv` |
| `.../benchmark_conversion/full_v0/benchmark_candidate_splits.csv` | `datasets/candidate_pool/v1/candidates.csv` |
| `.../benchmark_candidate_pool/eligible_without_plan03_review.csv` | `selections/provisional_evaluation_pool/v1/selection.csv` |

The historical paths remain valid rollback/provenance sources during this
migration; Plan 03 does not delete them.
