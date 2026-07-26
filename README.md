# Vietnamese Grade-9 Informatics Tutor Benchmark

This repository is building a human-in-the-loop benchmark for evaluating how well large language models tutor Vietnamese grade-9 Informatics students.

## Current status

The project is in the proof-of-concept stage. P01 specialist-agent infrastructure has been approved, and the approved July 1 follow-up added learning-resource and benchmark-specification specialists. After the July 8, 2026 HNMU update, active work has moved to experiment `20260709_155523`: HNMU supplies raw exemplary dialogues and supporting information, while UET owns lossless mapping into the internal author-form structure, task/rubric assignment, and evaluation design. The July 5 experiment remains the versioned source of research synthesis, task/rubric v0, coverage design, and teacher examples. The benchmark taxonomy, production dataset, and evaluation pipeline remain provisional.

Active planning roadmap: [experiments/20260709_155523/roadmap.md](experiments/20260709_155523/roadmap.md)
Previous design roadmap: [experiments/20260705_215045/roadmap.md](experiments/20260705_215045/roadmap.md)
Historical baseline roadmap: [experiments/20260620_115236/roadmap.md](experiments/20260620_115236/roadmap.md)

Approved plans:

- [P01 — Specialist-agent foundation](experiments/20260620_115236/plans/01-specialist-agent-foundation.md)
- [Plan 01 — Specialist expansion for learning resources and benchmark specification](experiments/20260701_100006/plans/01-specialist-expansion-learning-resource-and-benchmark-spec.md)
- [Experiment 20260709 Plan 01 — Benchmark quality literature review](experiments/20260709_155523/plans/01-benchmark-quality-literature-review.md)
- [Experiment 20260709 Plan 02 — Shared data and code layout](experiments/20260709_155523/plans/02-shared-data-and-code-layout.md)
- [Experiment 20260709 Plan 03 — Learning resource normalization phases 0–2, derived PDFs, and OCR probes](experiments/20260709_155523/plans/03-learning-resource-normalization-and-retrieval-system.md)
- [Experiment 20260709 Plan 03.4–03.5 — Fragment and retrieval from Nguyen OCR Markdown](experiments/20260709_155523/plans/03-phase4-5-fragment-and-retrieval-from-nguyen-ocr.md)
- [Experiment 20260709 Plan 04 — HNMU dialogue intake, coverage, consistency, and dedup audit](experiments/20260709_155523/plans/04-hnmu-dialogue-intake-coverage-consistency-dedup.md)
- [Experiment 20260709 Plan 07 — HNMU dialogue auditor specialist](experiments/20260709_155523/plans/07-hnmu-dialogue-auditor-specialist.md)
- [Experiment 20260709 Plan 08 — HNMU dialogue-audit teacher bundle](experiments/20260709_155523/plans/08-hnmu-dialogue-audit-teacher-bundle.md)
- [Experiment 20260709 Plan 08b — HNMU dialogue-audit teacher bundle v2](experiments/20260709_155523/plans/08b-hnmu-dialogue-audit-teacher-bundle-v2.md)

## People and decision authority

- **AI engineers** build the codebase, adapters, validation, provenance, and evaluation infrastructure.
- **Expert teachers** author, review, and adjudicate pedagogical and subject-matter content. Their judgment is required; agents do not replace it.

## Language policy / Quy ước ngôn ngữ

- Code-facing and agent-facing materials should prefer English so future agents can parse and operate reliably. This includes `AGENTS.md`, runtime adapters, validator code, schema/reference docs mainly consumed by agents, and implementation tests.
- Human-facing materials should prefer Vietnamese. This includes plans, meeting notes, reports, handoffs, teacher-facing packets, HNMU-facing review materials, and final summaries to the project lead.
- Mixed-audience files such as this README should keep operational and runtime instructions English-first. Vietnamese can be used where the reader is primarily the project lead, HNMU, or teacher reviewers.
- Keep exact names unchanged for files, commands, field IDs, model/tool names, paper titles, DOI/URL strings, and source quotes.
- Explain unavoidable English terms in Vietnamese when they affect teacher-facing or HNMU-facing understanding.

