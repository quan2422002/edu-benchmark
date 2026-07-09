# Specialist handoff

- Delegation ID: P06-student-work-semantics-revision-single-agent-20260708
- Agent: single-agent mode using `teacher-collaboration-designer` skill
- Status: completed
- Native thread ID/label: parent Codex thread; no hidden specialist thread spawned

## Delegation prompt

Revise P06 examples so the author-form field `Bài làm của học sinh` is not confused with the internal student-work-type/category axis.

## Follow-up or steer messages

User clarified that `Bài làm của học sinh` should mean the concrete assignment/problem and the student's actual work if present. If there is no work, state that clearly. If there is no assignment/work, the `student_prompt` is simply the student's direct question. Example 6 was specifically identified as unclear.

## Inputs read

- `experiments/20260705_215045/teacher_examples/author_form_example_*.md`
- `experiments/20260705_215045/teacher_packet/05-author-template.md`
- `experiments/20260705_215045/teacher_examples/author_form_field_reference_v0.csv`

## Outputs created or updated

- Updated all 13 `teacher_examples/author_form_example_*.md` files.
- Updated `teacher_examples/author_form_counterexample.md`.
- Updated `teacher_examples/author_form_field_reference_v0.csv`.
- Updated `teacher_examples/selected_coverage_cells_v0.csv`.
- Updated `teacher_examples/example_coverage_summary.md`.
- Updated `teacher_packet/04-examples.md` and `teacher_packet/05-author-template.md`.
- Updated `reports/P06-teacher-examples-and-packet-summary.md`.

## Result summary

`student_work` now follows a teacher-readable convention: write the assignment/problem and the student's work when available; write that the student has no work yet when applicable; write that there is no separate assignment/work when the student only asks a direct question.

## Orchestrator decision

Use this version as P06 author-form examples v2. Keep internal `student_work_type` only as a coverage-control field, not as the content of the author-form `student_work` field.

## Uncertainty

The project still needs HNMU/UET confirmation on the official five student-work formats referenced by Công văn 7991.

## Open questions and next human decisions

- Decide whether to add a separate visible field for “dạng bài” in future author forms, or keep it internal to UET coverage tracking.
- Confirm whether every example with a scenario should explicitly label it as `Đề bài/tình huống`.
