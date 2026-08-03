#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/quannda/Kaggle/edu-benchmark"
PYTHON="/home/quannda/miniconda3/envs/benchmark_env/bin/python"
RECOVERY_ROOT="/tmp/edu-benchmark-plan05-gemini-recovery-1536"
FOLLOWUP_ROOT="$RECOVERY_ROOT/followup_2048"
FOLLOWUP_MANIFEST="$FOLLOWUP_ROOT/candidate_manifest.json"
BUNDLE="$ROOT/shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v2.yaml"

: "${ACTUAL_SPEND_TO_DATE_USD:?Set ACTUAL_SPEND_TO_DATE_USD to 72.557325 or a newer estimate.}"
HARD_BUDGET_USD="${HARD_BUDGET_USD:-250}"
RESERVE_USD="${RESERVE_USD:-25}"
EXECUTE_API="${EXECUTE_API:-0}"

if [[ "$EXECUTE_API" != "0" && "$EXECUTE_API" != "1" ]]; then
  echo "EXECUTE_API must be 0 (preflight) or 1 (paid API run)." >&2
  exit 1
fi
for required in \
  "$RECOVERY_ROOT/candidate_manifest.json" \
  "$RECOVERY_ROOT/run_responses.jsonl" \
  "$RECOVERY_ROOT/run_manifest.json"; do
  if [[ ! -f "$required" ]]; then
    echo "Missing required first-pass recovery artifact: $required" >&2
    exit 1
  fi
done

API_FLAG=()
if [[ "$EXECUTE_API" == "1" ]]; then
  API_FLAG=(--execute-api)
fi

cd "$ROOT"

"$PYTHON" scripts/benchmark_evaluation/recover_truncated_targets.py \
  build-followup --max-output-tokens 2048

CANDIDATE_COUNT="$($PYTHON -c 'import json,sys; print(json.load(open(sys.argv[1]))["candidate_count"])' "$FOLLOWUP_MANIFEST")"
REUSED_COUNT="$($PYTHON -c 'import json,sys; print(json.load(open(sys.argv[1]))["parent_completed_count"])' "$FOLLOWUP_MANIFEST")"
if [[ "$CANDIDATE_COUNT" != "19" || "$REUSED_COUNT" != "417" ]]; then
  echo "Unexpected recovery state: reuse=$REUSED_COUNT follow_up=$CANDIDATE_COUNT; expected 417 and 19." >&2
  exit 1
fi

echo "Reusing $REUSED_COUNT completed responses from the 1,536-token pass."
echo "Recovering only $CANDIDATE_COUNT remaining responses at max_output_tokens=2,048."
echo "Conservative follow-up upper bound with two retries: 1.307124 USD."

COMMAND=(
  "$PYTHON" scripts/benchmark_evaluation/run_vertex_smoke.py
  --run-kind recovery
  --provider gemini
  --project edu-benchmark
  --location global
  --model gemini-3.5-flash
  --output-dir "$FOLLOWUP_ROOT"
  --candidate-manifest "$FOLLOWUP_MANIFEST"
  --instruction-bundle "$BUNDLE"
  --max-candidates "$CANDIDATE_COUNT"
  --max-output-tokens 2048
  --seed 20260728
  --concurrency 19
  --max-retries 2
  --upper-bound-input-tokens 3000
  --input-usd-per-million 1.50
  --output-usd-per-million 9.00
  --actual-spend-to-date-usd "$ACTUAL_SPEND_TO_DATE_USD"
  --hard-budget-usd "$HARD_BUDGET_USD"
  --reserve-usd "$RESERVE_USD"
  --stage-cap-usd 1.31
)
"${COMMAND[@]}" "${API_FLAG[@]}"

if [[ "$EXECUTE_API" == "1" ]]; then
  "$PYTHON" scripts/benchmark_evaluation/recover_truncated_targets.py \
    finalize-followup
  "$PYTHON" scripts/benchmark_evaluation/recover_truncated_targets.py merge
  "$PYTHON" -c 'import shutil,sys; shutil.rmtree(sys.argv[1])' \
    "$RECOVERY_ROOT"
  echo "Follow-up finalized and all 436 recovery records merged in place."
  echo "Temporary staging was removed."
else
  "$PYTHON" -c 'import shutil,sys; shutil.rmtree(sys.argv[1])' \
    "$FOLLOWUP_ROOT"
  echo "Preflight only; source and first-pass staging were not modified."
fi
