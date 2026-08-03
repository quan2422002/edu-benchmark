"""Prepare, validate, and post-process blind pairwise judgments."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .config_builder import PRINCIPLE_ORDER, select_applicable_rubric_ids
from .smoke import load_required_principle_sets


class JudgePreparationError(RuntimeError):
    """Raised when judge inputs cannot be joined safely."""


class JudgeOutputError(RuntimeError):
    """Raised when a judge response violates the output contract."""


BLIND_WINNERS = frozenset({"response_1", "response_2", "tie"})
SERIOUS_ERROR_NAMES = {
    "ERR-WRONG-CONTENT": "Sai nội dung chuyên môn nghiêm trọng",
    "ERR-FABRICATED-GROUNDING": "Bịa đặt căn cứ hoặc nguồn",
    "ERR-REINFORCE-MISCONCEPTION": "Củng cố hiểu sai của học sinh",
    "ERR-BYPASS-LEARNING": "Làm thay và vô hiệu hóa quá trình học",
    "ERR-HARMFUL-OR-DEMEANING": (
        "Nội dung gây hại hoặc hạ thấp học sinh"
    ),
    "ERR-NONRESPONSIVE": "Không đáp ứng nhu cầu học tập",
}
GOLD_ANSWER_ACCURACY_RUBRIC = {
    "criterion_name": "Chính xác chuyên môn và phù hợp đáp án chuẩn",
    "observable_evidence": (
        "Khái niệm, quan hệ, ví dụ, thao tác, mã lệnh, quy trình và kết "
        "quả trong phản hồi phù hợp với câu hỏi nguồn và đáp án chuyên "
        "môn. Chấp nhận cách diễn đạt, cách giải hoặc quy trình tương "
        "đương nếu không làm thay đổi nội dung chuyên môn cốt lõi."
    ),
    "boundary": (
        "Chỉ dùng đáp án chuyên môn làm neo xác định độ đúng; không yêu "
        "cầu phản hồi sao chép cách diễn đạt của đáp án. Chỉ coi khác "
        "phương pháp là bất lợi khi câu hỏi nguồn bắt buộc đúng phương "
        "pháp đó. Nếu đáp án chuyên môn không đủ để phân xử khác biệt thì "
        "chọn Tie thay vì dùng kiến thức ngoài input để suy đoán."
    ),
    "positive_anchor": (
        "Nội dung đúng với điểm quyết định trong đáp án chuyên môn; có "
        "thể diễn đạt khác hoặc bổ sung thông tin không mâu thuẫn."
    ),
    "near_miss_anchor": (
        "Cơ bản phù hợp đáp án chuyên môn nhưng thiếu một chi tiết hữu "
        "ích, không làm đổi bản chất hoặc dẫn học sinh sai."
    ),
    "negative_anchor": (
        "Mâu thuẫn với đáp án chuyên môn ở khái niệm, quy trình, mã lệnh "
        "hoặc kết quả theo cách có thể khiến học sinh học hay làm sai."
    ),
}
GOLD_ANSWER_ONLY_CRITERION_NAME_ALIASES = {
    # Gemini occasionally inserts the semantically neutral word "độ".
    "Mức độ chi tiết và cách diễn đạt phù hợp người học": (
        "Mức chi tiết và cách diễn đạt phù hợp người học"
    ),
    # Observed copy-only deviations in the full Gemini batch. These aliases
    # preserve fail-closed validation for unrelated or ambiguous names.
    "Mức hỗ trợ vừa đủ và bảo toàn phần việc có ý nghĩa for học sinh": (
        "Mức hỗ trợ vừa đủ và bảo toàn phần việc có ý nghĩa cho học sinh"
    ),
    "Mẫu hỗ trợ chuyển giao thay việc làm thay": (
        "Mẫu hỗ trợ chuyển giao thay vì làm thay"
    ),
    "Phần biệt phần đúng, điểm cần cải thiện và ý nghĩa của chúng": (
        "Phân biệt phần đúng, điểm cần cải thiện và ý nghĩa của chúng"
    ),
}


@dataclass(frozen=True)
class PreparedJudgeRequest:
    comparison_id: str
    benchmark_candidate_id: str
    target_run_id: str
    target_response_id: str
    target_model_id: str
    required_principle_ids: tuple[str, ...]
    applicable_rubric_ids: tuple[str, ...]
    rubric_name_to_id: tuple[tuple[str, str], ...]
    error_name_to_id: tuple[tuple[str, str], ...]
    error_name_to_affected_rubric_ids: tuple[
        tuple[str, tuple[str, ...]], ...
    ]
    learning_evidence_fragment_ids: tuple[str, ...]
    response_1_source: str
    response_2_source: str
    system_prompt: str
    system_prompt_version: str
    system_prompt_sha256: str
    user_prompt: str
    request_sha256: str
    judge_output_contract_version: str = "v2"
    include_serious_errors: bool = True
    include_learning_evidence: bool = True

    def trace_fields(self) -> dict[str, Any]:
        return {
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "system_prompt_version": self.system_prompt_version,
            "system_prompt_sha256": self.system_prompt_sha256,
            "request_sha256": self.request_sha256,
            "judge_output_contract_version": (
                self.judge_output_contract_version
            ),
            "required_principle_ids": list(self.required_principle_ids),
            "applicable_rubric_ids": list(self.applicable_rubric_ids),
            "rubric_name_id_map": dict(self.rubric_name_to_id),
            "error_name_id_map": dict(self.error_name_to_id),
            "error_name_affected_rubric_id_map": {
                name: list(rubric_ids)
                for name, rubric_ids in (
                    self.error_name_to_affected_rubric_ids
                )
            },
            "learning_evidence_fragment_ids": list(
                self.learning_evidence_fragment_ids
            ),
            "learning_evidence_included": self.include_learning_evidence,
            "blind_pair_order": {
                "response_1": self.response_1_source,
                "response_2": self.response_2_source,
            },
        }


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise JudgePreparationError(
                f"{path}:{number}: invalid JSON"
            ) from exc
        if not isinstance(value, dict):
            raise JudgePreparationError(f"{path}:{number}: object required")
        rows.append(value)
    return rows


def _index(rows, key: str, source: Path):
    result = {}
    for row in rows:
        value = str(row.get(key) or "").strip()
        if not value or value in result:
            raise JudgePreparationError(
                f"{source}: missing or duplicate {key}={value!r}"
            )
        result[value] = row
    return result


def _json_array(value: str, *, field: str, identity: str) -> list[Any]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise JudgePreparationError(
            f"{identity}: invalid JSON in {field}"
        ) from exc
    if not isinstance(parsed, list):
        raise JudgePreparationError(f"{identity}: {field} must be a list")
    return parsed


def _version(path: Path) -> str:
    value = path.stem.rsplit("_", 1)[-1]
    if not value.startswith("v") or not value[1:].isdigit():
        raise JudgePreparationError("prompt filename must end in _vN")
    return value


def _target_first(seed: int, comparison_id: str) -> bool:
    digest = hashlib.sha256(
        f"{seed}:{comparison_id}".encode("utf-8")
    ).digest()
    return digest[0] % 2 == 0


def _evidence(sample_id, conversions, fragments):
    source = conversions.get(sample_id)
    if source is None:
        raise JudgePreparationError(
            f"{sample_id}: conversion provenance missing"
        )
    ids = _json_array(
        source["raw_audit_all_evidence_fragment_ids"],
        field="raw_audit_all_evidence_fragment_ids",
        identity=sample_id,
    )
    ids = [str(value) for value in ids if str(value).startswith("LM-")]
    if not ids:
        raise JudgePreparationError(f"{sample_id}: no SGK/SGV fragment")
    result = []
    for fragment_id in ids:
        row = fragments.get(fragment_id)
        if row is None:
            raise JudgePreparationError(f"missing fragment {fragment_id}")
        text = str(
            row.get("markdown_text") or row.get("text_preview") or ""
        ).strip()
        book_title = str(row.get("book_title") or "").strip()
        lesson_title = str(row.get("lesson_title") or "").strip()
        if not text:
            raise JudgePreparationError(f"empty fragment {fragment_id}")
        if not book_title or not lesson_title:
            raise JudgePreparationError(
                f"{fragment_id}: book_title and lesson_title are required"
            )
        result.append(
            {
                "fragment_id": fragment_id,
                "book_title": book_title,
                "lesson_title": lesson_title,
                "content": text,
            }
        )
    return result


def _replace_internal_ids(
    text: str,
    *,
    rubric_names_by_id: Mapping[str, str],
    error_names_by_id: Mapping[str, str],
) -> str:
    replacements = {**rubric_names_by_id, **error_names_by_id}
    result = text
    for identifier in sorted(replacements, key=len, reverse=True):
        result = result.replace(identifier, replacements[identifier])
    result = result.replace(
        "affected_rubric_ids", "các tiêu chí bị ảnh hưởng"
    )
    result = result.replace("suggested_action", "hành động đề xuất")
    result = result.replace("Error", "Lỗi").replace("error", "lỗi")
    result = result.replace("rubric", "tiêu chí")
    return result


def _rubric(
    row,
    *,
    rubric_names_by_id,
    error_names_by_id,
    use_gold_answer_accuracy: bool = False,
):
    if (
        use_gold_answer_accuracy
        and row["rubric_id"] == "RUB-GEN-ACC"
    ):
        return dict(GOLD_ANSWER_ACCURACY_RUBRIC)
    humanize = lambda value: _replace_internal_ids(
        value,
        rubric_names_by_id=rubric_names_by_id,
        error_names_by_id=error_names_by_id,
    )
    return {
        "criterion_name": row["criterion"],
        "observable_evidence": humanize(row["observable_evidence"]),
        "boundary": humanize(row["boundary"]),
        "positive_anchor": humanize(row["positive_anchor"]),
        "near_miss_anchor": humanize(row["near_miss_anchor"]),
        "negative_anchor": humanize(row["negative_anchor"]),
    }


def _affected_rubric_ids(row, applicable_rubric_ids):
    active = set(applicable_rubric_ids)
    affected = tuple(
        value.strip()
        for value in str(row["affected_rubric_ids"]).split(";")
        if value.strip() in active
    )
    if not affected:
        raise JudgePreparationError(
            f"{row['error_id']}: no affected rubric is active"
        )
    return affected


def _error(
    row,
    *,
    rubric_names_by_id,
    error_names_by_id,
    applicable_rubric_ids,
):
    humanize = lambda value: _replace_internal_ids(
        value,
        rubric_names_by_id=rubric_names_by_id,
        error_names_by_id=error_names_by_id,
    )
    affected_ids = _affected_rubric_ids(row, applicable_rubric_ids)
    return {
        "error_name": error_names_by_id[row["error_id"]],
        "description": humanize(row["description"]),
        "trigger_evidence": humanize(row["trigger_evidence"]),
        "affected_criterion_names": [
            rubric_names_by_id[value] for value in affected_ids
        ],
    }


def _markdown_value(value: Any) -> str:
    text = str(value or "").strip()
    return text if text else "(Không có)"


def _conversation_history(candidate) -> str:
    history = _json_array(
        candidate["conversation_history"],
        field="conversation_history",
        identity=candidate["benchmark_candidate_id"],
    )
    if not history:
        return "(Không có)"
    lines = []
    role_names = {"student": "Học sinh", "tutor": "Gia sư"}
    for index, turn in enumerate(history, 1):
        if not isinstance(turn, dict):
            raise JudgePreparationError(
                f"{candidate['benchmark_candidate_id']}: invalid history turn"
            )
        role = str(turn.get("role") or "").strip()
        content = str(turn.get("content") or "").strip()
        if role not in role_names or not content:
            raise JudgePreparationError(
                f"{candidate['benchmark_candidate_id']}: invalid history turn"
            )
        lines.append(f"{index}. **{role_names[role]}:** {content}")
    return "\n".join(lines)


def _learning_evidence_markdown(learning_evidence) -> str:
    groups: dict[tuple[str, str], list[str]] = {}
    for item in learning_evidence:
        heading = (item["book_title"], item["lesson_title"])
        groups.setdefault(heading, []).append(item["content"])
    sections = []
    for (book_title, lesson_title), contents in groups.items():
        sections.append(
            f"### {book_title} — {lesson_title}\n\n"
            + "\n\n-----\n\n".join(contents)
        )
    return "\n\n".join(sections)


def _rubrics_markdown(applicable_rubrics) -> str:
    sections = []
    for rubric in applicable_rubrics:
        sections.append(
            f"### {rubric['criterion_name']}\n\n"
            f"- **Dấu hiệu cần quan sát:** "
            f"{rubric['observable_evidence']}\n"
            f"- **Ranh giới:** {rubric['boundary']}\n"
            f"- **Mức tốt:** {rubric['positive_anchor']}\n"
            f"- **Trường hợp gần đạt:** "
            f"{rubric['near_miss_anchor']}\n"
            f"- **Mức không đạt:** {rubric['negative_anchor']}"
        )
    return "\n\n".join(sections)


def _errors_markdown(serious_errors) -> str:
    sections = []
    for error in serious_errors:
        names = "; ".join(error["affected_criterion_names"])
        sections.append(
            f"### {error['error_name']}\n\n"
            f"- **Mô tả:** {error['description']}\n"
            f"- **Dấu hiệu kích hoạt:** {error['trigger_evidence']}\n"
            f"- **Các tiêu chí bị ảnh hưởng trong yêu cầu này:** {names}"
        )
    return "\n\n".join(sections)


def build_judge_user_prompt(
    *,
    candidate,
    grounding,
    learning_evidence,
    applicable_rubrics,
    serious_errors,
    response_1,
    response_2,
    include_serious_errors: bool = True,
    include_learning_evidence: bool = True,
) -> str:
    """Build one source-blind Vietnamese Markdown request."""

    evidence_section = ""
    if include_learning_evidence:
        evidence_section = f"""## Căn cứ học liệu

