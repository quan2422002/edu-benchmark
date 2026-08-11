"""CLI for config-driven, offline experiment preflight and execution."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from edu_benchmark.benchmark_evaluation.section_v_ablation import (
    build_results,
    write_results_atomic,
)

from .config import (
    RuntimeConfig,
    RuntimeConfigError,
    build_preflight_manifest,
    load_runtime_config,
    semantic_result_hash,
    sha256_file,
    validate_runtime_contract,
    write_json_atomic,
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeConfigError(f"Expected a JSON object: {path}")
    return value


def _completed_manifest(
    config: RuntimeConfig,
    preflight: dict[str, Any],
    *,
    result_path: Path,
    semantic_hash: str,
) -> dict[str, Any]:
    manifest = copy.deepcopy(preflight)
    manifest["status"] = "completed"
    manifest["completed_at"] = preflight["generated_at"]
    manifest["result"] = {
        "path": result_path.relative_to(config.repo_root).as_posix(),
        "sha256": sha256_file(result_path),
        "semantic_sha256": semantic_hash,
        "validation_status": "passed",
    }
    manifest["resume"]["history"] = [
        {
            "action": "full_offline_rebuild",
            "status": "completed",
            "pending_id_count": 0,
            "recorded_at": preflight["generated_at"],
        }
    ]
    return manifest


def run_configured_section_v(config: RuntimeConfig) -> dict[str, Any]:
    validate_runtime_contract(config)
    parameters = config.raw["parameters"]
    iterations = parameters["bootstrap_iterations"]
    seed = parameters["seed"]

    candidate = config.input("candidate_pool")
    gemini = config.input("gemini_judge")
    gpt = config.input("gpt_judge")
    provenance_paths = {
        "candidate_pool": candidate.relative_path,
        "gemini_judge": gemini.relative_path,
        "gpt_judge": gpt.relative_path,
    }
    results = build_results(
        candidate_pool=candidate.path,
        gemini_judge=gemini.path,
        gpt_judge=gpt.path,
        iterations=iterations,
        seed=seed,
        provenance_paths=provenance_paths,
    )
    baseline = _load_json(config.equivalence_baseline[1])
    baseline_semantic_hash = semantic_result_hash(
        baseline,
        config.repo_root,
        expected_paths=provenance_paths,
    )
    result_semantic_hash = semantic_result_hash(
        results,
        config.repo_root,
        expected_paths=provenance_paths,
    )
    if result_semantic_hash != baseline_semantic_hash:
        raise RuntimeConfigError(
            "Configured Section V result differs from baseline beyond portable paths"
        )

    result_path = config.output_path("result")
    write_results_atomic(results, result_path)
    preflight = build_preflight_manifest(config)
    manifest = _completed_manifest(
        config,
        preflight,
        result_path=result_path,
        semantic_hash=result_semantic_hash,
    )
    manifest["equivalence"].update(
        {
            "status": "passed",
            "baseline_semantic_sha256": baseline_semantic_hash,
            "result_semantic_sha256": result_semantic_hash,
            "allowed_difference": "repository_absolute_paths_to_relative_paths",
        }
    )
    write_json_atomic(config.output_path("run_manifest"), manifest)
    return {
        "status": "completed",
        "config": config.relative_path,
        "config_sha256": config.sha256,
        "result": result_path.relative_to(config.repo_root).as_posix(),
        "result_sha256": sha256_file(result_path),
        "semantic_sha256": result_semantic_hash,
        "baseline_semantic_sha256": baseline_semantic_hash,
        "validation": results["judge_robustness"]["validation"]["status"],
    }


def preflight(config: RuntimeConfig) -> dict[str, Any]:
    manifest = build_preflight_manifest(config)
    manifest_path = config.output_path("run_manifest")
    completed_manifest_preserved = False
    completed_manifest_matches_preflight: bool | None = None
    completed_manifest_state = "not_present"
    if manifest_path.exists():
        existing_manifest = _load_json(manifest_path)
        completed_manifest_preserved = existing_manifest.get("status") == "completed"
        if completed_manifest_preserved:
            try:
                _validate_manifest_contract(existing_manifest, manifest)
            except RuntimeConfigError:
                completed_manifest_matches_preflight = False
                completed_manifest_state = "stale_preserved"
            else:
                completed_manifest_matches_preflight = True
                completed_manifest_state = "matched_preserved"
        else:
            completed_manifest_state = "non_completed_replaced"
    if not completed_manifest_preserved:
        write_json_atomic(manifest_path, manifest)
    return {
        "status": "preflight_passed",
        "config": config.relative_path,
        "config_sha256": config.sha256,
        "preflight_fingerprint": manifest["preflight_fingerprint"],
        "input_count": len(config.inputs),
        "run_manifest": config.outputs["run_manifest"][0],
        "completed_manifest_preserved": completed_manifest_preserved,
        "completed_manifest_matches_preflight": (
            completed_manifest_matches_preflight
        ),
        "checks": {
            "runtime_contract": "passed",
            "config_inputs_and_code": "passed",
            "completed_manifest": completed_manifest_state,
        },
    }


def _validate_manifest_contract(
    manifest: dict[str, Any],
    current_preflight: dict[str, Any],
) -> None:
    if manifest.get("preflight_fingerprint") != current_preflight[
        "preflight_fingerprint"
    ]:
        raise RuntimeConfigError(
            "Run manifest preflight fingerprint differs from current config, inputs, "
            "or code"
        )
    for key in (
        "config",
        "pipeline",
        "inputs",
        "outputs",
        "parameters",
        "provenance",
        "secret_scan",
    ):
        if manifest.get(key) != current_preflight[key]:
            raise RuntimeConfigError(f"Run manifest {key} differs from current preflight")
    manifest_resume = manifest.get("resume")
    if not isinstance(manifest_resume, dict):
        raise RuntimeConfigError("Run manifest resume contract is missing")
    for key in ("policy", "note"):
        if manifest_resume.get(key) != current_preflight["resume"][key]:
            raise RuntimeConfigError(
                f"Run manifest resume.{key} differs from current preflight"
            )
    manifest_equivalence = manifest.get("equivalence")
    if not isinstance(manifest_equivalence, dict):
        raise RuntimeConfigError("Run manifest equivalence contract is missing")
    for key in (
        "baseline_result_path",
        "baseline_result_sha256",
        "comparison",
    ):
        if manifest_equivalence.get(key) != current_preflight["equivalence"][key]:
            raise RuntimeConfigError(
                f"Run manifest equivalence.{key} differs from current preflight"
            )


def validate(config: RuntimeConfig) -> dict[str, Any]:
    result_path = config.output_path("result")
    manifest_path = config.output_path("run_manifest")
    if not result_path.is_file() or not manifest_path.is_file():
        raise RuntimeConfigError("Configured result or run manifest is missing")
    result = _load_json(result_path)
    baseline = _load_json(config.equivalence_baseline[1])
    expected_paths = {
        role: item.relative_path for role, item in config.inputs.items()
    }
    result_semantic_hash = semantic_result_hash(
        result,
        config.repo_root,
        expected_paths=expected_paths,
    )
    baseline_semantic_hash = semantic_result_hash(
        baseline,
        config.repo_root,
        expected_paths=expected_paths,
    )
    if result_semantic_hash != baseline_semantic_hash:
        raise RuntimeConfigError("Result semantic hash differs from baseline")
    manifest = _load_json(manifest_path)
    if manifest.get("status") != "completed":
        raise RuntimeConfigError("Run manifest is not completed")
    current_preflight = build_preflight_manifest(config)
    _validate_manifest_contract(manifest, current_preflight)
    if manifest.get("result", {}).get("sha256") != sha256_file(result_path):
        raise RuntimeConfigError("Run manifest result checksum mismatch")
    if manifest.get("result", {}).get("semantic_sha256") != result_semantic_hash:
        raise RuntimeConfigError("Run manifest result semantic checksum mismatch")
    if manifest.get("result", {}).get("validation_status") != "passed":
        raise RuntimeConfigError("Run manifest result validation is not passed")
    manifest_equivalence = manifest["equivalence"]
    if manifest_equivalence.get("status") != "passed":
        raise RuntimeConfigError("Run manifest equivalence is not passed")
    if (
        manifest_equivalence.get("baseline_semantic_sha256")
        != baseline_semantic_hash
    ):
        raise RuntimeConfigError("Run manifest baseline semantic checksum mismatch")
    if manifest_equivalence.get("result_semantic_sha256") != result_semantic_hash:
        raise RuntimeConfigError("Run manifest equivalence result checksum mismatch")
    try:
        anchor_status = result["judge_robustness"]["validation"]["status"]
    except (KeyError, TypeError) as exc:
        raise RuntimeConfigError("Section V result validation status is missing") from exc
    if anchor_status != "passed":
        raise RuntimeConfigError("Section V result validation is not passed")
    return {
        "status": "passed",
        "config_sha256": config.sha256,
        "result_sha256": sha256_file(result_path),
        "semantic_sha256": result_semantic_hash,
        "baseline_semantic_sha256": baseline_semantic_hash,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run portable, config-driven offline experiment workflows"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("preflight", "run", "validate"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--config", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_runtime_config(args.config)
        if args.command == "preflight":
            summary = preflight(config)
        elif args.command == "run":
            summary = run_configured_section_v(config)
        else:
            summary = validate(config)
    except (RuntimeConfigError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {"status": f"{args.command}_failed", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
