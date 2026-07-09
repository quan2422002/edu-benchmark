# Specialist handoff

- Delegation ID: P06-student-work-includes-problem-statement-single-agent-20260708
- Agent: single-agent mode using `teacher-collaboration-designer` skill
- Status: completed
- Native thread ID/label: parent Codex thread; no hidden specialist thread spawned

## Delegation prompt

Revise P06 examples after user clarified that the problem statement/assignment must remain inside the author-form field `Bài làm của học sinh`.

## Follow-up or steer messages

User clarified: “đề bài vẫn nằm trong student_work nhé”.

## Inputs read

- 13 `teacher_examples/author_form_example_*.md` files
- `teacher_packet/04-examples.md`
- `teacher_packet/05-author-template.md`
- P06 report, plan, and field reference

## Outputs created or updated

- Updated all 13 examples so `student_work` contains `Đề bài: ...` and `Bài làm: ...`.
- Updated counterexample, field reference, teacher packet summary, author template, P06 summary/report/plan.

## Result summary

The `student_work` field now includes both assignment/problem statement and student work, with no extra explanation beyond those two parts.

## Orchestrator decision

Use this as P06 examples v5 for teacher-facing review.

## Uncertainty

If future forms split `Đề bài` into a separate field, this convention should be migrated deliberately rather than edited silently.

## Open questions and next human decisions

- Confirm whether direct student questions with no separate assignment should keep `Đề bài: Không có đề bài riêng; học sinh hỏi trực tiếp: ...`.
