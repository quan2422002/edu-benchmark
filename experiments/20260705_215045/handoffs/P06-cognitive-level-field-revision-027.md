# Specialist handoff

- Delegation ID: P06-cognitive-level-field-revision-single-agent-20260707
- Agent: single-agent mode using `benchmark-specification-designer`, `teacher-collaboration-designer`, and Google Sheets/Drive read workflow
- Status: completed
- Native thread ID/label: parent Codex thread; no hidden specialist thread spawned

## Delegation prompt

Update P06 examples and teacher packet after the project lead provided a new `review_form.xlsx` where `Mức độ nhận thức` is an official author-form field.

## Follow-up or steer messages

User clarified that the new author form has a `Mức độ nhận thức` column with three values: Biết, Hiểu, Vận dụng.

## Inputs read

- Google Drive file `review_form.xlsx`, ID `1EhlzymX71I9q_dC42B8PPyAlBa1jcVfV`, modified `2026-07-07T16:08:49.622Z`.
- Existing P06 field reference, examples, teacher packet, report, and plan.

## Outputs created or updated

- Updated `teacher_examples/author_form_field_reference_v0.csv` with `cognitive_level`.
- Updated 13 `teacher_examples/author_form_example_*.md` files with `Mức độ nhận thức` as field 4.
- Updated `teacher_examples/author_form_counterexample.md` with the same field and error explanation.
- Updated `teacher_packet/04-examples.md` and `teacher_packet/05-author-template.md`.
- Updated `reports/P06-teacher-examples-and-packet-summary.md`.
- Updated P06 plan status.

## Result summary

`Mức độ nhận thức` is no longer treated only as internal coverage metadata. It is now represented as an official author-form field with valid values Biết, Hiểu, and Vận dụng.

## Orchestrator decision

Use this as P06 author-form-aligned v1. Keep task-code mismatch between local T1–T4 and Drive T01–T07 as an open mapping issue until UET/HNMU decides whether to migrate task codes.

## Uncertainty

- The new Drive workbook contains task codes T01–T07, while current P04/P05/P06 local artifacts use T1–T4. This was not changed in this revision to avoid silently migrating the task taxonomy.
- The Drive workbook is an Office `.xlsx` opened in Google Sheets, not a native Google Sheet; it was read through Drive raw/text extraction rather than Sheets API metadata.

## Open questions and next human decisions

- Decide whether P04/P05/P06 should migrate task IDs from T1–T4 to T01–T07 or keep an explicit mapping table.
- Confirm final capitalization/order of cognitive-level values. Current local convention uses Biết, Hiểu, Vận dụng.
