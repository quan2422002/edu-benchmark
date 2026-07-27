# Two-pass unordered-set pedagogical-principle annotation contract

This is the agent-facing operational contract for Plan-03 schema v3. Vietnamese
project documents remain canonical for scientific definitions and authority.

## Runtime reading and provenance

Read these compact CSV files completely:

1. `experiments/20260722_000940/outputs/benchmark_specification/task_discovery/pedagogical_principles.csv`
2. `experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/tutor_capabilities.csv`
3. `experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/capability_overlap_matrix.csv`

Verify, but open only for unresolved boundaries:

4. `experiments/20260722_000940/outputs/benchmark_specification/task_discovery/task_discovery_codebook.md`
5. `experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/tutor_capability_model.md`

The grounding manifest locks all five documents, this contract, and the skill.
The principle table decides labels. Capability tables describe how well a
response performs; capability IDs are never principle labels.

Do not read
`experiments/20260722_000940/outputs/benchmark_specification/legacy/eight_task_candidate_branch/`
during annotation.

## Principle-set rule

Allison and Tharby describe the principles as interrelated and flexibly
connected. KMP-Bench selects one or two while planning a tutor action, but does
not establish two as a universal limit for post-hoc annotation.

Assign an unordered subset of:

- `PRINCIPLE-CHALLENGE`
- `PRINCIPLE-EXPLANATION`
- `PRINCIPLE-MODELLING`
- `PRINCIPLE-PRACTICE`
- `PRINCIPLE-FEEDBACK`
- `PRINCIPLE-QUESTIONING`

There is no primary/secondary order and no hard two-label limit. For every
selected principle, apply the indispensability test:

> If this principle is removed, does an independent pedagogical need of the
> learner remain unmet?

Do not select a principle when it is only surface form, incidental wording, or
an uncertainty marker. More than three selected principles is allowed but must
enter the review queue with `high_label_count`.

Functional boundaries:

- `Challenge`: raise cognitive demand or preserve productive struggle.
- `Explanation`: make a concept, relation, method, or reason clear.
- `Modelling`: demonstrate a procedure, thought process, decision path, or exemplar.
- `Practice`: require learner performance to build memory, fluency, or independence.
- `Feedback`: judge observable learner work or reasoning to guide improvement.
- `Questioning`: require a learner answer for diagnosis, reasoning continuity, or deeper thought.

## Input isolation

Pass 1 contains exactly:

```text
benchmark_candidate_id
sample_id
grade
lesson
position
bloom_level
student_prompt
conversation_history
```

Pass 2 contains those fields plus:

```text
source_question
gold_answer
```

Both views must have identical ordered `(benchmark_candidate_id, sample_id)`
pairs. `source_question` is materialized by code through `sample_id`; never
trace raw snapshots yourself.

Neither input may contain `gold_response`. Never retrieve or infer it. Labels
must be reconstructed only from evidence available before the target tutor
response.

`gold_answer` is a subject-matter anchor, not a pedagogical-strategy label. It
does not mechanically determine Questioning, Explanation, Modelling, Practice,
Feedback, or Challenge.

## Candidate metadata schema

Both `principle_annotation_pass1.csv` and
`principle_annotation_final.csv` use:

```text
benchmark_candidate_id
sample_id
student_state_summary
coverage_gap_reason
grounding_effect
grounding_change_reason
coder_id
review_status
adjudication_status
```

Pass 1 uses `grounding_effect=not_seen` and an empty
`grounding_change_reason`. Final `grounding_effect` is:

- `unchanged`: code finds no set/gap change;
- `changed`: code finds a set/gap change;
- `conflict`: context and grounding support incompatible interpretations.

The annotator may declare only semantic `conflict`. The reconciler derives
`changed` and `unchanged`.

Exactly one condition is true for each candidate:

- at least one principle-label row exists and `coverage_gap_reason` is empty;
- no principle-label row exists and `coverage_gap_reason` is non-empty.

Every AI row uses `review_status=needs_uet_review` and leaves
`adjudication_status` empty.

## Principle-label relation schema

Both `principle_annotation_pass1_labels.csv` and
`principle_annotation_final_labels.csv` use one row per
candidate–principle pair:

```text
benchmark_candidate_id
principle_id
selection_rationale
context_evidence
grounding_evidence
coder_id
review_status
```

Requirements:

- no duplicate candidate–principle pair;
- `selection_rationale` explains the independent indispensable function;
- `context_evidence` points to observable prompt/history evidence;
- pass-1 `grounding_evidence` is empty;
- final `grounding_evidence` may cite `source_question` or `gold_answer`;
- never cite `gold_response`;
- label rows use the same coder ID and `needs_uet_review`.

## Grounding stability

Pass 1 asks what a good response must do based on pre-target context. Pass 2
adds source-task and answer grounding, not a reference response.

- Keep the set unchanged when grounding only confirms subject matter.
- Change the set only when new, context-compatible grounding changes an
  indispensable pedagogical function.
- Use `conflict` when grounding is incompatible with a context-indispensable
  function; preserve the context-supported set and route to UET.
- Do not add Questioning merely because a source question is phrased as a question.
- Do not add Explanation merely because `gold_answer` contains explanatory text.
- Do not use the union of two passes merely to preserve uncertainty.

## Review queue

Use:

```text
benchmark_candidate_id
sample_id
coder_id
review_reason_codes
context_principle_set
final_principle_set
context_coverage_gap_reason
final_coverage_gap_reason
grounding_change_reason
suggested_reviewer_action
```

Allowed semicolon-separated reason codes:

```text
label_set_changed
coverage_decision_changed
context_grounding_conflict
coverage_gap
high_label_count
principle_boundary_ambiguous
codebook_clarification_proposed
```

The deterministic reconciler inserts mandatory rows for set/gap changes and
sets above three labels.

## Required output files

Write only inside the delegated run directory:

```text
principle_annotation_pass1.csv
principle_annotation_pass1_labels.csv
principle_annotation_final.csv
principle_annotation_final_labels.csv
principle_annotation_review_queue.csv
principle_annotation_run_manifest.json
handoff.md
```

The run manifest uses version `plan03-principle-annotation-run-v3` and records
coder ID, model, reasoning effort, input-manifest SHA-256, candidate count,
timestamps, validation status, and `closed=true` only after completion.

The Vietnamese handoff reports scope, paths, counts by principle, set changes,
gaps, conflicts, high-label-count cases, uncertainty, and required UET review.
It must not claim labels are confirmed.
