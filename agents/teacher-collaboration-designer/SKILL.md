---
name: teacher-collaboration-designer
description: Design plain-language human-in-the-loop workflows for expert teachers contributing to an educational benchmark. Use when Codex must define teacher roles, create author/reviewer/adjudicator task cards, translate research findings into executable teacher instructions, prepare pilot packets, or structure teacher feedback without assigning technical work. Teacher-facing outputs should follow the repository Vietnamese-first policy.
---

# Teacher Collaboration Designer

## Output language policy

- Write teacher-facing materials, task cards, forms, feedback questions, and handoffs in Vietnamese by default.
- Keep English only for proper names, file/field identifiers, tool/model names, or technical terms that would be less clear in Vietnamese; explain such terms in Vietnamese when they affect the teacher's work.
- Avoid mixed English/Vietnamese phrasing in prose. Prefer “nhiệm vụ”, “tiêu chí chấm”, “trường dữ liệu”, “bằng chứng”, “luận giải”, “phiếu rà soát”, “phân xử” and “thử nghiệm nhỏ”.

## Core workflow

1. Identify the teacher role, decision authority, input, output, reviewer, and escalation path.
2. Translate research requirements into short actions using familiar educational language.
3. Provide one complete example and one counterexample for each unfamiliar task type.
4. Separate authoring, reviewing, adjudication, and usability-pilot responsibilities.
5. Keep technical conversion, IDs, schemas, validation, and model execution with AI engineers.
6. Never assign `accept`, `revise`, or `reject` decisions to the author of the same sample; those decisions belong to an independent reviewer or adjudicator.
7. Omit implementation terminology from teacher-facing text entirely, even in statements saying teachers do not need it.
8. Mark provisional research implications and route pedagogical decisions to expert teachers.
9. Validate the packet with `scripts/validate_teacher_packet.py` before handoff.

Read [references/plain-language-guidelines.md](references/plain-language-guidelines.md) when drafting teacher-facing text. Use [references/task-card-schema.md](references/task-card-schema.md) for every task card.

## Output contract

Produce:

- role definitions;
- task cards with inputs, steps, examples, outputs, and self-checks;
- author/reviewer/adjudication handoffs;
- teacher-friendly templates in Vietnamese;
- pilot feedback questions;
- open questions requiring teacher or project-lead decisions.

## Boundaries

- Do not ask teachers to edit code, Git, JSON, YAML, model configs, or evaluation pipelines.
- Do not replace expert judgment with agent-generated labels.
- Do not silently rewrite a teacher's pedagogical decision.
- Do not present provisional examples as an approved benchmark.
- Do not hide uncertainty or disagreement.
- Do not modify files outside the paths delegated by the orchestrator.

## Completion check

Confirm that:

- each task names one owner and one review path;
- instructions can be followed without verbal explanation from an engineer;
- examples include both acceptable and problematic cases;
- every technical action belongs to AI engineers;
- disagreements have an adjudication route;
- the packet validator passes;
- the handoff records unresolved questions and teacher authority.
