from __future__ import annotations

import csv
import json
import io
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.vertex_ai_call.requirement_scoring import (
    GROUNDING_HEADER,
    PRINCIPLE_IDS,
    GenerationConfig,
    RequirementScoringError,
    atomic_write_json,
    build_grounding_payload,
    build_request_hash,
    canonical_json_hash,
    compare_runs,
    derive_principle_sets,
    lint_principle_scores,
    load_calibration_cases,
    parse_and_validate_response,
    serialize_user_prompt,
    select_pilot,
    validate_run_records,
    validate_snapshot_manifest,
    validate_specification_manifest,
    write_pilot_input,
)
from src.vertex_ai_call.run_requirement_scoring import (
    _ProgressBar,
    _load_schema,
    build_parser,
    execute_run,
    finalize_full,
    main,
    prepare,
)
from src.vertex_ai_call.vertex_client import VertexRequirementClient


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _row(grade: int, family: int, *, with_history: bool) -> dict:
    suffix = "H" if with_history else "N"
    return {
        "benchmark_candidate_id": f"BC-G{grade}-{family:03d}-{suffix}",
        "sample_id": f"S-G{grade}-{family:03d}",
        "grade": grade,
        "lesson": f"Bài {family % 4}",
        "position": f"Mục {family % 3}",
        "bloom_level": ("Biết", "Thông hiểu", "Vận dụng")[family % 3],
        "student_prompt": "Em cần hỗ trợ ạ.",
        "conversation_history": (
            [
                {"turn_index": 2, "role": "tutor", "content": "Em đã thử gì?"},
                {"turn_index": 3, "role": "student", "content": "Em đã thử một bước."},
            ]
            if with_history
            else []
        ),
        "source_question": "Câu hỏi nguồn",
        "gold_answer": "Đáp án chuyên môn",
    }


def _response(scores: dict[str, int] | None = None) -> dict:
    values = scores or {principle: 3 for principle in PRINCIPLE_IDS}
    return {
        "principle_scores": [
            {
                "principle_id": principle,
                "requirement_score": values[principle],
                "rationale": (
                    "Nhu cầu độc lập: học sinh cần chức năng này. "
                    "Nếu bỏ nguyên tắc này: nhu cầu sẽ không được đáp ứng."
                    if values[principle] >= 4
                    else "Lập luận tiếng Việt."
                ),
                "evidence": "Bằng chứng từ payload.",
            }
            for principle in PRINCIPLE_IDS
        ],
    }


def _record(run_id: str, row: dict, response: dict) -> dict:
    normalized = {
        "benchmark_candidate_id": row["benchmark_candidate_id"],
        "principle_scores": response["principle_scores"],
    }
    required, alternative = derive_principle_sets(normalized)
    return {
        "run_id": run_id,
        "benchmark_candidate_id": row["benchmark_candidate_id"],
        "request_hash": "a" * 64,
        "user_prompt": serialize_user_prompt(build_grounding_payload(row)),
        "model": "fake-model",
        "model_version": "fake-v1",
        "response_id": f"response-{run_id}",
        "finish_reason": "STOP",
        "usage_metadata": {},
        "raw_response_text": json.dumps(response, ensure_ascii=False),
        "normalized_response": normalized,
        "required_principle_set": required,
        "alternative_principle_set": alternative,
        "created_at": "2026-07-27T00:00:00+00:00",
    }


def test_select_pilot_is_balanced_and_family_unique() -> None:
    rows = []
    for grade in (6, 7, 8, 9):
        for family in range(12):
            rows.append(_row(grade, family, with_history=False))
            rows.append(_row(grade, family + 20, with_history=True))
    pilot = select_pilot(rows, seed=17)
    assert len(pilot) == 40
    assert len({row["sample_id"] for row in pilot}) == 40
    for grade in (6, 7, 8, 9):
        grade_rows = [row for row in pilot if row["grade"] == grade]
        assert len(grade_rows) == 10
        assert sum(row["has_history"] for row in grade_rows) == 5


def test_response_validation_and_code_derived_sets() -> None:
    scores = {principle: 2 for principle in PRINCIPLE_IDS}
    scores["PRINCIPLE-EXPLANATION"] = 5
    scores["PRINCIPLE-QUESTIONING"] = 3
    raw = json.dumps(_response(scores), ensure_ascii=False)
    normalized = parse_and_validate_response(raw, expected_candidate_id="BC-1")
    required, alternative = derive_principle_sets(normalized)
    assert required == ["PRINCIPLE-EXPLANATION"]
    assert alternative == ["PRINCIPLE-QUESTIONING"]


