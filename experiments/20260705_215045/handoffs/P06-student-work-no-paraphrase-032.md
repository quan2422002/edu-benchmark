# Specialist handoff

- Delegation ID: P06-student-work-no-paraphrase-single-agent-20260708
- Agent: single-agent mode using `teacher-collaboration-designer` skill
- Status: completed
- Native thread ID/label: parent Codex thread; no hidden specialist thread spawned

## Delegation prompt

Clarify P06 `student_work`: the problem statement remains in the field, but the student-answer part must not be paraphrased as “học sinh chọn/làm...”.

## Follow-up or steer messages

User clarified that the issue is not the presence of the problem statement, but the paraphrasing of the student work in the `Bài làm` part.

## Inputs read

- 13 `teacher_examples/author_form_example_*.md` files
- `teacher_packet/04-examples.md`
- `teacher_packet/05-author-template.md`
- P06 report, summary, and field reference

## Outputs created or updated

- Updated no-assignment examples to avoid explanatory wording inside `Đề bài`.
- Updated `author_form_field_reference_v0.csv` and `05-author-template.md` to require direct student answer/work text.
- Rebuilt `04-examples.md` from current fields.
- Updated P06 report/summary wording.

## Result summary

`student_work` now keeps `Đề bài`, and the `Bài làm` portion is direct: answer, sentence, formula, code, or product description, not a paraphrase like “học sinh chọn A”.

## Orchestrator decision

Use this as P06 examples v6 for teacher-facing review.

## Uncertainty

Some product-based examples still use a concise textual description of the product because no image file is attached.

## Open questions and next human decisions

- Confirm whether product-based examples should include actual screenshots/images in future packets.
