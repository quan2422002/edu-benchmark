#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/quannda/Kaggle/edu-benchmark"
PYTHON="/home/quannda/miniconda3/envs/benchmark_env/bin/python"
PILOT_ROOT="$ROOT/experiments/20260727_170150/outputs/benchmark_evaluation/pilot_80_v1"
GEMINI_TARGET="$PILOT_ROOT/target_gemini35/run_responses.jsonl"
LLAMA_TARGET="$PILOT_ROOT/target_llama4_maverick/run_responses.jsonl"
LEARNLM_TARGET="$PILOT_ROOT/target_gemini35_learnlm_prompted/run_responses.jsonl"

cd "$ROOT"

for target in "$GEMINI_TARGET" "$LLAMA_TARGET" "$LEARNLM_TARGET"; do
  if [[ ! -f "$target" ]]; then
    echo "Missing completed target run: $target" >&2
    exit 1
  fi
done

"$PYTHON" scripts/benchmark_evaluation/run_claude_judge_smoke.py \
  --run-kind pilot \
  --provider gemini \
  --project edu-benchmark \
  --location global \
  --model gemini-3.5-flash \
  --output-dir "$PILOT_ROOT/judge_gemini35" \
  --system-prompt shared/prompts/benchmark_response_judging/system_prompt_v2.md \
  --target-run "$GEMINI_TARGET" \
  --target-run "$LLAMA_TARGET" \
  --target-run "$LEARNLM_TARGET" \
  --thinking-level medium \
  --max-output-tokens 8192 \
  --concurrency 16 \
  --max-retries 1 \
  --input-usd-per-million 1.50 \
  --output-usd-per-million 9.00 \
  --upper-bound-input-tokens 10000 \
  --actual-spend-to-date-usd 67.00 \
  --hard-budget-usd 250 \
  --reserve-usd 25 \
  --stage-cap-usd 45 \
  --execute-api
