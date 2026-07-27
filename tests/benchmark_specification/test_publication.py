from pathlib import Path

from edu_benchmark.benchmark_specification.publication import (
    validate_capability_draft,
    validate_specialist_draft,
)


def test_missing_specialist_bundle_fails_closed(tmp_path: Path):
    experiment = tmp_path / "experiments" / "E1"
    experiment.mkdir(parents=True)
    errors, summary = validate_specialist_draft(
        tmp_path,
        experiment,
        experiment / "draft",
    )
    assert errors
    assert errors[0].startswith("missing_file:")
    assert summary == {}


def test_missing_capability_bundle_fails_closed(tmp_path: Path):
    experiment = tmp_path / "experiments" / "E1"
    experiment.mkdir(parents=True)
    errors, summary = validate_capability_draft(
        tmp_path,
        experiment,
        experiment / "draft",
    )
    assert errors
    assert errors[0].startswith("missing_file:")
    assert summary == {}
