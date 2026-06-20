# Repository agent instructions

Read [README.md](README.md), [ARCHITECTURE.md](ARCHITECTURE.md), and the active roadmap before changing files.

## Required workflow

- Use only `/home/quannda/miniconda3/envs/benchmark_env/bin/python` for project Python commands, package installation, validators, and tests. Do not install project packages into Conda base or system Python.
- Do not implement a plan unless its file explicitly says `APPROVED`.
- Modify only paths owned by the active plan; preserve unrelated user changes.
- Announce the specialist name, task, inputs, allowed writes, and expected output before delegation.
- Spawn specialists only through native observable subagent threads.
- Never use nested `codex exec`, `claude -p`, daemons, or hidden terminal processes for interactive specialist work.
- Append coordination events and create a handoff using `experiments/_templates/`.
- If native specialist visibility is unavailable, fail closed or load the canonical skill in the parent thread as `single-agent` mode.
- Do not claim access to private chain-of-thought.
- Do not replace expert-teacher judgment on subject matter or pedagogy.
- Run the relevant validation and tests before reporting completion.
- Report the exact Python executable used for validation when it matters to reproducibility.
- Update `ARCHITECTURE.md` with component/runtime/ownership changes and `README.md` with onboarding/status changes.

## Current P01 specialists

- `research-methodologist`
- `teacher-collaboration-designer`

Canonical instructions live under `agents/<name>/`; runtime adapters must remain thin.
