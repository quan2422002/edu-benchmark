# Specialist handoff

- Delegation ID: P06-remove-student-work-type-confusion-single-agent-20260708
- Agent: single-agent mode using `teacher-collaboration-designer` skill
- Status: completed
- Native thread ID/label: parent Codex thread; no hidden specialist thread spawned

## Delegation prompt

Remove remaining confusion between the internal coverage label `student_work_type` and the author-form field `student_work` in P06 examples and teacher-facing packet files.

## Follow-up or steer messages

User noticed that some example files still displayed “dạng bài” in places that could be read as part of the student-work field.

## Inputs read

- 13 `teacher_examples/author_form_example_*.md` files
- `teacher_packet/04-examples.md`
- `teacher_packet/05-author-template.md`
- P06 report, plan, and selected coverage registry

## Outputs created or updated

- Removed the “Dạng bài làm/câu hỏi của học sinh” row from the internal table in all 13 example files.
- Rebuilt `teacher_packet/04-examples.md` to show `Bài làm của học sinh` instead of internal type labels.
- Updated template/report/summary wording to keep type labels internal and keep `student_work` concrete.

## Result summary

Teacher-facing examples now show concrete `student_work` content only: assignment/problem plus student work, explicit no-work status, or explicit no-separate-assignment status. Internal type labels remain in CSV tracking only.

## Orchestrator decision

Use this as P06 examples v3 for teacher-facing review. If internal coverage labels are needed later, keep them in UET-facing matrices, not in the author-form example body.

## Uncertainty

The official five formats from Công văn 7991 still need HNMU/UET confirmation.

## Open questions and next human decisions

- Decide whether teacher-facing materials should include any separate field for “loại đề bài/bài làm”, or whether UET should maintain it entirely outside the author form.