## Current specialists

- `research-methodologist`: evidence-focused literature review, traceable claims, limitations, and open research questions.
- `learning-resource-curator`: v0 learning-resource source maps, simple learning-material IDs, fragments, topic maps, and grade-6–8 prerequisite grounding for grade 9.
- `benchmark-specification-designer`: benchmark task definitions, rubrics, serious-error catalogs, and provenance matrices grounded in research and learning resources.
- `teacher-collaboration-designer`: teacher-facing author/reviewer/adjudicator workflows, checklists, examples, and handoffs.
- `hnmu-dialogue-auditor`: raw HNMU dialogue audit specialist for checklist-level consistency, SGK/SGV evidence, confidence, and review-queue suggestions before benchmark conversion.

Cost-control defaults are pinned in Codex adapters: `research-methodologist`, `learning-resource-curator`, and `hnmu-dialogue-auditor` use `gpt-5.4-mini` with reasoning `medium`; `benchmark-specification-designer` uses `gpt-5.4-mini` with reasoning `high` for synthesis. Do not spawn multiple instances of the same specialist unless the project lead approves the instance count, rationale, model, reasoning effort, allowed writes, expected output, and merge plan.

The orchestrator delegates to specialists through native observable agent threads:

```text
User → Orchestrator → Specialist thread → Auditable artifact → Human review
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for component and runtime details.

## Runtime support

| Runtime | Status |
|---|---|
| Codex CLI | Runtime smoke-tested target; use `/agent` to inspect and steer specialist threads. |
| Codex App | Supported when native agent activity is visible. |
| Codex IDE Extension | Do not spawn hidden specialists when agent visibility is unavailable; use single-agent mode or switch to CLI/App. |
| Claude Code | Project adapters are generated and statically validated; runtime testing is deferred. |

Interactive specialist work must not be implemented with nested `codex exec`, `claude -p`, daemons, or hidden terminal processes.

## Repository map

```text
agents/                 Canonical specialist skills, references, and validators
.agents/skills/         Skill discovery links for Codex
.codex/agents/          Codex custom-agent adapters
.claude/agents/         Claude project-agent adapters; static validation only
experiments/            Modular plans, coordination records, and reports
shared/                 Shared raw data and learning resources reused across experiments
src/edu_benchmark/      Shared project code for data I/O, audit, conversion, resources, and quality checks
document/               User-provided project source documents
tests/agents/           Agent and documentation tests
```

## Shared data and code layout

Experiment `20260709_155523` Plan 02 established the shared layout:

- HNMU raw dialogue batches live under `shared/raw_data/HNMU-teacher_dialog_samples/` and are registered in `manifest.csv`. Do not edit the raw Excel files directly.
- Shared SGK/SGV learning resources belong under `shared/learning_resources/`. Plan 03 will populate this area with copied SGK images, SGV sources, registries, OCR text, and fragments.
- Processed learning-resource pages should use Markdown with front matter and stable anchors as the temporary human-readable source for review and retrieval indexing. These Markdown pages should be generated from OCR text plus bounding boxes through a layout-reconstruction step, not from plain text alone. JSON/crop debug artifacts are optional and should be generated only when bbox/table/cell-level inspection is needed.
- Nguyen OCR Markdown for SGK/SGV Tin học 6–9 is registered through `shared/learning_resources/registries/ocr_text_manifest.csv` (154 OCR units), split into `shared/learning_resources/fragments/learning_resource_fragments.csv` (2,750 fragments), and indexed through a generated SQLite FTS artifact under `shared/learning_resources/indexes/`. The SQLite file is rebuildable and ignored by Git. `shared/learning_resources/agent_context/` is the navigation hub for audit agents that need the checklist, fragments, index, scaffolding notes, and retrieval tools without copying canonical source files.
- Reusable implementation code belongs under `src/edu_benchmark/`. Experiments should store run outputs, not reusable code.
- Plan 04 dialogue audit v0 reads HNMU raw Excel files through `src/edu_benchmark/data_io/` and `src/edu_benchmark/dialogue_audit/`, then writes experiment-scoped audit tables. The lớp 6–7 audit remains under `experiments/20260709_155523/outputs/hnmu_dialogue_audit/`; the separate lớp 8–9 follow-up audit is under `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/`. Both runs are draft audits and do not replace HNMU/UET subject-matter review.
- Agent-assisted Plan 04 outputs must aggregate the main sample-level `agent_shard_audit/merged/quality_check_suggestions.csv` from criterion-level `raw_dialogue_checklist_results*.csv` with the strict checklist rule implemented in `src/edu_benchmark/dialogue_audit/checklist_aggregation.py` and `scripts/dialogue_audit/sync_quality_suggestions_from_checklist.py`. This file uses the canonical `quality_decision` labels `pass`, `need_human_review`, and `failed`. A sample cannot remain `pass` if any required criterion is `fail` or `uncertain`.
- Plan 08 v1 remains preserved under `experiments/20260709_155523/deliverables/hnmu_dialogue_audit_phase1/`; it is not overwritten by later packaging work.
- Plan 08b now rebuilds the v2 bundle from the repaired grade 6–7 checklist and regex-repaired grade 8–9 checklist. At root, `05_report_fragment_va_ty_le_dat.md` answers one HNMU-facing question about fragment criterion coverage and official pass; `05_phu_luc_ky_thuat_phan_tich_fragment.xlsx` exposes five readable/checking sheets and preserves the original 396 × 29 technical table in a final traceability sheet. Each grade directory retains its eight-row summary and technical appendix. The root also contains shared guidance, the criterion catalog, cross-grade status/lesson coverage, and four combined CSVs; `lop_6/` through `lop_9/` retain grade-only normalized, coverage, overall-status, criterion-detail, missing-field, duplicate, summary, and appendix files. Lesson coverage is left-joined from the complete 75-lesson registry, duplicate detection runs across all 1,050 normalized samples, and teacher-facing paths are portable. The validator reopens every CSV/workbook, verifies 1,050 samples × 18 criteria, source hashes, the six-sheet root appendix, one-sheet workbooks elsewhere, and absence of internal path leaks.


## Project Python environment

The required project environment is the Conda environment `benchmark_env`. The current remote development machine is Ubuntu, so use the Linux executable by default:

```text
Linux:   /home/quannda/miniconda3/envs/benchmark_env/bin/python
Windows: D:\conda-envs\benchmark_env\python.exe
```

Activate it before installing packages or running Python tools:

```bash
conda activate benchmark_env
python -c "import sys; print(sys.executable)"
```

The executable must resolve to one of the paths above. All package installation, Python scripts, validators, and tests must use `benchmark_env`. Do not use Conda base or system Python. For reproducible commands, use the absolute interpreter path.

Install the project dependencies into `benchmark_env`:

```powershell
D:\conda-envs\benchmark_env\python.exe -m pip install -r requirements.txt
```

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip install -r requirements.txt
```

