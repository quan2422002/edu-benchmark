#!/usr/bin/env bash
set -euo pipefail

# Plan 01 owns only the local runtime/provider boundary. This launcher pulls and
# preloads one pinned model, but it does not send an inference prompt or invoke
# a benchmark workflow.
readonly OLLAMA_RUNTIME_ROOT="/workspace/quannd/local_llm_runtime/ollama/v0.32.14"
readonly LOCAL_LLM_CACHE_ROOT="/workspace/quannd/local_llm_cache"
readonly OLLAMA_BINARY="${OLLAMA_RUNTIME_ROOT}/bin/ollama"
readonly OLLAMA_RELEASE_ARCHIVE="${OLLAMA_RUNTIME_ROOT}/downloads/ollama-linux-amd64.tar.zst"
readonly OLLAMA_RELEASE_SIZE_BYTES="1421191399"
readonly OLLAMA_RELEASE_SHA256="c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f"
readonly OLLAMA_VERSION="0.32.14"
readonly OLLAMA_BASE_URL="http://127.0.0.1:11436"
readonly MODEL_TAG="qwen3.8:latest"
readonly REQUESTED_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-1}"
readonly GPU_UUID="GPU-5e1bf88a-a431-9a0c-b462-37cd95b5e9b8"
readonly MIN_CACHE_FREE_BYTES="$((30 * 1024 * 1024 * 1024))"
readonly MIN_GPU_FREE_MIB="$((20 * 1024))"
readonly BENCHMARK_PYTHON="/workspace/quannd/miniconda3/envs/benchmark_env/bin/python"
readonly REPOSITORY_ROOT="$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.."
  pwd
)"
readonly LOG_PATH="${REPOSITORY_ROOT}/experiments/20260902_082403/logs/ollama-qwen38-service.log"
readonly LOCK_PATH="${REPOSITORY_ROOT}/experiments/20260902_082403/logs/ollama-qwen38-service.lock"

mkdir -p "$(dirname -- "${LOG_PATH}")"
touch "${LOG_PATH}" "${LOCK_PATH}"
chmod 640 "${LOG_PATH}" "${LOCK_PATH}"
exec > >(/usr/bin/tee -a "${LOG_PATH}") 2>&1

log() {
  printf '[%s] %s\n' "$(date --iso-8601=seconds)" "$*"
}

fail() {
  log "ERROR: $*"
  exit 2
}

server_pid=""

stop_server() {
  if [[ -n "${server_pid}" ]] && kill -0 "${server_pid}" 2>/dev/null; then
    log "Stopping Ollama server PID ${server_pid}"
    kill -TERM "${server_pid}" 2>/dev/null || true
    wait "${server_pid}" 2>/dev/null || true
  fi
}

on_exit() {
  local status=$?
	stop_server
	if ((status == 0)); then
	  log "Launcher exited cleanly"
	else
	  log "Launcher exited with status ${status}"
	fi
}

trap on_exit EXIT
trap 'exit 130' INT HUP
trap 'exit 143' TERM

exec 9>"${LOCK_PATH}"
if ! /usr/bin/flock -n 9; then
  fail "Another Plan 01 Ollama launcher already owns ${LOCK_PATH}"
fi

log "Starting consolidated Ollama/Qwen3.8 launcher"
log "Progress log: ${LOG_PATH}"

umask 027
mkdir -p \
  "${LOCAL_LLM_CACHE_ROOT}/ollama/models" \
  "${LOCAL_LLM_CACHE_ROOT}/huggingface/hub" \
  "${LOCAL_LLM_CACHE_ROOT}/huggingface/datasets" \
  "${LOCAL_LLM_CACHE_ROOT}/huggingface/assets" \
  "${LOCAL_LLM_CACHE_ROOT}/huggingface/xet" \
  "${LOCAL_LLM_CACHE_ROOT}/vllm" \
  "${LOCAL_LLM_CACHE_ROOT}/torch" \
  "${LOCAL_LLM_CACHE_ROOT}/triton" \
  "${LOCAL_LLM_CACHE_ROOT}/tmp"
chmod 750 \
  "${LOCAL_LLM_CACHE_ROOT}" \
  "${LOCAL_LLM_CACHE_ROOT}/ollama" \
  "${LOCAL_LLM_CACHE_ROOT}/ollama/models" \
  "${LOCAL_LLM_CACHE_ROOT}/huggingface" \
  "${LOCAL_LLM_CACHE_ROOT}/huggingface/hub" \
  "${LOCAL_LLM_CACHE_ROOT}/huggingface/datasets" \
  "${LOCAL_LLM_CACHE_ROOT}/huggingface/assets" \
  "${LOCAL_LLM_CACHE_ROOT}/huggingface/xet" \
  "${LOCAL_LLM_CACHE_ROOT}/vllm" \
  "${LOCAL_LLM_CACHE_ROOT}/torch" \
  "${LOCAL_LLM_CACHE_ROOT}/triton" \
  "${LOCAL_LLM_CACHE_ROOT}/tmp"

