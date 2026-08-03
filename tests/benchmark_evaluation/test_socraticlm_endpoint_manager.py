from types import SimpleNamespace

import pytest

from scripts.benchmark_evaluation.manage_socraticlm_endpoint import (
    CommandExecutionError,
    _assert_manifest_redeployable,
    _budget_summary,
    _can_reuse_built_container,
    _matching_models,
    _require_at_most_one,
    _resource_from_output,
    _run_cleanup_command,
    _vertex_service_agent_email,
)


def test_resource_parser_extracts_vertex_resources():
    output = (
        "Created "
        "projects/edu-benchmark/locations/us-central1/endpoints/123456"
    )
    assert _resource_from_output(output, "endpoints").endswith("/123456")


def test_endpoint_budget_includes_build_and_runtime_upper_bound():
    args = SimpleNamespace(
        max_endpoint_hours=2.0,
        hourly_price_usd=1.0,
        build_storage_upper_usd=3.0,
        stage_cap_usd=20.0,
        hard_budget_usd=250.0,
        reserve_usd=25.0,
        actual_spend_to_date_usd=56.5,
    )
    assert _budget_summary(args)["stage_upper_bound_usd"] == 5.0


def test_endpoint_budget_rejects_stage_cap():
    args = SimpleNamespace(
        max_endpoint_hours=20.0,
        hourly_price_usd=1.0,
        build_storage_upper_usd=3.0,
        stage_cap_usd=20.0,
        hard_budget_usd=250.0,
        reserve_usd=25.0,
        actual_spend_to_date_usd=56.5,
    )
    with pytest.raises(RuntimeError, match="stage cap"):
        _budget_summary(args)


def test_failed_deploy_with_resources_requires_cleanup():
    with pytest.raises(RuntimeError, match="run cleanup"):
        _assert_manifest_redeployable(
            {
                "status": "failed",
                "model_resource": (
                    "projects/p/locations/us-central1/models/123"
                ),
                "endpoint_resource": None,
                "deployed_model_id": None,
            }
        )
    _assert_manifest_redeployable(
        {
            "status": "failed",
            "model_resource": None,
            "endpoint_resource": None,
            "deployed_model_id": None,
        }
    )
    _assert_manifest_redeployable({"status": "cleanup_completed"})


def test_vertex_service_agent_email_is_derived_from_project_number():
    assert _vertex_service_agent_email("26637432505") == (
        "service-26637432505"
        "@gcp-sa-aiplatform.iam.gserviceaccount.com"
    )
    with pytest.raises(RuntimeError, match="project number"):
        _vertex_service_agent_email("edu-benchmark")


def test_failed_post_build_deploy_can_reuse_exact_container():
    plan = {"container_image_uri": "region.pkg/image:v1"}
    existing = {
        "status": "failed",
        "container_built_at": "2026-07-28T14:15:19+00:00",
        "container_image_uri": "region.pkg/image:v1",
        "model_resource": None,
        "endpoint_resource": None,
        "deployed_model_id": None,
    }
    assert _can_reuse_built_container(existing, plan) is True
    existing["model_resource"] = "projects/p/locations/l/models/1"
    assert _can_reuse_built_container(existing, plan) is True


def test_matching_models_recovers_exact_uploaded_resource():
    rows = [
        {
            "name": "projects/266/locations/us-central1/models/414",
            "displayName": "socraticlm-vllm-20260728-143424",
            "containerSpec": {"imageUri": "region.pkg/image:v1"},
        },
        {
            "name": "projects/266/locations/us-central1/models/999",
            "displayName": "unrelated",
            "containerSpec": {"imageUri": "region.pkg/image:v1"},
        },
    ]
    matches = _matching_models(
        rows,
        image_uri="region.pkg/image:v1",
        display_name=None,
    )
    assert [row["name"] for row in matches] == [
        "projects/266/locations/us-central1/models/414"
    ]
    assert (
        _require_at_most_one(matches, label="model")["displayName"]
        == "socraticlm-vllm-20260728-143424"
    )


def test_multiple_recovered_models_fail_closed():
    rows = [{"name": "models/1"}, {"name": "models/2"}]
    with pytest.raises(RuntimeError, match="multiple matching"):
        _require_at_most_one(rows, label="model")


def test_run_raises_structured_command_error(monkeypatch):
    from scripts.benchmark_evaluation import manage_socraticlm_endpoint

    result = SimpleNamespace(returncode=1, stdout="out", stderr="denied")
    monkeypatch.setattr(
        manage_socraticlm_endpoint.subprocess,
        "run",
        lambda *args, **kwargs: result,
    )
    with pytest.raises(CommandExecutionError) as captured:
        manage_socraticlm_endpoint._run(["gcloud", "test"])
    assert captured.value.returncode == 1
    assert captured.value.stderr == "denied"


def test_cleanup_command_does_not_hide_unknown_failure(monkeypatch):
    result = SimpleNamespace(returncode=1, stdout="", stderr="permission denied")
    monkeypatch.setattr(
        "scripts.benchmark_evaluation.manage_socraticlm_endpoint._run",
        lambda command, check=False: result,
    )
    with pytest.raises(RuntimeError, match="cleanup command failed"):
        _run_cleanup_command(["gcloud", "ai", "endpoints", "delete", "123"])


def test_cleanup_command_accepts_already_absent_resource(monkeypatch):
    result = SimpleNamespace(
        returncode=1,
        stdout="",
        stderr="NOT_FOUND: endpoint does not exist",
    )
    monkeypatch.setattr(
        "scripts.benchmark_evaluation.manage_socraticlm_endpoint._run",
        lambda command, check=False: result,
    )
    _run_cleanup_command(["gcloud", "ai", "endpoints", "delete", "123"])
