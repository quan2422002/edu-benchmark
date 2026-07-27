from pathlib import Path

from edu_benchmark.benchmark_specification.manifest import (
    build_input_manifest,
    sha256_file,
)
from edu_benchmark.benchmark_specification.provenance import (
    validate_provenance_ids,
)


def test_input_manifest_uses_relative_paths_and_hashes(tmp_path: Path):
    source = tmp_path / "input.txt"
    source.write_text("benchmark\n", encoding="utf-8")
    manifest = build_input_manifest(
        tmp_path,
        [source],
        created_at="2026-07-25T00:00:00+07:00",
    )
    assert manifest["files"][0] == {
        "path": "input.txt",
        "size_bytes": 10,
        "sha256": sha256_file(source),
    }


def test_provenance_rejects_unknown_source_ids():
    rows = [
        {
            "item_id": "TASK-01",
            "research_ids": "RS-UNKNOWN",
            "learning_material_ids": "LM-UNKNOWN",
            "status": "needs_hnmu_review",
        }
    ]
    errors = validate_provenance_ids(
        rows,
        known_item_ids={"TASK-01"},
        known_research_ids={"RS-1"},
        known_learning_material_ids={"LM-1"},
    )
    assert "row_2:unknown_research_id:RS-UNKNOWN" in errors
    assert "row_2:unknown_learning_material_id:LM-UNKNOWN" in errors
