# Vietnamese Lower-Secondary Informatics Tutor Benchmark

This repository is building a human-in-the-loop benchmark for evaluating how well large language models tutor Vietnamese lower-secondary Informatics students in grades 6–9.

## Current status

Dự án đang ở giai đoạn proof-of-concept nhằm xây dựng benchmark gia sư AI môn Tin học THCS lớp 6–9. Experiment cải tổ repository `20260806_145124` đang là roadmap active; Plan 01–04 đã hoàn tất governance, packaging, shared benchmark registry và cấu hình/đường dẫn khả chuyển cho quy trình Section V đại diện. Plan 05 đang chờ project lead duyệt. Experiment benchmark `20260727_170150` vẫn là nguồn hiện trạng khoa học: đã khóa 1.400 candidate ưu tiên, sinh đủ 1.400 response cho ba target và hoàn thành full judge `gold-answer-only-v4` bằng Gemini cùng GPT, mỗi judge có đúng 4.200 phán quyết hợp lệ. Rubric, score model, instruction và phán quyết của model vẫn là kết quả tạm thời, chưa phải ground truth hoặc nội dung HNMU đã xác nhận. Bản thảo KSE nằm tại `kse_submit_manuscript/`.

Judge cost-pilot v2 đã hoàn thành 90/90 phép chấm cho cả Gemini 3.5 Flash
và `gpt-5.4-mini-2026-03-17`. Đối chiếu phát hiện thành phần lỗi nghiêm
trọng không ổn định theo response đối đầu. Theo quyết định UET, contract
`rubric-only-v3` loại phần này khỏi cả system/user prompt, output model và
hậu xử lý; các trường tương thích trong record được giữ rỗng. Wrapper chung
cho hai judge đã hoàn thành đúng 90 phép so sánh mỗi mô hình, không ghi đè
bundle v2. Gemini và GPT đạt agreement 86,7% ở overall và 77,2% ở cấp
rubric; điểm tổng hợp kiểu KMP-Bench cùng xếp LearnLM-prompted cao nhất,
Gemini baseline thứ hai và Llama Maverick thứ ba. Cost-pilot vẫn chỉ là
bằng chứng thăm dò vì có 30 candidate và Gemini vừa là target vừa là judge.

Audit fragment trên 30 candidate cho thấy 2 mẫu có evidence sai, 20 mẫu có
evidence không đủ và chỉ 8 mẫu đủ hoặc gần đủ ở cấp candidate. UET vì vậy
đã mở contract `gold-answer-only-v4`: giữ nguyên v2/v3, bỏ fragment khỏi
judge input, dùng `gold_answer` làm neo duy nhất cho `RUB-GEN-ACC` và ghi
policy loại evidence trong manifest/record. Đoạn này ghi trạng thái lịch sử
trước khi v4 được chạy đủ và cổng batch được UET mở.

Lần chạy trả phí v4 đầu tiên giữ được 88/90 phán quyết Gemini; hai lỗi còn
lại là một biến thể tên tiêu chí tương đương và một output `MAX_TOKENS`.
Recovery đã được cô lập cho v4: chuẩn hóa đúng alias đã biết, chỉ chạy bù
hai request Gemini ở 12.288 token rồi mới chạy GPT ở giới hạn 8.192 token.

V4 hiện đã hoàn thành 90/90 cho cả Gemini và GPT. UET đã mở full judge cho
1.400 candidate × ba target bằng hai judge. Pipeline Batch API mới giữ
nguyên prompt/hậu xử lý v4, tách hoàn toàn khỏi runner synchronous, dùng p95
usage của pilot để khóa ngân sách. Sau collect và recovery, cả Gemini và
GPT đều hoàn thành 4.200/4.200 request; wrapper hoạt động là
`scripts/benchmark_evaluation/run_full_1400_judge_batch.sh`.