def test_response_validation_rejects_duplicate_principle() -> None:
    response = _response()
    response["principle_scores"][1]["principle_id"] = "PRINCIPLE-CHALLENGE"
    with pytest.raises(RequirementScoringError, match="duplicate"):
        parse_and_validate_response(
            json.dumps(response, ensure_ascii=False),
            expected_candidate_id="BC-1",
        )


def test_compare_runs_routes_threshold_crossing_to_review() -> None:
    pilot = []
    run_a_records = []
    run_b_records = []
    for grade in (6, 7, 8, 9):
        for family in range(10):
            row = _row(grade, family, with_history=bool(family % 2))
            pilot.append(row)
            scores_a = {principle: 2 for principle in PRINCIPLE_IDS}
            scores_a["PRINCIPLE-EXPLANATION"] = 4
            scores_b = dict(scores_a)
            if grade == 6 and family == 0:
                scores_b["PRINCIPLE-EXPLANATION"] = 3
            response_a = _response(scores_a)
            response_b = _response(scores_b)
            run_a_records.append(_record("a", row, response_a))
            run_b_records.append(_record("b", row, response_b))
    run_a = validate_run_records(run_a_records, pilot, run_id="a")
    run_b = validate_run_records(run_b_records, pilot, run_id="b")
    metrics, review = compare_runs(run_a, run_b, pilot, spot_check_count=0)
    assert metrics["threshold_crossing_candidate_count"] == 1
    assert metrics["no_threshold_crossing_rate"] == pytest.approx(39 / 40)
    assert len(review) == 1
    assert "threshold_crossing" in review[0]["review_reasons"]
    assert "Nhu cầu độc lập:" in review[0]["run_a_principle_scores_json"]
    assert "Bằng chứng từ payload." in review[0]["run_b_principle_scores_json"]


def test_request_hash_is_deterministic() -> None:
    payload = build_grounding_payload(_row(6, 1, with_history=False))
    config = GenerationConfig(model="fake")
    left = build_request_hash(
        payload=payload,
        prompt_sha256="1" * 64,
        schema_sha256="2" * 64,
        generation_config=config,
    )
    right = build_request_hash(
        payload=payload,
        prompt_sha256="1" * 64,
        schema_sha256="2" * 64,
        generation_config=config,
    )
    assert left == right


def test_model_payload_excludes_trace_ids_and_serializes_exactly() -> None:
    row = _row(6, 1, with_history=True)
    payload = build_grounding_payload(row)
    assert tuple(payload) == (
        "grade",
        "lesson",
        "position",
        "bloom_level",
        "student_prompt",
        "conversation_history",
        "source_question",
        "gold_answer",
    )
    assert "benchmark_candidate_id" not in payload
    assert "sample_id" not in payload
    user_prompt = serialize_user_prompt(payload)
    assert json.loads(user_prompt) == payload
    assert "BC-G6" not in user_prompt
    assert "S-G6" not in user_prompt


def test_progress_bar_reports_sweep_and_overall_counts() -> None:
    stream = io.StringIO()
    progress = _ProgressBar(
        label="Run A | initial",
        total=2,
        overall_total=40,
        request_ceiling=120,
        enabled=True,
        stream=stream,
        width=10,
    )
    progress.update(processed=0, completed=0, failed=0, requests=2)
    progress.finish(processed=2, completed=1, failed=1, requests=2)
    output = stream.getvalue()
    assert "Run A | initial" in output
    assert "[##########] 2/2" in output
    assert "completed 1/40" in output
    assert "failed 1" in output
    assert "requests 2/120" in output


def test_vertex_client_uses_injected_fake_without_network() -> None:
    response = _response()

    class FakeModels:
        def __init__(self) -> None:
            self.calls = []

        def generate_content(self, **kwargs):
            self.calls.append(kwargs)
            return SimpleNamespace(
                text=json.dumps(response, ensure_ascii=False),
                candidates=[SimpleNamespace(finish_reason="STOP")],
                usage_metadata=None,
                response_id="fake-response",
                model_version="fake-version",
            )

    fake = SimpleNamespace(models=FakeModels(), close=lambda: None)
    client = VertexRequirementClient(
        project="edu-benchmark",
        location="global",
        system_prompt="Prompt tiếng Việt",
        response_schema={"type": "object"},
        generation_config=GenerationConfig(
            model="fake-model",
            temperature=0.0,
            top_p=1.0,
            thinking_budget=0,
        ),
        client=fake,
    )
    user_prompt = '{"grade":6}'
    result = client.generate(user_prompt)
    assert result["response_id"] == "fake-response"
    assert len(fake.models.calls) == 1
    assert fake.models.calls[0]["model"] == "fake-model"
    assert fake.models.calls[0]["contents"] == user_prompt
    request_config = fake.models.calls[0]["config"]
    assert request_config.temperature == 0.0
    assert request_config.top_p == 1.0
    assert request_config.max_output_tokens == 4096
    assert request_config.seed == 20260727
    assert request_config.thinking_config.thinking_budget == 0


