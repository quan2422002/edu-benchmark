#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/quannda/Kaggle/edu-benchmark"
PYTHON="/home/quannda/miniconda3/envs/benchmark_env/bin/python"
FULL_ROOT="$ROOT/experiments/20260727_170150/outputs/benchmark_evaluation/full_1400_v1"
SOURCE_ROOT="$FULL_ROOT/target_gemini35_learnlm_prompted"
RECOVERY_ROOT="/tmp/edu-benchmark-plan05-learnlm-recovery-2048"
RECOVERY_MANIFEST="$RECOVERY_ROOT/candidate_manifest.json"
BUNDLE="$ROOT/shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v3_learnlm.yaml"
EXPECTED_CANDIDATE_COUNT="386"

: "${ACTUAL_SPEND_TO_DATE_USD:?Set ACTUAL_SPEND_TO_DATE_USD to 84.48388625 or a newer estimate.}"
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

"$PYTHON" scripts/benchmark_evaluation/recover_truncated_targets.py \
  build \
  --source-output "$SOURCE_ROOT/run_responses.jsonl" \
  --source-manifest "$SOURCE_ROOT/run_manifest.json" \
  --output "$RECOVERY_MANIFEST" \
  --max-output-tokens 2048

CANDIDATE_COUNT="$($PYTHON -c 'import json,sys; print(json.load(open(sys.argv[1]))["candidate_count"])' "$RECOVERY_MANIFEST")"
if [[ "$CANDIDATE_COUNT" != "$EXPECTED_CANDIDATE_COUNT" ]]; then
  echo "Unexpected LearnLM recovery count: $CANDIDATE_COUNT; expected $EXPECTED_CANDIDATE_COUNT." >&2
  exit 1
fi

echo "Recovering exactly $CANDIDATE_COUNT truncated LearnLM-prompted responses."
echo "max_output_tokens=2,048; conservative upper bound with two retries: 27.250056 USD."

COMMAND=(
  "$PYTHON" scripts/benchmark_evaluation/run_vertex_smoke.py
  --run-kind recovery
  --provider gemini
  --project edu-benchmark
  --location global
  --model gemini-3.5-flash
  --output-dir "$RECOVERY_ROOT"
  --candidate-manifest "$RECOVERY_MANIFEST"
  --instruction-bundle "$BUNDLE"
  --max-candidates "$CANDIDATE_COUNT"
  --max-output-tokens 2048
  --seed 20260728
  --concurrency 20
  --max-retries 2
  --upper-bound-input-tokens 3400
  --input-usd-per-million 1.50
  --output-usd-per-million 9.00
  --actual-spend-to-date-usd "$ACTUAL_SPEND_TO_DATE_USD"
  --hard-budget-usd "$HARD_BUDGET_USD"
  --reserve-usd "$RESERVE_USD"
  --stage-cap-usd 27.26
)
"${COMMAND[@]}" "${API_FLAG[@]}"

if [[ "$EXECUTE_API" == "1" ]]; then
  "$PYTHON" scripts/benchmark_evaluation/recover_truncated_targets.py \
    merge \
    --source-output "$SOURCE_ROOT/run_responses.jsonl" \
    --source-manifest "$SOURCE_ROOT/run_manifest.json" \
    --recovery-output "$RECOVERY_ROOT/run_responses.jsonl" \
    --recovery-manifest "$RECOVERY_MANIFEST" \
    --recovery-run-manifest "$RECOVERY_ROOT/run_manifest.json"
  "$PYTHON" -c 'import shutil,sys; shutil.rmtree(sys.argv[1])' \
    "$RECOVERY_ROOT"
  echo "LearnLM recovery merged in place; temporary staging was removed."
else
  "$PYTHON" -c 'import shutil,sys; shutil.rmtree(sys.argv[1])' \
    "$RECOVERY_ROOT"
  echo "Preflight only; canonical LearnLM bundle was not modified."
fi
