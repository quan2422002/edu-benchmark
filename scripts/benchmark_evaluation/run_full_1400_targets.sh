#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/quannda/Kaggle/edu-benchmark"
PYTHON="/home/quannda/miniconda3/envs/benchmark_env/bin/python"
FULL_ROOT="$ROOT/experiments/20260727_170150/outputs/benchmark_evaluation/full_1400_v1"
MANIFEST="$FULL_ROOT/candidate_manifest.json"
BASELINE_BUNDLE="$ROOT/shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v2.yaml"
LEARNLM_BUNDLE="$ROOT/shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v3_learnlm.yaml"

: "${ACTUAL_SPEND_TO_DATE_USD:?Set ACTUAL_SPEND_TO_DATE_USD from the latest billing snapshot.}"
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

sum_usd() {
  "$PYTHON" -c 'import sys; print(sum(float(v) for v in sys.argv[1:]))' "$@"
}

# Conservative upper bounds include all three attempts per remaining request.
LLAMA_UPPER_USD="9.35592"
LEARNLM_UPPER_USD="60.1272"
SPEND_BEFORE_LLAMA="$ACTUAL_SPEND_TO_DATE_USD"

cd "$ROOT"

if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing locked full manifest: $MANIFEST" >&2
  echo "Run scripts/benchmark_evaluation/build_full_manifest.py first." >&2
  exit 1
fi

BASELINE_MANIFEST="$FULL_ROOT/target_gemini35/run_manifest.json"
BASELINE_OUTPUT="$FULL_ROOT/target_gemini35/run_responses.jsonl"
"$PYTHON" -c 'import json,sys
from pathlib import Path
manifest=json.load(open(sys.argv[1]))
rows=[json.loads(line) for line in Path(sys.argv[2]).read_text().splitlines() if line.strip()]
ids={row.get("benchmark_candidate_id") for row in rows}
if manifest.get("status")!="completed" or len(rows)!=1400 or len(ids)!=1400:
    raise SystemExit("Gemini baseline is not a complete 1,400-record bundle")
if any(row.get("response_status")!="completed" or row.get("finish_reason") not in {"STOP","END_TURN"} for row in rows):
    raise SystemExit("Gemini baseline still contains incomplete responses")' \
  "$BASELINE_MANIFEST" "$BASELINE_OUTPUT"
echo "Gemini baseline is complete; skipping it and running only Llama + LearnLM."

"$PYTHON" scripts/benchmark_evaluation/run_vertex_smoke.py \
  --run-kind full \
  --provider openai-maas \
  --project edu-benchmark \
  --location us-east5 \
  --model meta/llama-4-maverick-17b-128e-instruct-maas \
  --output-dir "$FULL_ROOT/target_llama4_maverick" \
  --candidate-manifest "$MANIFEST" \
  --instruction-bundle "$BASELINE_BUNDLE" \
  --max-candidates 1400 \
  --max-output-tokens 1024 \
  --seed 20260728 \
  --concurrency 2 \
  --max-retries 2 \
  --retry-backoff-base-seconds 15 \
  --retry-backoff-max-seconds 60 \
  --retry-jitter-seconds 5 \
  --upper-bound-input-tokens 3000 \
  --input-usd-per-million 0.35 \
  --output-usd-per-million 1.15 \
  --actual-spend-to-date-usd "$SPEND_BEFORE_LLAMA" \
  --hard-budget-usd "$HARD_BUDGET_USD" \
  --reserve-usd "$RESERVE_USD" \
  --stage-cap-usd 10 \
  "${API_FLAG[@]}"

if [[ "$EXECUTE_API" == "1" ]]; then
  LLAMA_COST="$($PYTHON -c 'import json,sys
m=json.load(open(sys.argv[1]))
if m.get("status")!="completed" or len(m.get("completed_candidate_ids") or [])!=1400:
    raise SystemExit("Llama target is not complete; blocking LearnLM")
print(float(m.get("new_estimated_cost_usd") or 0))' \
    "$FULL_ROOT/target_llama4_maverick/run_manifest.json")"
else
  LLAMA_COST="$LLAMA_UPPER_USD"
fi
SPEND_BEFORE_LEARNLM="$(sum_usd "$SPEND_BEFORE_LLAMA" "$LLAMA_COST")"

"$PYTHON" scripts/benchmark_evaluation/run_vertex_smoke.py \
  --run-kind full \
  --provider gemini \
  --project edu-benchmark \
  --location global \
  --model gemini-3.5-flash \
  --output-dir "$FULL_ROOT/target_gemini35_learnlm_prompted" \
  --candidate-manifest "$MANIFEST" \
  --instruction-bundle "$LEARNLM_BUNDLE" \
  --max-candidates 1400 \
  --max-output-tokens 1024 \
  --seed 20260728 \
  --concurrency 20 \
  --max-retries 2 \
  --upper-bound-input-tokens 3400 \
  --input-usd-per-million 1.50 \
  --output-usd-per-million 9.00 \
  --actual-spend-to-date-usd "$SPEND_BEFORE_LEARNLM" \
  --hard-budget-usd "$HARD_BUDGET_USD" \
  --reserve-usd "$RESERVE_USD" \
  --stage-cap-usd 61 \
  "${API_FLAG[@]}"

if [[ "$EXECUTE_API" == "1" ]]; then
  LEARNLM_COST="$($PYTHON -c 'import json,sys
m=json.load(open(sys.argv[1]))
if m.get("status")!="completed" or len(m.get("completed_candidate_ids") or [])!=1400:
    raise SystemExit("LearnLM-prompted target is not complete")
print(float(m.get("new_estimated_cost_usd") or 0))' \
    "$FULL_ROOT/target_gemini35_learnlm_prompted/run_manifest.json")"
  SPEND_AFTER_TARGETS="$(sum_usd "$SPEND_BEFORE_LEARNLM" "$LEARNLM_COST")"
  echo "ACTUAL_SPEND_AFTER_TARGETS_USD=$SPEND_AFTER_TARGETS"
fi
