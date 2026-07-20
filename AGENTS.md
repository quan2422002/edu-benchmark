# Repository agent instructions

Read [README.md](README.md), [ARCHITECTURE.md](ARCHITECTURE.md), and the active roadmap before changing files.

## Required workflow

- Use only the platform-specific `benchmark_env` interpreter for project Python commands, package installation, validators, and tests: `D:\conda-envs\benchmark_env\python.exe` on Windows or `/home/quannda/miniconda3/envs/benchmark_env/bin/python` on Linux. Do not install project packages into Conda base or system Python.
- Do not implement a plan unless its file explicitly says `APPROVED`.
- Modify only paths owned by the active plan; preserve unrelated user changes.
- Announce the specialist name, model when pinned, task, inputs, allowed writes, and expected output before delegation.
- Do not spawn more than one instance of the same specialist for one task unless the user explicitly approves the agent count, reason for fan-out, and expected marginal value.
- Spawn specialists only through native observable subagent threads.
- Never use nested `codex exec`, `claude -p`, daemons, or hidden terminal processes for interactive specialist work.
- Append coordination events and create a handoff using `experiments/_templates/`.
- If native specialist visibility is unavailable, fail closed or load the canonical skill in the parent thread as `single-agent` mode.
- Do not claim access to private chain-of-thought.
- Do not replace expert-teacher judgment on subject matter or pedagogy.
- Use English for code-facing and agent-facing instructions, including `AGENTS.md`, adapter instructions, validator comments, schema/reference docs intended mainly for agents, and implementation tests. Use Vietnamese for human-facing plans, reports, handoffs, teacher-facing materials, HNMU-facing artifacts, and final user summaries. Specialist outputs should follow the audience: Vietnamese for project/HNMU-facing artifacts; English is acceptable inside internal runtime instructions when it improves reliability.
- Run the relevant validation and tests before reporting completion.
- Report the exact Python executable used for validation when it matters to reproducibility.
- Update `ARCHITECTURE.md` with component/runtime/ownership changes and `README.md` with onboarding/status changes.

## Current specialists

Canonical instructions live under `agents/<name>/`; runtime adapters must remain thin and must not fork workflow logic.

- `research-methodologist` — evidence-focused literature review specialist. Codex model pinned to `gpt-5.4-mini`, reasoning `medium`, for token/cost control.
- `learning-resource-curator` — learning-resource mapping specialist for v0 source maps, simple learning-material IDs, fragments, topic maps, and prerequisite grounding. Codex model pinned to `gpt-5.4-mini`, reasoning `medium`.
- `benchmark-specification-designer` — benchmark specification specialist for task definitions, rubrics, serious-error catalogs, and provenance matrices grounded in research and learning resources. Codex model pinned to `gpt-5.4-mini`, reasoning `high`.
- `teacher-collaboration-designer` — teacher-workflow specialist for author/reviewer/adjudicator instructions and teacher-facing materials.
- `hnmu-dialogue-auditor` — raw HNMU dialogue audit specialist for checklist-level consistency, SGK/SGV evidence, confidence, and review-queue suggestions before benchmark conversion. Codex model pinned to `gpt-5.4-mini`, reasoning `medium`.

## Specialist fan-out policy

- Default to one instance of a specialist per task.
- If multiple instances of the same specialist are needed, the user must approve the count, rationale, model, reasoning effort, input split, allowed writes, expected output, and merge plan.
- Parallel specialist branches must write to separate files/directories. The orchestrator or a dedicated synthesis task performs the merge.