{_learning_evidence_markdown(learning_evidence)}
"""
    error_section = ""
    if include_serious_errors:
        error_section = f"""
## Danh mục lỗi nghiêm trọng

{_errors_markdown(serious_errors)}
"""

    return f"""Hãy chấm mù hai phản hồi dưới đây theo đúng system prompt.
Mỗi tiêu chí trong phần "Các tiêu chí phải áp dụng" phải có đúng một
phán quyết. Không áp dụng tiêu chí nào không xuất hiện trong phần đó.

# Dữ liệu đánh giá

## Bối cảnh học tập

- **Lớp:** {_markdown_value(candidate["grade"])}
- **Bài học:** {_markdown_value(candidate["lesson"])}
- **Mức nhận thức Bloom:** {_markdown_value(candidate["bloom_level"])}

### Câu hỏi nguồn

{_markdown_value(grounding["source_question"])}

### Đáp án chuyên môn

{_markdown_value(candidate["gold_answer"])}

### Lời mở đầu của học sinh

{_markdown_value(candidate["student_prompt"])}

### Lịch sử hội thoại

{_conversation_history(candidate)}

{evidence_section}
## Các tiêu chí phải áp dụng

{_rubrics_markdown(applicable_rubrics)}

{error_section}

## Hai phản hồi

