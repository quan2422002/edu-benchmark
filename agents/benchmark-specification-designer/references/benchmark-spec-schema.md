# Benchmark specification schema v0

Use CSV artifacts for deterministic validation during the PoC. Markdown summaries may accompany these files, but CSV is the validator target.

## `benchmark_tasks.csv`

Required columns:

```text
task_id, task_name, definition, scope, input_requirements, output_requirements, status, research_ids, learning_material_ids, teacher_decision_needed
```

Rules:

- `task_id` must be unique and stable.
- `status` must be `draft`, `needs_uet_review`, `needs_hnmu_review`, `confirmed`, or `retired`.
- A confirmed task should have both research grounding and learning-resource grounding.
- If grounding is missing, keep status as `needs_uet_review` or `needs_hnmu_review` and explain the decision need.

## `rubrics.csv`

Required columns:

```text
rubric_id, task_id, criterion, observable_evidence, score_levels, status
```

Rules:

- `rubric_id` must be unique.
- `task_id` must exist in `benchmark_tasks.csv`.
- `criterion` and `observable_evidence` must be concrete enough for a teacher or reviewer to inspect.

## `serious_errors.csv`

Required columns:

```text
error_id, description, suggested_action, affected_rubric_ids, status
```

Rules:

- `error_id` must be unique.
- `affected_rubric_ids` must reference known rubric IDs.
- `suggested_action` should say whether the issue normally triggers review, revision, exclusion, or score cap; HNMU must confirm final policy.

## `provenance_matrix.csv`

Required columns:

```text
item_id, item_type, research_ids, learning_material_ids, rationale, status
```

Allowed `item_type` values:

```text
task, rubric, serious_error
```

Rules:

- `item_id` must exist in the corresponding task/rubric/error file.
- `research_ids` and `learning_material_ids` may contain `;` or `,` separated IDs.
- If both evidence columns are empty, status must indicate that review is still needed.
