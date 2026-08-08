"""Deterministic promotion of validated experiment artifacts into shared storage."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


REGISTRY_FIELDS = (
    "artifact_id",
    "artifact_type",
    "version",
    "status",
    "canonical_path",
    "source_experiment",
    "source_path",
    "sha256",
    "schema_version",
    "dialogue_count",
    "family_count",
    "candidate_count",
    "approval_authority",
    "approved_at",
    "supersedes",
    "access_policy",
    "notes",
)

CHECKLIST_CRITERIA = Path(
    "experiments/20260722_000940/inherited_resources/from_20260709_155523/"
    "checklists/raw-dialogue-audit-criteria-v0.csv"
)
CHECKLIST_MARKDOWN = Path(
    "experiments/20260722_000940/inherited_resources/from_20260709_155523/"
    "checklists/raw-dialogue-quality-checklist-v0.md"
)
PHASE1_DIALOGUES = Path(
    "experiments/20260722_000940/outputs/benchmark_conversion/"
    "conversion_input_pass_samples.csv"
)
CONVERSION_ROOT = Path(
    "experiments/20260722_000940/outputs/benchmark_conversion/full_v0"
)
CANDIDATES = CONVERSION_ROOT / "benchmark_candidate_splits.csv"
TRACE = CONVERSION_ROOT / "conversion_trace.csv"
DISPOSITIONS = CONVERSION_ROOT / "conversion_dispositions.csv"
SELECTION_SOURCE = Path(
    "experiments/20260727_170150/outputs/benchmark_candidate_pool/"
    "eligible_without_plan03_review.csv"
)
SCORING_ROOT = Path(
    "experiments/20260727_170150/outputs/principle_requirement_scoring/"
    "full_gemini35_medium_v1"
)
SCORING_ANALYSIS = SCORING_ROOT / "full_run_analysis.json"
SCORING_REVIEW_QUEUE = SCORING_ROOT / "full_run_review_queue.csv"
SCORING_RUN_MANIFEST = SCORING_ROOT / "run_manifest.json"
SCORING_RAW_LOCATOR = SCORING_ROOT / "run_full.jsonl"
CAPABILITY_ROOT = Path(
    "experiments/20260727_170150/inherited_resources/from_20260722_000940/"
    "benchmark_specification/capability_model"
)
PRINCIPLE_ROOT = Path(
    "experiments/20260727_170150/inherited_resources/from_20260722_000940/"
    "benchmark_specification/principle_foundation"
)
RUBRIC_ROOT = Path(
    "experiments/20260727_170150/outputs/benchmark_rubric"
)


class PromotionError(RuntimeError):
    """Raised when a source or promoted artifact violates the locked contract."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_path(repo_root: Path, relative_path: Path) -> Path:
    path = repo_root / relative_path
    if not path.is_file():
        raise PromotionError(f"required source is missing: {relative_path}")
    return path


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(
    path: Path,
    fieldnames: Sequence[str],
    rows: Iterable[Mapping[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _copy(repo_root: Path, source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(_repo_path(repo_root, source), destination)


def _unique(rows: Sequence[Mapping[str, str]], key: str, expected: int) -> set[str]:
    values = [row.get(key, "") for row in rows]
    if any(not value for value in values):
        raise PromotionError(f"blank {key} in locked source")
    unique_values = set(values)
    if len(rows) != expected or len(unique_values) != expected:
        raise PromotionError(
            f"{key} invariant failed: rows={len(rows)}, unique={len(unique_values)}, "
            f"expected={expected}"
        )
    return unique_values


def _source_record(repo_root: Path, path: Path, role: str) -> dict[str, Any]:
    source = _repo_path(repo_root, path)
    record: dict[str, Any] = {
        "path": path.as_posix(),
        "role": role,
        "sha256": sha256_file(source),
    }
    if source.suffix == ".csv":
        record["row_count"] = len(_read_csv(source))
    return record


def _output_record(shared_root: Path, relative_path: Path) -> dict[str, Any]:
    output = shared_root / relative_path
    record: dict[str, Any] = {
        "path": relative_path.as_posix(),
        "sha256": sha256_file(output),
    }
    if output.suffix == ".csv":
        record["row_count"] = len(_read_csv(output))
    return record


def _manifest(
    *,
    artifact_id: str,
    artifact_type: str,
    version: str,
    status: str,
    canonical_path: str,
    source_experiment: str,
    sources: Sequence[Mapping[str, Any]],
    files: Sequence[Mapping[str, Any]],
    transformation_mode: str,
    invariants: Mapping[str, Any],
    approval_authority: str,
    approved_at: str | None,
    pending_authorities: Sequence[str],
    access_policy: str,
    limitations: Sequence[str],
    upstream_locators: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "version": version,
        "status": status,
        "canonical_path": canonical_path,
        "source_experiment": source_experiment,
        "sources": list(sources),
        "upstream_locators": list(upstream_locators),
        "transformation": {
            "command": (
                "/home/quannda/miniconda3/envs/benchmark_env/bin/python "
                "scripts/benchmark_registry/promote_shared_benchmark.py"
            ),
            "implementation": (
                "src/edu_benchmark/benchmark_registry/promotion.py"
            ),
            "mode": transformation_mode,
        },
        "files": list(files),
        "invariants": dict(invariants),
        "authority": {
            "approval_authority": approval_authority,
            "approved_at": approved_at,
            "pending_authorities": list(pending_authorities),
        },
        "access_policy": access_policy,
        "limitations": list(limitations),
    }


def _validate_sources(repo_root: Path) -> dict[str, Any]:
    criteria = _read_csv(_repo_path(repo_root, CHECKLIST_CRITERIA))
    criterion_ids = _unique(criteria, "criterion_id", 18)

    dialogues = _read_csv(_repo_path(repo_root, PHASE1_DIALOGUES))
    dialogue_ids = _unique(dialogues, "sample_id", 665)
    if {row["raw_quality_decision"] for row in dialogues} != {"pass"}:
        raise PromotionError("Phase-1 input contains a non-pass dialogue")

    candidates = _read_csv(_repo_path(repo_root, CANDIDATES))
    candidate_ids = _unique(candidates, "benchmark_candidate_id", 2028)
    candidate_families = {row["sample_id"] for row in candidates}
    if candidate_families != dialogue_ids:
        raise PromotionError("candidate families do not equal Phase-1 dialogue IDs")

    trace = _read_csv(_repo_path(repo_root, TRACE))
    trace_ids = _unique(trace, "benchmark_candidate_id", 2028)
    if trace_ids != candidate_ids:
        raise PromotionError("candidate/trace ID sets differ")

    dispositions = _read_csv(_repo_path(repo_root, DISPOSITIONS))
    disposition_ids = _unique(dispositions, "sample_id", 665)
    if disposition_ids != dialogue_ids:
        raise PromotionError("conversion dispositions do not cover all families")
    if {row["conversion_disposition"] for row in dispositions} != {"converted"}:
        raise PromotionError("conversion dispositions contain a non-converted row")

    selection = _read_csv(_repo_path(repo_root, SELECTION_SOURCE))
    selected_ids = _unique(selection, "benchmark_candidate_id", 1400)
    selected_families = {row["sample_id"] for row in selection}
    if len(selected_families) != 655:
        raise PromotionError("provisional selection must contain 655 families")
    if not selected_ids <= candidate_ids:
        raise PromotionError("selection contains an ID outside candidate pool")
    if {row["eligibility_status"] for row in selection} != {
        "eligible_without_plan03_review"
    }:
        raise PromotionError("selection contains an unexpected eligibility status")

    analysis = json.loads(_repo_path(repo_root, SCORING_ANALYSIS).read_text())
    eligibility = analysis["eligibility"]["candidate_ids"]
    eligible_ids = set(eligibility["eligible_without_plan03_review"])
    review_ids = set(eligibility["needs_uet_review"])
    blocked_ids = set(eligibility["blocked"])
    if len(eligible_ids) != 1400 or len(review_ids) != 628 or blocked_ids:
        raise PromotionError("eligibility count invariant is not 1400/628/0")
    if eligible_ids != selected_ids:
        raise PromotionError("selection IDs differ from analysis eligible IDs")
    if eligible_ids & review_ids or eligible_ids | review_ids != candidate_ids:
        raise PromotionError("eligibility sets are not disjoint/exhaustive")

    queue = _read_csv(_repo_path(repo_root, SCORING_REVIEW_QUEUE))
    flagged = [row for row in queue if row["queue_type"] == "flagged"]
    if len(flagged) != 628:
        raise PromotionError("review queue must contain 628 flagged candidates")
    if {row["benchmark_candidate_id"] for row in flagged} != review_ids:
        raise PromotionError("review queue IDs differ from analysis review IDs")

    return {
        "criteria": criteria,
        "criterion_ids": criterion_ids,
        "dialogues": dialogues,
        "dialogue_ids": dialogue_ids,
        "candidates": candidates,
        "candidate_ids": candidate_ids,
        "trace": trace,
        "dispositions": dispositions,
        "selection": selection,
        "selected_ids": selected_ids,
        "selected_families": selected_families,
        "analysis": analysis,
        "eligible_ids": eligible_ids,
        "review_ids": review_ids,
        "flagged_queue": flagged,
    }


def _build_selection_rows(source: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, row in enumerate(source, 2):
        rows.append(
            {
                "benchmark_candidate_id": row["benchmark_candidate_id"],
                "sample_id": row["sample_id"],
                "family_id": row["sample_id"],
                "selection_status": "provisional_selected",
                "eligibility_status": row["eligibility_status"],
                "selection_reason": "no_plan03_review_flag",
                "source_experiment": "20260727_170150",
                "source_path": SELECTION_SOURCE.as_posix(),
                "source_row_number": str(index),
            }
        )
    return rows


def _build_requirement_score_rows(inventory: Mapping[str, Any]) -> list[dict[str, str]]:
    selected_by_id = {
        row["benchmark_candidate_id"]: row for row in inventory["selection"]
    }
    review_by_id = {
        row["benchmark_candidate_id"]: row for row in inventory["flagged_queue"]
    }
    sample_by_id = {
        row["benchmark_candidate_id"]: row["sample_id"]
        for row in inventory["candidates"]
    }
    rows: list[dict[str, str]] = []
    for candidate_id in sorted(inventory["candidate_ids"]):
        if candidate_id in selected_by_id:
            source = selected_by_id[candidate_id]
            eligibility_status = "eligible_without_plan03_review"
            review_reasons = ""
            source_path = SELECTION_SOURCE
        else:
            source = review_by_id[candidate_id]
            eligibility_status = "needs_uet_review"
            review_reasons = source["review_reasons"]
            source_path = SCORING_REVIEW_QUEUE
        rows.append(
            {
                "benchmark_candidate_id": candidate_id,
                "sample_id": sample_by_id[candidate_id],
                "eligibility_status": eligibility_status,
                "required_principle_set": source["required_principle_set"],
                "alternative_principle_set": source["alternative_principle_set"],
                "principle_scores_json": source["principle_scores_json"],
                "review_reasons": review_reasons,
                "source_path": source_path.as_posix(),
            }
        )
    return rows


def _readme() -> str:
    return """# Shared benchmark artifacts

This directory is the canonical discovery surface for stable benchmark inputs.
Historical experiments remain immutable provenance and are not deleted.

## What is here

- `artifact_registry.csv`: one row per versioned bundle, including status,
  source, checksum, counts, authority, access policy, and limitations.
- `checklists/raw_dialogue/v1/`: the 18-criterion raw-dialogue audit checklist.
- `datasets/phase1_pass_dialogues/v1/`: 665 dialogue families that passed the
  operational Phase-1 audit; this is not final HNMU approval.
- `datasets/candidate_pool/v1/`: 2,028 validated conversion candidates from the
  665 families, with one-to-one trace and family dispositions.
- `selections/provisional_evaluation_pool/v1/`: a minimal 1,400-ID provisional
  selection plus compact scores/status for all 2,028 candidates. The remaining
  628 require UET review; zero are structurally blocked.
- `specifications/`: the current capability, pedagogical-principle, and rubric
  bundles. Their source status remains `needs_hnmu_review`.

## Status and authority

`shared` means canonical for discovery and consumption, not scientifically
final. The 1,400 selection is a `provisional_evaluation_pool`, never benchmark
v1 or ground truth. Model-derived requirement scores are operational evidence,
not expert labels. Read each manifest before use.

## Access and large/local sources

Tracked payloads were already tracked in their source experiments or are compact
projections of tracked analysis tables. Raw HNMU XLSX, raw model JSONL, provider
responses, and large evaluation outputs are not copied here. Manifests retain
their locators and hashes when they are part of upstream provenance.

## Consumer migration and rollback

The representative migrated consumer is
`scripts/benchmark_specification/build_principle_grounding_pool.py`, whose
default candidate input is now
`shared/benchmark/datasets/candidate_pool/v1/candidates.csv`.

Deprecated source-to-canonical mapping:

| Historical source | Canonical path |
|---|---|
| `.../checklists/raw-dialogue-audit-criteria-v0.csv` | `checklists/raw_dialogue/v1/criteria.csv` |
| `.../benchmark_conversion/conversion_input_pass_samples.csv` | `datasets/phase1_pass_dialogues/v1/dialogues.csv` |
| `.../benchmark_conversion/full_v0/benchmark_candidate_splits.csv` | `datasets/candidate_pool/v1/candidates.csv` |
| `.../benchmark_candidate_pool/eligible_without_plan03_review.csv` | `selections/provisional_evaluation_pool/v1/selection.csv` |

The historical paths remain valid rollback/provenance sources during this
migration; Plan 03 does not delete them.
"""


def _write_bundle_manifest(
    shared_root: Path,
    relative_root: Path,
    manifest: Mapping[str, Any],
) -> str:
    path = shared_root / relative_root / "manifest.json"
    _write_json(path, manifest)
    return sha256_file(path)


def _build_shared_tree(repo_root: Path, shared_root: Path) -> dict[str, Any]:
    inventory = _validate_sources(repo_root)
    shared_root.mkdir(parents=True, exist_ok=True)
    (shared_root / "README.md").write_text(_readme(), encoding="utf-8")

    registry_rows: list[dict[str, Any]] = []

    checklist_root = Path("checklists/raw_dialogue/v1")
    _copy(repo_root, CHECKLIST_CRITERIA, shared_root / checklist_root / "criteria.csv")
    _copy(repo_root, CHECKLIST_MARKDOWN, shared_root / checklist_root / "checklist.md")
    manifest = _manifest(
        artifact_id="raw_dialogue_checklist",
        artifact_type="checklist",
        version="v1",
        status="operational_v0_awaiting_hnmu_review",
        canonical_path=f"shared/benchmark/{checklist_root.as_posix()}",
        source_experiment="20260709_155523",
        sources=[
            _source_record(repo_root, CHECKLIST_CRITERIA, "criteria"),
            _source_record(repo_root, CHECKLIST_MARKDOWN, "human_checklist"),
        ],
        files=[
            _output_record(shared_root, checklist_root / "criteria.csv"),
            _output_record(shared_root, checklist_root / "checklist.md"),
        ],
        transformation_mode="byte_copy",
        invariants={"criterion_count": 18, "unique_criterion_count": 18},
        approval_authority="UET operational audit use",
        approved_at=None,
        pending_authorities=["HNMU integrated methodology confirmation"],
        access_policy="repository_internal_research",
        limitations=["Not a benchmark-response evaluation rubric."],
    )
    manifest_hash = _write_bundle_manifest(shared_root, checklist_root, manifest)
    registry_rows.append(
        {
            "artifact_id": "raw_dialogue_checklist",
            "artifact_type": "checklist",
            "version": "v1",
            "status": "operational_v0_awaiting_hnmu_review",
            "canonical_path": f"shared/benchmark/{checklist_root.as_posix()}",
            "source_experiment": "20260709_155523",
            "source_path": CHECKLIST_CRITERIA.as_posix(),
            "sha256": manifest_hash,
            "schema_version": "raw-dialogue-audit-criteria-v0",
            "approval_authority": "UET operational audit use",
            "access_policy": "repository_internal_research",
            "notes": "18 criteria; HNMU integrated confirmation pending",
        }
    )

    phase1_root = Path("datasets/phase1_pass_dialogues/v1")
    _copy(repo_root, PHASE1_DIALOGUES, shared_root / phase1_root / "dialogues.csv")
    manifest = _manifest(
        artifact_id="phase1_pass_dialogues",
        artifact_type="dataset",
        version="v1",
        status="provisional_phase1_pass",
        canonical_path=f"shared/benchmark/{phase1_root.as_posix()}",
        source_experiment="20260722_000940",
        sources=[_source_record(repo_root, PHASE1_DIALOGUES, "phase1_pass_input")],
        files=[_output_record(shared_root, phase1_root / "dialogues.csv")],
        transformation_mode="byte_copy",
        invariants={
            "dialogue_count": 665,
            "unique_sample_id_count": 665,
            "quality_decision": "pass",
        },
        approval_authority="UET operational Phase-1 audit",
        approved_at=None,
        pending_authorities=["HNMU final sample review"],
        access_policy="repository_internal_research",
        limitations=[
            "Operational Phase-1 pass does not mean final HNMU approval."
        ],
    )
    manifest_hash = _write_bundle_manifest(shared_root, phase1_root, manifest)
    registry_rows.append(
        {
            "artifact_id": "phase1_pass_dialogues",
            "artifact_type": "dataset",
            "version": "v1",
            "status": "provisional_phase1_pass",
            "canonical_path": f"shared/benchmark/{phase1_root.as_posix()}",
            "source_experiment": "20260722_000940",
            "source_path": PHASE1_DIALOGUES.as_posix(),
            "sha256": manifest_hash,
            "schema_version": "conversion-input-pass-samples-v1",
            "dialogue_count": 665,
            "family_count": 665,
            "approval_authority": "UET operational Phase-1 audit",
            "access_policy": "repository_internal_research",
            "notes": "Not final HNMU approval",
        }
    )

    candidate_root = Path("datasets/candidate_pool/v1")
    for source, name in (
        (CANDIDATES, "candidates.csv"),
        (TRACE, "trace.csv"),
        (DISPOSITIONS, "dispositions.csv"),
    ):
        _copy(repo_root, source, shared_root / candidate_root / name)
    manifest = _manifest(
        artifact_id="candidate_pool",
        artifact_type="dataset",
        version="v1",
        status="conversion_validated_provisional",
        canonical_path=f"shared/benchmark/{candidate_root.as_posix()}",
        source_experiment="20260722_000940",
        sources=[
            _source_record(repo_root, CANDIDATES, "candidate_payload"),
            _source_record(repo_root, TRACE, "one_to_one_trace"),
            _source_record(repo_root, DISPOSITIONS, "family_disposition"),
        ],
        files=[
            _output_record(shared_root, candidate_root / "candidates.csv"),
            _output_record(shared_root, candidate_root / "trace.csv"),
            _output_record(shared_root, candidate_root / "dispositions.csv"),
        ],
        transformation_mode="byte_copy",
        invariants={
            "candidate_count": 2028,
            "unique_candidate_count": 2028,
            "family_count": 665,
            "trace_count": 2028,
            "converted_disposition_count": 665,
            "blocking_error_count": 0,
        },
        approval_authority="Project lead/UET conversion contract",
        approved_at="2026-07-23",
        pending_authorities=["UET/HNMU candidate quality review"],
        access_policy="repository_internal_research",
        limitations=[
            "Conversion validation does not make this a frozen benchmark."
        ],
    )
    manifest_hash = _write_bundle_manifest(shared_root, candidate_root, manifest)
    registry_rows.append(
        {
            "artifact_id": "candidate_pool",
            "artifact_type": "dataset",
            "version": "v1",
            "status": "conversion_validated_provisional",
            "canonical_path": f"shared/benchmark/{candidate_root.as_posix()}",
            "source_experiment": "20260722_000940",
            "source_path": CANDIDATES.as_posix(),
            "sha256": manifest_hash,
            "schema_version": "each-tutor-turn-v1",
            "dialogue_count": 665,
            "family_count": 665,
            "candidate_count": 2028,
            "approval_authority": "Project lead/UET conversion contract",
            "approved_at": "2026-07-23",
            "access_policy": "repository_internal_research",
            "notes": "Validated conversion output; not raw data or benchmark v1",
        }
    )

    selection_root = Path("selections/provisional_evaluation_pool/v1")
    selection_fields = (
        "benchmark_candidate_id",
        "sample_id",
        "family_id",
        "selection_status",
        "eligibility_status",
        "selection_reason",
        "source_experiment",
        "source_path",
        "source_row_number",
    )
    score_fields = (
        "benchmark_candidate_id",
        "sample_id",
        "eligibility_status",
        "required_principle_set",
        "alternative_principle_set",
        "principle_scores_json",
        "review_reasons",
        "source_path",
    )
    _write_csv(
        shared_root / selection_root / "selection.csv",
        selection_fields,
        _build_selection_rows(inventory["selection"]),
    )
    _write_csv(
        shared_root / selection_root / "requirement_scores.csv",
        score_fields,
        _build_requirement_score_rows(inventory),
    )
    run_manifest = json.loads(
        _repo_path(repo_root, SCORING_RUN_MANIFEST).read_text(encoding="utf-8")
    )
    expected_raw_hash = run_manifest["integrity"]["run_file_sha256"]
    raw_path = repo_root / SCORING_RAW_LOCATOR
    if raw_path.is_file() and sha256_file(raw_path) != expected_raw_hash:
        raise PromotionError("local raw scoring run differs from its tracked manifest")
    raw_locator = [
        {
            "path": SCORING_RAW_LOCATOR.as_posix(),
            "sha256": expected_raw_hash,
            "record_count": run_manifest["integrity"]["record_count"],
            "tracked_payload": False,
            "role": "upstream_raw_model_run_not_copied",
        }
    ]
    manifest = _manifest(
        artifact_id="provisional_evaluation_pool",
        artifact_type="selection",
        version="v1",
        status="provisional_awaiting_uet_hnmu_review",
        canonical_path=f"shared/benchmark/{selection_root.as_posix()}",
        source_experiment="20260727_170150",
        sources=[
            _source_record(repo_root, SELECTION_SOURCE, "selected_payload_source"),
            _source_record(repo_root, SCORING_ANALYSIS, "eligibility_analysis"),
            _source_record(repo_root, SCORING_REVIEW_QUEUE, "review_backlog"),
            _source_record(repo_root, SCORING_RUN_MANIFEST, "run_provenance"),
        ],
        upstream_locators=raw_locator,
        files=[
            _output_record(shared_root, selection_root / "selection.csv"),
            _output_record(shared_root, selection_root / "requirement_scores.csv"),
        ],
        transformation_mode="compact_projection_and_join",
        invariants={
            "candidate_pool_count": 2028,
            "selected_candidate_count": 1400,
            "selected_family_count": 655,
            "needs_uet_review_count": 628,
            "blocked_count": 0,
            "duplicate_candidate_id_count": 0,
        },
        approval_authority="UET operational priority decision",
        approved_at="2026-07-28",
        pending_authorities=[
            "UET disposition for 628 review candidates",
            "HNMU integrated task/rubric review",
        ],
        access_policy="repository_internal_research",
        limitations=[
            "Selection is not benchmark v1, ground truth, or HNMU confirmation.",
            "Requirement scores come from one model run without expert accuracy labels.",
        ],
    )
    manifest_hash = _write_bundle_manifest(shared_root, selection_root, manifest)
    registry_rows.append(
        {
            "artifact_id": "provisional_evaluation_pool",
            "artifact_type": "selection",
            "version": "v1",
            "status": "provisional_awaiting_uet_hnmu_review",
            "canonical_path": f"shared/benchmark/{selection_root.as_posix()}",
            "source_experiment": "20260727_170150",
            "source_path": SELECTION_SOURCE.as_posix(),
            "sha256": manifest_hash,
            "schema_version": "provisional-evaluation-pool-v1",
            "family_count": 655,
            "candidate_count": 1400,
            "approval_authority": "UET operational priority decision",
            "approved_at": "2026-07-28",
            "access_policy": "repository_internal_research",
            "notes": "1,400 selected; 628 need UET review; 0 blocked",
        }
    )

    specification_bundles = (
        {
            "artifact_id": "tutor_capabilities",
            "root": Path("specifications/tutor_capabilities/v0"),
            "source_root": CAPABILITY_ROOT,
            "files": ("tutor_capabilities.csv", "tutor_capability_model.md"),
            "primary": "tutor_capabilities.csv",
            "count_key": "capability_count",
            "count": 6,
            "type": "specification",
        },
        {
            "artifact_id": "pedagogical_principles",
            "root": Path("specifications/pedagogical_principles/v0"),
            "source_root": PRINCIPLE_ROOT,
            "files": ("pedagogical_principles.csv",),
            "primary": "pedagogical_principles.csv",
            "count_key": "principle_count",
            "count": 6,
            "type": "specification",
        },
        {
            "artifact_id": "rubric_library",
            "root": Path("specifications/rubric_library/v0"),
            "source_root": RUBRIC_ROOT,
            "files": (
                "benchmark_tasks.csv",
                "rubrics.csv",
                "serious_errors.csv",
                "provenance_matrix.csv",
                "rubric_review_packet.md",
            ),
            "primary": "rubrics.csv",
            "count_key": "rubric_count",
            "count": 22,
            "type": "specification",
        },
    )
    for bundle in specification_bundles:
        relative_root = bundle["root"]
        sources: list[dict[str, Any]] = []
        outputs: list[dict[str, Any]] = []
        for name in bundle["files"]:
            source = bundle["source_root"] / name
            _copy(repo_root, source, shared_root / relative_root / name)
            sources.append(_source_record(repo_root, source, name))
            outputs.append(_output_record(shared_root, relative_root / name))
        primary_rows = _read_csv(
            shared_root / relative_root / str(bundle["primary"])
        )
        if len(primary_rows) != bundle["count"]:
            raise PromotionError(f"{bundle['artifact_id']} count invariant failed")
        if {row["status"] for row in primary_rows} != {"needs_hnmu_review"}:
            raise PromotionError(
                f"{bundle['artifact_id']} status is not needs_hnmu_review"
            )
        manifest = _manifest(
            artifact_id=str(bundle["artifact_id"]),
            artifact_type=str(bundle["type"]),
            version="v0",
            status="needs_hnmu_review",
            canonical_path=f"shared/benchmark/{relative_root.as_posix()}",
            source_experiment="20260727_170150",
            sources=sources,
            files=outputs,
            transformation_mode="byte_copy",
            invariants={str(bundle["count_key"]): bundle["count"]},
            approval_authority="UET provisional operational use",
            approved_at=None,
            pending_authorities=["HNMU content confirmation"],
            access_policy="repository_internal_research",
            limitations=[
                "Provisional specification; not a validated or frozen benchmark contract."
            ],
        )
        manifest_hash = _write_bundle_manifest(shared_root, relative_root, manifest)
        registry_rows.append(
            {
                "artifact_id": bundle["artifact_id"],
                "artifact_type": bundle["type"],
                "version": "v0",
                "status": "needs_hnmu_review",
                "canonical_path": f"shared/benchmark/{relative_root.as_posix()}",
                "source_experiment": "20260727_170150",
                "source_path": (bundle["source_root"] / str(bundle["primary"])).as_posix(),
                "sha256": manifest_hash,
                "schema_version": f"{bundle['artifact_id']}-v0",
                "approval_authority": "UET provisional operational use",
                "access_policy": "repository_internal_research",
                "notes": "HNMU content confirmation pending",
            }
        )

    _write_csv(shared_root / "artifact_registry.csv", REGISTRY_FIELDS, registry_rows)
    return validate_shared_benchmark(shared_root)


def _validate_manifest(shared_root: Path, registry_row: Mapping[str, str]) -> None:
    prefix = "shared/benchmark/"
    canonical = registry_row["canonical_path"]
    if not canonical.startswith(prefix):
        raise PromotionError(f"non-canonical registry path: {canonical}")
    relative_root = Path(canonical.removeprefix(prefix))
    manifest_path = shared_root / relative_root / "manifest.json"
    if not manifest_path.is_file():
        raise PromotionError(f"missing manifest: {manifest_path}")
    if sha256_file(manifest_path) != registry_row["sha256"]:
        raise PromotionError(f"registry/manifest hash mismatch: {canonical}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["artifact_id"] != registry_row["artifact_id"]:
        raise PromotionError(f"registry/manifest artifact mismatch: {canonical}")
    for record in manifest["files"]:
        output = shared_root / record["path"]
        if not output.is_file() or sha256_file(output) != record["sha256"]:
            raise PromotionError(f"manifest file hash mismatch: {record['path']}")
        if output.suffix == ".csv" and len(_read_csv(output)) != record["row_count"]:
            raise PromotionError(f"manifest row count mismatch: {record['path']}")


def validate_shared_benchmark(shared_root: Path) -> dict[str, Any]:
    """Validate registry, manifests, checksums, counts, joins, and authority flags."""

    registry_path = shared_root / "artifact_registry.csv"
    if not registry_path.is_file():
        raise PromotionError(f"missing artifact registry: {registry_path}")
    registry = _read_csv(registry_path)
    if len(registry) != 7 or len({row["artifact_id"] for row in registry}) != 7:
        raise PromotionError("registry must contain seven unique bundles")
    for row in registry:
        _validate_manifest(shared_root, row)

    criteria = _read_csv(
        shared_root / "checklists/raw_dialogue/v1/criteria.csv"
    )
    dialogues = _read_csv(
        shared_root / "datasets/phase1_pass_dialogues/v1/dialogues.csv"
    )
    candidates = _read_csv(
        shared_root / "datasets/candidate_pool/v1/candidates.csv"
    )
    trace = _read_csv(shared_root / "datasets/candidate_pool/v1/trace.csv")
    dispositions = _read_csv(
        shared_root / "datasets/candidate_pool/v1/dispositions.csv"
    )
    selection = _read_csv(
        shared_root / "selections/provisional_evaluation_pool/v1/selection.csv"
    )
    scores = _read_csv(
        shared_root
        / "selections/provisional_evaluation_pool/v1/requirement_scores.csv"
    )

    criterion_ids = _unique(criteria, "criterion_id", 18)
    dialogue_ids = _unique(dialogues, "sample_id", 665)
    candidate_ids = _unique(candidates, "benchmark_candidate_id", 2028)
    trace_ids = _unique(trace, "benchmark_candidate_id", 2028)
    disposition_ids = _unique(dispositions, "sample_id", 665)
    selected_ids = _unique(selection, "benchmark_candidate_id", 1400)
    score_ids = _unique(scores, "benchmark_candidate_id", 2028)

    if trace_ids != candidate_ids or score_ids != candidate_ids:
        raise PromotionError("candidate/trace/score ID sets are not equal")
    candidate_families = {row["sample_id"] for row in candidates}
    if candidate_families != dialogue_ids or disposition_ids != dialogue_ids:
        raise PromotionError("dialogue/family/disposition sets are not equal")
    if not selected_ids <= candidate_ids:
        raise PromotionError("selected IDs are not a subset of candidate pool")
    if len({row["family_id"] for row in selection}) != 655:
        raise PromotionError("selection family count is not 655")
    statuses = Counter(row["eligibility_status"] for row in scores)
    if statuses != Counter(
        {"eligible_without_plan03_review": 1400, "needs_uet_review": 628}
    ):
        raise PromotionError(f"score eligibility invariant failed: {statuses}")
    if {
        row["benchmark_candidate_id"]
        for row in scores
        if row["eligibility_status"] == "eligible_without_plan03_review"
    } != selected_ids:
        raise PromotionError("score eligibility IDs differ from selection IDs")
    if any(row["status"] != "needs_hnmu_review" for row in registry[-3:]):
        raise PromotionError("specification registry statuses are not provisional")
    if list(shared_root.rglob("run_full.jsonl")):
        raise PromotionError("raw model run must not be promoted into shared")

    return {
        "status": "passed",
        "registry_bundle_count": 7,
        "criterion_count": len(criterion_ids),
        "phase1_dialogue_count": len(dialogue_ids),
        "candidate_count": len(candidate_ids),
        "candidate_family_count": len(candidate_families),
        "trace_count": len(trace_ids),
        "disposition_count": len(disposition_ids),
        "selected_candidate_count": len(selected_ids),
        "selected_family_count": len({row["family_id"] for row in selection}),
        "needs_uet_review_count": statuses["needs_uet_review"],
        "blocked_count": 0,
        "duplicate_candidate_id_count": 0,
        "registry_sha256": sha256_file(registry_path),
    }


def promote_shared_benchmark(repo_root: Path, output_root: Path | None = None) -> dict[str, Any]:
    """Build a complete staged shared tree, validate it, then swap it atomically."""

    repo_root = repo_root.resolve()
    destination = (output_root or repo_root / "shared/benchmark").resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.with_name(f".{destination.name}.staging")
    backup = destination.with_name(f".{destination.name}.backup")
    if staging.exists():
        shutil.rmtree(staging)
    if backup.exists():
        shutil.rmtree(backup)
    summary = _build_shared_tree(repo_root, staging)
    try:
        if destination.exists():
            destination.replace(backup)
        staging.replace(destination)
    except BaseException:
        if destination.exists() and backup.exists():
            shutil.rmtree(destination)
        if backup.exists():
            backup.replace(destination)
        raise
    if backup.exists():
        shutil.rmtree(backup)
    return summary
