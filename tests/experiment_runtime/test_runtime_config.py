import json
from pathlib import Path

import pytest
import yaml

from edu_benchmark.experiment_runtime.config import (
    RuntimeConfigError,
    build_preflight_manifest,
    discover_repository_root,
    load_runtime_config,
    semantic_result_hash,
    sha256_file,
)


ROOT = Path(__file__).resolve().parents[2]


def _build_fixture_repo(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "repo"
    (root / "src/edu_benchmark").mkdir(parents=True)
    (root / "experiments/configs").mkdir(parents=True)
    (root / "scripts").mkdir()
    (root / "inputs").mkdir()
    (root / "baseline").mkdir()
    (root / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    (root / "scripts/runner.py").write_text("# fixture runner\n")
    (root / "inputs/candidates.csv").write_text("id\nC1\n", encoding="utf-8")
    (root / "inputs/gemini.jsonl").write_text("{}\n", encoding="utf-8")
    (root / "inputs/gpt.jsonl").write_text("{}\n", encoding="utf-8")
    baseline = {
        "instruction_ablation": {
            "provenance": {
                "inputs": {
                    "candidate_pool": {
                        "path": str((root / "inputs/candidates.csv").resolve()),
                        "sha256": "candidate",
                    },
                    "gemini_judge": {
                        "path": str((root / "inputs/gemini.jsonl").resolve()),
                        "sha256": "gemini",
                    },
                    "gpt_judge": {
                        "path": str((root / "inputs/gpt.jsonl").resolve()),
                        "sha256": "gpt",
                    },
                }
            }
        }
    }
    baseline_path = root / "baseline/results.json"
    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
    config = {
        "schema_version": "1.0",
        "config_id": "fixture-v1",
        "config_version": "v1",
        "pipeline_id": "section_v_ablation",
        "experiment_id": "fixture",
        "repository_root": "../..",
        "execution": {
            "mode": "offline",
            "runner": "scripts/runner.py",
            "resume_policy": "unsupported",
            "resume_note": "Full deterministic rebuild.",
        },
        "inputs": [
            {
                "role": role,
                "artifact_id": role,
                "version": "v1",
                "path": path,
                "sha256": sha256_file(root / path),
                "record_count": 1,
                "format": file_format,
            }
            for role, path, file_format in (
                ("candidate_pool", "inputs/candidates.csv", "csv"),
                ("gemini_judge", "inputs/gemini.jsonl", "jsonl"),
                ("gpt_judge", "inputs/gpt.jsonl", "jsonl"),
            )
        ],
        "outputs": {
            "result": {
                "path": "outputs/results.json",
                "schema_version": "result-v1",
            },
            "run_manifest": {
                "path": "outputs/run_manifest.json",
                "schema_version": "manifest-v1",
            },
        },
        "parameters": {"bootstrap_iterations": 1, "seed": 1},
        "provenance": {
            "code_commit": None,
            "code_paths": ["scripts/runner.py"],
            "prompt_bundle": None,
            "provider": {"name": None, "model": None, "location": None},
            "credential_policy": "external_only",
        },
        "equivalence": {
            "baseline_result_path": "baseline/results.json",
            "baseline_result_sha256": sha256_file(baseline_path),
            "comparison": "normalize_repository_paths_only",
        },
    }
    config_path = root / "experiments/configs/config.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return root, config_path


def test_runtime_config_is_cwd_independent_and_manifest_is_portable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    root, config_path = _build_fixture_repo(tmp_path)
    first = load_runtime_config(
        Path("experiments/configs/config.yaml"), repo_root=root
    )
    monkeypatch.chdir(tmp_path)
    second = load_runtime_config(
        Path("experiments/configs/config.yaml"), repo_root=root
    )
    first_manifest = build_preflight_manifest(first)
    second_manifest = build_preflight_manifest(second)
    assert first.sha256 == second.sha256
    assert (
        first_manifest["preflight_fingerprint"]
        == second_manifest["preflight_fingerprint"]
    )
    assert str(root) not in json.dumps(first_manifest)
    assert first.relative_path == "experiments/configs/config.yaml"
    assert discover_repository_root(config_path) == root


def test_runtime_config_fails_closed_on_checksum_mismatch(tmp_path: Path):
    root, config_path = _build_fixture_repo(tmp_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["inputs"][0]["sha256"] = "0" * 64
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    with pytest.raises(RuntimeConfigError, match="checksum mismatch"):
        load_runtime_config(config_path, repo_root=root)


def test_runtime_config_rejects_path_escape_and_serialized_secret(tmp_path: Path):
    root, config_path = _build_fixture_repo(tmp_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["outputs"]["result"]["path"] = "../outside.json"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    with pytest.raises(RuntimeConfigError, match="escapes the repository"):
        load_runtime_config(config_path, repo_root=root)

    root, config_path = _build_fixture_repo(tmp_path / "secret-case")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["provenance"]["api_key"] = "not-even-a-real-key"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    with pytest.raises(RuntimeConfigError, match="Serialized secret field"):
        load_runtime_config(config_path, repo_root=root)


def test_semantic_result_hash_normalizes_only_repository_paths(tmp_path: Path):
    root, _ = _build_fixture_repo(tmp_path)
    absolute = {
        "instruction_ablation": {
            "provenance": {
                "inputs": {
                    "candidate_pool": {
                        "path": str(root / "inputs/candidates.csv")
                    }
                }
            }
        },
        "value": 1,
    }
    relative = {
        "instruction_ablation": {
            "provenance": {
                "inputs": {
                    "candidate_pool": {"path": "inputs/candidates.csv"}
                }
            }
        },
        "value": 1,
    }
    assert semantic_result_hash(absolute, root) == semantic_result_hash(relative, root)
    relative["value"] = 2
    assert semantic_result_hash(absolute, root) != semantic_result_hash(relative, root)


def test_semantic_hash_accepts_a_locked_path_from_another_clone(tmp_path: Path):
    root, _ = _build_fixture_repo(tmp_path)
    historical = {
        "instruction_ablation": {
            "provenance": {
                "inputs": {
                    "candidate_pool": {
                        "path": "/old/machine/checkout/inputs/candidates.csv"
                    }
                }
            }
        }
    }
    portable = {
        "instruction_ablation": {
            "provenance": {
                "inputs": {
                    "candidate_pool": {"path": "inputs/candidates.csv"}
                }
            }
        }
    }
    expected = {"candidate_pool": "inputs/candidates.csv"}
    assert semantic_result_hash(
        historical, root, expected_paths=expected
    ) == semantic_result_hash(portable, root, expected_paths=expected)
    historical["instruction_ablation"]["provenance"]["inputs"][
        "candidate_pool"
    ]["path"] = "/old/machine/checkout/inputs/other.csv"
    with pytest.raises(RuntimeConfigError, match="locked config path"):
        semantic_result_hash(historical, root, expected_paths=expected)


def test_active_section_v_entrypoint_has_no_machine_or_experiment_default():
    source = (
        ROOT / "scripts/benchmark_evaluation/analyze_section_v_ablation.py"
    ).read_text(encoding="utf-8")
    assert "/home/" not in source
    assert "20260727_170150" not in source
    assert "--config" not in source  # The shared CLI owns argument parsing.