def test_vertex_client_omits_sampling_for_gemini_35() -> None:
    response = _response()

    class FakeModels:
        def __init__(self) -> None:
            self.calls = []

        def generate_content(self, **kwargs):
            self.calls.append(kwargs)
            return SimpleNamespace(
                text=json.dumps(response, ensure_ascii=False),
                candidates=[SimpleNamespace(finish_reason="STOP")],
                usage_metadata=None,
                response_id="fake-response",
                model_version="gemini-3.5-flash",
            )

    fake = SimpleNamespace(models=FakeModels(), close=lambda: None)
    generation_config = GenerationConfig(
        model="gemini-3.5-flash",
        thinking_level="MEDIUM",
        include_thoughts=False,
    )
    client = VertexRequirementClient(
        project="edu-benchmark",
        location="global",
        system_prompt="Prompt tiếng Việt",
        response_schema={"type": "object"},
        generation_config=generation_config,
        client=fake,
    )
    client.generate('{"grade":6}')
    request_config = fake.models.calls[0]["config"]
    serialized = request_config.model_dump(exclude_none=True)
    assert "temperature" not in serialized
    assert "top_p" not in serialized
    assert serialized["thinking_config"]["thinking_level"] == "MEDIUM"
    assert serialized["thinking_config"]["include_thoughts"] is False
    assert "thinking_budget" not in serialized["thinking_config"]


def test_gemini_35_configuration_rejects_legacy_sampling_and_budget() -> None:
    with pytest.raises(
        RequirementScoringError,
        match="must omit temperature and top_p",
    ):
        GenerationConfig(
            model="gemini-3.5-flash",
            temperature=0.0,
            thinking_level="MEDIUM",
        )
    with pytest.raises(
        RequirementScoringError,
        match="mutually exclusive",
    ):
        GenerationConfig(
            model="gemini-3.5-flash",
            thinking_budget=0,
            thinking_level="MEDIUM",
        )


def test_request_hash_ignores_runtime_only_concurrency() -> None:
    payload = build_grounding_payload(_row(6, 1, with_history=False))
    serial = GenerationConfig(model="fake", concurrency=1)
    parallel = GenerationConfig(model="fake", concurrency=16)
    serial_hash = build_request_hash(
        payload=payload,
        prompt_sha256="1" * 64,
        schema_sha256="2" * 64,
        generation_config=serial,
    )
    parallel_hash = build_request_hash(
        payload=payload,
        prompt_sha256="1" * 64,
        schema_sha256="2" * 64,
        generation_config=parallel,
    )
    assert serial_hash == parallel_hash


