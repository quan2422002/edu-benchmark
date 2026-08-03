#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
BENCHMARK_PYTHON="/home/quannda/miniconda3/envs/benchmark_env/bin/python"

if [[ ! -x "${BENCHMARK_PYTHON}" ]]; then
  echo "benchmark_env Python not found: ${BENCHMARK_PYTHON}" >&2
  exit 1
fi

cd "${PROJECT_ROOT}"

# This command calls the paid Claude API through Vertex AI.
exec "${BENCHMARK_PYTHON}" \
  scripts/benchmark_evaluation/run_claude_judge_smoke.py \
  --project edu-benchmark \
  --location us-east5 \
  --model claude-sonnet-4-6 \
  --output-dir experiments/20260727_170150/outputs/benchmark_evaluation/judge_smoke_claude_blind_v2 \
  --system-prompt shared/prompts/benchmark_response_judging/system_prompt_v2.md \
  --target-run experiments/20260727_170150/outputs/benchmark_evaluation/smoke_gemini35_instruction_v2/run_smoke.jsonl \
  --target-run experiments/20260727_170150/outputs/benchmark_evaluation/smoke_llama4_maverick_instruction_v2_retry1/run_smoke.jsonl \
  --temperature 0 \
  --max-output-tokens 3072 \
  --concurrency 2 \
  --max-retries 2 \
  --input-usd-per-million 3.30 \
  --output-usd-per-million 16.50 \
  --upper-bound-input-tokens 10000 \
  --actual-spend-to-date-usd 56.52 \
  --hard-budget-usd 250 \
  --reserve-usd 25 \
  --stage-cap-usd 2 \
  --execute-api \
  "$@"
