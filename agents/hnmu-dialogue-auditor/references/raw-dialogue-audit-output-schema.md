# Raw dialogue audit output schema

This reference defines the CSV schema for `hnmu-dialogue-auditor` outputs. It is schema-focused only; subject-matter judgment remains with HNMU/UET.

## Primary file

`raw_dialogue_checklist_results.csv` is the required detailed output. Each row represents one audit criterion applied to one raw HNMU sample.

## Required columns

| Column | Meaning | Required value rule |
|---|---|---|
| `sample_id` | Stable ID of the raw HNMU row/sample being checked. | Non-empty. Must match the delegated sample list. |
| `criterion_id` | Checklist criterion ID from the raw-dialogue checklist. | Non-empty. Recommended form: `RAW-...`. |
| `criterion_group` | Checklist group, such as coverage, metadata consistency, learning-resource consistency, dialogue quality, scaffolding, or review routing. | Non-empty. |
| `criterion_name` | Human-readable criterion name. | Non-empty Vietnamese label is preferred. |
| `result` | Criterion-level decision. | One of `pass`, `fail`, `uncertain`, `not_applicable`. |
| `confidence_score` | Confidence in this criterion-level decision. | Number from `0.0` to `1.0`. Use lower values for missing, weak, ambiguous, or contradictory evidence. Draft status alone is not a reason to lower confidence when metadata and content match. |
| `evidence_fragment_id` | Fragment ID used as evidence. | Can be empty only when evidence is unavailable, not applicable, or the criterion does not require learning-resource evidence. |
| `evidence_source` | Source name/path for evidence, such as SGK/SGV title, fragment index, or raw row field. | Non-empty when `evidence_fragment_id` is present. |
| `evidence_match_reason` | Why the evidence supports or fails to support the criterion. | Vietnamese explanation preferred. |
| `reason` | Short reason for the decision. | Non-empty for `fail` and `uncertain`; recommended for all rows. |
| `suggested_reviewer_action` | What HNMU/UET or UET should do next. | Non-empty for `fail` and `uncertain`; can be `Không cần hành động` for clear pass. |
| `checked_by` | Agent/human identifier. | Use `hnmu-dialogue-auditor` for agent-generated rows unless delegated otherwise. |
| `checked_at` | Timestamp of the audit decision. | ISO-like timestamp, preferably with timezone. |

## Allowed `result` values

- `pass`: the criterion is satisfied with enough evidence.
- `fail`: the criterion is not satisfied, or there is a clear contradiction.
- `uncertain`: evidence is insufficient, ambiguous, missing, contradictory, or requires HNMU/UET judgment. Do not use `uncertain` solely because a matching fragment is marked `draft`.
- `not_applicable`: the criterion does not apply to this sample.

## Aggregated suggestion files

`quality_check_suggestions.csv` and `hnmu_review_queue_suggestions.csv` are optional during a pilot run. In an approved merged Plan 04 run, `agent_shard_audit/merged/quality_check_suggestions.csv` is the main sample-level review file. The root-level `quality_check_results.csv`, when present, is a quick code/mechanical result and must not be treated as the main agent-audit review file.

`raw_dialogue_checklist_results.csv` is the source of truth for these aggregated files. Do not let a specialist re-interpret sample-level status independently from the detailed checklist. The strict aggregation rule is:

1. if a sample has one or more criterion rows with `result = fail`, its sample-level decision is `failed`;
2. otherwise, if it has one or more rows with `result = uncertain`, its sample-level decision is `need_human_review`;
3. otherwise, if all rows are `pass` or `not_applicable`, its sample-level decision is `pass`.

The sample-level `confidence_score` is confidence in the aggregated decision, not a score for the sample's pedagogical quality. It is derived from criterion-level confidence as follows:

1. `failed`: lowest confidence among failed criteria;
2. `need_human_review`: lowest confidence among uncertain criteria;
3. `pass`: lowest confidence among all criteria for the sample.

Every sample with sample-level `failed` or `need_human_review` must appear in `hnmu_review_queue_suggestions.csv`. Use `src/edu_benchmark/dialogue_audit/checklist_aggregation.py` or `scripts/dialogue_audit/sync_quality_suggestions_from_checklist.py` for synchronized merged outputs.

Canonical columns for `agent_shard_audit/merged/quality_check_suggestions.csv`:

```text
sample_id
source_file
source_row_number
grade
lesson
quality_decision
confidence_score
failure_reasons
blocking_criterion_ids
suggested_reviewer_action
needs_hnmu_review
needs_learning_resource_review
needs_sgv_verification
evidence_fragment_ids
checked_by
checked_at
source_shard
```

Allowed `quality_decision` values:

```text
pass
need_human_review
failed
```

Recommended columns for `hnmu_review_queue_suggestions.csv`:

```text
sample_id
review_reason
priority
suggested_question_to_hnmu
related_criterion_ids
evidence_fragment_ids
checked_by
checked_at
```

## Criteria registry coverage

For Plan 04 audit outputs, `experiments/20260709_155523/reports/raw-dialogue-audit-criteria-v0.csv` is the authoritative per-sample criteria registry. Every `sample_id` must have exactly one row for every `criterion_id` whose `required_per_sample` is `true`. Missing criteria and ad-hoc extra criteria are validation errors.

## Validation expectation

Run `scripts/validate_raw_dialogue_audit_output.py` on every detailed checklist file before using it downstream. By default, the validator checks both CSV schema and per-sample coverage against the criteria registry. Use `--no-criteria-registry` only for legacy schema fixtures, not for Plan 04 audit outputs.
