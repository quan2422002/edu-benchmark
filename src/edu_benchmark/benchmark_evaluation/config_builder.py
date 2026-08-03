"""Build the compact Plan 05 evaluation configuration bundle."""

from __future__ import annotations

import csv
from io import StringIO
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .dialogue_transport import build_native_conversation
from .instruction_bundle import (
    InstructionBundle,
    PRINCIPLE_ORDER,
    load_instruction_bundle,
)


class EvaluationConfigError(RuntimeError):
    """Raised when source artifacts and generated configuration disagree."""


MODEL_FIELDS = (
    "model_id",
    "model_name",
    "provider",
    "model_class",
    "selection_role",
    "scientific_basis",
    "operational_basis",
    "specialization_evidence",
    "access_mode",
    "region",
    "license",
    "language_support",
    "native_multiturn_status",
    "input_usd_per_million",
    "output_usd_per_million",
    "endpoint_price_status",
    "price_snapshot_date",
    "price_source",
    "smoke_test_status",
    "selection_status",
    "generation_config_json",
    "thinking_config_json",
    "config_status",
)

INSTRUCTION_FIELDS = (
    "instruction_id",
    "instruction_type",
    "principle_id",
    "principle_name_vi",
    "instruction_vi",
    "instruction_bundle_version",
    "instruction_bundle_sha256",
    "source_ids",
    "basis_summary",
    "source_locator",
    "status",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV into dictionaries."""

    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _csv_text(
    fields: Iterable[str], rows: Iterable[Mapping[str, Any]]
) -> str:
    stream = StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=list(fields), lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def model_rows() -> list[dict[str, str]]:
    """Return the provisional closed/open/specialized model panel."""

    price_url = (
        "https://cloud.google.com/gemini-enterprise-agent-platform/"
        "generative-ai/pricing"
    )
    common = {
        "price_snapshot_date": "2026-07-28",
        "price_source": price_url,
    }
    return [
        {
            **common,
            "model_id": "gemini-3.5-flash",
            "model_name": "Gemini 3.5 Flash",
            "provider": "Google",
            "model_class": "closed_general",
            "selection_role": "core_closed_target_and_primary_judge",
            "scientific_basis": (
                "Đại diện model đóng đa dụng; kế thừa cấu trúc nhóm model "
                "của KMP-Bench."
            ),
            "operational_basis": (
                "Target smoke v2 đã hoàn thành 10/10; blind judge v2 "
                "lần đầu hoàn tất 11/20; retry1 preflight đúng 20 phép so sánh với trần 1,77456 USD."
            ),
            "specialization_evidence": (
                "Không; đây không phải model chuyên biệt giáo dục."
            ),
            "access_mode": "Vertex AI managed API",
            "region": "global",
            "license": "Google managed service terms",
            "language_support": "Vietnamese passed smoke v1",
            "native_multiturn_status": "target_smoke_v2_passed",
            "input_usd_per_million": "1.50",
            "output_usd_per_million": "9.00",
            "endpoint_price_status": "not_applicable",
            "smoke_test_status": "target_v2_passed_judge_preflight_passed",
            "selection_status": "provisional_core",
            "generation_config_json": (
                '{"target":{"max_output_tokens":1024,"seed":20260728,'
                '"sampling_parameters":"omitted"},'
                '"judge":{"max_output_tokens":8192,"seed":20260728,'
                '"sampling_parameters":"omitted"}}'
            ),
            "thinking_config_json": (
                '{"thinking_level":"MEDIUM","include_thoughts":false}'
            ),
            "config_status": "target_passed_judge_smoke_ready",
        },
        {
            **common,
            "model_id": "meta/llama-4-maverick-17b-128e-instruct-maas",
            "model_name": "Llama 4 Maverick",
            "provider": "Meta via Google Cloud",
            "model_class": "open_weight_general",
            "selection_role": "core_open_target",
            "scientific_basis": (
                "Đại diện model open-weight đa dụng để so sánh khác cơ chế "
                "phát hành."
            ),
            "operational_basis": (
                "MaaS trên Vertex AI; trường model của OpenAPI request phải "
                "dùng định danh publisher/model là "
                "meta/llama-4-maverick-17b-128e-instruct-maas; smoke v2 đã "
                "chạy thành công trên 10/10 candidate."
            ),
            "specialization_evidence": (
                "Không; đây không phải model chuyên biệt giáo dục."
            ),
            "access_mode": "Vertex AI partner MaaS",
            "region": "us-east5",
            "license": (
                "Llama 4 Community License and Vertex EULA acceptance required"
            ),
            "language_support": "Vietnamese passed 10-candidate smoke v2",
            "native_multiturn_status": "smoke_v2_passed",
            "input_usd_per_million": "0.35",
            "output_usd_per_million": "1.15",
            "endpoint_price_status": "not_applicable",
            "smoke_test_status": "v2_completed_10_of_10",
            "selection_status": "provisional_core",
            "generation_config_json": (
                '{"max_tokens":1024,"sampling_parameters":"omitted"}'
            ),
            "thinking_config_json": "{}",
            "config_status": "smoke_passed_provisional",
        },
        {
            **common,
            "model_id": (
                "CogBase-USTC/Qwen2.5-Math-7B-Instruct-SocraticLM"
            ),
            "model_name": "SocraticLM",
            "provider": "Self-deployed on Vertex AI",
            "model_class": "specialized_education",
            "selection_role": "core_specialized_target_candidate",
            "scientific_basis": (
                "Ứng viên có mục tiêu huấn luyện cho đối thoại dạy học kiểu "
                "Socrates; phải kiểm bằng chứng và pilot."
            ),
            "operational_basis": (
                "Checkpoint Hugging Face được phục vụ bằng vLLM 0.9.2 trên "
                "custom Vertex endpoint g2-standard-12 + một L4; request dùng "
                "rawPredict và endpoint phải được dọn ngay sau smoke."
            ),
            "specialization_evidence": (
                "Model card tuyên bố chuyên biệt dạy học; chưa xác nhận "
                "chất lượng tiếng Việt."
            ),
            "access_mode": "Vertex AI self-deployed endpoint",
            "region": "us-central1",
            "license": (
                "Model card declares license=other; explicit manual review "
                "acknowledgement required before deployment"
            ),
            "language_support": "English/Chinese stated; Vietnamese unknown",
            "native_multiturn_status": (
                "vertex_raw_predict_adapter_implemented_smoke_pending"
            ),
            "input_usd_per_million": "",
            "output_usd_per_million": "",
            "endpoint_price_status": (
                "g2-standard-12 snapshot 1.000416348 USD/hour; verify billing "
                "before deployment"
            ),
            "smoke_test_status": (
                "pending_license_deployment_and_vietnamese_smoke"
            ),
            "selection_status": "provisional_gap_if_smoke_fails",
            "generation_config_json": (
                '{"max_tokens":1024,"temperature":0.0,"seed":20260728}'
            ),
            "thinking_config_json": "{}",
            "config_status": "endpoint_tooling_ready_smoke_pending",
        },
        {
            **common,
            "model_id": "claude-sonnet-4-6",
            "model_name": "Claude Sonnet 4.6",
            "provider": "Anthropic via Google Cloud",
            "model_class": "closed_general_optional",
            "selection_role": "optional_second_pilot_judge",
            "scientific_basis": (
                "Judge khác họ để kiểm độ bền kết luận trên tập con."
            ),
            "operational_basis": (
                "Partner MaaS; lần chạy 20 cặp thất bại HTTP 404 vì "
                "project chưa kích hoạt sản phẩm Anthropic trên "
                "Google Cloud Marketplace; chi phí bằng 0 USD."
            ),
            "specialization_evidence": (
                "Không; đây không phải model chuyên biệt giáo dục."
            ),
            "access_mode": "Vertex AI partner MaaS",
            "region": "us-east5",
            "license": "Anthropic and Vertex partner service terms",
            "language_support": "Vietnamese must pass judge smoke",
            "native_multiturn_status": (
                "anthropic_judge_adapter_implemented_access_blocked"
            ),
            "input_usd_per_million": "3.30",
            "output_usd_per_million": "16.50",
            "endpoint_price_status": "not_applicable",
            "smoke_test_status": "failed_20_of_20_marketplace_not_enabled",
            "selection_status": "deferred_marketplace_blocked",
            "generation_config_json": (
                '{"max_tokens":3072,"temperature":0.0}'
            ),
            "thinking_config_json": "{}",
            "config_status": "blocked_external_access",
        },
    ]


def instruction_rows(
    principles: list[dict[str, str]],
    instruction_bundle: InstructionBundle,
) -> list[dict[str, str]]:
    """Build one general and six principle instructions deterministically."""

    by_id = {row["principle_id"]: row for row in principles}
    if set(by_id) != set(PRINCIPLE_ORDER):
        raise EvaluationConfigError(
            "principle registry must contain exactly six canonical IDs"
        )
    bundle_principles = instruction_bundle.principles_by_id
    if set(bundle_principles) != set(PRINCIPLE_ORDER):
        raise EvaluationConfigError(
            "instruction bundle must contain exactly six canonical IDs"
        )
    for principle_id in PRINCIPLE_ORDER:
        if (
            bundle_principles[principle_id].principle_name_vi
            != by_id[principle_id]["principle_name_vi"]
        ):
            raise EvaluationConfigError(
                f"{principle_id}: Vietnamese name differs between the "
                "instruction bundle and principle registry"
            )
    rows = [
        {
            "instruction_id": "INST-GENERAL-001",
            "instruction_type": "general",
            "principle_id": "",
            "principle_name_vi": "",
            "instruction_vi": instruction_bundle.general_instruction,
            "instruction_bundle_version": (
                instruction_bundle.bundle_version
            ),
            "instruction_bundle_sha256": instruction_bundle.sha256,
            "source_ids": (
                "CAP-ACC;CAP-STATE;CAP-STRAT;CAP-SCAFF;CAP-AGENCY;CAP-CARE"
            ),
            "basis_summary": (
                "Tổng hợp sáu năng lực gia sư thành các điều kiện nền: đúng "
                "chuyên môn, bám trạng thái học sinh, chọn và điều tiết hỗ "
                "trợ phù hợp, giữ quyền chủ động, giao tiếp phù hợp lứa tuổi."
            ),
            "source_locator": (
                "inherited_resources/from_20260722_000940/"
                "benchmark_specification/capability_model/"
                "tutor_capability_model.md; "
                "outputs/benchmark_rubric/rubrics.csv"
            ),
            "status": "needs_hnmu_review",
        }
    ]
    for principle_id in PRINCIPLE_ORDER:
        source = by_id[principle_id]
        rows.append(
            {
                "instruction_id": (
                    f"INST-{principle_id.removeprefix('PRINCIPLE-')}-001"
                ),
                "instruction_type": "principle",
                "principle_id": principle_id,
                "principle_name_vi": (
                    bundle_principles[principle_id].principle_name_vi
                ),
                "instruction_vi": instruction_bundle.render_principle(
                    principle_id
                ),
                "instruction_bundle_version": (
                    instruction_bundle.bundle_version
                ),
                "instruction_bundle_sha256": instruction_bundle.sha256,
                "source_ids": source["research_ids"],
                "basis_summary": (
                    "Biên soạn từ định nghĩa, điều kiện gán/không gán và "
                    "dấu hiệu quan sát được của nguyên tắc; thêm ràng buộc "
                    "không làm mất quyền chủ động từ mô hình năng lực gia sư."
                ),
                "source_locator": (
                    f"{source['source_locator']}; "
                    "inherited_resources/from_20260722_000940/"
                    "benchmark_specification/principle_foundation/"
                    "pedagogical_principles.csv"
                ),
                "status": "needs_hnmu_review",
            }
        )
    return rows


def select_applicable_rubric_ids(
    rubrics: list[dict[str, str]],
    required_principle_ids: Iterable[str],
) -> tuple[str, ...]:
    """Select all general and only score>=4 principle-specific rubrics."""

    required = set(required_principle_ids)
    unknown = required - set(PRINCIPLE_ORDER)
    if unknown:
        raise EvaluationConfigError(
            f"unknown required principles: {sorted(unknown)}"
        )
    if not required:
        raise EvaluationConfigError("at least one required principle is needed")
    selected = tuple(
        row["rubric_id"]
        for row in rubrics
        if row["tier"] == "general"
        or (
            row["tier"] == "principle"
            and row["principle_id"] in required
        )
    )
    expected_count = 4 + 3 * len(required)
    if len(selected) != expected_count:
        raise EvaluationConfigError(
            "applicable rubric count does not match four general plus three "
            "for each required principle"
        )
    return selected


def evaluation_schema(
    rubrics: list[dict[str, str]],
    serious_errors: list[dict[str, str]],
) -> dict[str, Any]:
    """Create a schema with one bundled record per judge call."""

    rubric_ids = [row["rubric_id"] for row in rubrics]
    general_rubric_ids = [
        row["rubric_id"] for row in rubrics if row["tier"] == "general"
    ]
    principle_rubric_ids = {
        principle_id: [
            row["rubric_id"]
            for row in rubrics
            if row["tier"] == "principle"
            and row["principle_id"] == principle_id
        ]
        for principle_id in PRINCIPLE_ORDER
    }
    if len(general_rubric_ids) != 4 or any(
        len(ids) != 3 for ids in principle_rubric_ids.values()
    ):
        raise EvaluationConfigError(
            "rubrics must contain four general criteria and exactly three "
            "criteria for each canonical principle"
        )
    error_ids = [row["error_id"] for row in serious_errors]
    principle_set = {
        "type": "array",
        "minItems": 1,
        "uniqueItems": True,
        "items": {"enum": list(PRINCIPLE_ORDER)},
        "description": (
            "The exact unordered set derived by code from "
            "requirement_score >= 4. Score-3 principles are forbidden."
        ),
    }
    usage = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "input_tokens",
            "output_tokens",
            "estimated_cost_usd",
        ],
        "properties": {
            "input_tokens": {"type": "integer", "minimum": 0},
            "output_tokens": {"type": "integer", "minimum": 0},
            "estimated_cost_usd": {"type": "number", "minimum": 0},
        },
    }
    target = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "record_type",
            "response_id",
            "benchmark_candidate_id",
            "experiment_id",
            "plan_id",
            "pipeline_stage",
            "run_id",
            "model_id",
            "response_text",
            "finish_reason",
            "response_status",
            "completion_issue",
            "system_prompt",
            "user_prompt",
            "conversation_messages",
            "input_hash",
            "system_instruction_hash",
            "messages_hash",
            "instruction_bundle_version",
            "instruction_bundle_sha256",
            "required_principle_ids",
            "usage",
        ],
        "properties": {
            "record_type": {"const": "target_response"},
            "response_id": {"type": "string", "minLength": 1},
            "benchmark_candidate_id": {"type": "string", "minLength": 1},
            "experiment_id": {"type": "string", "minLength": 1},
            "plan_id": {"type": "string", "minLength": 1},
            "pipeline_stage": {
                "enum": [
                    "benchmark_evaluation_target_smoke",
                    "benchmark_evaluation_target_pilot",
                    "benchmark_evaluation_target_full",
                ]
            },
            "run_id": {"type": "string", "minLength": 1},
            "model_id": {"type": "string", "minLength": 1},
            "response_text": {"type": "string", "minLength": 1},
            "finish_reason": {"type": "string", "minLength": 1},
            "response_status": {
                "enum": ["completed", "needs_review"]
            },
            "completion_issue": {
                "type": ["string", "null"],
            },
            "system_prompt": {"type": "string", "minLength": 1},
            "user_prompt": {"type": "string", "minLength": 1},
            "conversation_messages": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["role", "content"],
                    "properties": {
                        "role": {"enum": ["user", "assistant"]},
                        "content": {"type": "string", "minLength": 1},
                    },
                },
            },
            "input_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "system_instruction_hash": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
            "messages_hash": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
            "instruction_bundle_version": {
                "type": "string",
                "minLength": 1,
            },
            "instruction_bundle_sha256": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
            "required_principle_ids": {
                "$ref": "#/$defs/required_principle_set"
            },
            "usage": {"$ref": "#/$defs/usage"},
            "created_at": {"type": "string", "format": "date-time"},
            "model_version": {"type": "string"},
            "latency_seconds": {"type": "number", "minimum": 0},
            "attempt": {"type": "integer", "minimum": 1},
        },
    }
    criterion = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "rubric_id",
            "judgment",
            "rationale",
            "model_response_evidence",
            "gold_response_evidence",
        ],
        "properties": {
            "rubric_id": {"enum": rubric_ids},
            "judgment": {"enum": ["Win", "Tie", "Lose"]},
            "rationale": {"type": "string", "minLength": 1},
            "model_response_evidence": {"type": "string"},
            "gold_response_evidence": {"type": "string"},
        },
    }
    serious_error = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "error_id",
            "detected",
            "rationale",
            "applied_action",
        ],
        "properties": {
            "error_id": {"enum": error_ids},
            "detected": {"type": "boolean"},
            "rationale": {"type": "string"},
            "applied_action": {"type": "string"},
        },
    }
    evaluation = {
        "type": "object",
        "additionalProperties": False,
        "description": (
            "One judge call returns every applicable criterion, serious "
            "error decision and overall judgment for one target response."
        ),
        "required": [
            "record_type",
            "judge_call_id",
            "response_id",
            "benchmark_candidate_id",
            "judge_model_id",
            "pair_order",
            "required_principle_ids",
            "applicable_rubric_ids",
            "criterion_judgments",
            "serious_errors",
            "overall_judgment",
            "same_model_family",
            "usage",
        ],
        "properties": {
            "record_type": {"const": "evaluation_record"},
            "judge_call_id": {"type": "string", "minLength": 1},
            "response_id": {"type": "string", "minLength": 1},
            "benchmark_candidate_id": {"type": "string", "minLength": 1},
            "judge_model_id": {"type": "string", "minLength": 1},
            "pair_order": {
                "enum": ["model_A_gold_B", "gold_A_model_B"]
            },
            "required_principle_ids": {
                "$ref": "#/$defs/required_principle_set"
            },
            "applicable_rubric_ids": {
                "type": "array",
                "minItems": 7,
                "uniqueItems": True,
                "items": {"enum": rubric_ids},
            },
            "criterion_judgments": {
                "type": "array",
                "minItems": 4,
                "items": {"$ref": "#/$defs/criterion_judgment"},
            },
            "serious_errors": {
                "type": "array",
                "items": {"$ref": "#/$defs/serious_error_judgment"},
            },
            "overall_judgment": {"enum": ["Win", "Tie", "Lose"]},
            "same_model_family": {"type": "boolean"},
            "usage": {"$ref": "#/$defs/usage"},
        },
        "allOf": [
            *[
                {
                    "properties": {
                        "applicable_rubric_ids": {
                            "contains": {"const": rubric_id}
                        }
                    }
                }
                for rubric_id in general_rubric_ids
            ],
            *[
                {
                    "if": {
                        "properties": {
                            "required_principle_ids": {
                                "contains": {"const": principle_id}
                            }
                        }
                    },
                    "then": {
                        "allOf": [
                            {
                                "properties": {
                                    "applicable_rubric_ids": {
                                        "contains": {"const": rubric_id}
                                    }
                                }
                            }
                            for rubric_id in principle_rubric_ids[
                                principle_id
                            ]
                        ]
                    },
                    "else": {
                        "properties": {
                            "applicable_rubric_ids": {
                                "not": {
                                    "contains": {
                                        "enum": principle_rubric_ids[
                                            principle_id
                                        ]
                                    }
                                }
                            }
                        }
                    },
                }
                for principle_id in PRINCIPLE_ORDER
            ],
        ],
    }
    blind_target_judgment = {"enum": ["Win", "Tie", "Lose"]}
    blind_criterion = {
        "type": "object",
        "required": ["criterion_name", "rubric_id", "target_judgment"],
        "properties": {
            "criterion_name": {"type": "string", "minLength": 1},
            "rubric_id": {"enum": rubric_ids},
            "target_judgment": {
                "$ref": "#/$defs/blind_target_judgment"
            },
        },
    }
    blind_error = {
        "type": "object",
        "required": [
            "error_name",
            "error_id",
            "affected_rubric_ids",
            "detected_sources",
            "target_detected",
            "reference_detected",
        ],
        "properties": {
            "error_name": {"type": "string", "minLength": 1},
            "error_id": {"enum": error_ids},
            "affected_rubric_ids": {
                "type": "array",
                "minItems": 1,
                "uniqueItems": True,
                "items": {"enum": rubric_ids},
            },
            "detected_sources": {
                "type": "array",
                "uniqueItems": True,
                "items": {"enum": ["target", "reference"]},
            },
            "target_detected": {"type": "boolean"},
            "reference_detected": {"type": "boolean"},
        },
    }
    blind_adjustment = {
        "type": "object",
        "required": [
            "rubric_id",
            "criterion_name",
            "raw_target_judgment",
            "adjusted_target_judgment",
            "changed",
            "serious_errors",
        ],
        "properties": {
            "rubric_id": {"enum": rubric_ids},
            "criterion_name": {"type": "string", "minLength": 1},
            "raw_target_judgment": {
                "$ref": "#/$defs/blind_target_judgment"
            },
            "adjusted_target_judgment": {
                "$ref": "#/$defs/blind_target_judgment"
            },
            "changed": {"type": "boolean"},
            "serious_errors": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "object"},
            },
        },
    }
    blind_evaluation = {
        "type": "object",
        "description": (
            "Plan 05 v2 blind pairwise judge record with raw and "
            "serious-error-adjusted criterion judgments."
        ),
        "required": [
            "record_type",
            "record_status",
            "comparison_id",
            "benchmark_candidate_id",
            "target_run_id",
            "target_response_id",
            "target_model_id",
            "judge_model_id",
            "system_prompt",
            "user_prompt",
            "judge_output_contract_version",
            "raw_judge_response",
            "blind_judgment",
            "raw_criterion_judgments",
            "serious_error_findings",
            "adjusted_criterion_judgments",
            "criterion_adjustments",
            "overall_judgment",
            "usage",
        ],
        "properties": {
            "record_type": {"const": "blind_pairwise_judgment"},
            "record_status": {"const": "completed"},
            "comparison_id": {"type": "string", "minLength": 1},
            "benchmark_candidate_id": {
                "type": "string",
                "minLength": 1,
            },
            "target_run_id": {"type": "string", "minLength": 1},
            "target_response_id": {"type": "string"},
            "target_model_id": {"type": "string", "minLength": 1},
            "judge_model_id": {"type": "string", "minLength": 1},
            "system_prompt": {"type": "string", "minLength": 1},
            "user_prompt": {"type": "string", "minLength": 1},
            "judge_output_contract_version": {"const": "v2"},
            "raw_judge_response": {"type": "string", "minLength": 1},
            "blind_judgment": {"type": "object"},
            "raw_criterion_judgments": {
                "type": "array",
                "minItems": 4,
                "items": {
                    "$ref": "#/$defs/blind_criterion_judgment_v2"
                },
            },
            "serious_error_findings": {
                "type": "array",
                "items": {"$ref": "#/$defs/serious_error_finding_v2"},
            },
            "adjusted_criterion_judgments": {
                "type": "array",
                "minItems": 4,
                "items": {
                    "$ref": "#/$defs/blind_criterion_judgment_v2"
                },
            },
            "criterion_adjustments": {
                "type": "array",
                "items": {"$ref": "#/$defs/criterion_adjustment_v2"},
            },
            "overall_judgment": {
                "type": "object",
                "required": ["target_judgment"],
                "properties": {
                    "target_judgment": {
                        "$ref": "#/$defs/blind_target_judgment"
                    }
                },
            },
            "usage": {"type": "object"},
        },
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "benchmark-evaluation-schema-v2.json",
        "title": "Tutor benchmark target and bundled judge records",
        "x-principle-selection-policy": {
            "source_field": "requirement_score",
            "operator": ">=",
            "threshold": 4,
            "score_3_selected": False,
        },
        "oneOf": [
            {"$ref": "#/$defs/target_response"},
            {"$ref": "#/$defs/evaluation_record"},
            {"$ref": "#/$defs/blind_pairwise_judgment_v2"},
        ],
        "$defs": {
            "usage": usage,
            "required_principle_set": principle_set,
            "target_response": target,
            "criterion_judgment": criterion,
            "serious_error_judgment": serious_error,
            "evaluation_record": evaluation,
            "blind_target_judgment": blind_target_judgment,
            "blind_criterion_judgment_v2": blind_criterion,
            "serious_error_finding_v2": blind_error,
            "criterion_adjustment_v2": blind_adjustment,
            "blind_pairwise_judgment_v2": blind_evaluation,
        },
    }


def protocol_text(
    *,
    candidate_count: int,
    eligible_count: int,
    rubric_count: int,
    error_count: int,
    instruction_bundle: InstructionBundle,
) -> str:
    """Return the concise human-facing protocol."""

    candidate_count_vi = f"{candidate_count:,}".replace(",", ".")
    eligible_count_vi = f"{eligible_count:,}".replace(",", ".")
    bundle_path = instruction_bundle.source_path
    try:
        bundle_locator = str(bundle_path.relative_to(Path.cwd().resolve()))
    except ValueError:
        bundle_locator = str(bundle_path)
    return f"""# Giao thức đánh giá phản hồi gia sư — Plan 05

Trạng thái: **smoke v2 đã hoàn thành; phương án hybrid đã khóa: sinh full
ba cấu hình, rồi judge cost-pilot 30 mẫu; instruction vẫn chờ HNMU review**.

## Phạm vi

- Pool nguồn: {candidate_count_vi} candidate; pool ưu tiên: {eligible_count_vi} candidate.
- Thư viện tạm dùng: {rubric_count} rubric (4 chung + {rubric_count - 4} riêng) và {error_count} lỗi nghiêm trọng.
- Score nguyên tắc và rubric chưa phải nhãn chuyên gia.

## Request cho tutor model

System instruction được gửi riêng và chỉ chứa vai trò gia sư, lớp, bài học,
câu hỏi nguồn, instruction chung và instruction của các nguyên tắc bắt buộc.
Nguồn instruction đã khóa là `{instruction_bundle.bundle_version}` tại
`{bundle_locator}` với SHA-256
`{instruction_bundle.sha256}`. Mỗi yêu cầu ghi rõ tên tiếng Việt, mục tiêu,
hành vi cần thể hiện, điều cần tránh và cách bảo toàn quyền chủ động của
học sinh.
Registry gốc hiện vẫn dùng bundle `v1` để bảo toàn baseline. Smoke v2
phải truyền tường minh bundle `v2` và manifest smoke v1 để chỉ thay đổi
yêu cầu trả lời cô đọng trên đúng cùng 10 candidate.
`student_prompt` là message `user` đầu tiên; từng lượt history giữ nguyên
ranh giới và role native. Request không chứa `gold_answer`, `gold_response`,
fragment, rubric, score, candidate ID hoặc sample ID.

Mỗi target record lưu nguyên system prompt, user prompt cuối cùng và toàn
bộ message có role; các hash phải khớp lại với chính nội dung đã lưu.
Record đồng thời lưu `finish_reason`, `response_status` và
`completion_issue`. Kết quả dừng vì `MAX_TOKENS`, `length` hoặc lý do
không thành công khác phải vào review, không được tính là hoàn thành.
Hợp đồng ba trường này áp dụng từ smoke v2; bundle v1 là baseline lịch sử
không được tự suy diễn ngược `finish_reason` khi provider metadata không
còn trong artifact.
Manifest và record cùng ghi experiment, plan, pipeline stage và run ID.
Toàn bộ cấu hình cùng run sinh/chấm thuộc phase này nằm dưới một gốc
`outputs/benchmark_evaluation/`.

Tập nguyên tắc bắt buộc được code tái lập chính xác từ
`requirement_score >= 4`. Nguyên tắc điểm `3` không được đưa vào
instruction, không kích hoạt rubric riêng và không được gửi judge.

Validator dừng đóng nếu history không phải danh sách, `turn_index` không
tăng, role sai/không xen kẽ, content rỗng hoặc ngữ cảnh không bắt đầu và
kết thúc bằng học sinh.

## Panel và smoke test

Panel vận hành hiện có Gemini 3.5 Flash và Llama 4 Maverick. Pilot còn có
một prompt ablation dùng cùng Gemini 3.5 Flash với bundle
`instruction_bundle_v3_learnlm.yaml`; đây không phải model độc lập hoặc
model chuyên biệt. SocraticLM chưa vượt deployment smoke và Claude Sonnet
4.6 chưa được kích hoạt trên Marketplace. Nếu model chuyên biệt không đạt,
phải báo khoảng trống thay vì thay bằng model đa dụng.

## Sinh và chấm

Một judge call cho một cặp candidate–target response phải trả toàn bộ phán
quyết theo tiêu chí, lỗi nghiêm trọng và phán quyết tổng thể; không gọi
riêng từng rubric. Hai response được ẩn danh và tráo bằng seed.

System prompt chuẩn là
`shared/prompts/benchmark_response_judging/system_prompt_v2.md` và được gửi
qua system field native. User prompt là một message Markdown; mọi nội dung
trong bối cảnh, lịch sử, học liệu và response đều là dữ liệu, không phải
instruction cho judge.

Căn cứ học liệu được nhóm theo đúng `book_title + lesson_title`. Mỗi nhóm
chỉ gửi heading và content; fragment cùng nhóm giữ thứ tự và cách nhau bằng
`-----`. `position`, `scope`, fragment metadata, ID và cột quản trị lỗi
không được gửi model.

Judge chỉ nhận/trả tên tiêu chí và tên lỗi. Code ánh xạ tên về ID sau khi
kiểm catalog. Mỗi lỗi chỉ mang tên các rubric vừa bị lỗi ảnh hưởng vừa đang
áp dụng cho candidate. Judge kiểm lỗi độc lập cho hai response; cả hai có
thể cùng mắc lỗi.

Sau unblind, code giữ phán quyết raw và áp cổng xác định trên mỗi tiêu chí
bị ảnh hưởng: không bên nào mắc lỗi thì giữ raw; chỉ target mắc thì
`Lose`; chỉ reference mắc thì `Win`; cả hai mắc thì target vẫn `Lose`.
Nhiều lỗi cùng ảnh hưởng một tiêu chí chỉ tạo một điều chỉnh. Phán quyết
tổng thể của judge được giữ làm kết quả phụ và không bị cổng này ghi đè.

Smoke judge đã hoàn thành đủ 20/20 cặp trên 10 candidate. Pilot kế tiếp
dùng manifest `pilot_80_v1`: 80 candidate thuộc 80 family, đúng 20 mẫu mỗi
lớp, giữ 10 smoke anchor, lấy đủ 8 mẫu Challenge và bao phủ có chủ đích
Practice/Modelling, lịch sử hội thoại, Bloom cùng kích thước tập nguyên
tắc. Ba target configuration tạo 240 response: Gemini 3.5 Flash baseline,
Llama 4 Maverick và cùng Gemini 3.5 Flash với system instruction định hướng
LearnLM. Cấu hình LearnLM là một prompt ablation trên cùng base model, không
phải model thứ ba độc lập hay model chuyên biệt. Gemini 3.5 Flash chấm đủ
240 cặp. Hai cấu hình Gemini phải được nhóm theo `target_run_id`, không được
gộp chỉ vì cùng `model_id`.
Pilot không đại diện phân bố quần thể và chưa có calibration người–judge
độc lập mới. Kết quả target Gemini phải được báo riêng vì target và judge
cùng model. Lần chạy Claude thất bại do chưa kích hoạt Marketplace được
giữ làm provenance, không được resume như một Gemini run.

Kết quả báo Win/Tie/Lose theo tiêu chí chung, nguyên tắc, lớp,
candidate-macro và family-macro. Mặc định không đổi Tie thành 0,5.

## Ngân sách

Hard cap toàn experiment là 250 USD: 56 USD lịch sử, 20 USD smoke/endpoint,
55 USD pilot, 94 USD main và 25 USD dự phòng. Trước batch kế tiếp, runner
phải bảo đảm:

```text
actual_spend_to_date
+ current_plan_spend
+ upper_bound(next_batch)
+ reserve
<= 250 USD
```

Pilot hiện tại dùng Gemini 3.5 Flash làm judge duy nhất. Cận trên gồm mọi
attempt retry là 3,29184 USD cho Gemini baseline, 0,534624 USD cho Llama,
3,43584 USD cho Gemini+LearnLM prompt và 42,58944 USD cho judge; tổng
49,851744 USD, dưới trần pilot 55 USD. Model chuyên biệt vẫn là khoảng
trống vận hành và không được thay thế ngầm bằng cấu hình LearnLM này.

Lần Gemini baseline đầu ghi đủ 1.400 record nhưng 436 response chạm
`MAX_TOKENS` ở cap 1.024; không có API exception. Recovery giữ nguyên model,
prompt, seed và MEDIUM thinking, chỉ tăng cap lên 1.536 rồi chạy lại đúng
436 ID. Source bundle chỉ được dựng lại và thay thế nguyên tử khi 436/436 hoàn
chỉnh; staging nằm trong `/tmp`, bị xóa sau merge, còn provenance được nhúng
vào manifest chính. Cận trên recovery là 23,967792 USD.

Phương án hybrid khóa đúng 1.400 candidate từ export eligible. Ba target
full tạo 4.200 response; cận trên bảo thủ là 127,09032 USD và ngoại suy từ
smoke khoảng 18,678072 USD. Sau đó judge chỉ chấm 30 candidate trên cả ba
cấu hình, tức 90 phép so sánh; cận trên 15,97104 USD và ngoại suy khoảng
3,223544 USD. Tập 30 mẫu chỉ đo chi phí/vận hành, không đại diện quần thể.

Nếu cost-pilot đạt cổng, full judge chỉ xét Gemini baseline và Llama, tức
2.800 phép so sánh; LearnLM chỉ được phân tích ở cost-pilot. Cận trên full
judge hiện là 496,8768 USD nên cổng này vẫn đóng dưới hard cap 250 USD và
phải được tái dự toán từ usage cost-pilot.

## Cổng còn mở

- Người dùng chạy recovery 436 response Gemini trước; sau khi merge đủ 1.400/1.400 mới resume wrapper full để chạy Llama và LearnLM.
- Khi đủ 4.200 response, người dùng chạy wrapper judge cost-pilot 30 mẫu.
- Giá, model version và actual billing phải được chụp lại trước mỗi run.
- UET duyệt usage/chi phí cost-pilot trước khi cân nhắc full judge hai model.
- HNMU duyệt instruction và diễn giải rubric.
"""


def build_evaluation_config(
    *,
    output_dir: Path,
    principles_csv: Path,
    rubrics_csv: Path,
    serious_errors_csv: Path,
    candidates_csv: Path,
    analysis_json: Path,
    instruction_bundle_path: Path,
) -> dict[str, Any]:
    """Validate source inputs and publish exactly four configuration files."""

    principles = read_csv(principles_csv)
    rubrics = read_csv(rubrics_csv)
    serious_errors = read_csv(serious_errors_csv)
    candidates = read_csv(candidates_csv)
    analysis = json.loads(analysis_json.read_text(encoding="utf-8"))
    instruction_bundle = load_instruction_bundle(instruction_bundle_path)
    eligible_ids = analysis["eligibility"]["candidate_ids"][
        "eligible_without_plan03_review"
    ]

    if len(rubrics) != 22:
        raise EvaluationConfigError("expected 22 rubric rows")
    if sum(row["tier"] == "general" for row in rubrics) != 4:
        raise EvaluationConfigError("expected four general rubrics")
    if len(serious_errors) != 6:
        raise EvaluationConfigError("expected six serious errors")
    candidate_ids = {
        row["benchmark_candidate_id"] for row in candidates
    }
    if len(candidate_ids) != 2028:
        raise EvaluationConfigError("expected 2,028 unique candidates")
    if len(eligible_ids) != 1400 or not set(eligible_ids) <= candidate_ids:
        raise EvaluationConfigError("eligible pool is inconsistent")
    for candidate in candidates:
        build_native_conversation(
            candidate["student_prompt"],
            candidate["conversation_history"],
        )

    models = model_rows()
    instructions = instruction_rows(principles, instruction_bundle)
    artifacts = {
        "evaluation_protocol.md": protocol_text(
            candidate_count=len(candidates),
            eligible_count=len(eligible_ids),
            rubric_count=len(rubrics),
            error_count=len(serious_errors),
            instruction_bundle=instruction_bundle,
        ),
        "model_registry.csv": _csv_text(MODEL_FIELDS, models),
        "instruction_registry.csv": _csv_text(
            INSTRUCTION_FIELDS, instructions
        ),
        "evaluation_schema.json": (
            json.dumps(
                evaluation_schema(rubrics, serious_errors),
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        ),
    }
    for name, content in artifacts.items():
        _atomic_write(output_dir / name, content)

    return {
        "candidate_count": len(candidates),
        "eligible_count": len(eligible_ids),
        "rubric_count": len(rubrics),
        "serious_error_count": len(serious_errors),
        "model_count": len(models),
        "instruction_count": len(instructions),
        "instruction_bundle_version": instruction_bundle.bundle_version,
        "instruction_bundle_sha256": instruction_bundle.sha256,
        "output_files": sorted(artifacts),
    }
