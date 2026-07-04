# Vietnamese Grade-9 Informatics Tutor Benchmark

This repository is building a human-in-the-loop benchmark for evaluating how well large language models tutor Vietnamese grade-9 Informatics students.

## Current status

The project is in the proof-of-concept stage. P01 specialist-agent infrastructure has been approved, and the current approved follow-up adds learning-resource and benchmark-specification specialists after the HNMU meeting on July 1, 2026. The benchmark taxonomy, production dataset, and evaluation pipeline are still provisional until UET/HNMU confirm them.

Active roadmap: [experiments/20260620_115236/roadmap.md](experiments/20260620_115236/roadmap.md)

Approved plans:

- [P01 — Specialist-agent foundation](experiments/20260620_115236/plans/01-specialist-agent-foundation.md)
- [Plan 01 — Specialist expansion for learning resources and benchmark specification](experiments/20260701_100006/plans/01-specialist-expansion-learning-resource-and-benchmark-spec.md)

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

Cost-control defaults are pinned in Codex adapters: `research-methodologist` and `learning-resource-curator` use `gpt-5.4-mini` with reasoning `medium`; `benchmark-specification-designer` uses `gpt-5.4-mini` with reasoning `high` for synthesis. Do not spawn multiple instances of the same specialist unless the project lead approves the instance count, rationale, model, reasoning effort, allowed writes, expected output, and merge plan.

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
document/               User-provided project source documents
tests/agents/           Agent and documentation tests
```

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