Phân tích Section V đã được tái lập hoàn toàn bằng code trên hai full judge
bundle. Artifact tinh gọn chứa instruction ablation, độ bền vững giữa hai
judge và descriptive position sensitivity tại
`experiments/20260727_170150/outputs/benchmark_evaluation/section_v_ablation_analysis_v1/results.json`;
mọi cổng 4.200/38.832 và các anchor đã khóa đều đạt. Không có model call mới
trong bước này.

Active repository-refactor roadmap: [experiments/20260806_145124/roadmap.md](experiments/20260806_145124/roadmap.md)
Current benchmark/evaluation roadmap: [experiments/20260727_170150/roadmap.md](experiments/20260727_170150/roadmap.md)
Previous phase-2 construction roadmap: [experiments/20260722_000940/roadmap.md](experiments/20260722_000940/roadmap.md)
Previous raw-dialogue audit roadmap: [experiments/20260709_155523/roadmap.md](experiments/20260709_155523/roadmap.md)
Previous design roadmap: [experiments/20260705_215045/roadmap.md](experiments/20260705_215045/roadmap.md)
Historical baseline roadmap: [experiments/20260620_115236/roadmap.md](experiments/20260620_115236/roadmap.md)

Approved plans:

- [Experiment 20260722 Plan 01 — Raw-dialogue to benchmark-candidate conversion contract and pilot](experiments/20260722_000940/plans/01-audited-raw-dialogue-to-benchmark-candidate-conversion.md)
- [Experiment 20260722 Plan 02 — Multi-candidate conversion from every tutor turn](experiments/20260722_000940/plans/02-split-policy-and-full-benchmark-conversion.md)
- [Experiment 20260722 Plan 03 — Measurement foundations, six capabilities, six KMP principles, and two-tier rubrics](experiments/20260722_000940/plans/03-thcs-task-rubric-specification-and-coverage.md)
- [P01 — Specialist-agent foundation](experiments/20260620_115236/plans/01-specialist-agent-foundation.md)
- [Plan 01 — Specialist expansion for learning resources and benchmark specification](experiments/20260701_100006/plans/01-specialist-expansion-learning-resource-and-benchmark-spec.md)
- [Experiment 20260709 Plan 01 — Benchmark quality literature review](experiments/20260709_155523/plans/01-benchmark-quality-literature-review.md)
- [Experiment 20260709 Plan 02 — Shared data and code layout](experiments/20260709_155523/plans/02-shared-data-and-code-layout.md)
- [Experiment 20260709 Plan 03 — Learning resource normalization phases 0–2, derived PDFs, and OCR probes](experiments/20260709_155523/plans/03-learning-resource-normalization-and-retrieval-system.md)
- [Experiment 20260709 Plan 03.4–03.5 — Fragment and retrieval from Nguyen OCR Markdown](experiments/20260709_155523/plans/03-phase4-5-fragment-and-retrieval-from-nguyen-ocr.md)
- [Experiment 20260709 Plan 04 — HNMU dialogue intake, coverage, consistency, and dedup audit](experiments/20260709_155523/plans/04-hnmu-dialogue-intake-coverage-consistency-dedup.md)
- [Experiment 20260709 Plan 07 — HNMU dialogue auditor specialist](experiments/20260709_155523/plans/07-hnmu-dialogue-auditor-specialist.md)

Current plans:

- [Experiment 20260727 Plan 01 — Principle requirement-score specification](experiments/20260727_170150/plans/01-principle-requirement-score-specification.md)
- [Experiment 20260727 Plan 02 — Vertex AI requirement-scoring pilot](experiments/20260727_170150/plans/02-vertex-ai-requirement-scoring-pilot.md)
- [Experiment 20260727 Plan 03 — Full-run statistics and analysis](experiments/20260727_170150/plans/03-full-run-statistics-and-analysis.md)
- [Experiment 20260727 Plan 04 — Two-tier rubric library](experiments/20260727_170150/plans/04-two-tier-rubric-library.md)
- [Experiment 20260727 Plan 05 — Benchmark evaluation configuration](experiments/20260727_170150/plans/05-benchmark-evaluation-configuration.md)

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
- `pedagogical-principle-annotator`: specialist thử nghiệm của phương pháp Plan 03 cũ; các run đã trở thành diagnostic legacy. Experiment active dùng Vertex AI API trực tiếp cho `requirement_score`, không dùng specialist này để chấm từng candidate.