### response_1

{_markdown_value(response_1)}

### response_2

{_markdown_value(response_2)}
"""

def prepare_judge_requests(
    *,
    candidate_csv: Path,
    grounding_pool_csv: Path,
    conversion_input_csv: Path,
    learning_fragments_csv: Path,
    requirement_run_jsonl: Path,
    rubrics_csv: Path,
    serious_errors_csv: Path,
    target_run_jsonls: Sequence[Path],
    system_prompt_path: Path,
    seed: int = 20260728,
    expected_candidates_per_run: int = 10,
    expected_target_run_count: int = 2,
    fixed_candidate_ids: Sequence[str] | None = None,
    judge_output_contract_version: str = "v2",
) -> list[PreparedJudgeRequest]:
    if judge_output_contract_version not in {
        "v2",
        "rubric-only-v3",
        "gold-answer-only-v4",
    }:
        raise JudgePreparationError("unsupported judge output contract")
    include_serious_errors = judge_output_contract_version == "v2"
    include_learning_evidence = (
        judge_output_contract_version != "gold-answer-only-v4"
    )
    use_gold_answer_accuracy = (
        judge_output_contract_version == "gold-answer-only-v4"
    )
    if len(target_run_jsonls) != expected_target_run_count:
        raise JudgePreparationError(
            f"expected exactly {expected_target_run_count} target runs"
        )
    selected_ids = None
    if fixed_candidate_ids is not None:
        selected_ids = tuple(
            str(value).strip() for value in fixed_candidate_ids
        )
        if (
            len(selected_ids) != expected_candidates_per_run
            or any(not value for value in selected_ids)
            or len(set(selected_ids)) != len(selected_ids)
        ):
            raise JudgePreparationError(
                "fixed candidate IDs must be non-empty, unique, and match "
                "expected_candidates_per_run"
            )
    candidates = _index(
        _read_csv(candidate_csv), "benchmark_candidate_id", candidate_csv
    )
    grounding = _index(
        _read_csv(grounding_pool_csv),
        "benchmark_candidate_id",
        grounding_pool_csv,
    )
    conversions = {}
    fragments = {}
    if include_learning_evidence:
        conversions = _index(
            _read_csv(conversion_input_csv),
            "sample_id",
            conversion_input_csv,
        )
        fragments = _index(
            _read_csv(learning_fragments_csv),
            "fragment_id",
            learning_fragments_csv,
        )
    required_sets = load_required_principle_sets(requirement_run_jsonl)
    rubrics = _read_csv(rubrics_csv)
    rubric_by_id = _index(rubrics, "rubric_id", rubrics_csv)
    rubric_names_by_id = {
        row["rubric_id"]: row["criterion"] for row in rubrics
    }
    if use_gold_answer_accuracy:
        rubric_names_by_id["RUB-GEN-ACC"] = (
            GOLD_ANSWER_ACCURACY_RUBRIC["criterion_name"]
        )
    if len(set(rubric_names_by_id.values())) != len(rubric_names_by_id):
        raise JudgePreparationError("rubric criterion names must be unique")
    errors = (
        _read_csv(serious_errors_csv) if include_serious_errors else []
    )
    error_by_id = (
        _index(errors, "error_id", serious_errors_csv)
        if include_serious_errors
        else {}
    )
    if include_serious_errors and set(error_by_id) != set(
        SERIOUS_ERROR_NAMES
    ):
        raise JudgePreparationError(
            "serious-error catalog does not match display-name registry"
        )
    error_name_to_id = tuple(
        (SERIOUS_ERROR_NAMES[row["error_id"]], row["error_id"])
        for row in errors
    )
    system = system_prompt_path.read_text(encoding="utf-8").strip()
    if not system:
        raise JudgePreparationError("empty system prompt")
    system_hash = hashlib.sha256(system.encode("utf-8")).hexdigest()

    runs = []
    common_ids = None
    for path in target_run_jsonls:
        rows = _read_jsonl(path)
        indexed = _index(rows, "benchmark_candidate_id", path)
        if selected_ids is not None:
            missing = [value for value in selected_ids if value not in indexed]
            if missing:
                raise JudgePreparationError(
                    f"{path}: missing fixed candidate IDs {missing}"
                )
            rows = [indexed[value] for value in selected_ids]
            indexed = _index(rows, "benchmark_candidate_id", path)
        if len(rows) != expected_candidates_per_run:
            raise JudgePreparationError(
                f"{path}: expected {expected_candidates_per_run} records"
            )
        ids = set(indexed)
        if common_ids is None:
            common_ids = ids
        elif ids != common_ids:
            raise JudgePreparationError("target candidate sets differ")
        runs.append((path, rows))

    prepared = []
    for path, rows in runs:
        run_id = path.parent.name
        for target in rows:
            candidate_id = str(target["benchmark_candidate_id"])
            candidate = candidates.get(candidate_id)
            ground = grounding.get(candidate_id)
            if candidate is None or ground is None:
                raise JudgePreparationError(f"{candidate_id}: join failed")
            for field in (
                "sample_id",
                "grade",
                "lesson",
                "position",
                "bloom_level",
                "student_prompt",
                "conversation_history",
                "gold_answer",
            ):
                if candidate[field] != ground[field]:
                    raise JudgePreparationError(
                        f"{candidate_id}: mismatch in {field}"
                    )
            if target.get("response_status") != "completed":
                raise JudgePreparationError(
                    f"{candidate_id}: target is not completed"
                )
            target_text = str(target.get("response_text") or "").strip()
            reference_text = str(candidate.get("gold_response") or "").strip()
            if not target_text or not reference_text:
                raise JudgePreparationError(f"{candidate_id}: empty response")
            required = required_sets.get(candidate_id)
            if not required or not set(required) <= set(PRINCIPLE_ORDER):
                raise JudgePreparationError(
                    f"{candidate_id}: invalid required principles"
                )
            if tuple(target.get("required_principle_ids", [])) != required:
                raise JudgePreparationError(
                    f"{candidate_id}: required principle mismatch"
                )
            rubric_ids = select_applicable_rubric_ids(rubrics, required)
            comparison_id = f"JUDGE-{run_id}-{candidate_id}"
            first = _target_first(seed, comparison_id)
            response_1 = target_text if first else reference_text
            response_2 = reference_text if first else target_text
            evidence = (
                _evidence(candidate["sample_id"], conversions, fragments)
                if include_learning_evidence
                else []
            )
            error_affected = tuple(
                (
                    SERIOUS_ERROR_NAMES[row["error_id"]],
                    _affected_rubric_ids(row, rubric_ids),
                )
                for row in errors
            )
            user = build_judge_user_prompt(
                candidate=candidate,
                grounding=ground,
                learning_evidence=evidence,
                applicable_rubrics=[
                    _rubric(
                        rubric_by_id[value],
                        rubric_names_by_id=rubric_names_by_id,
                        error_names_by_id=SERIOUS_ERROR_NAMES,
                        use_gold_answer_accuracy=use_gold_answer_accuracy,
                    )
                    for value in rubric_ids
                ],
                serious_errors=[
                    _error(
                        row,
                        rubric_names_by_id=rubric_names_by_id,
                        error_names_by_id=SERIOUS_ERROR_NAMES,
                        applicable_rubric_ids=rubric_ids,
                    )
                    for row in errors
                ],
                response_1=response_1,
                response_2=response_2,
                include_serious_errors=include_serious_errors,
                include_learning_evidence=include_learning_evidence,
            )
            request_hash = hashlib.sha256(
                json.dumps(
                    {"system_prompt": system, "user_prompt": user},
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            prepared.append(
                PreparedJudgeRequest(
                    comparison_id=comparison_id,
                    benchmark_candidate_id=candidate_id,
                    target_run_id=run_id,
                    target_response_id=str(
                        target.get("response_id") or ""
                    ),
                    target_model_id=str(target.get("model_id") or ""),
                    required_principle_ids=required,
                    applicable_rubric_ids=rubric_ids,
                    rubric_name_to_id=tuple(
                        (rubric_names_by_id[value], value)
                        for value in rubric_ids
                    ),
                    error_name_to_id=error_name_to_id,
                    error_name_to_affected_rubric_ids=error_affected,
                    learning_evidence_fragment_ids=tuple(
                        item["fragment_id"] for item in evidence
                    ),
                    response_1_source="target" if first else "reference",
                    response_2_source="reference" if first else "target",
                    system_prompt=system,
                    system_prompt_version=_version(system_prompt_path),
                    system_prompt_sha256=system_hash,
                    user_prompt=user,
                    request_sha256=request_hash,
                    judge_output_contract_version=(
                        judge_output_contract_version
                    ),
                    include_serious_errors=include_serious_errors,
                    include_learning_evidence=include_learning_evidence,
                )
            )
    expected = expected_target_run_count * expected_candidates_per_run
    if len(prepared) != expected:
        raise JudgePreparationError(
            f"expected {expected} comparisons, found {len(prepared)}"
        )
    if len({row.comparison_id for row in prepared}) != expected:
        raise JudgePreparationError("duplicate comparison IDs")
    return prepared


def _json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        stripped = "\n".join(lines[1:-1]).strip()
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise JudgeOutputError("judge response is not valid JSON") from exc
    if not isinstance(value, dict):
        raise JudgeOutputError("judge response must be an object")
    return value


def _confidence(value, identity):
    if isinstance(value, bool):
        raise JudgeOutputError(f"{identity}: invalid confidence")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise JudgeOutputError(f"{identity}: invalid confidence") from exc
    if not 0 <= result <= 1:
        raise JudgeOutputError(f"{identity}: confidence outside [0,1]")
    return result


def _text(value, identity):
    if not isinstance(value, str) or not value.strip():
        raise JudgeOutputError(f"{identity}: non-empty text required")
    return value.strip()


def validate_judge_output(
    text: str,
    *,
    rubric_name_to_id: Mapping[str, str],
    error_name_to_id: Mapping[str, str],
    error_name_to_affected_rubric_ids: Mapping[str, Sequence[str]],
    include_serious_errors: bool = True,
    criterion_name_aliases: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    value = _json_object(text)
    expected_top_level = {
        "criterion_judgments",
        "overall_judgment",
    }
    if include_serious_errors:
        expected_top_level.add("serious_error_findings")
    if set(value) != expected_top_level:
        raise JudgeOutputError("invalid top-level fields")
    criteria = value["criterion_judgments"]
    if not isinstance(criteria, list):
        raise JudgeOutputError("criterion_judgments must be a list")
    expected_fields = {
        "criterion_name",
        "winner",
        "confidence",
        "rationale",
        "response_1_evidence",
        "response_2_evidence",
    }
    normalized = []
    seen_names = set()
    for index, item in enumerate(criteria):
        identity = f"criterion[{index}]"
        if not isinstance(item, dict) or set(item) != expected_fields:
            raise JudgeOutputError(f"{identity}: invalid fields")
        raw_name = str(item["criterion_name"]).strip()
        name = (criterion_name_aliases or {}).get(raw_name, raw_name)
        rubric_id = rubric_name_to_id.get(name)
        if rubric_id is None:
            raise JudgeOutputError(f"{identity}: unknown criterion name")
        if name in seen_names:
            raise JudgeOutputError(f"duplicate criterion name {name}")
        seen_names.add(name)
        winner = str(item["winner"])
        if winner not in BLIND_WINNERS:
            raise JudgeOutputError(f"{identity}: invalid winner")
        normalized.append(
            {
                "criterion_name": name,
                "rubric_id": rubric_id,
                "winner": winner,
                "confidence": _confidence(item["confidence"], identity),
                "rationale": _text(item["rationale"], identity),
                "response_1_evidence": _text(
                    item["response_1_evidence"], identity
                ),
                "response_2_evidence": _text(
                    item["response_2_evidence"], identity
                ),
            }
        )
    if seen_names != set(rubric_name_to_id):
        raise JudgeOutputError("criterion-name coverage mismatch")

    findings = value.get("serious_error_findings", [])
    if not isinstance(findings, list):
        raise JudgeOutputError("serious_error_findings must be a list")
    normalized_findings = []
    seen_errors = set()
    side_fields = {"detected", "confidence", "rationale"}
    for index, item in enumerate(findings):
        identity = f"finding[{index}]"
        if not isinstance(item, dict) or set(item) != {
            "error_name",
            "response_1",
            "response_2",
        }:
            raise JudgeOutputError(f"{identity}: invalid fields")
        name = str(item["error_name"]).strip()
        error_id = error_name_to_id.get(name)
        affected_ids = error_name_to_affected_rubric_ids.get(name)
        if error_id is None or affected_ids is None:
            raise JudgeOutputError(f"{identity}: unknown error name")
        if name in seen_errors:
            raise JudgeOutputError(f"{identity}: duplicate error name")
        seen_errors.add(name)
        sides = {}
        for side in ("response_1", "response_2"):
            side_value = item[side]
            if not isinstance(side_value, dict) or set(side_value) != side_fields:
                raise JudgeOutputError(f"{identity}.{side}: invalid fields")
            detected = side_value["detected"]
            if not isinstance(detected, bool):
                raise JudgeOutputError(
                    f"{identity}.{side}: detected must be boolean"
                )
            sides[side] = {
                "detected": detected,
                "confidence": _confidence(
                    side_value["confidence"], f"{identity}.{side}"
                ),
                "rationale": _text(
                    side_value["rationale"], f"{identity}.{side}"
                ),
            }
        if not (
            sides["response_1"]["detected"]
            or sides["response_2"]["detected"]
        ):
            raise JudgeOutputError(
                f"{identity}: omit findings where both responses are false"
            )
        normalized_findings.append(
            {
                "error_name": name,
                "error_id": error_id,
                "affected_rubric_ids": list(affected_ids),
                **sides,
            }
        )
    overall = value["overall_judgment"]
    if not isinstance(overall, dict) or set(overall) != {
        "winner",
        "confidence",
        "rationale",
    }:
        raise JudgeOutputError("invalid overall_judgment")
    winner = str(overall["winner"])
    if winner not in BLIND_WINNERS:
        raise JudgeOutputError("invalid overall winner")
    return {
        "criterion_judgments": normalized,
        "serious_error_findings": normalized_findings,
        "overall_judgment": {
            "winner": winner,
            "confidence": _confidence(overall["confidence"], "overall"),
            "rationale": _text(overall["rationale"], "overall"),
        },
    }


def _target_judgment(winner, first_source, second_source):
    if winner == "tie":
        return "Tie"
    source = first_source if winner == "response_1" else second_source
    return "Win" if source == "target" else "Lose"


def postprocess_judge_output(
    normalized,
    *,
    response_1_source: str,
    response_2_source: str,
) -> dict[str, Any]:
    if {response_1_source, response_2_source} != {"target", "reference"}:
        raise JudgeOutputError("invalid blind order")

    raw_criteria = []
    for item in normalized["criterion_judgments"]:
        converted = dict(item)
        converted["target_judgment"] = _target_judgment(
            item["winner"], response_1_source, response_2_source
        )
        raw_criteria.append(converted)

    findings = []
    for item in normalized["serious_error_findings"]:
        converted = dict(item)
        converted["detected_sources"] = [
            source
            for side, source in (
                ("response_1", response_1_source),
                ("response_2", response_2_source),
            )
            if item[side]["detected"]
        ]
        converted["target_detected"] = "target" in converted[
            "detected_sources"
        ]
        converted["reference_detected"] = "reference" in converted[
            "detected_sources"
        ]
        findings.append(converted)

    forced_by_rubric: dict[str, dict[str, Any]] = {}
    for finding in findings:
        if finding["target_detected"]:
            forced = "Lose"
        elif finding["reference_detected"]:
            forced = "Win"
        else:
            continue
        for rubric_id in finding["affected_rubric_ids"]:
            entry = forced_by_rubric.setdefault(
                rubric_id,
                {"forced": forced, "errors": []},
            )
            if forced == "Lose":
                entry["forced"] = "Lose"
            entry["errors"].append(
                {
                    "error_id": finding["error_id"],
                    "error_name": finding["error_name"],
                    "target_detected": finding["target_detected"],
                    "reference_detected": finding["reference_detected"],
                }
            )

    adjusted_criteria = []
    adjustments = []
    for raw in raw_criteria:
        adjusted = dict(raw)
        gate = forced_by_rubric.get(raw["rubric_id"])
        if gate is not None:
            before = raw["target_judgment"]
            after = gate["forced"]
            adjusted["target_judgment"] = after
            adjustments.append(
                {
                    "rubric_id": raw["rubric_id"],
                    "criterion_name": raw["criterion_name"],
                    "raw_target_judgment": before,
                    "adjusted_target_judgment": after,
                    "changed": before != after,
                    "serious_errors": gate["errors"],
                }
            )
        adjusted_criteria.append(adjusted)

    overall = dict(normalized["overall_judgment"])
    overall["target_judgment"] = _target_judgment(
        overall["winner"], response_1_source, response_2_source
    )
    return {
        "raw_criterion_judgments": raw_criteria,
        "serious_error_findings": findings,
        "adjusted_criterion_judgments": adjusted_criteria,
        "criterion_adjustments": adjustments,
        "overall_judgment": overall,
    }
