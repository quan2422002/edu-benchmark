from __future__ import annotations

import hashlib
from pathlib import Path

from edu_benchmark.benchmark_registry import (
    promote_shared_benchmark,
    validate_shared_benchmark,
)


ROOT = Path(__file__).resolve().parents[2]
SHARED = ROOT / "shared/benchmark"
HISTORICAL_CANDIDATES = (
    ROOT
    / "experiments/20260722_000940/outputs/benchmark_conversion/full_v0"
    / "benchmark_candidate_splits.csv"
)
CANONICAL_CANDIDATES = SHARED / "datasets/candidate_pool/v1/candidates.csv"


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_shared_registry_counts_joins_and_authority_contract() -> None:
    result = validate_shared_benchmark(SHARED)
    assert result["status"] == "passed"
    assert result["criterion_count"] == 18
    assert result["phase1_dialogue_count"] == 665
    assert result["candidate_count"] == 2028
    assert result["candidate_family_count"] == 665
    assert result["selected_candidate_count"] == 1400
    assert result["selected_family_count"] == 655
    assert result["needs_uet_review_count"] == 628
    assert result["blocked_count"] == 0
    assert result["duplicate_candidate_id_count"] == 0


def test_promotion_is_byte_idempotent(tmp_path: Path) -> None:
    output = tmp_path / "shared/benchmark"
    first = promote_shared_benchmark(ROOT, output)
    first_hashes = _tree_hashes(output)
    second = promote_shared_benchmark(ROOT, output)
    assert second == first
    assert _tree_hashes(output) == first_hashes


def test_representative_candidate_consumer_is_byte_equivalent() -> None:
    assert CANONICAL_CANDIDATES.read_bytes() == HISTORICAL_CANDIDATES.read_bytes()
    consumer = (
        ROOT / "scripts/benchmark_specification/build_principle_grounding_pool.py"
    ).read_text(encoding="utf-8")
    assert "shared/benchmark/datasets/candidate_pool/v1/candidates.csv" in consumer


def test_local_or_large_payloads_are_not_promoted() -> None:
    assert not list(SHARED.rglob("*.jsonl"))
    assert not list(SHARED.rglob("*.xlsx"))
    assert not list(SHARED.rglob("provider_output*"))