Cost-control defaults are pinned in Codex adapters: `research-methodologist`, `learning-resource-curator`, `hnmu-dialogue-auditor`, and `pedagogical-principle-annotator` use `gpt-5.4-mini` with reasoning `medium`; `benchmark-specification-designer` uses `gpt-5.4-mini` with reasoning `high` for synthesis. Do not spawn multiple instances of the same specialist unless the project lead approves the instance count, rationale, model, reasoning effort, allowed writes, expected output, and merge plan.

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
docs/decisions/         Durable architecture decision records (ADRs)
experiments/            Plans, machine-readable status, runbooks, coordination, and reports
pyproject.toml           Src-layout package metadata and dependency groups
environment.yml          Human-maintained Conda environment specification
shared/benchmark/       Versioned benchmark registry, canonical datasets, selections, and provisional specifications
shared/                 Shared raw data, learning resources, prompts, and benchmark artifacts
src/edu_benchmark/      Shared project code for data I/O, audit, conversion, resources, and quality checks
src/edu_benchmark/experiment_runtime/ Portable YAML config, path resolution, preflight, and offline execution
scripts/benchmark_registry/ Thin CLI for deterministic shared benchmark promotion/validation
scripts/governance/     Thin CLI for experiment-governance validation
src/vertex_ai_call/     Vertex AI pilot runner for six-principle requirement scoring
document/               User-provided project source documents
kse_submit_manuscript/  KSE 2026 writing plan, LaTeX source, evidence registry, and releases
tests/agents/           Agent and documentation tests
```

## Shared data and code layout

Experiment `20260709_155523` Plan 02 established the shared layout:

- Canonical benchmark discovery begins at `shared/benchmark/README.md` and
  `shared/benchmark/artifact_registry.csv`. The registry points to the
  18-criterion checklist, 665 Phase-1 dialogues, 2,028-candidate conversion
  pool, provisional 1,400-candidate selection with the 628/0 backlog state, and
  provisional capability/principle/rubric bundles. Each bundle has a manifest
  with source hashes, counts, authority, access policy, and limitations.
- HNMU raw dialogue batches live under `shared/raw_data/HNMU-teacher_dialog_samples/` and are registered in `manifest.csv`. Do not edit the raw Excel files directly.
- Shared SGK/SGV learning resources belong under `shared/learning_resources/`. Plan 03 will populate this area with copied SGK images, SGV sources, registries, OCR text, and fragments.
- Processed learning-resource pages should use Markdown with front matter and stable anchors as the temporary human-readable source for review and retrieval indexing. These Markdown pages should be generated from OCR text plus bounding boxes through a layout-reconstruction step, not from plain text alone. JSON/crop debug artifacts are optional and should be generated only when bbox/table/cell-level inspection is needed.
- Nguyen OCR Markdown for SGK/SGV Tin học 6–9 is registered through `shared/learning_resources/registries/ocr_text_manifest.csv` (154 OCR units), split into `shared/learning_resources/fragments/learning_resource_fragments.csv` (2,750 fragments), and indexed through a generated SQLite FTS artifact under `shared/learning_resources/indexes/`. The SQLite file is rebuildable and ignored by Git. `shared/learning_resources/agent_context/` is the navigation hub for audit agents that need the checklist, fragments, index, scaffolding notes, and retrieval tools without copying canonical source files.
- Reusable implementation code belongs under `src/edu_benchmark/`. Experiments should store run outputs, not reusable code.
- Plan 04 dialogue audit v0 reads HNMU raw Excel files through `src/edu_benchmark/data_io/` and `src/edu_benchmark/dialogue_audit/`, then writes experiment-scoped audit tables. The lớp 6–7 audit remains under `experiments/20260709_155523/outputs/hnmu_dialogue_audit/`; the separate lớp 8–9 follow-up audit is under `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/`. Both runs are draft audits and do not replace HNMU/UET subject-matter review.
- Agent-assisted Plan 04 outputs must aggregate the main sample-level `agent_shard_audit/merged/quality_check_suggestions.csv` from criterion-level `raw_dialogue_checklist_results*.csv` with the strict checklist rule implemented in `src/edu_benchmark/dialogue_audit/checklist_aggregation.py` and `scripts/dialogue_audit/sync_quality_suggestions_from_checklist.py`. This file uses the canonical `quality_decision` labels `pass`, `need_human_review`, and `failed`. A sample cannot remain `pass` if any required criterion is `fail` or `uncertain`.

## Experiment governance

New experiments use [experiments/_templates/README.md](experiments/_templates/README.md).
The concise Markdown plan is the approval surface; a machine-readable status
file cannot grant implementation authority. After approval, situational changes
go into one chronological amendment log rather than rewriting the baseline.

Validate a governed experiment from the repository root with:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/governance/validate_experiment.py experiments/20260806_145124
```

