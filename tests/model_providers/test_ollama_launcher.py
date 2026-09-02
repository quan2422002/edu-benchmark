from __future__ import annotations

import subprocess
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = REPOSITORY_ROOT / "scripts/model_providers/run_ollama_server.sh"


def test_ollama_launcher_has_valid_bash_syntax() -> None:
    subprocess.run(["bash", "-n", str(LAUNCHER)], check=True)


def test_ollama_launcher_owns_the_complete_non_inference_startup_sequence() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")

    required_in_order = [
        '"${OLLAMA_BINARY}" serve &',
        '"${OLLAMA_BINARY}" pull "${MODEL_TAG}"',
        "scripts/model_providers/probe_ollama.py",
        '"${OLLAMA_BASE_URL}/api/generate"',
        '"${OLLAMA_BASE_URL}/api/ps"',
    ]
    positions = [text.index(marker) for marker in required_in_order]
    positions.append(text.rindex('wait "${server_pid}"'))
    assert positions == sorted(positions)
    assert '"stream":false' in text
    assert '"num_ctx":4096' in text
    assert '"keep_alive":-1' in text
    assert '"keep_alive":"-1"' not in text
    assert "--fail-with-body" not in text
    assert "--write-out" in text
    assert "preload_http_status" in text
    assert "--execute-model" not in text


def test_ollama_launcher_keeps_service_under_operator_owned_screen_lifecycle() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")

    assert "trap 'exit 130' INT HUP" in text
    assert 'wait "${server_pid}"' in text
    assert "service remains active until the operator stops this screen session" in text


def test_ollama_launcher_owns_a_fixed_auditable_log() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")

    assert "experiments/20260902_082403/logs/ollama-qwen38-service.log" in text
    assert 'exec > >(/usr/bin/tee -a "${LOG_PATH}") 2>&1' in text
    assert 'chmod 640 "${LOG_PATH}" "${LOCK_PATH}"' in text
    assert "/usr/bin/flock -n 9" in text


def test_ollama_launcher_uses_the_plan01_amended_loopback_port() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'OLLAMA_BASE_URL="http://127.0.0.1:11436"' in text
    assert 'OLLAMA_HOST="127.0.0.1:11436"' in text
    assert "127.0.0.1:11435" not in text


def test_launcher_supports_parallel_two_without_changing_default() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")

    assert 'REQUESTED_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-1}"' in text
    assert 'export OLLAMA_NUM_PARALLEL="${REQUESTED_NUM_PARALLEL}"' in text
    assert '"${REQUESTED_NUM_PARALLEL}" != "2"' in text
    assert '--expected-num-parallel "${OLLAMA_NUM_PARALLEL}"' in text