Optional OCR GPU stacks for SGK/SGV image probes:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip install -r requirements-ocr-easyocr-gpu.txt
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip install -r requirements-ocr-paddle-gpu.txt
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip install -r requirements-ocr-paddle-vietocr-cpu.txt
```

Standalone VietOCR GPU recognition should use a separate Conda environment:

```bash
conda create -n ocr_vietocr_gpu python=3.10 -y
conda activate ocr_vietocr_gpu
python -m pip install -r requirements-ocr-vietocr-gpu.txt
```

These optional stacks are intentionally separate from `requirements.txt` because CUDA wheels and OCR model dependencies are large and only needed on OCR workstations. Do not casually mix EasyOCR GPU, PaddleOCR GPU, and VietOCR GPU in one long-lived environment because their CUDA runtime dependencies can conflict. The current best OCR direction from the July 15 probes is PaddleOCR for detection/layout plus VietOCR GPU for Vietnamese recognition, using separate environments: `vgg_transformer` is better for quality, while `vgg_seq2seq` is better for speed. The OCR result should then pass through a layout-reconstruction step before Markdown is written, especially for tables and tables of contents. CPU-only OCR dependencies remain in `requirements-ocr-cpu.txt`.

For Plan 03 Phases 3–5, reusable code belongs under `src/edu_benchmark/learning_resources/`. Thin command-line wrappers, if needed, should live under `scripts/learning_resources/`. Use `benchmark_env` for orchestration, layout reconstruction, Markdown export, fragment/index building, tests, and validation. Use `/home/quannda/miniconda3/envs/ocr_vietocr_gpu/bin/python` only for VietOCR GPU recognition, then pass intermediate OCR outputs back to the `benchmark_env` steps.

Standalone MinerU probes should also use a separate Conda environment because MinerU pulls a large document-parsing stack, including Torch/CUDA runtime packages:

```bash
conda create -n ocr_mineru python=3.11 -y
/home/quannda/miniconda3/envs/ocr_mineru/bin/python -m pip install -r requirements-ocr-mineru-core.txt
```

Use `/home/quannda/miniconda3/envs/ocr_mineru/bin/mineru` only for MinerU library/model probes. Do not install MinerU into `benchmark_env`. The first setup on 2026-07-16 installed `mineru[core]==3.4.4` and confirmed Torch CUDA outside the sandbox on the local RTX 4060 Ti. Model download and parsing are separate follow-up steps.

Plan 03 Phase A now has reusable preparation scripts for book-level MinerU runs. Use `benchmark_env` to create per-book manifests, filtered PDFs, and user-run MinerU commands. By default, the preparation step excludes original pages `1-4` and the final 2 pages of each book from the MinerU input PDF while preserving them in the manifest for traceability:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/prepare_mineru_book_phase_a.py
```

