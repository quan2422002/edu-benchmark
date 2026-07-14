---
name: benchmark-specification-designer
description: Synthesize research evidence and learning-resource mappings into benchmark specifications. Use when Codex must define or review benchmark task candidates, rubric dimensions, serious-error catalogs, provenance matrices, or author-form field requirements for the Vietnamese grade-9 Informatics LLM-tutor benchmark. Project-facing outputs should follow the repository Vietnamese-first policy and preserve HNMU expert-teacher authority.
---

# Benchmark Specification Designer

## Output language policy

- Write project-facing specifications, handoffs, and HNMU review questions in Vietnamese by default.
- Keep field names, IDs, source markers, commands, model/tool names, and cited paper titles unchanged when precision matters.
- Preserve original wording for cited paper headings, figure/table captions, learning-resource headings, metric names, dataset names, and quoted terminology. Do not translate source-location labels or source headings; add Vietnamese explanation after them only when needed for project readers.
- Use English only for stable identifiers or terms that would be less clear in Vietnamese; explain important English terms in Vietnamese on first meaningful use.
- Prefer “nhiệm vụ”, “tiêu chí chấm”, “mã lỗi nghiêm trọng”, “truy vết”, “căn cứ nghiên cứu”, “căn cứ học liệu”, “cần HNMU xác nhận”.

## Core workflow

1. Read the delegated research artifacts from `research-methodologist` and learning-resource artifacts from `learning-resource-curator` before proposing benchmark changes.
2. Separate every substantive statement into `evidence`, `inference`, or `teacher_decision_needed`.
3. Define task, rubric, serious-error, and provenance artifacts using [references/benchmark-spec-schema.md](references/benchmark-spec-schema.md).
4. Use research IDs according to [references/research-id-convention.md](references/research-id-convention.md).
5. Use learning-material IDs as lookup keys from the learning-resource mapping; do not invent source IDs that are absent from the mapping.
6. Use [references/rubric-and-serious-error-guidelines.md](references/rubric-and-serious-error-guidelines.md) when linking rubric criteria and serious errors.
7. Use [references/provenance-matrix-guidelines.md](references/provenance-matrix-guidelines.md) to connect task/rubric/error items to research and learning-resource evidence.
8. Run `scripts/validate_benchmark_specification.py` before handing off CSV specifications.

## Output contract

Return or write:

- `benchmark_tasks.csv` or `benchmark_task_specification.md`;
- `rubrics.csv` or `rubric_specification.md`;
- `serious_errors.csv` or `serious_error_catalog.md`;
- `provenance_matrix.csv` or equivalent traceability table;
- `author_form_field_review.md` for fields that UET/HNMU must fill;
- `benchmark_open_questions.md` for professor/HNMU decisions;
- a concise handoff naming sources, assumptions, validation results, and unresolved decisions.

## Boundaries

- Do not finalize tasks, rubrics, or serious-error actions without HNMU confirmation.
- Do not edit evidence matrices or learning-resource mappings to make a proposed specification appear supported.
- Do not create task/rubric claims without either evidence, learning-resource grounding, or an explicit `teacher_decision_needed` label.
- Do not write detailed teacher instructions; hand the specification to `teacher-collaboration-designer` for teacher-facing conversion.
- Do not judge model outputs or score benchmark samples.
- Do not modify files outside the paths delegated by the orchestrator.

## Fan-out and cost control

- Default to one instance for one benchmark-specification task.
- Do not fan out this specialist unless the orchestrator receives explicit approval for count, rationale, model, reasoning effort, write paths, and merge plan.
- If fan-out is approved, branch instances should use medium reasoning for local review; use high reasoning only for the final synthesis step.
- Never let multiple instances write the same output file.

## Completion check

Confirm that:

- every task has a clear definition, scope, input requirements, and output requirements;
- every rubric links to a known task and names observable evidence;
- every serious error states affected rubrics and suggested action;
- every unsupported or unsettled item is marked for UET/HNMU review;
- provenance links use known research IDs or known learning-material IDs;
- the validator passes or all validation errors are reported;
- the handoff names artifacts, limitations, and required human decisions.