def test_concurrent_run_writes_successes_and_retries_after_full_sweep(
    tmp_path: Path,
) -> None:
    pilot_rows = []
    for grade in (6, 7, 8, 9):
        for family in range(10):
            row = _row(grade, family, with_history=bool(family % 2))
            row["has_history"] = bool(row["conversation_history"])
            row["history_turn_count"] = len(row["conversation_history"])
            row["selection_reason"] = "synthetic-test"
            pilot_rows.append(row)
    pilot_dir = tmp_path / "pilot_v4"
    write_pilot_input(pilot_dir / "pilot_input.csv", pilot_rows)
    config = GenerationConfig(
        model="fake-model",
        max_retries=1,
        max_requests=41,
        concurrency=4,
        retry_base_delay_seconds=0.0,
    )
    manifest = {
        "status": "prepared",
        "prompt_language": "vi",
        "generation_config_sha256": canonical_json_hash(config.as_dict()),
        "provider": {
            "mode": "standard_adc",
            "project": "edu-benchmark",
            "location": "global",
        },
        "api_request_attempt_count": 0,
        "runs": {
            "a": {
                "status": "pending",
                "completed_count": 0,
                "attempts_by_candidate": {},
                "failed_candidate_ids": [],
            },
            "b": {
                "status": "pending",
                "completed_count": 0,
                "attempts_by_candidate": {},
                "failed_candidate_ids": [],
            },
        },
        "errors": [],
    }
    atomic_write_json(pilot_dir / "run_manifest.json", manifest)
    first_candidate = pilot_rows[0]["benchmark_candidate_id"]
    pilot_rows[0]["student_prompt"] = "Mẫu lỗi tạm thời duy nhất."
    write_pilot_input(pilot_dir / "pilot_input.csv", pilot_rows)
    prompt_to_candidate = {
        serialize_user_prompt(build_grounding_payload(row)): row[
            "benchmark_candidate_id"
        ]
        for row in pilot_rows
    }

    class FakeRequirementClient:
        def __init__(self) -> None:
            self.lock = threading.Lock()
            self.calls: list[str] = []
            self.attempts: dict[str, int] = {}

        def generate(self, user_prompt):
            candidate_id = prompt_to_candidate[user_prompt]
            with self.lock:
                self.calls.append(candidate_id)
                self.attempts[candidate_id] = self.attempts.get(candidate_id, 0) + 1
                attempt = self.attempts[candidate_id]
            if candidate_id == first_candidate and attempt == 1:
                raise RuntimeError("synthetic transient failure")
            response = _response()
            return {
                "raw_response_text": json.dumps(response, ensure_ascii=False),
                "response_id": f"response-{candidate_id}",
                "model_version": "fake-v1",
                "finish_reason": "STOP",
                "usage_metadata": {},
            }

    fake = FakeRequirementClient()
    args = SimpleNamespace(
        execute_api=True,
        output_root=tmp_path,
        prompt=(
            REPOSITORY_ROOT
            / "shared/prompts/benchmark_candidate_task_assigning/system_prompt_v4.md"
        ),
        schema=(
            REPOSITORY_ROOT
            / "experiments/20260727_170150/outputs/principle_requirement_scoring/"
            "scoring_schema_v2.json"
        ),
        project="edu-benchmark",
        location="global",
        model=config.model,
        temperature=config.temperature,
        top_p=config.top_p,
        max_output_tokens=config.max_output_tokens,
        seed=config.seed,
        thinking_budget=config.thinking_budget,
        thinking_level=config.thinking_level,
        include_thoughts=config.include_thoughts,
        timeout_seconds=config.timeout_seconds,
        max_retries=config.max_retries,
        max_requests=config.max_requests,
        concurrency=config.concurrency,
        retry_base_delay_seconds=config.retry_base_delay_seconds,
    )
    execute_run(args, run_id="a", client=fake)
    run_lines = (pilot_dir / "run_a.jsonl").read_text().splitlines()
    assert len(run_lines) == 40
    first_record = json.loads(run_lines[0])
    assert json.loads(first_record["user_prompt"]) == build_grounding_payload(
        next(
            row
            for row in pilot_rows
            if row["benchmark_candidate_id"]
            == first_record["benchmark_candidate_id"]
        )
    )
    assert "benchmark_candidate_id" not in json.loads(first_record["user_prompt"])
    assert "sample_id" not in json.loads(first_record["user_prompt"])
    assert fake.attempts[first_candidate] == 2
    second_attempt_index = len(fake.calls) - 1
    assert fake.calls[second_attempt_index] == first_candidate
    assert set(fake.calls[:second_attempt_index]) == {
        row["benchmark_candidate_id"] for row in pilot_rows
    }


def test_cli_refuses_network_without_explicit_flag(tmp_path: Path) -> None:
    exit_code = main(
        [
            "pilot",
            "--output-root",
            str(tmp_path),
        ]
    )
    assert exit_code == 2
    assert not list(tmp_path.iterdir())


def test_calibration_prepare_validates_and_writes_no_copied_input(
    tmp_path: Path,
) -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["calibration", "--output-root", str(tmp_path)]
    )
    for field in (
        "pool",
        "output_root",
        "prompt",
        "schema",
        "spec_manifest",
        "calibration_input",
        "snapshot_manifest",
    ):
        setattr(args, field, getattr(args, field).resolve())
    manifest = prepare(args)
    calibration_dir = tmp_path / "calibration_gemini35_medium_v1"
    assert manifest["pilot_version"] == "calibration_gemini35_medium_v1"
    assert manifest["input"]["candidate_count"] == 36
    assert manifest["bundle_type"] == "semantic_boundary_calibration"
    assert manifest["generation_config"]["model"] == "gemini-3.5-flash"
    assert manifest["generation_config"]["temperature"] is None
    assert manifest["generation_config"]["top_p"] is None
    assert manifest["generation_config"]["thinking_budget"] is None
    assert manifest["generation_config"]["thinking_level"] == "MEDIUM"
    assert manifest["generation_config"]["include_thoughts"] is False
    assert (calibration_dir / "run_manifest.json").is_file()
    assert not (calibration_dir / "pilot_input.csv").exists()


