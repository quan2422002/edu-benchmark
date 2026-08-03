#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/quannda/Kaggle/edu-benchmark"
PYTHON="/home/quannda/miniconda3/envs/benchmark_env/bin/python"
FULL_ROOT="$ROOT/experiments/20260727_170150/outputs/benchmark_evaluation/full_1400_v1"
PILOT_ROOT="$FULL_ROOT/judge_cost_pilot_30"
CANDIDATE_MANIFEST="$PILOT_ROOT/candidate_manifest.json"
GEMINI_TARGET="$FULL_ROOT/target_gemini35/run_responses.jsonl"
LLAMA_TARGET="$FULL_ROOT/target_llama4_maverick/run_responses.jsonl"
LEARNLM_TARGET="$FULL_ROOT/target_gemini35_learnlm_prompted/run_responses.jsonl"

ACTUAL_SPEND_TO_DATE_USD="${ACTUAL_SPEND_TO_DATE_USD:-93.2647}"
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
for input in \
  "$CANDIDATE_MANIFEST" \
  "$GEMINI_TARGET" \
  "$LLAMA_TARGET" \
  "$LEARNLM_TARGET" \
  "$ROOT/src/.env"; do
  if [[ ! -f "$input" ]]; then
    echo "Missing required input: $input" >&2
    exit 1
  fi
done

echo "OpenAI judge pilot: 30 candidates x 3 target configurations = 90 comparisons."
echo "Model snapshot: gpt-5.4-mini-2026-03-17; reasoning effort: medium."
echo "Output is isolated from the existing Gemini judge bundle."

"$PYTHON" scripts/benchmark_evaluation/run_claude_judge_smoke.py \
  --run-kind cost-pilot \
  --provider openai \
  --model gpt-5.4-mini-2026-03-17 \
  --output-dir "$PILOT_ROOT/judge_openai_gpt54_mini_medium_v1" \
  --candidate-manifest "$CANDIDATE_MANIFEST" \
  --system-prompt shared/prompts/benchmark_response_judging/system_prompt_v2.md \
  --target-run "$GEMINI_TARGET" \
  --target-run "$LLAMA_TARGET" \
  --target-run "$LEARNLM_TARGET" \
  --reasoning-effort medium \
  --max-output-tokens 8192 \
  --concurrency 4 \
  --max-retries 2 \
  --retry-backoff-base-seconds 5 \
  --retry-backoff-max-seconds 30 \
  --retry-jitter-seconds 2 \
  --input-usd-per-million 0.75 \
  --output-usd-per-million 4.50 \
  --upper-bound-input-tokens 10000 \
  --actual-spend-to-date-usd "$ACTUAL_SPEND_TO_DATE_USD" \
  --hard-budget-usd "$HARD_BUDGET_USD" \
  --reserve-usd "$RESERVE_USD" \
  --stage-cap-usd 12 \
  "${API_FLAG[@]}"
