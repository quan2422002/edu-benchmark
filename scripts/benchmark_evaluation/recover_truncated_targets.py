"""Build or merge a fail-closed truncated-target recovery batch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


from edu_benchmark.benchmark_evaluation.recovery import (  # noqa: E402
    build_followup_recovery_manifest,
    build_recovery_manifest,
    finalize_followup_recovery_bundle,
    merge_recovery_bundle,
)

ROOT = Path(__file__).resolve().parents[2]
FULL_ROOT = (
    ROOT
    / "experiments/20260727_170150/outputs/benchmark_evaluation/"
    "full_1400_v1"
)
SOURCE_ROOT = FULL_ROOT / "target_gemini35"
RECOVERY_ROOT = Path("/tmp/edu-benchmark-plan05-gemini-recovery-1536")
FOLLOWUP_ROOT = RECOVERY_ROOT / "followup_2048"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument(
        "--source-output",
        type=Path,
        default=SOURCE_ROOT / "run_responses.jsonl",
    )
    build.add_argument(
        "--source-manifest",
        type=Path,
        default=SOURCE_ROOT / "run_manifest.json",
    )
    build.add_argument(
        "--output",
        type=Path,
        default=RECOVERY_ROOT / "candidate_manifest.json",
    )
    build.add_argument("--max-output-tokens", type=int, default=1536)
    followup = subparsers.add_parser("build-followup")
    followup.add_argument(
        "--recovery-output",
        type=Path,
        default=RECOVERY_ROOT / "run_responses.jsonl",
    )
    followup.add_argument(
        "--recovery-manifest",
        type=Path,
        default=RECOVERY_ROOT / "candidate_manifest.json",
    )
    followup.add_argument(
        "--recovery-run-manifest",
        type=Path,
        default=RECOVERY_ROOT / "run_manifest.json",
    )
    followup.add_argument(
        "--output",
        type=Path,
        default=FOLLOWUP_ROOT / "candidate_manifest.json",
    )
    followup.add_argument(
        "--max-output-tokens", type=int, default=2048
    )
    finalize = subparsers.add_parser("finalize-followup")
    finalize.add_argument(
        "--recovery-output", type=Path,
        default=RECOVERY_ROOT / "run_responses.jsonl",
    )
    finalize.add_argument(
        "--recovery-manifest", type=Path,
        default=RECOVERY_ROOT / "candidate_manifest.json",
    )
    finalize.add_argument(
        "--recovery-run-manifest", type=Path,
        default=RECOVERY_ROOT / "run_manifest.json",
    )
    finalize.add_argument(
        "--followup-output", type=Path,
        default=FOLLOWUP_ROOT / "run_responses.jsonl",
    )
    finalize.add_argument(
        "--followup-manifest", type=Path,
        default=FOLLOWUP_ROOT / "candidate_manifest.json",
    )
    finalize.add_argument(
        "--followup-run-manifest", type=Path,
        default=FOLLOWUP_ROOT / "run_manifest.json",
    )
    merge = subparsers.add_parser("merge")
    merge.add_argument(
        "--source-output",
        type=Path,
        default=SOURCE_ROOT / "run_responses.jsonl",
    )
    merge.add_argument(
        "--source-manifest",
        type=Path,
        default=SOURCE_ROOT / "run_manifest.json",
    )
    merge.add_argument(
        "--recovery-output",
        type=Path,
        default=RECOVERY_ROOT / "run_responses.jsonl",
    )
    merge.add_argument(
        "--recovery-manifest",
        type=Path,
        default=RECOVERY_ROOT / "candidate_manifest.json",
    )
    merge.add_argument(
        "--recovery-run-manifest",
        type=Path,
        default=RECOVERY_ROOT / "run_manifest.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "build":
        result = build_recovery_manifest(
            source_output=args.source_output,
            source_manifest=args.source_manifest,
            recovery_max_output_tokens=args.max_output_tokens,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_name(f".{args.output.name}.tmp")
        temporary.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(args.output)
        output = {
            "status": "locked",
            "candidate_count": result["candidate_count"],
            "max_output_tokens": result["recovery_max_output_tokens"],
            "output": str(args.output),
        }
    elif args.command == "build-followup":
        result = build_followup_recovery_manifest(
            recovery_output=args.recovery_output,
            recovery_manifest=args.recovery_manifest,
            recovery_run_manifest=args.recovery_run_manifest,
            followup_max_output_tokens=args.max_output_tokens,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_name(f".{args.output.name}.tmp")
        temporary.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(args.output)
        output = {
            "status": "locked",
            "candidate_count": result["candidate_count"],
            "reused_candidate_count": result["parent_completed_count"],
            "max_output_tokens": result["followup_max_output_tokens"],
            "output": str(args.output),
        }
    elif args.command == "finalize-followup":
        output = finalize_followup_recovery_bundle(
            recovery_output=args.recovery_output,
            recovery_manifest=args.recovery_manifest,
            recovery_run_manifest=args.recovery_run_manifest,
            followup_output=args.followup_output,
            followup_manifest=args.followup_manifest,
            followup_run_manifest=args.followup_run_manifest,
        )
    else:
        output = merge_recovery_bundle(
            source_output=args.source_output,
            source_manifest=args.source_manifest,
            recovery_output=args.recovery_output,
            recovery_manifest=args.recovery_manifest,
            recovery_run_manifest=args.recovery_run_manifest,
        )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