def test_calibration_bundle_name_is_separate_and_safe(tmp_path: Path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "calibration",
            "--output-root",
            str(tmp_path),
            "--bundle-name",
            "calibration_gemini35_medium_test",
        ]
    )
    for field in (
        "pool",
        "output_root",
        "prompt",
        "schema",
        "spec_manifest",
        "calibration_input",
        "snapshot_manifest",
    ):
        setattr(args, field, getattr(args, field).resolve())
    manifest = prepare(args)
    assert manifest["pilot_version"] == "calibration_gemini35_medium_test"
    assert (
        tmp_path
        / "calibration_gemini35_medium_test"
        / "run_manifest.json"
    ).is_file()


def test_full_single_run_uses_all_rows_and_publishes_integrity(
    tmp_path: Path,
) -> None:
    pool_path = tmp_path / "grounding_pool.csv"
    pool_rows = [
        _row(grade, grade, with_history=bool(grade % 2))
        for grade in (6, 7, 8, 9)
    ]
    with pool_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=GROUNDING_HEADER)
        writer.writeheader()
        for row in pool_rows:
            serialized = dict(row)
            serialized["conversation_history"] = json.dumps(
                row["conversation_history"],
                ensure_ascii=False,
            )
            writer.writerow(serialized)

    parser = build_parser()
    defaults = parser.parse_args(["full"])
    assert defaults.concurrency == 20
    assert defaults.max_requests == 2500

    args = parser.parse_args(
        [
            "full",
            "--pool",
            str(pool_path),
            "--output-root",
            str(tmp_path),
            "--bundle-name",
            "full_test",
            "--max-requests",
            "4",
            "--concurrency",
            "2",
            "--execute-api",
        ]
    )
    for field in (
        "pool",
        "output_root",
        "prompt",
        "schema",
        "spec_manifest",
        "calibration_input",
        "snapshot_manifest",
    ):
        setattr(args, field, getattr(args, field).resolve())
    manifest = prepare(args)
    bundle_dir = tmp_path / "full_test"
    assert manifest["bundle_type"] == "full_single_run_requirement_scoring"
    assert manifest["input"]["candidate_count"] == 4
    assert manifest["input"]["input_role"] == "full_grounding_pool"
    assert set(manifest["runs"]) == {"full"}
    assert not (bundle_dir / "pilot_input.csv").exists()

    prompt_to_candidate = {
        serialize_user_prompt(build_grounding_payload(row)): row[
            "benchmark_candidate_id"
        ]
        for row in pool_rows
    }

    class FakeRequirementClient:
        def generate(self, user_prompt):
            candidate_id = prompt_to_candidate[user_prompt]
            return {
                "raw_response_text": json.dumps(
                    _response(),
                    ensure_ascii=False,
                ),
                "response_id": f"response-{candidate_id}",
                "model_version": "gemini-3.5-flash",
                "finish_reason": "STOP",
                "usage_metadata": {},
            }

    execute_run(args, run_id="full", client=FakeRequirementClient())
    completed = finalize_full(args)
    assert completed["status"] == "completed_awaiting_analysis"
    assert completed["integrity"]["validated"] is True
    assert completed["integrity"]["record_count"] == 4
    assert completed["integrity"]["score_count"] == 24
    assert completed["integrity"]["distinct_response_id_count"] == 4
    assert len((bundle_dir / "run_full.jsonl").read_text().splitlines()) == 4


def test_full_command_refuses_network_without_explicit_flag(
    tmp_path: Path,
) -> None:
    exit_code = main(
        [
            "full",
            "--output-root",
            str(tmp_path),
        ]
    )
    assert exit_code == 2
    assert not list(tmp_path.iterdir())


