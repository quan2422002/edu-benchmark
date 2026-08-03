#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/quannda/Kaggle/edu-benchmark"
PYTHON="/home/quannda/miniconda3/envs/benchmark_env/bin/python"
FULL_ROOT="$ROOT/experiments/20260727_170150/outputs/benchmark_evaluation/full_1400_v1"
GEMINI_TARGET="$FULL_ROOT/target_gemini35/run_responses.jsonl"
LLAMA_TARGET="$FULL_ROOT/target_llama4_maverick/run_responses.jsonl"

: "${ACTUAL_SPEND_TO_DATE_USD:?Set ACTUAL_SPEND_TO_DATE_USD after all target runs complete.}"
HARD_BUDGET_USD="${HARD_BUDGET_USD:-250}"
RESERVE_USD="${RESERVE_USD:-25}"
EXECUTE_API="${EXECUTE_API:-0}"

if [[ "$EXECUTE_API" != "0" && "$EXECUTE_API" != "1" ]]; then
  echo "EXECUTE_API must be 0 (preflight) or 1 (paid API run)." >&2
  exit 1
fi
API_FLAG=()
if [[ "$EXECUTE_API" == "1" ]]; then
  API_FLAG=(--execute-api)
fi

cd "$ROOT"

for target in "$GEMINI_TARGET" "$LLAMA_TARGET"; do
  if [[ ! -f "$target" ]]; then
    echo "Missing completed full target run: $target" >&2
    exit 1
  fi
done

echo "Conservative judge upper bound: 496.8768 USD for 2,800 comparisons."
echo "The default 250 USD hard budget is expected to block this stage."

"$PYTHON" scripts/benchmark_evaluation/run_claude_judge_smoke.py \
  --run-kind full \
  --provider gemini \
  --project edu-benchmark \
  --location global \
  --model gemini-3.5-flash \
  --output-dir "$FULL_ROOT/judge_gemini35" \
  --system-prompt shared/prompts/benchmark_response_judging/system_prompt_v2.md \
  --target-run "$GEMINI_TARGET" \
  --target-run "$LLAMA_TARGET" \
  --thinking-level medium \
  --max-output-tokens 8192 \
  --concurrency 16 \
  --max-retries 1 \
  --input-usd-per-million 1.50 \
  --output-usd-per-million 9.00 \
  --upper-bound-input-tokens 10000 \
  --actual-spend-to-date-usd "$ACTUAL_SPEND_TO_DATE_USD" \
  --hard-budget-usd "$HARD_BUDGET_USD" \
  --reserve-usd "$RESERVE_USD" \
  --stage-cap-usd 497 \
  "${API_FLAG[@]}"