if [[ ! -x "${OLLAMA_BINARY}" ]]; then
  fail "Ollama binary is missing or not executable: ${OLLAMA_BINARY}"
fi
if [[ ! -x "${BENCHMARK_PYTHON}" ]]; then
  fail "benchmark_env Python is missing: ${BENCHMARK_PYTHON}"
fi
if [[ ! -f "${OLLAMA_RELEASE_ARCHIVE}" ]]; then
  fail "Ollama release archive is missing: ${OLLAMA_RELEASE_ARCHIVE}"
fi

export OLLAMA_MODELS="${LOCAL_LLM_CACHE_ROOT}/ollama/models"
export HF_HOME="${LOCAL_LLM_CACHE_ROOT}/huggingface"
export HF_HUB_CACHE="${LOCAL_LLM_CACHE_ROOT}/huggingface/hub"
export HF_DATASETS_CACHE="${LOCAL_LLM_CACHE_ROOT}/huggingface/datasets"
export HF_ASSETS_CACHE="${LOCAL_LLM_CACHE_ROOT}/huggingface/assets"
export HF_XET_CACHE="${LOCAL_LLM_CACHE_ROOT}/huggingface/xet"
export VLLM_CACHE_ROOT="${LOCAL_LLM_CACHE_ROOT}/vllm"
export TORCH_HOME="${LOCAL_LLM_CACHE_ROOT}/torch"
export TRITON_CACHE_DIR="${LOCAL_LLM_CACHE_ROOT}/triton"
export TMPDIR="${LOCAL_LLM_CACHE_ROOT}/tmp"
export OLLAMA_HOST="127.0.0.1:11436"
if [[ "${REQUESTED_NUM_PARALLEL}" != "1" && "${REQUESTED_NUM_PARALLEL}" != "2" ]]; then
  fail "OLLAMA_NUM_PARALLEL must be 1 or 2 for this approved launcher"
fi
export OLLAMA_NUM_PARALLEL="${REQUESTED_NUM_PARALLEL}"
export OLLAMA_MAX_LOADED_MODELS="1"
export OLLAMA_FLASH_ATTENTION="1"
export OLLAMA_KV_CACHE_TYPE="f16"
export CUDA_VISIBLE_DEVICES="${GPU_UUID}"
export LD_LIBRARY_PATH="${OLLAMA_RUNTIME_ROOT}/lib/ollama:${OLLAMA_RUNTIME_ROOT}/lib/ollama/cuda_v12${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"

