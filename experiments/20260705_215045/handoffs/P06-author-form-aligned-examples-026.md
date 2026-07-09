# Specialist handoff

- Delegation ID: P06-author-form-alignment-single-agent-20260707
- Agent: single-agent mode using `benchmark-specification-designer` and `teacher-collaboration-designer` skills
- Status: completed
- Native thread ID/label: parent Codex thread; no hidden specialist thread spawned

## Delegation prompt

Align P06 teacher examples with the actual author-form fields defined in sheet “Luận giải chi tiết trường dữ liệu” of `experiments/20260701_100006/drive_snapshot/files/teacher_packet/review_form.xlsx`.

## Follow-up or steer messages

User clarified that the previous examples were too loose and must be based on the author form.

## Inputs read

- `experiments/20260701_100006/drive_snapshot/files/teacher_packet/review_form.xlsx`
- `experiments/20260705_215045/benchmark_design/benchmark_tasks.csv`
- `experiments/20260705_215045/benchmark_design/rubrics.csv`
- `experiments/20260705_215045/topic_taxonomy/tin9_sgk_topics_v0.csv`
- `experiments/20260705_215045/coverage_design/coverage_axis_values_v0.csv`
- Existing P06 teacher examples and teacher packet files.

## Outputs created

- `teacher_examples/author_form_field_reference_v0.csv`
- Updated `teacher_examples/selected_coverage_cells_v0.csv`
- Updated `teacher_examples/author_form_example_*.md`
- Updated `teacher_examples/author_form_counterexample.md`
- Updated `teacher_examples/example_coverage_summary.md`
- Updated `teacher_packet/04-examples.md`
- Updated `teacher_packet/05-author-template.md`
- Updated `reports/P06-teacher-examples-and-packet-summary.md`

## Result summary

The example set now follows the author-form fields directly. Coverage metadata is preserved as internal traceability, but every example now includes author name, task ID, topic, student prompt, student work, conversation history, reference learning materials, gold response, accepted alternatives, Likert rubric scores, truthfulness score, boundary-adherence scores, cross-validator field, timestamps, and notes.

## Orchestrator decision

Use this version as the P06 v0 teacher-facing example packet. Do not treat the examples as final dataset records until HNMU reviews task names, topic labels, and learning-resource references.

## Uncertainty

- Page numbers and topic labels still depend on the v0 SGK Tin học 9 table of contents/OCR and need HNMU/UET confirmation.
- The author-form sheet references five official student-work formats from Công văn 7991, but P06 still uses the project’s current v0 student-work-type labels for internal coverage.

## Open questions and next human decisions

- HNMU should confirm whether the current task names T1–T4 are acceptable in the author form.
- HNMU/UET should confirm whether the current SGK Tin học 9 lesson/page references are sufficiently precise for pilot authoring.
