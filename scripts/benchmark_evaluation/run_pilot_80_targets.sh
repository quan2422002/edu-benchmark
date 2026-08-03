#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/quannda/Kaggle/edu-benchmark"
PYTHON="/home/quannda/miniconda3/envs/benchmark_env/bin/python"
PILOT_ROOT="$ROOT/experiments/20260727_170150/outputs/benchmark_evaluation/pilot_80_v1"
MANIFEST="$PILOT_ROOT/candidate_manifest.json"
BUNDLE="$ROOT/shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v2.yaml"

cd "$ROOT"

if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing locked pilot manifest: $MANIFEST" >&2
  echo "Run build_pilot_manifest.py and review coverage first." >&2
  exit 1
fi

"$PYTHON" scripts/benchmark_evaluation/run_vertex_smoke.py \
  --run-kind pilot \
  --provider gemini \
  --project edu-benchmark \
  --location global \
  --model gemini-3.5-flash \
  --output-dir "$PILOT_ROOT/target_gemini35" \
  --candidate-manifest "$MANIFEST" \
  --instruction-bundle "$BUNDLE" \
  --max-candidates 80 \
  --max-output-tokens 1024 \
  --seed 20260728 \
  --concurrency 20 \
  --max-retries 2 \
  --upper-bound-input-tokens 3000 \
  --input-usd-per-million 1.50 \
  --output-usd-per-million 9.00 \
  --actual-spend-to-date-usd 58.00 \
  --hard-budget-usd 250 \
  --reserve-usd 25 \
  --stage-cap-usd 4 \
  --execute-api

"$PYTHON" scripts/benchmark_evaluation/run_vertex_smoke.py \
  --run-kind pilot \
  --provider openai-maas \
  --project edu-benchmark \
  --location us-east5 \
  --model meta/llama-4-maverick-17b-128e-instruct-maas \
  --output-dir "$PILOT_ROOT/target_llama4_maverick" \
  --candidate-manifest "$MANIFEST" \
  --instruction-bundle "$BUNDLE" \
  --max-candidates 80 \
  --max-output-tokens 1024 \
  --seed 20260728 \
  --concurrency 20 \
  --max-retries 2 \
  --upper-bound-input-tokens 3000 \
  --input-usd-per-million 0.35 \
  --output-usd-per-million 1.15 \
  --actual-spend-to-date-usd 62.00 \
  --hard-budget-usd 250 \
  --reserve-usd 25 \
  --stage-cap-usd 1 \
  --execute-api

"$PYTHON" scripts/benchmark_evaluation/run_vertex_smoke.py \
  --run-kind pilot \
  --provider gemini \
  --project edu-benchmark \
  --location global \
  --model gemini-3.5-flash \
  --output-dir "$PILOT_ROOT/target_gemini35_learnlm_prompted" \
  --candidate-manifest "$MANIFEST" \
  --instruction-bundle "$ROOT/shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v3_learnlm.yaml" \
  --max-candidates 80 \
  --max-output-tokens 1024 \
  --seed 20260728 \
  --concurrency 20 \
  --max-retries 2 \
  --upper-bound-input-tokens 3400 \
  --input-usd-per-million 1.50 \
  --output-usd-per-million 9.00 \
  --actual-spend-to-date-usd 63.00 \
  --hard-budget-usd 250 \
  --reserve-usd 25 \
  --stage-cap-usd 4 \
  --execute-api
