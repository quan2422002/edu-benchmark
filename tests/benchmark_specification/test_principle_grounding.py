from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from edu_benchmark.benchmark_specification.manifest import sha256_file
from edu_benchmark.benchmark_specification.principle_grounding import (
    GROUNDING_POOL_COLUMNS,
    materialize_principle_grounding_pool,
)


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _candidate(candidate_id: str = "BC-01", sample_id: str = "S-01") -> dict[str, str]:
    return {
        "benchmark_candidate_id": candidate_id,
        "sample_id": sample_id,
        "grade": "6",
        "lesson": "Bài 1",
        "position": "Mục 1",
        "bloom_level": "Nhận biết",
        "student_prompt": "Bit là gì ạ?",
        "conversation_history": "[]",
        "gold_response": "Em thử nhớ lại nhé.",
        "gold_answer": "Bit",
    }


def _source(sample_id: str = "S-01") -> dict[str, str]:
    return {
        "sample_id": sample_id,
        "grade": "6",
        "lesson": "Bài 1",
        "position": "Mục 1",
        "bloom_level": "Nhận biết",
        "question": "Máy tính dùng đơn vị nhỏ nhất nào để đo thông tin?",
        "answer_sgv": "Bit",
    }


def _build(tmp_path: Path) -> tuple[Path, Path]:
    candidate_path = tmp_path / "candidate.csv"
    source_path = tmp_path / "source.csv"
    _write_csv(candidate_path, list(_candidate()), [_candidate()])
    _write_csv(source_path, list(_source()), [_source()])
    materialize_principle_grounding_pool(
        repo_root=tmp_path,
        candidate_path=candidate_path,
        source_dialogue_paths=(source_path,),
        output_dir=tmp_path / "output",
        created_at="2026-07-27T00:00:00+07:00",
    )
    return tmp_path / "output/candidate_principle_grounding_pool.csv", (
        tmp_path / "output/candidate_principle_grounding_pool_manifest.json"
    )


def test_materializes_source_question_without_gold_response(tmp_path: Path) -> None:
    output_path, manifest_path = _build(tmp_path)

    with output_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert tuple(reader.fieldnames or ()) == GROUNDING_POOL_COLUMNS
        rows = list(reader)
    assert rows[0]["source_question"] == _source()["question"]
    assert "gold_response" not in rows[0]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["join_policy"]["join_key"] == "sample_id"
    assert manifest["join_policy"]["gold_response_excluded"] is True
    assert manifest["output"]["sha256"] == sha256_file(output_path)
    assert manifest["candidate_input"]["unique_sample_count"] == 1


def test_rerun_preserves_created_at(tmp_path: Path) -> None:
    _, manifest_path = _build(tmp_path)
    first = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidate_path = tmp_path / "candidate.csv"
    source_path = tmp_path / "source.csv"

    materialize_principle_grounding_pool(
        repo_root=tmp_path,
        candidate_path=candidate_path,
        source_dialogue_paths=(source_path,),
        output_dir=tmp_path / "output",
    )

    second = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert second["created_at"] == first["created_at"]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("missing", "sample_id not found"),
        ("empty_question", "source question is empty"),
        ("mismatch", "source/candidate mismatch"),
    ],
)
def test_fails_closed_on_invalid_join(
    tmp_path: Path, mutation: str, message: str
) -> None:
    candidate = _candidate()
    source = _source()
    if mutation == "missing":
        source["sample_id"] = "S-OTHER"
    elif mutation == "empty_question":
        source["question"] = ""
    elif mutation == "mismatch":
        source["answer_sgv"] = "Byte"
    candidate_path = tmp_path / "candidate.csv"
    source_path = tmp_path / "source.csv"
    _write_csv(candidate_path, list(candidate), [candidate])
    _write_csv(source_path, list(source), [source])

    with pytest.raises(ValueError, match=message):
        materialize_principle_grounding_pool(
            repo_root=tmp_path,
            candidate_path=candidate_path,
            source_dialogue_paths=(source_path,),
            output_dir=tmp_path / "output",
        )


def test_fails_closed_on_duplicate_source_sample_id(tmp_path: Path) -> None:
    candidate_path = tmp_path / "candidate.csv"
    source_a = tmp_path / "source_a.csv"
    source_b = tmp_path / "source_b.csv"
    _write_csv(candidate_path, list(_candidate()), [_candidate()])
    _write_csv(source_a, list(_source()), [_source()])
    _write_csv(source_b, list(_source()), [_source()])

    with pytest.raises(ValueError, match="Duplicate source sample_id"):
        materialize_principle_grounding_pool(
            repo_root=tmp_path,
            candidate_path=candidate_path,
            source_dialogue_paths=(source_a, source_b),
            output_dir=tmp_path / "output",
        )
