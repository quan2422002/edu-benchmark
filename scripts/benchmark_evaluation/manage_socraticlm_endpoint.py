"""Build, deploy, inspect, and remove the SocraticLM Vertex endpoint."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any, Sequence


from edu_benchmark.benchmark_evaluation.costing import (  # noqa: E402
    BudgetPolicy,
    estimate_self_deployed_cost,
)
from edu_benchmark.benchmark_evaluation.vertex_endpoint import (  # noqa: E402
    endpoint_id_from_resource,
)


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_ID = "20260727_170150"
PLAN_ID = "plan05"
HF_MODEL_ID = "CogBase-USTC/Qwen2.5-Math-7B-Instruct-SocraticLM"
VLLM_VERSION = "0.9.2"
BASE_IMAGE = f"vllm/vllm-openai:v{VLLM_VERSION}"
DEFAULT_LOCATION = "us-central1"
DEFAULT_MACHINE_TYPE = "g2-standard-12"
DEFAULT_ACCELERATOR_TYPE = "nvidia-l4"
DEFAULT_HOURLY_PRICE_USD = 1.000416348
DEFAULT_MANIFEST = (
    ROOT
    / "experiments/20260727_170150/outputs/benchmark_evaluation/"
    "socraticlm_endpoint/lifecycle_manifest.json"
)
CONTAINER_CONTEXT = (
    ROOT / "scripts/benchmark_evaluation/socraticlm_container"
)


class CommandExecutionError(RuntimeError):
    """gcloud failure with diagnostics suitable for the lifecycle manifest."""

    def __init__(
        self,
        *,
        command: Sequence[str],
        returncode: int,
        stdout: str,
        stderr: str,
    ) -> None:
        self.command = tuple(command)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(
            f"command failed with exit code {returncode}: "
            f"{_command_text(command)}"
        )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _command_text(command: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def _run(
    command: Sequence[str],
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    print(f"$ {_command_text(command)}", flush=True)
    result = subprocess.run(
        list(command),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.rstrip(), flush=True)
    if result.stderr.strip():
        print(result.stderr.rstrip(), file=sys.stderr, flush=True)
    if check and result.returncode:
        raise CommandExecutionError(
            command=command,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    return result


def _run_cleanup_command(command: Sequence[str]) -> None:
    """Run an idempotent cleanup command without hiding real failures."""

    result = _run(command, check=False)
    if result.returncode == 0:
        return
    diagnostic = f"{result.stdout}\n{result.stderr}".lower()
    already_absent_markers = (
        "not_found",
        "not found",
        "does not exist",
        "no deployedmodels",
        "not deployed",
    )
    if any(marker in diagnostic for marker in already_absent_markers):
        return
    raise RuntimeError(
        f"cleanup command failed with exit code {result.returncode}: "
        f"{_command_text(command)}"
    )


def _resource_from_output(output: str, resource_type: str) -> str:
    match = re.search(
        rf"projects/[^/\s]+/locations/[^/\s]+/{resource_type}/[^/\s]+",
        output,
    )
    if not match:
        raise RuntimeError(
            f"could not parse {resource_type} resource from gcloud output"
        )
    return match.group(0)


def _resource_id(resource: str) -> str:
    return resource.rstrip("/").rsplit("/", 1)[-1]


def _gcloud(args: argparse.Namespace) -> list[str]:
    path = args.gcloud.resolve()
    if not path.is_file():
        raise FileNotFoundError(f"gcloud executable not found: {path}")
    return [str(path)]


def _common_gcloud(args: argparse.Namespace) -> list[str]:
    return [
        f"--project={args.project}",
        f"--region={args.location}",
        "--quiet",
    ]


def _budget_summary(args: argparse.Namespace) -> dict[str, float]:
    endpoint_upper = estimate_self_deployed_cost(
        endpoint_hours=args.max_endpoint_hours,
        hourly_price_usd=args.hourly_price_usd,
        storage_network_usd=args.build_storage_upper_usd,
    )
    if endpoint_upper > args.stage_cap_usd:
        raise RuntimeError(
            f"endpoint upper bound ${endpoint_upper:.2f} exceeds stage cap "
            f"${args.stage_cap_usd:.2f}"
        )
    BudgetPolicy(
        hard_budget_usd=args.hard_budget_usd,
        reserve_usd=args.reserve_usd,
    ).assert_next_batch_allowed(
        actual_spend_usd=args.actual_spend_to_date_usd,
        next_batch_upper_bound_usd=endpoint_upper,
    )
    return {
        "hourly_price_usd": args.hourly_price_usd,
        "max_endpoint_hours": args.max_endpoint_hours,
        "build_storage_upper_usd": args.build_storage_upper_usd,
        "stage_upper_bound_usd": round(endpoint_upper, 8),
        "actual_spend_to_date_usd": args.actual_spend_to_date_usd,
        "hard_budget_usd": args.hard_budget_usd,
        "reserve_usd": args.reserve_usd,
    }


def _deployment_plan(args: argparse.Namespace) -> dict[str, Any]:
    image_uri = (
        f"{args.location}-docker.pkg.dev/{args.project}/"
        f"{args.artifact_repository}/socraticlm-vllm:v{VLLM_VERSION}"
    )
    return {
        "experiment_id": EXPERIMENT_ID,
        "plan_id": PLAN_ID,
        "status": "preflight",
        "generated_at": utc_now(),
        "project": args.project,
        "location": args.location,
        "hf_model_id": HF_MODEL_ID,
        "model_card": (
            "https://huggingface.co/CogBase-USTC/"
            "Qwen2.5-Math-7B-Instruct-SocraticLM"
        ),
        "license_status": (
            "other; user acknowledgement required before deployment"
        ),
        "vllm_version": VLLM_VERSION,
        "base_image": BASE_IMAGE,
        "container_image_uri": image_uri,
        "machine_type": args.machine_type,
        "accelerator_type": args.accelerator_type,
        "accelerator_count": 1,
        "max_model_len": args.max_model_len,
        "max_num_seqs": args.max_num_seqs,
        "budget": _budget_summary(args),
        "lifecycle_manifest": str(args.manifest),
        "execute": args.execute,
        "model_resource": None,
        "endpoint_resource": None,
        "deployed_model_id": None,
        "deployed_at": None,
        "delete_by": None,
        "cleanup_completed_at": None,
    }


def _assert_manifest_redeployable(manifest: dict[str, Any]) -> None:
    """Prevent a retry from orphaning resources recorded by a failed deploy."""

    status = manifest.get("status")
    if status == "cleanup_completed":
        return
    if status == "failed" and not any(
        manifest.get(field)
        for field in (
            "model_resource",
            "endpoint_resource",
            "deployed_model_id",
        )
    ):
        return
    if status == "failed":
        raise RuntimeError(
            "failed deployment still owns model or endpoint resources; "
            "run cleanup before deploying again"
        )
    raise RuntimeError(
        "lifecycle manifest already owns live or incomplete resources; "
        "inspect or clean it before another deploy"
    )


def _ensure_artifact_repository(
    args: argparse.Namespace, gcloud: list[str]
) -> None:
    describe = [
        *gcloud,
        "artifacts",
        "repositories",
        "describe",
        args.artifact_repository,
        f"--location={args.location}",
        f"--project={args.project}",
        "--format=value(name)",
    ]
    if _run(describe, check=False).returncode == 0:
        return
    _run(
        [
            *gcloud,
            "artifacts",
            "repositories",
            "create",
            args.artifact_repository,
            "--repository-format=docker",
            f"--location={args.location}",
            f"--project={args.project}",
            "--description=SocraticLM vLLM runtime images",
            "--quiet",
        ]
    )


def _vertex_service_agent_email(project_number: str) -> str:
    if not project_number.isdigit():
        raise RuntimeError("gcloud returned an invalid project number")
    return (
        f"service-{project_number}"
        "@gcp-sa-aiplatform.iam.gserviceaccount.com"
    )


def _grant_vertex_service_agent_artifact_reader(
    args: argparse.Namespace,
    gcloud: list[str],
) -> str:
    """Grant the least-privilege repository role required to pull the image."""

    project = _run(
        [
            *gcloud,
            "projects",
            "describe",
            args.project,
            "--format=value(projectNumber)",
        ]
    )
    service_agent = _vertex_service_agent_email(project.stdout.strip())
    _run(
        [
            *gcloud,
            "artifacts",
            "repositories",
            "add-iam-policy-binding",
            args.artifact_repository,
            f"--location={args.location}",
            f"--project={args.project}",
            f"--member=serviceAccount:{service_agent}",
            "--role=roles/artifactregistry.reader",
            "--quiet",
        ]
    )
    return service_agent


def _can_reuse_built_container(
    existing: dict[str, Any] | None,
    plan: dict[str, Any],
) -> bool:
    """Allow a failed post-build deploy to resume without rebuilding."""

    return bool(
        existing
        and existing.get("status") == "failed"
        and existing.get("container_built_at")
        and existing.get("container_image_uri")
        == plan.get("container_image_uri")
    )


def _container_image_exists(
    args: argparse.Namespace,
    gcloud: list[str],
    image_uri: str,
) -> bool:
    return (
        _run(
            [
                *gcloud,
                "artifacts",
                "docker",
                "images",
                "describe",
                image_uri,
                f"--project={args.project}",
                "--format=value(image_summary.digest)",
            ],
            check=False,
        ).returncode
        == 0
    )


def _json_rows(result: subprocess.CompletedProcess[str], label: str) -> list[dict[str, Any]]:
    try:
        rows = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"gcloud returned invalid JSON for {label}") from exc
    if not isinstance(rows, list) or not all(
        isinstance(row, dict) for row in rows
    ):
        raise RuntimeError(f"gcloud returned invalid {label} rows")
    return rows


def _matching_models(
    rows: Sequence[dict[str, Any]],
    *,
    image_uri: str,
    display_name: str | None,
) -> list[dict[str, Any]]:
    matches = []
    for row in rows:
        row_display_name = str(row.get("displayName") or "")
        row_image_uri = str(
            (row.get("containerSpec") or {}).get("imageUri") or ""
        )
        if row_image_uri != image_uri:
            continue
        if display_name is not None:
            if row_display_name != display_name:
                continue
        elif not row_display_name.startswith("socraticlm-vllm-"):
            continue
        if not str(row.get("name") or "").strip():
            raise RuntimeError("matching Vertex model lacks resource name")
        matches.append(row)
    return matches


def _list_matching_models(
    args: argparse.Namespace,
    gcloud: list[str],
    *,
    image_uri: str,
    display_name: str | None,
) -> list[dict[str, Any]]:
    result = _run(
        [
            *gcloud,
            "ai",
            "models",
            "list",
            f"--project={args.project}",
            f"--region={args.location}",
            (
                "--format=json(name,displayName,createTime,"
                "containerSpec.imageUri)"
            ),
        ]
    )
    return _matching_models(
        _json_rows(result, "Vertex model"),
        image_uri=image_uri,
        display_name=display_name,
    )


def _list_matching_endpoints(
    args: argparse.Namespace,
    gcloud: list[str],
    *,
    display_name: str,
) -> list[dict[str, Any]]:
    result = _run(
        [
            *gcloud,
            "ai",
            "endpoints",
            "list",
            f"--project={args.project}",
            f"--region={args.location}",
            "--format=json(name,displayName,createTime)",
        ]
    )
    rows = _json_rows(result, "Vertex endpoint")
    matches = [
        row
        for row in rows
        if row.get("displayName") == display_name
        and str(row.get("name") or "").strip()
    ]
    return matches


def _require_at_most_one(
    rows: Sequence[dict[str, Any]],
    *,
    label: str,
) -> dict[str, Any] | None:
    if len(rows) > 1:
        resources = [str(row.get("name") or "") for row in rows]
        raise RuntimeError(
            f"multiple matching {label} resources found; fail closed: "
            + ", ".join(resources)
        )
    return rows[0] if rows else None


def deploy(args: argparse.Namespace) -> int:
    plan = _deployment_plan(args)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if not args.execute:
        print("Preflight only. Add --execute after reviewing license and cost.")
        return 0
    if not args.acknowledge_license_review:
        raise RuntimeError(
            "--acknowledge-license-review is required because the "
            "SocraticLM model card declares license='other'"
        )
    existing: dict[str, Any] | None = None
    if args.manifest.exists():
        existing = json.loads(args.manifest.read_text(encoding="utf-8"))
        _assert_manifest_redeployable(existing)
    reuse_built_container = _can_reuse_built_container(existing, plan)
    atomic_json(args.manifest, plan)
    gcloud = _gcloud(args)
    try:
        _run(
            [
                *gcloud,
                "services",
                "enable",
                "aiplatform.googleapis.com",
                "artifactregistry.googleapis.com",
                "cloudbuild.googleapis.com",
                "compute.googleapis.com",
                f"--project={args.project}",
                "--quiet",
            ]
        )
        _ensure_artifact_repository(args, gcloud)
        plan["vertex_service_agent"] = (
            _grant_vertex_service_agent_artifact_reader(args, gcloud)
        )
        atomic_json(args.manifest, plan)
        if reuse_built_container and _container_image_exists(
            args, gcloud, str(plan["container_image_uri"])
        ):
            plan["container_reused"] = True
            plan["container_built_at"] = existing["container_built_at"]
        else:
            _run(
                [
                    *gcloud,
                    "builds",
                    "submit",
                    str(CONTAINER_CONTEXT),
                    f"--tag={plan['container_image_uri']}",
                    f"--project={args.project}",
                    f"--region={args.location}",
                    "--timeout=2h",
                    "--quiet",
                ]
            )
            plan["container_reused"] = False
            plan["container_built_at"] = utc_now()
        plan["status"] = "container_built"
        atomic_json(args.manifest, plan)

        prior_display_name = (
            str(existing.get("model_display_name") or "") or None
            if existing
            else None
        )
        recovered_model = _require_at_most_one(
            _list_matching_models(
                args,
                gcloud,
                image_uri=str(plan["container_image_uri"]),
                display_name=prior_display_name,
            ),
            label="SocraticLM model",
        )
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        display_name = (
            str(recovered_model["displayName"])
            if recovered_model
            else f"socraticlm-vllm-{timestamp}"
        )
        container_command = (
            "python3,-m,vllm.entrypoints.openai.api_server"
        )
        container_args = ",".join(
            [
                "--host=0.0.0.0",
                "--port=8080",
                f"--model={HF_MODEL_ID}",
                f"--served-model-name={HF_MODEL_ID}",
                f"--max-model-len={args.max_model_len}",
                "--dtype=bfloat16",
                "--gpu-memory-utilization=0.90",
                f"--max-num-seqs={args.max_num_seqs}",
                "--trust-remote-code",
                "--disable-log-stats",
            ]
        )
        plan["model_display_name"] = display_name
        if recovered_model:
            plan["model_resource"] = str(recovered_model["name"])
            plan["model_recovered"] = True
        else:
            atomic_json(args.manifest, plan)
            _run(
                [
                    *gcloud,
                    "ai",
                    "models",
                    "upload",
                    f"--project={args.project}",
                    f"--region={args.location}",
                    f"--display-name={display_name}",
                    f"--container-image-uri={plan['container_image_uri']}",
                    f"--container-command={container_command}",
                    f"--container-args={container_args}",
                    "--container-ports=8080",
                    "--container-predict-route=/v1/chat/completions",
                    "--container-health-route=/health",
                    "--container-shared-memory-size-mb=16384",
                    "--container-deployment-timeout-seconds=7200",
                    (
                        "--description=SocraticLM educational-model candidate "
                        "for experiment 20260727_170150"
                    ),
                    "--labels=experiment=20260727_170150,plan=plan05",
                    "--quiet",
                ]
            )
            uploaded_model = _require_at_most_one(
                _list_matching_models(
                    args,
                    gcloud,
                    image_uri=str(plan["container_image_uri"]),
                    display_name=display_name,
                ),
                label="newly uploaded SocraticLM model",
            )
            if uploaded_model is None:
                raise RuntimeError(
                    "model upload completed but the resource could not be "
                    "resolved by display name and image URI"
                )
            plan["model_resource"] = str(uploaded_model["name"])
            plan["model_recovered"] = False
        plan["status"] = "model_uploaded"
        atomic_json(args.manifest, plan)

        endpoint_display_name = f"{display_name}-endpoint"
        plan["endpoint_display_name"] = endpoint_display_name
        recovered_endpoint = _require_at_most_one(
            _list_matching_endpoints(
                args,
                gcloud,
                display_name=endpoint_display_name,
            ),
            label="SocraticLM endpoint",
        )
        if recovered_endpoint:
            plan["endpoint_resource"] = str(recovered_endpoint["name"])
            plan["endpoint_recovered"] = True
        else:
            atomic_json(args.manifest, plan)
            _run(
                [
                    *gcloud,
                    "ai",
                    "endpoints",
                    "create",
                    f"--project={args.project}",
                    f"--region={args.location}",
                    f"--display-name={endpoint_display_name}",
                    "--labels=experiment=20260727_170150,plan=plan05",
                    "--quiet",
                ]
            )
            created_endpoint = _require_at_most_one(
                _list_matching_endpoints(
                    args,
                    gcloud,
                    display_name=endpoint_display_name,
                ),
                label="newly created SocraticLM endpoint",
            )
            if created_endpoint is None:
                raise RuntimeError(
                    "endpoint creation completed but the resource could not "
                    "be resolved by display name"
                )
            plan["endpoint_resource"] = str(created_endpoint["name"])
            plan["endpoint_recovered"] = False
        plan["status"] = "endpoint_created"
        atomic_json(args.manifest, plan)

        endpoint_id = endpoint_id_from_resource(plan["endpoint_resource"])
        deploy_command = [
            *gcloud,
            "ai",
            "endpoints",
            "deploy-model",
            endpoint_id,
            f"--project={args.project}",
            f"--region={args.location}",
            f"--model={_resource_id(plan['model_resource'])}",
            f"--display-name={display_name}-deployed",
            f"--machine-type={args.machine_type}",
            (
                f"--accelerator=type={args.accelerator_type},"
                "count=1"
            ),
            "--min-replica-count=1",
            "--max-replica-count=1",
            "--required-replica-count=1",
            "--enable-access-logging",
            "--quiet",
        ]
        if args.service_account:
            deploy_command.append(
                f"--service-account={args.service_account}"
            )
        _run(deploy_command)

        endpoint_description = _run(
            [
                *gcloud,
                "ai",
                "endpoints",
                "describe",
                endpoint_id,
                f"--project={args.project}",
                f"--region={args.location}",
                "--format=json",
            ]
        )
        description = json.loads(endpoint_description.stdout)
        deployed_models = description.get("deployedModels") or []
        if len(deployed_models) != 1:
            raise RuntimeError(
                "expected exactly one deployed model on SocraticLM endpoint"
            )
        plan["deployed_model_id"] = str(deployed_models[0]["id"])
        deployed_at = datetime.now(timezone.utc)
        plan["deployed_at"] = deployed_at.isoformat()
        plan["delete_by"] = (
            deployed_at + timedelta(hours=args.max_endpoint_hours)
        ).isoformat()
        plan["status"] = "deployed"
        atomic_json(args.manifest, plan)
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        print(
            "Endpoint is billable now. Run the smoke test, then execute "
            "the cleanup command before delete_by."
        )
        return 0
    except Exception as exc:
        plan["status"] = "failed"
        plan["failure_at"] = utc_now()
        plan["failure"] = f"{type(exc).__name__}: {exc}"
        if isinstance(exc, CommandExecutionError):
            plan["failure_diagnostics"] = {
                "returncode": exc.returncode,
                "command": _command_text(exc.command),
                "stdout_tail": exc.stdout[-8000:],
                "stderr_tail": exc.stderr[-8000:],
            }
        atomic_json(args.manifest, plan)
        raise


def cleanup(args: argparse.Namespace) -> int:
    if not args.manifest.exists():
        raise FileNotFoundError(args.manifest)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    targets = {
        key: manifest.get(key)
        for key in (
            "project",
            "location",
            "endpoint_resource",
            "deployed_model_id",
            "model_resource",
            "container_image_uri",
            "status",
        )
    }
    print(json.dumps(targets, ensure_ascii=False, indent=2))
    if not args.execute:
        print("Cleanup preflight only. Add --execute to remove these targets.")
        return 0
    if manifest.get("status") == "cleanup_completed":
        print("Cleanup was already completed; no resources will be touched.")
        return 0
    manifest["status"] = "cleanup_in_progress"
    manifest["cleanup_started_at"] = utc_now()
    atomic_json(args.manifest, manifest)
    gcloud = _gcloud(args)
    project = str(manifest["project"])
    location = str(manifest["location"])
    endpoint_resource = manifest.get("endpoint_resource")
    model_resource = manifest.get("model_resource")
    deployed_model_id = manifest.get("deployed_model_id")
    if endpoint_resource:
        endpoint_id = endpoint_id_from_resource(str(endpoint_resource))
        if deployed_model_id:
            _run_cleanup_command(
                [
                    *gcloud,
                    "ai",
                    "endpoints",
                    "undeploy-model",
                    endpoint_id,
                    f"--deployed-model-id={deployed_model_id}",
                    f"--project={project}",
                    f"--region={location}",
                    "--quiet",
                ],
            )
        _run_cleanup_command(
            [
                *gcloud,
                "ai",
                "endpoints",
                "delete",
                endpoint_id,
                f"--project={project}",
                f"--region={location}",
                "--quiet",
            ],
        )
    if model_resource:
        _run_cleanup_command(
            [
                *gcloud,
                "ai",
                "models",
                "delete",
                _resource_id(str(model_resource)),
                f"--project={project}",
                f"--region={location}",
                "--quiet",
            ],
        )
    if args.delete_container_image and manifest.get("container_image_uri"):
        _run_cleanup_command(
            [
                *gcloud,
                "artifacts",
                "docker",
                "images",
                "delete",
                str(manifest["container_image_uri"]),
                f"--project={project}",
                "--delete-tags",
                "--quiet",
            ],
        )
    manifest["status"] = "cleanup_completed"
    manifest["cleanup_completed_at"] = utc_now()
    atomic_json(args.manifest, manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


def status(args: argparse.Namespace) -> int:
    if not args.manifest.exists():
        raise FileNotFoundError(args.manifest)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result: dict[str, Any] = {"manifest": manifest}
    deployed_at = manifest.get("deployed_at")
    if deployed_at and manifest.get("status") != "cleanup_completed":
        elapsed = (
            datetime.now(timezone.utc)
            - datetime.fromisoformat(str(deployed_at))
        ).total_seconds() / 3600
        hourly = float(manifest["budget"]["hourly_price_usd"])
        result["estimated_live_hours"] = round(max(elapsed, 0.0), 4)
        result["estimated_endpoint_cost_usd"] = round(
            max(elapsed, 0.0) * hourly, 6
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("deploy", "status", "cleanup"))
    parser.add_argument("--project", default="edu-benchmark")
    parser.add_argument("--location", default=DEFAULT_LOCATION)
    parser.add_argument(
        "--gcloud", type=Path, default=ROOT / "google-cloud-sdk/bin/gcloud"
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--artifact-repository", default="edu-benchmark-vllm"
    )
    parser.add_argument("--machine-type", default=DEFAULT_MACHINE_TYPE)
    parser.add_argument(
        "--accelerator-type", default=DEFAULT_ACCELERATOR_TYPE
    )
    parser.add_argument("--service-account")
    parser.add_argument("--max-model-len", type=int, default=4096)
    parser.add_argument("--max-num-seqs", type=int, default=8)
    parser.add_argument(
        "--hourly-price-usd",
        type=float,
        default=DEFAULT_HOURLY_PRICE_USD,
    )
    parser.add_argument("--max-endpoint-hours", type=float, default=2.0)
    parser.add_argument(
        "--build-storage-upper-usd", type=float, default=3.0
    )
    parser.add_argument(
        "--actual-spend-to-date-usd", type=float, default=56.51
    )
    parser.add_argument("--hard-budget-usd", type=float, default=250.0)
    parser.add_argument("--reserve-usd", type=float, default=25.0)
    parser.add_argument("--stage-cap-usd", type=float, default=20.0)
    parser.add_argument("--acknowledge-license-review", action="store_true")
    parser.add_argument("--delete-container-image", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.max_model_len < 1024:
        parser.error("--max-model-len must be at least 1024")
    if args.max_num_seqs < 1:
        parser.error("--max-num-seqs must be positive")
    if args.max_endpoint_hours <= 0 or args.hourly_price_usd <= 0:
        parser.error("endpoint hours and hourly price must be positive")
    return args


def main() -> int:
    args = parse_args()
    if args.action == "deploy":
        return deploy(args)
    if args.action == "cleanup":
        return cleanup(args)
    return status(args)


if __name__ == "__main__":
    raise SystemExit(main())
