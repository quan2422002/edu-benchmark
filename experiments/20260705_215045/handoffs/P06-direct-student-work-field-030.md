# Specialist handoff

- Delegation ID: P06-direct-student-work-field-single-agent-20260708
- Agent: single-agent mode using `teacher-collaboration-designer` skill
- Status: completed
- Native thread ID/label: parent Codex thread; no hidden specialist thread spawned

## Delegation prompt

Revise P06 examples so the author-form field `Bài làm của học sinh` contains only the student's actual work, except image submissions which should use the image. Do not include explanations or assignment text in this field.

## Follow-up or steer messages

User clarified: “ngoại trừ là dạng ảnh, hãy viết thẳng bài làm của học sinh vào đó, KHÔNG CẦN giải thích gì”.

## Inputs read

- 13 `teacher_examples/author_form_example_*.md` files
- `teacher_packet/04-examples.md`
- `teacher_packet/05-author-template.md`
- P06 report, plan, and field reference

## Outputs created or updated

- Updated all 13 example files: `student_work` now contains only direct student work or `Chưa có bài làm.`
- Updated `teacher_examples/author_form_counterexample.md`.
- Updated `teacher_examples/author_form_field_reference_v0.csv`.
- Updated `teacher_packet/04-examples.md` and `teacher_packet/05-author-template.md`.
- Updated P06 report/summary/plan wording.

## Result summary

The `student_work` field is now direct and minimal. Assignment context remains in `student_prompt`/conversation context, not in `student_work`.

## Orchestrator decision

Use this as P06 examples v4 for teacher-facing review.

## Uncertainty

If HNMU wants the original assignment text preserved in a separate field, the author form may need a future `problem_statement` or equivalent field. This revision does not add such a field.

## Open questions and next human decisions

- Decide whether the author form should eventually include a separate `Đề bài` field.
