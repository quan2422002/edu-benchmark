import copy
import csv
import json
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from edu_benchmark.experiment_runtime import cli as runtime_cli
from edu_benchmark.experiment_runtime.cli import preflight, validate
from edu_benchmark.experiment_runtime.config import (
    RuntimeConfig,
    RuntimeConfigError,
    build_preflight_manifest,
    discover_repository_root,
    load_runtime_config,
    semantic_result_hash,
    sha256_file,
    write_json_atomic,
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
        },
        "judge_robustness": {"validation": {"status": "passed"}},
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
                "schema_version": "section-v-ablation-analysis-v1",
            },
            "run_manifest": {
                "path": "outputs/run_manifest.json",
                "schema_version": "experiment-runtime-manifest-v1",
            },
        },
        "parameters": {"bootstrap_iterations": 1, "seed": 1},
        "provenance": {
            "code_commit": None,
            "code_commit_note": "Fixture run has no source commit.",
            "code_paths": ["scripts/runner.py"],
            "prompt_bundle": None,
            "provider": {
                "name": None,
                "model": None,
                "location": None,
                "reason": "Offline fixture; no model request is made.",
            },
            "credential_policy": "external_only_not_required_for_offline_analysis",
            "cost": {
                "currency": None,
                "amount": 0,
                "reason": "Offline fixture.",
            },
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


def _write_completed_fixture_run(config: RuntimeConfig) -> dict[str, object]:
    baseline = json.loads(config.equivalence_baseline[1].read_text(encoding="utf-8"))
    result_path = config.output_path("result")
    write_json_atomic(result_path, baseline)
    expected_paths = {
        role: item.relative_path for role, item in config.inputs.items()
    }
    semantic_hash = semantic_result_hash(
        baseline,
        config.repo_root,
        expected_paths=expected_paths,
    )
    manifest = build_preflight_manifest(config)
    manifest["status"] = "completed"
    manifest["equivalence"].update(
        {
            "status": "passed",
            "baseline_semantic_sha256": semantic_hash,
            "result_semantic_sha256": semantic_hash,
            "allowed_difference": "repository_absolute_paths_to_relative_paths",
        }
    )
    manifest["result"] = {
        "path": result_path.relative_to(config.repo_root).as_posix(),
        "sha256": sha256_file(result_path),
        "semantic_sha256": semantic_hash,
        "validation_status": "passed",
    }
    write_json_atomic(config.output_path("run_manifest"), manifest)
    return manifest


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


def test_preflight_preserves_a_completed_run_manifest(tmp_path: Path):
    root, config_path = _build_fixture_repo(tmp_path)
    config = load_runtime_config(config_path, repo_root=root)
    _write_completed_fixture_run(config)
    manifest_path = config.output_path("run_manifest")
    original = manifest_path.read_bytes()

    summary = preflight(config)

    assert summary["status"] == "preflight_passed"
    assert summary["completed_manifest_preserved"] is True
    assert summary["completed_manifest_matches_preflight"] is True
    assert summary["checks"]["completed_manifest"] == "matched_preserved"
    assert manifest_path.read_bytes() == original


def test_validate_detects_code_drift_after_a_completed_run(tmp_path: Path):
    root, config_path = _build_fixture_repo(tmp_path)
    config = load_runtime_config(config_path, repo_root=root)
    _write_completed_fixture_run(config)
    assert validate(config)["status"] == "passed"

    (root / "scripts/runner.py").write_text("# changed runner\n", encoding="utf-8")
    current_config = load_runtime_config(config_path, repo_root=root)
    stale_summary = preflight(current_config)
    assert stale_summary["status"] == "preflight_passed"
    assert stale_summary["completed_manifest_preserved"] is True
    assert stale_summary["completed_manifest_matches_preflight"] is False
    assert stale_summary["checks"]["completed_manifest"] == "stale_preserved"
    with pytest.raises(RuntimeConfigError, match="preflight fingerprint"):
        validate(current_config)


@pytest.mark.parametrize(
    ("case", "message"),
    (
        ("pipeline", "Unsupported pipeline"),
        ("missing_parameter", "parameters must contain exactly"),
        ("zero_iterations", "positive integer"),
        ("boolean_iterations", "positive integer"),
        ("invalid_seed", "seed must be an integer"),
        ("input_roles", "input roles must be exactly"),
        ("output_schema", "output result schema"),
        ("resume_policy", "resume policy must be unsupported"),
        ("runner_provenance", "runner must be included"),
    ),
)
def test_runtime_config_rejects_incomplete_preflight_contract(
    tmp_path: Path,
    case: str,
    message: str,
):
    root, config_path = _build_fixture_repo(tmp_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if case == "pipeline":
        config["pipeline_id"] = "unsupported"
    elif case == "missing_parameter":
        del config["parameters"]["seed"]
    elif case == "zero_iterations":
        config["parameters"]["bootstrap_iterations"] = 0
    elif case == "boolean_iterations":
        config["parameters"]["bootstrap_iterations"] = True
    elif case == "invalid_seed":
        config["parameters"]["seed"] = "not-an-integer"
    elif case == "input_roles":
        config["inputs"][2]["role"] = "unexpected_judge"
    elif case == "output_schema":
        config["outputs"]["result"]["schema_version"] = "unknown"
    elif case == "resume_policy":
        config["execution"]["resume_policy"] = "pending_only"
    else:
        config["provenance"]["code_paths"] = ["src/unrelated.py"]
        (root / "src/unrelated.py").write_text("# unrelated\n", encoding="utf-8")
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    with pytest.raises(RuntimeConfigError, match=message):
        load_runtime_config(config_path, repo_root=root)


def test_preflight_cli_reports_failed_status_for_invalid_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    root, config_path = _build_fixture_repo(tmp_path)
    config = load_runtime_config(config_path, repo_root=root)
    invalid_raw = copy.deepcopy(config.raw)
    invalid_raw["parameters"]["bootstrap_iterations"] = 0
    invalid_config = replace(config, raw=invalid_raw)
    monkeypatch.setattr(
        runtime_cli,
        "load_runtime_config",
        lambda _path: invalid_config,
    )

    exit_code = runtime_cli.main(["preflight", "--config", "ignored.yaml"])
    captured = capsys.readouterr()
    error = json.loads(captured.err)

    assert exit_code == 2
    assert captured.out == ""
    assert error["status"] == "preflight_failed"
    assert "positive integer" in error["error"]


def test_validate_detects_tampered_manifest_provenance(tmp_path: Path):
    root, config_path = _build_fixture_repo(tmp_path)
    config = load_runtime_config(config_path, repo_root=root)
    manifest = _write_completed_fixture_run(config)
    manifest["provenance"]["credential_policy"] = "tampered"
    write_json_atomic(config.output_path("run_manifest"), manifest)

    with pytest.raises(RuntimeConfigError, match="manifest provenance"):
        validate(config)


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


def test_plan04_inventory_covers_priority_pipeline_entrypoints():
    inventory_path = (
        ROOT
        / "experiments/20260806_145124/outputs/plan04/active_pipeline_inventory.csv"
    )
    with inventory_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    recorded = [row["entrypoint"] for row in rows]
    benchmark_entrypoints = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "scripts/benchmark_evaluation").iterdir()
        if path.is_file() and path.suffix in {".py", ".sh"}
    }
    requirement_entrypoints = {
        f"src/vertex_ai_call/{name}"
        for name in (
            "run_requirement_scoring.py",
            "analyze_requirement_scoring.py",
            "export_eligible_candidate_pool.py",
        )
    }
    expected = benchmark_entrypoints | requirement_entrypoints

    assert len(recorded) == len(set(recorded))
    assert set(recorded) == expected
    assert {row["classification"] for row in rows} <= {
        "active",
        "compatibility",
        "historical-only",
    }
