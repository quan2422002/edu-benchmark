#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/quannda/Kaggle/edu-benchmark"
PYTHON="/home/quannda/miniconda3/envs/benchmark_env/bin/python"
GCLOUD="$ROOT/google-cloud-sdk/bin/gcloud"
FULL_ROOT="$ROOT/experiments/20260727_170150/outputs/benchmark_evaluation/full_1400_v1"
BATCH_ROOT="$FULL_ROOT/judge_full_batch_gold_answer_only_v4"
TARGET_GEMINI="$FULL_ROOT/target_gemini35/run_responses.jsonl"
TARGET_LLAMA="$FULL_ROOT/target_llama4_maverick/run_responses.jsonl"
TARGET_LEARNLM="$FULL_ROOT/target_gemini35_learnlm_prompted/run_responses.jsonl"
CANDIDATE_MANIFEST="$FULL_ROOT/candidate_manifest.json"
SYSTEM_PROMPT="$ROOT/shared/prompts/benchmark_response_judging/system_prompt_gold_answer_only_v4.md"
PILOT_ROOT="$FULL_ROOT/judge_cost_pilot_30"
GEMINI_CALIBRATION="$PILOT_ROOT/judge_gemini35_gold_answer_only_v4/run_judgments.jsonl"
OPENAI_CALIBRATION="$PILOT_ROOT/judge_openai_gpt54_mini_medium_gold_answer_only_v4/run_judgments.jsonl"

ACTION="${ACTION:-prepare}"
GCS_BUCKET_URI="${GCS_BUCKET_URI:-gs://edu-benchmark-batch-judge-26637432505}"
VERTEX_REMAINING_BUDGET_VND="${VERTEX_REMAINING_BUDGET_VND:-5270693}"
VERTEX_RESERVE_VND="${VERTEX_RESERVE_VND:-500000}"
VND_PER_USD="${VND_PER_USD:-26299.5}"
OPENAI_STAGE_CAP_USD="${OPENAI_STAGE_CAP_USD:-50}"
POLL_SECONDS="${POLL_SECONDS:-60}"
MAX_BATCH_RETRIES="${MAX_BATCH_RETRIES:-1}"
GEMINI_RETRY_MAX_OUTPUT_TOKENS="${GEMINI_RETRY_MAX_OUTPUT_TOKENS:-}"

cd "$ROOT"

if [[ "$ACTION" == "setup" ]]; then
  if "$GCLOUD" storage buckets describe "$GCS_BUCKET_URI" \
      --project=edu-benchmark >/dev/null 2>&1; then
    echo "Batch bucket already exists: $GCS_BUCKET_URI"
  else
    "$GCLOUD" storage buckets create "$GCS_BUCKET_URI" \
      --project=edu-benchmark \
      --location=US \
      --uniform-bucket-level-access
    echo "Created dedicated batch bucket: $GCS_BUCKET_URI"
  fi
  exit 0
fi

case "$ACTION" in
  prepare|submit|status|collect|watch|retry-submit) ;;
  *)
    echo "ACTION must be setup, prepare, submit, status, collect, watch, or retry-submit." >&2
    exit 2
    ;;
esac

for input in \
  "$TARGET_GEMINI" \
  "$TARGET_LLAMA" \
  "$TARGET_LEARNLM" \
  "$CANDIDATE_MANIFEST" \
  "$SYSTEM_PROMPT" \
  "$GEMINI_CALIBRATION" \
  "$OPENAI_CALIBRATION" \
  "$ROOT/src/.env"; do
  if [[ ! -f "$input" ]]; then
    echo "Missing required input: $input" >&2
    exit 1
  fi
done

read -r VERTEX_REMAINING_USD VERTEX_STAGE_CAP_USD < <(
  "$PYTHON" -c 'import sys
remaining=float(sys.argv[1]); reserve=float(sys.argv[2]); rate=float(sys.argv[3])
if remaining <= reserve or rate <= 0:
    raise SystemExit("Invalid Vertex remaining budget/reserve/exchange rate")
print(remaining/rate, (remaining-reserve)/rate)' \
    "$VERTEX_REMAINING_BUDGET_VND" "$VERTEX_RESERVE_VND" "$VND_PER_USD"
)

API_FLAG=()
if [[ "$ACTION" != "prepare" ]]; then
  API_FLAG=(--execute-api)
fi

COMMON_ARGS=(
  --candidate-manifest "$CANDIDATE_MANIFEST"
  --system-prompt "$SYSTEM_PROMPT"
  --judge-contract gold-answer-only-v4
  --target-run "$TARGET_GEMINI"
  --target-run "$TARGET_LLAMA"
  --target-run "$TARGET_LEARNLM"
  --max-output-tokens 8192
  --max-batch-retries "$MAX_BATCH_RETRIES"
  --poll-seconds "$POLL_SECONDS"
  --budget-safety-multiplier 1.10
)

run_provider() {
  local provider="$1"
  shift
  "$PYTHON" scripts/benchmark_evaluation/run_batch_judge.py \
    "$ACTION" \
    --provider "$provider" \
    "${COMMON_ARGS[@]}" \
    "$@" \
    "${API_FLAG[@]}"
}

status=0

echo "[1/2] Gemini 3.5 Flash asynchronous batch judge: ACTION=$ACTION"
GEMINI_RETRY_TOKEN_ARGS=()
if [[ -n "$GEMINI_RETRY_MAX_OUTPUT_TOKENS" ]]; then
  GEMINI_RETRY_TOKEN_ARGS=(
    --retry-max-output-tokens "$GEMINI_RETRY_MAX_OUTPUT_TOKENS"
  )
fi
run_provider gemini \
  --project edu-benchmark \
  --location global \
  --model gemini-3.5-flash \
  --thinking-level medium \
  --output-dir "$BATCH_ROOT/gemini35" \
  --gcloud-bin "$GCLOUD" \
  --gcs-uri-prefix "$GCS_BUCKET_URI/plan05/full_1400_v1/gemini35_v4" \
  --calibration-judgments "$GEMINI_CALIBRATION" \
  --input-usd-per-million 0.75 \
  --output-usd-per-million 4.50 \
  --stage-cap-usd "$VERTEX_STAGE_CAP_USD" \
  --remaining-budget-usd "$VERTEX_REMAINING_USD" \
  "${GEMINI_RETRY_TOKEN_ARGS[@]}" || status=$?

echo "[2/2] GPT-5.4-mini asynchronous Batch API judge: ACTION=$ACTION"
run_provider openai \
  --model gpt-5.4-mini-2026-03-17 \
  --reasoning-effort medium \
  --output-dir "$BATCH_ROOT/openai_gpt54_mini_medium" \
  --calibration-judgments "$OPENAI_CALIBRATION" \
  --input-usd-per-million 0.375 \
  --output-usd-per-million 2.25 \
  --stage-cap-usd "$OPENAI_STAGE_CAP_USD" \
  --remaining-budget-usd "$OPENAI_STAGE_CAP_USD" || status=$?

if [[ "$status" -ne 0 ]]; then
  echo "At least one provider did not complete ACTION=$ACTION; inspect both batch manifests." >&2
  exit "$status"
fi

echo "Both providers completed ACTION=$ACTION."
echo "Batch root: $BATCH_ROOT"
