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
SYSTEM_PROMPT="$ROOT/shared/prompts/benchmark_response_judging/system_prompt_gold_answer_only_v4.md"
GEMINI_OUTPUT="$PILOT_ROOT/judge_gemini35_gold_answer_only_v4"
OPENAI_OUTPUT="$PILOT_ROOT/judge_openai_gpt54_mini_medium_gold_answer_only_v4"

ACTUAL_SPEND_TO_DATE_USD="${ACTUAL_SPEND_TO_DATE_USD:-100.274748}"
HARD_BUDGET_USD="${HARD_BUDGET_USD:-250}"
RESERVE_USD="${RESERVE_USD:-25}"
EXECUTE_API="${EXECUTE_API:-0}"
GEMINI_MAX_OUTPUT_TOKENS="${GEMINI_MAX_OUTPUT_TOKENS:-8192}"
OPENAI_MAX_OUTPUT_TOKENS="${OPENAI_MAX_OUTPUT_TOKENS:-8192}"

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
  "$SYSTEM_PROMPT" \
  "$ROOT/src/.env"; do
  if [[ ! -f "$input" ]]; then
    echo "Missing required input: $input" >&2
    exit 1
  fi
done

COMMON_ARGS=(
  --run-kind cost-pilot
  --judge-contract gold-answer-only-v4
  --candidate-manifest "$CANDIDATE_MANIFEST"
  --system-prompt "$SYSTEM_PROMPT"
  --target-run "$GEMINI_TARGET"
  --target-run "$LLAMA_TARGET"
  --target-run "$LEARNLM_TARGET"
  --upper-bound-input-tokens 10000
  --hard-budget-usd "$HARD_BUDGET_USD"
  --reserve-usd "$RESERVE_USD"
)

echo "[1/2] Gemini 3.5 Flash judge — gold-answer-only-v4, 90 comparisons."
"$PYTHON" scripts/benchmark_evaluation/run_claude_judge_smoke.py \
  "${COMMON_ARGS[@]}" \
  --provider gemini \
  --project edu-benchmark \
  --location global \
  --model gemini-3.5-flash \
  --output-dir "$GEMINI_OUTPUT" \
  --max-output-tokens "$GEMINI_MAX_OUTPUT_TOKENS" \
  --thinking-level medium \
  --concurrency 8 \
  --max-retries 1 \
  --retry-backoff-base-seconds 5 \
  --retry-backoff-max-seconds 30 \
  --retry-jitter-seconds 2 \
  --input-usd-per-million 1.50 \
  --output-usd-per-million 9.00 \
  --actual-spend-to-date-usd "$ACTUAL_SPEND_TO_DATE_USD" \
  --stage-cap-usd 16 \
  "${API_FLAG[@]}"

OPENAI_SPEND="$ACTUAL_SPEND_TO_DATE_USD"
if [[ "$EXECUTE_API" == "1" ]]; then
  OPENAI_SPEND="$($PYTHON -c 'import json,sys
p=sys.argv[1]
m=json.load(open(p, encoding="utf-8"))
print(float(sys.argv[2]) + float(m["budget"]["actual_run_cost_usd"]))' \
    "$GEMINI_OUTPUT/run_manifest.json" "$ACTUAL_SPEND_TO_DATE_USD")"
fi

echo "[2/2] GPT-5.4-mini judge — gold-answer-only-v4, 90 comparisons."
"$PYTHON" scripts/benchmark_evaluation/run_claude_judge_smoke.py \
  "${COMMON_ARGS[@]}" \
  --provider openai \
  --model gpt-5.4-mini-2026-03-17 \
  --output-dir "$OPENAI_OUTPUT" \
  --max-output-tokens "$OPENAI_MAX_OUTPUT_TOKENS" \
  --reasoning-effort medium \
  --concurrency 4 \
  --max-retries 2 \
  --retry-backoff-base-seconds 5 \
  --retry-backoff-max-seconds 30 \
  --retry-jitter-seconds 2 \
  --input-usd-per-million 0.75 \
  --output-usd-per-million 4.50 \
  --actual-spend-to-date-usd "$OPENAI_SPEND" \
  --stage-cap-usd 12 \
  "${API_FLAG[@]}"

if [[ "$EXECUTE_API" == "1" ]]; then
  echo "Both gold-answer-only-v4 judge runs completed."
  echo "Gemini output: $GEMINI_OUTPUT"
  echo "OpenAI output: $OPENAI_OUTPUT"
else
  echo "Both gold-answer-only-v4 judge preflights passed; no API was called."
fi