cache_path="$(readlink -f -- "${LOCAL_LLM_CACHE_ROOT}")"
if [[ "${cache_path}" != /workspace/* ]]; then
  fail "Local-LLM cache resolved outside /workspace: ${cache_path}"
fi
if [[ "$(stat -c '%U' -- "${LOCAL_LLM_CACHE_ROOT}")" != "$(id -un)" ]]; then
  fail "Local-LLM cache is not owned by the current user"
fi

archive_size="$(stat -c '%s' -- "${OLLAMA_RELEASE_ARCHIVE}")"
if [[ "${archive_size}" != "${OLLAMA_RELEASE_SIZE_BYTES}" ]]; then
  fail "Ollama release archive size mismatch: ${archive_size}"
fi
archive_sha256="$(sha256sum -- "${OLLAMA_RELEASE_ARCHIVE}" | awk '{print $1}')"
if [[ "${archive_sha256}" != "${OLLAMA_RELEASE_SHA256}" ]]; then
  fail "Ollama release archive SHA-256 mismatch: ${archive_sha256}"
fi
log "Verified Ollama ${OLLAMA_VERSION} release archive size and SHA-256"

cache_free_bytes="$(df -PB1 -- "${LOCAL_LLM_CACHE_ROOT}" | awk 'NR == 2 {print $4}')"
if ((cache_free_bytes < MIN_CACHE_FREE_BYTES)); then
  fail "Less than 30 GiB is free on the local-LLM cache filesystem"
fi
log "Cache preflight passed: ${cache_free_bytes} bytes free at ${cache_path}"
df -h /workspace /

gpu_free_mib="$(
  /usr/bin/nvidia-smi \
    --id="${GPU_UUID}" \
    --query-gpu=memory.free \
    --format=csv,noheader,nounits
)"
gpu_free_mib="${gpu_free_mib//[[:space:]]/}"
if [[ ! "${gpu_free_mib}" =~ ^[0-9]+$ ]]; then
  fail "Could not parse free GPU memory: ${gpu_free_mib}"
fi
if ((gpu_free_mib < MIN_GPU_FREE_MIB)); then
  fail "GPU preflight requires at least ${MIN_GPU_FREE_MIB} MiB free; found ${gpu_free_mib} MiB"
fi
log "GPU preflight passed: ${gpu_free_mib} MiB free on ${GPU_UUID}"
/usr/bin/nvidia-smi --id="${GPU_UUID}"
free -b

if /usr/bin/curl -fsS --max-time 2 "${OLLAMA_BASE_URL}/api/version" >/dev/null 2>&1; then
  fail "An Ollama server is already responding at ${OLLAMA_BASE_URL}"
fi

log "Starting Ollama server at ${OLLAMA_BASE_URL}"
log "Configured request parallelism: ${OLLAMA_NUM_PARALLEL}"
"${OLLAMA_BINARY}" serve &
server_pid=$!
log "Ollama server PID: ${server_pid}"

server_version=""
for _attempt in $(seq 1 90); do
  if ! kill -0 "${server_pid}" 2>/dev/null; then
    wait "${server_pid}" || true
    fail "Ollama server exited before becoming ready"
  fi
  if server_version="$(
    /usr/bin/curl -fsS --max-time 2 "${OLLAMA_BASE_URL}/api/version" 2>/dev/null \
      | "${BENCHMARK_PYTHON}" -c \
        'import json, sys; print(json.load(sys.stdin).get("version", ""))' \
        2>/dev/null
  )" && [[ -n "${server_version}" ]]; then
    break
  fi
  sleep 2
done
if [[ "${server_version}" != "${OLLAMA_VERSION}" ]]; then
  fail "Expected Ollama server ${OLLAMA_VERSION}; found ${server_version:-unavailable}"
fi
log "Ollama server health check passed with version ${server_version}"

log "Pulling ${MODEL_TAG} into ${OLLAMA_MODELS}; an interrupted pull can resume"
"${OLLAMA_BINARY}" pull "${MODEL_TAG}"
log "Model pull completed"
df -h /workspace /

log "Validating model tag, full digest, Q4_K_M, runtime asset, cache, RAM, and GPU preconditions"
(
  cd -- "${REPOSITORY_ROOT}"
  "${BENCHMARK_PYTHON}" scripts/model_providers/probe_ollama.py \
    --expected-num-parallel "${OLLAMA_NUM_PARALLEL}"
)

gpu_free_mib="$(
  /usr/bin/nvidia-smi \
    --id="${GPU_UUID}" \
    --query-gpu=memory.free \
    --format=csv,noheader,nounits
)"
gpu_free_mib="${gpu_free_mib//[[:space:]]/}"
if [[ ! "${gpu_free_mib}" =~ ^[0-9]+$ ]] || ((gpu_free_mib < MIN_GPU_FREE_MIB)); then
  fail "GPU availability changed before model preload; found ${gpu_free_mib:-unparseable} MiB free"
fi

log "Preloading ${MODEL_TAG} with num_ctx=4096 and keep_alive=-1; no inference prompt is sent"
preload_result=""
if ! preload_result="$(
  /usr/bin/curl \
    -sS \
    --max-time 900 \
    --write-out $'\n%{http_code}' \
    -H 'Content-Type: application/json' \
    -d '{"model":"qwen3.8:latest","stream":false,"keep_alive":-1,"options":{"num_ctx":4096}}' \
    "${OLLAMA_BASE_URL}/api/generate"
)"; then
  fail "Model preload request failed at the transport layer"
fi
preload_http_status="${preload_result##*$'\n'}"
preload_response="${preload_result%$'\n'*}"
log "Preload response: ${preload_response}"
if [[ ! "${preload_http_status}" =~ ^2[0-9][0-9]$ ]]; then
  fail "Model preload returned HTTP ${preload_http_status}"
fi

running_models="$(
  /usr/bin/curl -fsS --max-time 30 "${OLLAMA_BASE_URL}/api/ps"
)"
log "Running-model snapshot: ${running_models}"
if ! printf '%s\n' "${running_models}" | "${BENCHMARK_PYTHON}" -c '
import json
import sys

requested = sys.argv[1]
num_parallel = int(sys.argv[2])
models = json.load(sys.stdin).get("models", [])
matching = [
    model
    for model in models
    if model.get("name") == requested or model.get("model") == requested
]
if not matching:
    raise SystemExit("requested model is not loaded")
model = matching[0]
size = int(model.get("size", 0) or 0)
size_vram = int(model.get("size_vram", 0) or 0)
context_length = int(model.get("context_length", 0) or 0)
expected_context_length = 4096 * num_parallel
print(
    f"loaded_size={size} size_vram={size_vram} "
    f"context_length={context_length} parallel={num_parallel}"
)
if size <= 0 or size_vram < size * 0.99:
    raise SystemExit("model is not fully loaded on GPU")
if context_length != expected_context_length:
    raise SystemExit(
        f"model context length is not {expected_context_length}"
    )
' "${MODEL_TAG}" "${OLLAMA_NUM_PARALLEL}"; then
  fail "Loaded-model validation failed"
fi

/usr/bin/nvidia-smi --id="${GPU_UUID}"
free -b
log "READY: ${MODEL_TAG} is installed, preloaded, and served at ${OLLAMA_BASE_URL} with parallel=${OLLAMA_NUM_PARALLEL}"
log "No inference prompt has been sent; service remains active until the operator stops this screen session"

wait "${server_pid}"
