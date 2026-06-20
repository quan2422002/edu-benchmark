# Vietnamese Grade-9 Informatics Tutor Benchmark

This repository is building a human-in-the-loop benchmark for evaluating how well large language models tutor Vietnamese grade-9 Informatics students.

## Current status

The project is in the proof-of-concept stage. The current approved work establishes specialist-agent infrastructure before conducting a broader literature review. The benchmark taxonomy, production dataset, and evaluation pipeline are not yet approved or implemented.

Active roadmap: [experiments/20260620_115236/roadmap.md](experiments/20260620_115236/roadmap.md)

Approved plan: [P01 — Specialist-agent foundation](experiments/20260620_115236/plans/01-specialist-agent-foundation.md)

## People and decision authority

- **AI engineers** build the codebase, adapters, validation, provenance, and evaluation infrastructure.
- **Expert teachers** author, review, and adjudicate pedagogical and subject-matter content. Their judgment is required; agents do not replace it.

## Active specialists

- `research-methodologist`: runs traceable evidence reviews and separates evidence, inference, and open questions.
- `teacher-collaboration-designer`: turns research requirements into clear authoring and review tasks for teachers.

The orchestrator delegates to specialists through native agent threads:

```text
User → Orchestrator → Specialist thread → Auditable artifact → Human review
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for component and runtime details.

## Runtime support

| Runtime | P01 status |
|---|---|
| Codex CLI | Runtime smoke-tested target; use `/agent` to inspect and steer specialist threads. |
| Codex App | Supported when native agent activity is visible. |
| Codex IDE Extension | Do not spawn hidden specialists when agent visibility is unavailable; use single-agent mode or switch to CLI/App. |
| Claude Code | Project adapters are generated and statically validated; runtime testing is deferred. |

Interactive specialist work must not be implemented with nested `codex exec`, `claude -p`, daemons, or hidden terminal processes.

## Repository map

```text
agents/                 Canonical specialist skills, references, and validators
.agents/skills/         Repository skill discovery links for Codex
.codex/agents/          Codex custom-agent adapters
.claude/agents/         Claude project-agent adapters (static validation only)
experiments/            Modular plans, coordination records, and reports
document/               Project source material supplied by the user
tests/agents/           P01 validation and documentation tests
```

## Project Python environment

The required project environment is the Conda environment `benchmark_env`:

```text
/home/quannda/miniconda3/envs/benchmark_env
```

Activate it before installing packages or running Python tools:

```bash
conda activate benchmark_env
python -c "import sys; print(sys.executable)"
```

The executable must resolve to `/home/quannda/miniconda3/envs/benchmark_env/bin/python`. All package installation, Python scripts, validators, and tests must use this environment. For commands that cannot rely on shell activation, use the absolute interpreter path.

Install the project dependencies into `benchmark_env`:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip install -r requirements.txt
```

## Validate P01

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/research-methodologist
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/teacher-collaboration-designer
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/agents -q
```

Runtime smoke testing must be performed in an interactive Codex CLI/App session using native subagent tools. It is not run through `codex exec`.

## Working agreements

Agents and contributors must follow [AGENTS.md](AGENTS.md). Architecture changes must update [ARCHITECTURE.md](ARCHITECTURE.md) in the same commit.

Last verified against P01 on 2026-06-20.