def test_specification_manifest_hashes_are_valid() -> None:
    manifest = (
        REPOSITORY_ROOT
        / "experiments/20260727_170150/outputs/principle_requirement_scoring/"
        "specification_manifest_v4.json"
    )
    parsed = validate_specification_manifest(manifest, REPOSITORY_ROOT)
    assert parsed["prompt_language"] == "vi"
    assert parsed["specification_version"] == "v4"


def test_v4_prompt_contains_semantic_boundary_guardrails() -> None:
    prompt = (
        REPOSITORY_ROOT
        / "shared/prompts/benchmark_candidate_task_assigning/system_prompt_v4.md"
    ).read_text(encoding="utf-8")
    required_snippets = (
        "`Nhu cầu độc lập:`",
        "`Nếu bỏ nguyên tắc này:`",
        "Xác nhận đúng, khen, đồng tình",
        "phản hồi của gia sư phụ thuộc",
        "chỉ được tối đa `3`",
    )
    for snippet in required_snippets:
        assert snippet in prompt


def test_calibration_cases_are_balanced_and_provisional() -> None:
    path = (
        REPOSITORY_ROOT
        / "experiments/20260727_170150/outputs/principle_requirement_scoring/"
        "calibration_cases_v1.csv"
    )
    rows = load_calibration_cases(path)
    assert len(rows) == 36
    for principle in PRINCIPLE_IDS:
        principle_rows = [
            row for row in rows if row["focus_principle_id"] == principle
        ]
        assert sum(row["case_type"] == "positive" for row in principle_rows) == 3
        assert sum(row["case_type"] == "near_miss" for row in principle_rows) == 3
    assert {row["uet_status"] for row in rows} == {"pending_review"}


def test_semantic_lint_flags_high_score_without_required_reasoning() -> None:
    response = _response()
    questioning = next(
        item
        for item in response["principle_scores"]
        if item["principle_id"] == "PRINCIPLE-QUESTIONING"
    )
    questioning["requirement_score"] = 4
    questioning["rationale"] = (
        "Việc đặt câu hỏi có thể giúp học sinh suy nghĩ thêm."
    )
    reasons = lint_principle_scores(response)
    assert "high_score_missing_need:PRINCIPLE-QUESTIONING" in reasons
    assert "high_score_missing_counterfactual:PRINCIPLE-QUESTIONING" in reasons
    assert "high_score_modal_conflict:PRINCIPLE-QUESTIONING" in reasons
    assert "questioning_without_answer_dependency" in reasons


def test_semantic_lint_flags_confirmation_only_feedback() -> None:
    response = _response()
    feedback = next(
        item
        for item in response["principle_scores"]
        if item["principle_id"] == "PRINCIPLE-FEEDBACK"
    )
    feedback["requirement_score"] = 4
    feedback["rationale"] = (
        "Nhu cầu độc lập: học sinh cần được xác nhận để tự tin. "
        "Nếu bỏ nguyên tắc này: học sinh không được khen."
    )
    reasons = lint_principle_scores(response)
    assert "feedback_confirmation_only" in reasons


def test_semantic_lint_accepts_actionable_feedback_reasoning() -> None:
    response = _response()
    feedback = next(
        item
        for item in response["principle_scores"]
        if item["principle_id"] == "PRINCIPLE-FEEDBACK"
    )
    feedback["requirement_score"] = 4
    feedback["rationale"] = (
        "Nhu cầu độc lập: cách làm của học sinh có phần sai cần sửa. "
        "Nếu bỏ nguyên tắc này: học sinh không biết điểm cần điều chỉnh."
    )
    reasons = lint_principle_scores(response)
    assert "feedback_confirmation_only" not in reasons
    assert not [
        reason for reason in reasons if "PRINCIPLE-FEEDBACK" in reason
    ]


def test_inherited_snapshot_manifest_hashes_are_valid() -> None:
    manifest = (
        REPOSITORY_ROOT
        / "experiments/20260727_170150/inherited_resources/snapshot_manifest.csv"
    )
    rows = validate_snapshot_manifest(manifest)
    assert len(rows) == 41


def test_vertex_response_schema_is_resolved_before_sdk_call() -> None:
    schema_path = (
        REPOSITORY_ROOT
        / "experiments/20260727_170150/outputs/principle_requirement_scoring/"
        "scoring_schema_v2.json"
    )
    response_schema = _load_schema(schema_path)
    items = response_schema["properties"]["principle_scores"]["items"]
    assert "$ref" not in items
    assert items["properties"]["principle_id"]["enum"] == list(PRINCIPLE_IDS)
    assert set(response_schema["properties"]) == {"principle_scores"}
