#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/quannda/Kaggle/edu-benchmark"
PYTHON="/home/quannda/miniconda3/envs/benchmark_env/bin/python"
FULL_ROOT="$ROOT/experiments/20260727_170150/outputs/benchmark_evaluation/full_1400_v1"
CANDIDATE_MANIFEST="$FULL_ROOT/judge_cost_pilot_30/candidate_manifest.json"
GEMINI_TARGET="$FULL_ROOT/target_gemini35/run_responses.jsonl"
LLAMA_TARGET="$FULL_ROOT/target_llama4_maverick/run_responses.jsonl"
LEARNLM_TARGET="$FULL_ROOT/target_gemini35_learnlm_prompted/run_responses.jsonl"

HISTORICAL_SPEND_BEFORE_FULL_USD="${HISTORICAL_SPEND_BEFORE_FULL_USD:-56.52}"
ACTUAL_SPEND_TO_DATE_USD="${ACTUAL_SPEND_TO_DATE_USD:-}"
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
for input in "$CANDIDATE_MANIFEST" "$GEMINI_TARGET" "$LLAMA_TARGET" "$LEARNLM_TARGET"; do
  if [[ ! -f "$input" ]]; then
    echo "Missing required input: $input" >&2
    exit 1
  fi
done

GEMINI_MANIFEST="$FULL_ROOT/target_gemini35/run_manifest.json"
LLAMA_MANIFEST="$FULL_ROOT/target_llama4_maverick/run_manifest.json"
LEARNLM_MANIFEST="$FULL_ROOT/target_gemini35_learnlm_prompted/run_manifest.json"
for manifest in "$GEMINI_MANIFEST" "$LLAMA_MANIFEST" "$LEARNLM_MANIFEST"; do
  if [[ ! -f "$manifest" ]]; then
    echo "Missing required target manifest: $manifest" >&2
    exit 1
  fi
done

DERIVED_SPEND="$($PYTHON -c 'import json,sys
base=float(sys.argv[1])
paths=sys.argv[2:]
manifests=[json.load(open(path)) for path in paths]
for path,manifest in zip(paths,manifests):
    if manifest.get("status")!="completed" or len(manifest.get("completed_candidate_ids") or [])!=1400:
        raise SystemExit(f"target is not complete: {path}")
target_cost=sum(
    float(m.get("cumulative_estimated_cost_usd") or m.get("new_estimated_cost_usd") or 0)
    for m in manifests
)
print(base+target_cost)' \
  "$HISTORICAL_SPEND_BEFORE_FULL_USD" \
  "$GEMINI_MANIFEST" "$LLAMA_MANIFEST" "$LEARNLM_MANIFEST")"
if [[ -z "$ACTUAL_SPEND_TO_DATE_USD" ]]; then
  ACTUAL_SPEND_TO_DATE_USD="$DERIVED_SPEND"
  echo "Derived ACTUAL_SPEND_TO_DATE_USD=$ACTUAL_SPEND_TO_DATE_USD from target manifests."
else
  echo "Using caller-provided ACTUAL_SPEND_TO_DATE_USD=$ACTUAL_SPEND_TO_DATE_USD."
  echo "Manifest-derived reference is $DERIVED_SPEND USD."
fi

echo "Judge cost pilot: 30 candidates x 3 target configurations = 90 comparisons."
echo "The runner derives the conservative upper bound from pending comparisons only."

"$PYTHON" scripts/benchmark_evaluation/run_claude_judge_smoke.py \
  --run-kind cost-pilot \
  --provider gemini \
  --project edu-benchmark \
  --location global \
  --model gemini-3.5-flash \
  --output-dir "$FULL_ROOT/judge_cost_pilot_30/judge_gemini35" \
  --candidate-manifest "$CANDIDATE_MANIFEST" \
  --system-prompt shared/prompts/benchmark_response_judging/system_prompt_v2.md \
  --target-run "$GEMINI_TARGET" \
  --target-run "$LLAMA_TARGET" \
  --target-run "$LEARNLM_TARGET" \
  --thinking-level medium \
  --max-output-tokens 8192 \
  --concurrency 8 \
  --max-retries 1 \
  --retry-backoff-base-seconds 5 \
  --retry-backoff-max-seconds 30 \
  --retry-jitter-seconds 2 \
  --input-usd-per-million 1.50 \
  --output-usd-per-million 9.00 \
  --upper-bound-input-tokens 10000 \
  --actual-spend-to-date-usd "$ACTUAL_SPEND_TO_DATE_USD" \
  --hard-budget-usd "$HARD_BUDGET_USD" \
  --reserve-usd "$RESERVE_USD" \
  --stage-cap-usd 16 \
  "${API_FLAG[@]}"
