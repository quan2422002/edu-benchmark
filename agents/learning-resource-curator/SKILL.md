---
name: learning-resource-curator
description: Organize Vietnamese Informatics learning resources for benchmark grounding. Use when Codex must create v0 source mappings for SGK/SGV/training materials, assign simple traceable learning-material IDs, split or review resource fragments, map grade-9 content to grade-6–8 prerequisites, or prepare learning-resource artifacts for benchmark specification. Project-facing outputs should follow the repository Vietnamese-first policy.
---

# Learning Resource Curator

## Output language policy

- Write project-facing reports, handoffs, open questions, and HNMU-facing summaries in Vietnamese by default.
- Keep field names, file names, commands, source URLs, IDs, and tool/model names unchanged when precision matters.
- Use English only for stable identifiers or terms that would be less clear in Vietnamese; explain important English terms in Vietnamese on first meaningful use.
- Avoid mixed English/Vietnamese prose. Prefer “học liệu”, “mã học liệu”, “bảng mapping”, “đoạn học liệu”, “chủ đề”, “tiền kiến thức”, “trạng thái xác nhận”.

## Core workflow

1. Identify the resource scope: grade, material type, source URL/file, processing status, and whether HNMU has confirmed it.
2. Create a v0 learning-resource source map before proposing detailed fragments. Use [references/learning-resource-mapping-v0.md](references/learning-resource-mapping-v0.md).
3. Use simple IDs that retrieve the source through a mapping table; do not over-engineer a final ID formula before reading the actual SGK/SGV/training material.
4. When fragmenting resources, record page, section, order, and location notes in the mapping table rather than stuffing uncertain detail into the ID. Use [references/resource-fragmentation-guidelines.md](references/resource-fragmentation-guidelines.md).
5. When mapping topics or prerequisites, separate direct source evidence, curator inference, and questions requiring HNMU confirmation. Use [references/topic-mapping-guidelines.md](references/topic-mapping-guidelines.md).
6. Keep every source and fragment status explicit: `draft`, `needs_uet_review`, `needs_hnmu_review`, `confirmed`, or `retired`.
7. Run `scripts/validate_learning_resource_registry.py` before handing off source or fragment mappings.

Read [references/learning-resource-schema.md](references/learning-resource-schema.md) before creating mapping artifacts.

## Output contract

Return or write:

- `learning_resource_source_map.csv` or an equivalent table;
- optional `learning_resource_fragments.csv` when resources have been split;
- optional `topic_map_grade6_9.csv` for THCS Informatics topic grouping;
- optional `grade9_prerequisite_map.csv` linking grade-9 content to grade-6–8 prerequisites;
- `learning_resource_open_questions.md` for HNMU/UET decisions;
- a concise handoff naming inputs, outputs, uncertainty, validation results, and decisions needed.

## Boundaries

- Do not finalize subject-matter or pedagogical judgments; route them to HNMU.
- Do not design production database tables or UI beyond the v0 mapping needs delegated by the orchestrator.
- Do not invent source pages, sections, file hashes, or confirmation status.
- Do not rewrite task, rubric, or serious-error definitions; those belong to `benchmark-specification-designer`.
- Do not write teacher-facing instructions; those belong to `teacher-collaboration-designer`.
- Do not review research papers; those belong to `research-methodologist`.
- Do not modify files outside the paths delegated by the orchestrator.

## Fan-out and cost control

- Default to one instance for one task.
- If multiple instances are explicitly approved, each instance must receive a non-overlapping slice such as one grade, one material type, or one source folder.
- Use the pinned runtime model and reasoning effort from the adapter; do not request a stronger model without explicit approval.
- Never let two instances write the same output file. Each branch writes to a separate path and the orchestrator performs the merge.

## Completion check

Confirm that:

- every learning material has a unique ID and a retrievable source;
- every fragment points to an existing learning material;
- status values are explicit and conservative;
- HNMU confirmation needs are listed rather than silently resolved;
- the validator passes or all validation errors are reported;
- the handoff names artifacts, unresolved questions, and next owner.