The validator checks metadata, explicit approval, lifecycle/status consistency,
roadmap links, amendment references, coordination JSONL, registered artifacts,
and the default artifact budget. Historical experiments remain valid provenance
and do not require a cosmetic migration.

## Portable experiment runtime

Plan 04 established a config-driven runtime under
`src/edu_benchmark/experiment_runtime/`. Runtime YAML files use only
repository-relative paths. Loading fails closed on path escape, missing files,
checksum/count mismatch, unknown fields, or serialized credential material.

The representative Section V config is
`experiments/20260806_145124/configs/section-v-ablation-v1.yaml`. Preflight and
execution use the same command from the repository root or another working
directory after the editable package is installed:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  -m edu_benchmark.experiment_runtime preflight \
  --config experiments/20260806_145124/configs/section-v-ablation-v1.yaml

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  -m edu_benchmark.experiment_runtime run \
  --config experiments/20260806_145124/configs/section-v-ablation-v1.yaml
```

This representative run is offline and requires no provider credential. Its
two large judge JSONL inputs remain historical experiment artifacts rather than
clean-clone CI fixtures; unit tests use self-contained temporary fixtures.


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

Create the environment from the repository root:

```bash
conda env create -f environment.yml
conda activate benchmark_env
```

For an existing `benchmark_env`, synchronize direct dependencies and install
the src-layout package editable:

```powershell
D:\conda-envs\benchmark_env\python.exe -m pip install -r requirements.txt
D:\conda-envs\benchmark_env\python.exe -m pip install --no-deps -e .
```

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip install -r requirements.txt
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip install --no-deps -e .
```

`pyproject.toml` separates core, `dev`, and `providers` dependency groups.
`requirements.txt` intentionally installs their union for the current full
runner environment. Direct dependencies and Python 3.12 are pinned; transitive
pip/Conda packages are not yet fully locked, so `environment.yml` is not a
bit-for-bit lockfile.

The offline GitHub Actions workflow has two clean-clone lanes. The first installs
only `.[dev]` and runs provider-independent tests. The second installs the full
runner requirements and runs self-contained offline tests without credentials.
Tests that consume intentionally ignored raw XLSX or experiment JSONL remain
local integration tests and are not clean-clone CI gates.

After installation, verify import portability from outside the repository:

```bash
cd /tmp
/home/quannda/miniconda3/envs/benchmark_env/bin/python -I -c \
  "import edu_benchmark, vertex_ai_call; print(edu_benchmark.__file__); print(vertex_ai_call.__file__)"
```

The earlier PaddleOCR, VietOCR, and MinerU extraction attempts did not become a
supported repository workflow. Their experimental code, tests, and environment
files are retained only in the project lead's ignored local workspace for
historical reference; they are not part of the tracked package or the
`benchmark_env` reproducibility contract. Do not rely on those local files from
a clean clone. The active learning-resource path consumes the registered Nguyen
OCR Markdown and uses the tracked manifest, fragment, and retrieval modules.

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
