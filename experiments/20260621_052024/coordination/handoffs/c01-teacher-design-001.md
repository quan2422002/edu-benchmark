# Specialist handoff

- Delegation ID: `c01-teacher-design-001`
- Agent: `teacher-collaboration-designer`
- Status: completed
- Native thread ID/label: `019ee7ab-846a-7623-93d2-2ebe066ea2ec` / Liaison

## Delegation prompt

Review both mandatory sources and C01 grounding artifacts, classify non-overlapping example types, and prepare the project-lead sample-count decision gate. Do not create the actual example set.

## Follow-up or steer messages

None.

## Inputs read

- `experiments/20260621_052024/plan.md`
- both mandatory curriculum sources
- `grounding/source_registry.csv`
- `grounding/grade9_reference_matrix.csv`
- `grounding/reference_contract.md`
- `grounding/workbook_field_notes.md`
- the workbook as an internal draft reference
- canonical teacher-collaboration instructions

## Outputs created

- Native final response.
- Parent-created `grounding/example_coverage_proposal.md`.
- Parent-created `grounding/teacher_review_questions.md`.
- This handoff and append-only coordination events.

## Result summary

The specialist proposed eight core example types and one conditional cumulative-prerequisite module. The classification uses student evidence/state and tutoring purpose rather than workbook item type, and includes explicit rules preventing duplicate classification. It distinguishes core from optional curriculum topics and provides minimum/better sample counts, effort estimates, variants and coverage checks.

## Orchestrator decision

Accept the classification as the decision-gate proposal. Do not create examples until the project lead approves counts, prerequisite scope, optional topics and local tools/environments.

## Uncertainty

- Tutoring behavior remains provisional until P02 literature evidence is available.
- Local optional-topic selection, software access and programming environment are unknown.
- Estimated effort excludes independent expert-teacher review.

## Open questions and next human decisions

- Choose counts for Types 1–8.
- Decide whether Type 9 cumulative prerequisites are allowed.
- Confirm locally taught optional topics and available tools.
- Confirm programming environment, artifact format, multi-turn requirement and review capacity.
