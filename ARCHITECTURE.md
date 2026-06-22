# System architecture

## Goals and principles

The system supports a human-in-the-loop research workflow for a Vietnamese grade-9 Informatics LLM-tutor benchmark. Its current architecture prioritizes:

- modular plans with explicit file ownership;
- expert-teacher authority over pedagogical and subject-matter decisions;
- canonical specialist definitions with thin runtime adapters;
- native, observable delegation instead of hidden subprocess agents;
- append-only coordination records and artifact-based handoffs;
- fail-closed or single-agent fallback when specialist activity cannot be inspected.

## System context

```mermaid
flowchart LR
    U[Project lead / user] --> O[Orchestrator]
    O --> R[Research methodologist]
    O --> T[Teacher collaboration designer]
    R --> A[Research artifacts]
    T --> A
    A --> H[Expert teachers]
    H --> D[Human decisions and feedback]
    D --> O
```

In plain language: the user directs the orchestrator; the orchestrator delegates bounded tasks to specialists; specialists produce auditable artifacts; expert teachers review pedagogical implications; the orchestrator records and applies the human decisions.

## Components and ownership

| Component | Location | Owner | Status |
|---|---|---|---|
| Canonical specialist skills | `agents/<name>/` | P01 | Implemented by P01 |
| Codex adapters | `.codex/agents/` | P01 | Fresh-session runtime smoke-tested |
| Claude adapters | `.claude/agents/` | P01 | Static validation; runtime deferred |
| Skill discovery links | `.agents/skills/` | P01 | Generated and validated by P01 |
| Coordination contract | `experiments/_templates/` | P01 | Implemented by P01 |
| Modular plans | `experiments/<id>/plans/` | Respective plan | Active |
| F01 rapid evidence review | `experiments/20260621_135515/literature/` | F01 | Ready for expert review; does not complete P02 |
| F01 curriculum source package | `experiments/20260621_135515/curriculum_sources/` | F01 | Two mandatory sources, registry, hashes, and Grade-9 location matrix |
| F01 candidate benchmark framework | `experiments/20260621_135515/benchmark/` | F01 | Ready for expert review; not benchmark v1 |
| F01 teacher workflow and packet | `experiments/20260621_135515/teacher_packet/` | F01 | Ready for expert review; does not complete P03/P04 |
| F01 DOCX handoff | `experiments/20260621_135515/deliverables/` | F01 | Render-validated candidate handoff |
| Durable benchmark specification | Future P05 artifacts | P05 | Not implemented |
| Dataset tooling | Future P06 artifacts | P06 | Not implemented |
| Evaluation pipeline | Future P07 artifacts | P07 | Not implemented |

Canonical logic belongs in `agents/<name>/SKILL.md` and its resources. Runtime adapters may configure discovery and execution but must not fork the workflow logic.

## Delegation sequence

```mermaid
sequenceDiagram
    participant U as User
    participant O as Orchestrator
    participant S as Specialist thread
    participant L as Coordination log
    participant H as Human reviewer
    U->>O: Request work / approve plan
    O->>U: Announce agent, scope, inputs, writes, outputs
    O->>L: Append delegation_started
    O->>S: Spawn native agent with bounded task
    S-->>O: Result, artifacts, uncertainty
    O->>L: Append completion/failure event
    O->>H: Present artifact for domain decision
    H-->>O: Accept, revise, reject, or adjudicate
    O-->>U: Consolidated result and next action
```

The parent thread remains the decision surface. The user can inspect, steer, stop, or reject specialist delegation on supported runtimes.

## Observability model

Every delegation has:

1. a pre-delegation announcement in the parent thread;
2. a native agent thread when the runtime exposes one;
3. append-only events conforming to `experiments/_templates/coordination-event.schema.json`;
4. a handoff based on `experiments/_templates/handoff.md`;
5. paths to inputs and outputs;
6. a summary of the orchestrator decision and unresolved questions.

Observability covers messages exposed by the runtime, tool activity, artifacts, and decisions. It does not expose or claim access to private model chain-of-thought.

## Runtime model

| Surface | Delegation policy |
|---|---|
| Codex CLI | Use native custom-agent threads; inspect and steer with `/agent`. |
| Codex App | Use native threads when agent activity is visible. |
| Codex IDE Extension | If native visibility is unavailable, fail closed or use the canonical skill in the parent thread as single-agent mode. |
| Claude Code | Keep project adapters compatible; P01 does not run Claude runtime tests. |

Nested `codex exec`, `claude -p`, shell daemons, and hidden terminal agents are prohibited for interactive delegation. Non-interactive automation requires a separate approved plan.

## Python environment

The project has one authoritative Conda environment with platform-specific executable paths:

```text
Conda environment: benchmark_env
Windows Python: D:\conda-envs\benchmark_env\python.exe
Linux Python:   /home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Package installation, project scripts, validators, and tests must run with the matching `benchmark_env` interpreter for the active platform. Direct Python dependencies are pinned in `requirements.txt`. Agents must not install project packages into Conda base, system Python, or an ad-hoc virtual environment. Temporary isolated tooling is allowed only when an approved plan explicitly requires it and the result does not represent project validation.

## Permissions and safety

- The orchestrator declares allowed read/write paths before delegation.
- Specialists must stay within delegated paths.
- Unsupported or unobservable delegation fails closed.
- Single-agent fallback loads the canonical skill in the parent thread without pretending that a specialist process exists.
- Existing unrelated user changes are preserved.
- Expert-teacher decisions are recorded, not silently rewritten by agents.

## Dependency direction

P01 owns agent infrastructure and root documentation. F01 consumes the P01 specialists and the C01 grounding package to create a candidate review handoff without changing canonical skills or completing P02–P05. P02 may consume or revise F01 research artifacts; P03/P04 may consume or revise its teacher workflow; P05–P07 own durable benchmark, dataset, and evaluation artifacts respectively.

Later plans must not move canonical logic into runtime adapters or redefine P01 coordination semantics without an explicit architecture decision and migration plan.

## Extension points

- Add a specialist by creating one canonical skill, thin Codex/Claude adapters, tests, and an ownership declaration.
- Add a runtime by writing an adapter and observability policy without changing canonical workflows.
- Add an automated pipeline only through a separately approved non-interactive plan.
- Add architectural decisions as individual ADRs under `docs/decisions/` when the first durable cross-plan decision requires one.

## Known limitations and open decisions

- Codex IDE subagent visibility may be incomplete; CLI/App are the P01 audit surfaces.
- Claude adapters are not runtime-tested in P01.
- Coordination events are file-based and not yet backed by a database or UI.
- Native transcripts depend on runtime retention and do not include private chain-of-thought.
- The F01 task taxonomy and rubric are provisional and await teacher review/calibration; dataset schema and evaluation metrics remain unimplemented.
- Direct Python dependencies are pinned in `requirements.txt`; a complete Conda environment export and transitive lockfile have not yet been assigned to a dedicated plan.

Last verified against P01 and F01 on 2026-06-21.