The generated commands are written to:

```text
experiments/20260709_155523/outputs/mineru_book_phase_a/mineru_commands.md
```

Run MinerU itself outside the sandbox with `/home/quannda/miniconda3/envs/ocr_mineru/bin/mineru`, then collect Markdown outputs back with:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/collect_mineru_book_markdown.py
```

After MinerU completes, run the deterministic post-processing step in `benchmark_env` to create cleaned page-level Markdown, a page manifest, and a review queue:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/postprocess_mineru_book_phase.py
```

## Validate current specialists

Linux / current Ubuntu remote:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/research-methodologist
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/learning-resource-curator
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/benchmark-specification-designer
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/hnmu-dialogue-auditor
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/teacher-collaboration-designer
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/agents -q
```


Windows reference:

```powershell
D:\\conda-envs\\benchmark_env\\python.exe `
  C:\\Users\\Admin\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py `
  agents/research-methodologist
D:\\conda-envs\\benchmark_env\\python.exe `
  C:\\Users\\Admin\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py `
  agents/learning-resource-curator
D:\\conda-envs\\benchmark_env\\python.exe `
  C:\\Users\\Admin\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py `
  agents/benchmark-specification-designer
D:\\conda-envs\\benchmark_env\\python.exe `
  C:\\Users\\Admin\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py `
  agents/teacher-collaboration-designer
D:\\conda-envs\\benchmark_env\\python.exe -m pytest tests/agents -q
```

Runtime smoke testing must be performed in an interactive Codex CLI/App session using native subagent tools. It is not run through `codex exec`.

## Working agreements

Agents and contributors must follow [AGENTS.md](AGENTS.md). Architecture changes must update [ARCHITECTURE.md](ARCHITECTURE.md) in the same commit.

Last verified against the current specialist setup on 2026-07-04.
