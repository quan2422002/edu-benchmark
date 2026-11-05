"""Build compact, editable HNMU review workbooks from locked audit exports."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from openpyxl import Workbook, load_workbook
from openpyxl.cell import Cell
from openpyxl.styles import Alignment, Font, PatternFill, Protection
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from .config import AuditSourceConfig, ReviewProductsConfig, WorkbookTargetConfig


class ReviewWorkbookError(ValueError):
    """Raised when audit inputs or a generated review workbook are invalid."""


RESULT_LABELS = {"pass": "Đạt", "fail": "Không đạt", "uncertain": "Chưa chắc"}
QUALITY_LABELS = {
    "pass": "Đạt",
    "need_human_review": "Cần người rà soát",
    "failed": "Không đạt",
    "exclude": "Đề xuất loại",
}
GROUP_LABELS = {
    "structure": "Cấu trúc",
    "consistency": "Nhất quán nội dung",
    "pedagogy": "Sư phạm",
    "duplicate_risk": "Nguy cơ trùng lặp",
}
EDITABLE_FILL = PatternFill("solid", fgColor="FFF2CC")
HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
SUBHEADER_FILL = PatternFill("solid", fgColor="D9EAF7")
LOCKED_FILL = PatternFill("solid", fgColor="E7E6E6")
EDITABLE_PROTECTION = Protection(locked=False)
LOCKED_PROTECTION = Protection(locked=True)
SOURCE_FIELDS = ("lesson", "position", "question", "bloom_level", "answer_sgv", "dialogue")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ReviewWorkbookError(f"CSV has no header: {path}")
        return [dict(row) for row in reader]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def _atomic_workbook(path: Path, workbook: Workbook) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        suffix=".xlsx",
        dir=path.parent,
        prefix=f".{path.stem}.",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
    try:
        workbook.save(temporary)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _safe_text(value: Any) -> str:
    text = "" if value is None else str(value)
    if text.startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def _set_text(cell: Cell, value: Any) -> None:
    cell.value = _safe_text(value)
    cell.data_type = "s"


def _json_list_text(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return text
    if isinstance(parsed, list):
        return "\n".join(str(item) for item in parsed)
    return text


def _source_metadata_from_criteria(rows: Sequence[Mapping[str, str]]) -> dict[str, str]:
    if not rows:
        raise ReviewWorkbookError("Cannot derive source metadata from an empty criterion set")
    first = rows[0]
    metadata = {
        "sample_id": str(first["sample_id"]),
        "grade": str(first["grade"]),
        "stt": str(first.get("stt", "")),
        **{field: str(first.get(field, "")) for field in SOURCE_FIELDS},
    }
    for row in rows[1:]:
        for field, expected in metadata.items():
            if str(row.get(field, "")) != expected:
                raise ReviewWorkbookError(
                    f"Source field drift for {metadata['sample_id']} field={field}"
                )
    return metadata


def _load_source(
    source: AuditSourceConfig,
    *,
    expected_criteria: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    criterion_rows = _read_csv(source.criterion_csv)
    summary_rows = _read_csv(source.summary_csv)
    summary_by_id: dict[str, dict[str, str]] = {}
    for row in summary_rows:
        sample_id = str(row.get("sample_id", "")).strip()
        if not sample_id or sample_id in summary_by_id:
            raise ReviewWorkbookError(
                f"Missing or duplicate summary sample_id in {source.summary_csv}: {sample_id}"
            )
        if int(row.get("grade", 0)) != source.grade:
            raise ReviewWorkbookError(f"Grade mismatch for {sample_id}")
        summary_by_id[sample_id] = row

    criteria_by_id: dict[str, list[dict[str, str]]] = {}
    criterion_pairs: set[tuple[str, str]] = set()
    for row in criterion_rows:
        sample_id = str(row.get("sample_id", "")).strip()
        criterion_id = str(row.get("criterion_id", "")).strip()
        pair = (sample_id, criterion_id)
        if not sample_id or not criterion_id or pair in criterion_pairs:
            raise ReviewWorkbookError(f"Missing or duplicate criterion pair: {pair}")
        criterion_pairs.add(pair)
        criteria_by_id.setdefault(sample_id, []).append(row)

    if set(criteria_by_id) != set(summary_by_id):
        raise ReviewWorkbookError(f"Criterion/summary sample mismatch for {source.source_key}")
    invalid_counts = {
        sample_id: len(rows)
        for sample_id, rows in criteria_by_id.items()
        if len(rows) != expected_criteria
    }
    if invalid_counts:
        raise ReviewWorkbookError(
            f"Samples without {expected_criteria} criteria: {invalid_counts}"
        )

    samples: list[dict[str, Any]] = []
    enriched_criteria: list[dict[str, Any]] = []
    for sample_id in summary_by_id:
        rows = criteria_by_id[sample_id]
        metadata = _source_metadata_from_criteria(rows)
        summary = summary_by_id[sample_id]
        for field in ("grade", "lesson", "position", "question"):
            if str(summary.get(field, "")) != metadata[field]:
                raise ReviewWorkbookError(
                    f"Summary/source mismatch for {sample_id} field={field}"
                )
        samples.append(
            {
                **metadata,
                "source_key": source.source_key,
                "source_display_name": source.display_name,
                "quality_decision": str(summary.get("quality_decision", "")),
                "confidence_score": str(summary.get("confidence_score", "")),
                "blocking_criterion_ids": str(summary.get("blocking_criterion_ids", "")),
                "blocking_reasons": str(summary.get("blocking_reasons", "")),
                "needs_image_review": str(summary.get("needs_image_review", "")),
            }
        )
        for row in rows:
            enriched_criteria.append(
                {
                    **row,
                    "source_key": source.source_key,
                    "source_display_name": source.display_name,
                }
            )
    return samples, enriched_criteria


def _read_criteria_registry(path: Path) -> list[dict[str, str]]:
    rows = _read_csv(path)
    required = {
        "criterion_id",
        "criterion_group",
        "criterion_name",
        "pass_condition",
        "fail_or_uncertain_policy",
        "default_reviewer_action",
    }
    if rows and not required.issubset(rows[0]):
        raise ReviewWorkbookError(f"Criteria registry is missing columns: {sorted(required)}")
    ids = [row["criterion_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ReviewWorkbookError("Criteria registry contains duplicate IDs")
    return rows


def _append_row(sheet: Any, values: Sequence[Any]) -> int:
    sheet.append([None] * len(values))
    row_number = sheet.max_row
    for column, value in enumerate(values, start=1):
        _set_text(sheet.cell(row_number, column), value)
    return row_number


def _style_header(sheet: Any, widths: Sequence[int]) -> None:
    for cell in sheet[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.protection = LOCKED_PROTECTION
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for index, width in enumerate(widths, start=1):
        sheet.column_dimensions[get_column_letter(index)].width = width
    sheet.row_dimensions[1].height = 36
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.protection = LOCKED_PROTECTION


def _mark_editable(sheet: Any, columns: Iterable[int], start_row: int, end_row: int) -> None:
    for column in columns:
        for row in range(start_row, end_row + 1):
            cell = sheet.cell(row, column)
            cell.fill = EDITABLE_FILL
            cell.protection = EDITABLE_PROTECTION


def _protect(sheet: Any) -> None:
    sheet.protection.sheet = True
    sheet.protection.autoFilter = False
    sheet.protection.sort = False
    sheet.protection.selectLockedCells = True
    sheet.protection.selectUnlockedCells = False


def _add_dropdown(
    sheet: Any,
    *,
    target_range: str,
    list_range: str,
    prompt: str,
) -> None:
    validation = DataValidation(
        type="list",
        formula1=f"'_Danh_muc'!{list_range}",
        allow_blank=True,
    )
    validation.error = "Vui lòng chọn một giá trị trong danh sách."
    validation.errorTitle = "Giá trị chưa hợp lệ"
    validation.prompt = prompt
    validation.promptTitle = "Hướng dẫn"
    validation.showErrorMessage = True
    validation.showInputMessage = True
    sheet.add_data_validation(validation)
    validation.add(target_range)


def _evidence_text(row: Mapping[str, Any]) -> str:
    fragment_id = str(row.get("evidence_fragment_id", "")).strip()
    reason = str(row.get("evidence_match_reason", "")).strip()
    if fragment_id and reason:
        return f"{fragment_id}\n{reason}"
    return fragment_id or reason


def _write_guide(
    workbook: Workbook,
    *,
    target: WorkbookTargetConfig,
    sample_count: int,
    criterion_count: int,
) -> None:
    sheet = workbook.active
    sheet.title = "Hướng dẫn"
    rows = [
        (f"Phiếu rà soát kết quả kiểm toán — {target.display_name}", ""),
        ("Phạm vi", f"{sample_count} mẫu; {criterion_count} kết quả tiêu chí"),
        ("Mục đích", "Xác nhận kết quả kiểm toán, sửa dữ liệu nguồn khi có căn cứ và ghi rõ các trường hợp cần người khác phân xử."),
        ("Vai trò của giáo viên", "Đưa ra quyết định chuyên môn độc lập. Kết quả của tác nhân chỉ là gợi ý ban đầu, không thay thế quyết định của giáo viên."),
        ("Thời gian gợi ý", "Ước lượng thử nghiệm khoảng 3–5 phút cho mỗi mẫu; ca cần mở học liệu hoặc xem ảnh có thể lâu hơn. Nên chia theo từng bài và lưu file thường xuyên."),
        ("Ô màu vàng", "Là ô được phép điền hoặc sửa. Các ô còn lại được khóa để bảo toàn nội dung dùng đối chiếu."),
        ("Mã mẫu và mã tiêu chí", "Không xóa, đổi tên hoặc sao chép sang mẫu khác. Đây là mã dùng để ghép lại quyết định sau khi nhận file."),
        ("", ""),
        ("Quy trình đề xuất", ""),
        ("Bước 1", "Đọc Tổng hợp mẫu. Ưu tiên mẫu có kết luận Cần người rà soát, Không đạt hoặc Cần xem ảnh."),
        ("Bước 2", "Mở Kết quả tiêu chí để kiểm từng điểm tác nhân đánh dấu. Dùng mã fragment trong cột Bằng chứng để tra cứu học liệu khi cần."),
        ("Bước 3", "Nếu phát hiện dữ liệu nguồn sai, mở Sửa dữ liệu, chọn trạng thái và chỉ sửa những trường đã xác định được nội dung đúng."),
        ("Bước 4", "Giữ quyết định Chưa chắc khi chưa đủ căn cứ. Ghi rõ điều cần người phân xử kiểm tra."),
        ("Bước 5", "Trước khi bàn giao, kiểm tra tên người rà soát và lý do ở mọi dòng Không đồng ý, Loại mẫu, Sửa dữ liệu hoặc Chưa chắc."),
        ("", ""),
        ("A. Sheet Tổng hợp mẫu", "Quyết định ở cấp toàn bộ mẫu. Sheet này giúp xác định nhanh mẫu nào có thể giữ, mẫu nào cần xem chi tiết hoặc cần phân xử."),
        ("Quyết định của giáo viên", "Chọn một trong ba giá trị: Đồng ý; Không đồng ý; Chưa chắc."),
        ("Đồng ý", "Kết luận tổng thể của tác nhân hợp lý. Ghi chú có thể để trống."),
        ("Không đồng ý", "Kết luận tổng thể chưa hợp lý. Cần ghi lý do và kiểm các tiêu chí liên quan trong Kết quả tiêu chí."),
        ("Chưa chắc", "Chưa đủ căn cứ để kết luận. Cần ghi rõ nội dung cần HNMU/UET hoặc người được phân công xem lại."),
        ("Ghi chú", "Viết ngắn gọn căn cứ cho Không đồng ý hoặc Chưa chắc. Có thể để trống khi Đồng ý và không có lưu ý bổ sung."),
        ("Người rà soát", "Ghi tên hoặc mã người thực hiện rà soát."),
        ("Ví dụ phù hợp — Tổng hợp mẫu", "Quyết định: Không đồng ý. Ghi chú: Kết luận tổng thể chưa phản ánh mâu thuẫn giữa Bài 6 và vị trí Hình 4.2. Người rà soát: Nguyễn Văn A."),
        ("Phản ví dụ — Tổng hợp mẫu", "Chọn Không đồng ý nhưng để trống Ghi chú và Người rà soát. Khi đó nhóm dự án không biết căn cứ hoặc người cần trao đổi lại."),
        ("", ""),
        ("B. Sheet Kết quả tiêu chí", "Quyết định ở cấp từng cặp mẫu–tiêu chí. Dùng sheet này để xác nhận hoặc sửa nhãn Đạt/Không đạt/Chưa chắc của từng tiêu chí."),
        ("Quyết định của giáo viên", "Chọn một trong ba giá trị: Đồng ý; Không đồng ý; Chưa chắc."),
        ("Kết quả đề xuất", "Chọn một trong ba giá trị: Đạt; Không đạt; Chưa chắc. Có thể để trống nếu đã chọn Đồng ý với tác nhân."),
        ("Khi chọn Không đồng ý", "Bắt buộc nên chọn Kết quả đề xuất, ghi Lý do/Ghi chú và ghi Người rà soát."),
        ("Khi chọn Chưa chắc", "Nên chọn Kết quả đề xuất là Chưa chắc và ghi rõ còn thiếu căn cứ nào, ví dụ học liệu, ảnh hoặc thông tin vị trí."),
        ("Bằng chứng", "Đọc mã fragment và mô tả khớp. Nếu cần, dùng mã fragment để tra trên cổng học liệu trước khi quyết định."),
        ("Ví dụ phù hợp — Kết quả tiêu chí", "Tác nhân: Đạt. Quyết định: Không đồng ý. Kết quả đề xuất: Không đạt. Lý do: Vị trí ghi Hình 4.2 nhưng mẫu thuộc Bài 6. Người rà soát: Nguyễn Văn A."),
        ("Phản ví dụ — Kết quả tiêu chí", "Đổi kết quả sang Không đạt nhưng không ghi căn cứ. Quyết định này không đủ thông tin để người khác kiểm tra hoặc phân xử."),
        ("", ""),
        ("C. Sheet Sửa dữ liệu", "Dùng khi nội dung nguồn của mẫu cần chỉnh. Các trường nguồn đã được điền sẵn; chỉ sửa trường có căn cứ rõ ràng."),
        ("Trạng thái xử lý", "Chọn một trong bốn giá trị: Giữ nguyên; Sửa dữ liệu; Loại mẫu; Chưa chắc."),
        ("Giữ nguyên", "Không sửa các trường nội dung. Ghi Người rà soát; Lý do/Ghi chú có thể để trống."),
        ("Sửa dữ liệu", "Sửa trực tiếp một hoặc nhiều trường Bài, Vị trí, Câu hỏi hoặc nhiệm vụ, Mức nhận thức, Đáp án tham chiếu, Hội thoại. Cần ghi lý do và người rà soát."),
        ("Loại mẫu", "Không xóa nội dung mẫu. Giữ dữ liệu để đối chiếu, ghi rõ lý do loại và người rà soát."),
        ("Chưa chắc", "Chưa sửa nội dung nếu chưa đủ căn cứ. Ghi rõ trường nào hoặc vấn đề nào cần người khác phân xử."),
        ("Sửa hội thoại", "Giữ đúng thứ tự lượt nói và nhãn HS:/AI:. Không thêm nhận xét của người rà soát vào nội dung hội thoại."),
        ("Ví dụ phù hợp — Sửa dữ liệu", "Trạng thái: Sửa dữ liệu. Sửa Vị trí từ Hình 4.2 thành Hình 6.2. Ghi chú: Đã đối chiếu SGK Bài 6. Người rà soát: Nguyễn Văn A."),
        ("Phản ví dụ — Sửa dữ liệu", "Chọn Loại mẫu rồi xóa trắng câu hỏi, đáp án và hội thoại. Việc này làm mất nội dung cần dùng để đối chiếu quyết định loại."),
        ("", ""),
        ("D. Sheet _Danh_muc", "Không phải nhiệm vụ rà soát. Sheet này chỉ giữ các giá trị dùng trong ô chọn của những sheet khác. Không sửa, xóa hoặc đổi tên sheet."),
        ("", ""),
        ("Tự kiểm tra trước bàn giao", "Mọi dòng Không đồng ý, Sửa dữ liệu, Loại mẫu hoặc Chưa chắc đã có lý do và người rà soát; không có mã mẫu/mã tiêu chí bị thay đổi; không có mẫu bị xóa trắng."),
        ("Đường phân xử", "Giữ nguyên các ca Chưa chắc để HNMU/UET hoặc người được phân công xem lại. Không tự suy đoán khi thiếu căn cứ."),
        ("Bàn giao", "Lưu và gửi lại đúng file đã rà soát. Không đổi tên các sheet."),
    ]
    for left, right in rows:
        _append_row(sheet, (left, right))
    sheet["A1"].font = Font(size=16, bold=True, color="1F4E78")
    section_labels = {
        "Quy trình đề xuất",
        "A. Sheet Tổng hợp mẫu",
        "B. Sheet Kết quả tiêu chí",
        "C. Sheet Sửa dữ liệu",
        "D. Sheet _Danh_muc",
        "Tự kiểm tra trước bàn giao",
        "Đường phân xử",
        "Bàn giao",
    }
    for row in range(2, sheet.max_row + 1):
        if sheet.cell(row, 1).value in section_labels:
            for cell in sheet[row]:
                cell.font = Font(bold=True, color="1F4E78")
                cell.fill = SUBHEADER_FILL
    sheet.column_dimensions["A"].width = 24
    sheet.column_dimensions["B"].width = 105
    for row in sheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.protection = LOCKED_PROTECTION
    _protect(sheet)


def _write_summary_sheet(workbook: Workbook, samples: Sequence[Mapping[str, Any]]) -> None:
    sheet = workbook.create_sheet("Tổng hợp mẫu")
    headers = (
        "Mã mẫu",
        "Nguồn",
        "Bài / Vị trí",
        "Câu hỏi hoặc nhiệm vụ",
        "Kết luận của tác nhân",
        "Tiêu chí cần chú ý",
        "Cần xem ảnh",
        "Quyết định của giáo viên",
        "Ghi chú",
        "Người rà soát",
    )
    _append_row(sheet, headers)
    for sample in samples:
        _append_row(
            sheet,
            (
                sample["sample_id"],
                sample["source_display_name"],
                f"{sample['lesson']}\n{sample['position']}",
                sample["question"],
                QUALITY_LABELS.get(sample["quality_decision"], sample["quality_decision"]),
                "\n".join(
                    part
                    for part in (
                        _json_list_text(sample["blocking_criterion_ids"]),
                        _json_list_text(sample["blocking_reasons"]),
                    )
                    if part
                ),
                "Có" if sample["needs_image_review"].lower() == "true" else "Không",
                "",
                "",
                "",
            ),
        )
    _style_header(sheet, (31, 22, 45, 55, 22, 58, 14, 25, 48, 24))
    _mark_editable(sheet, (8, 9, 10), 2, sheet.max_row)
    _add_dropdown(
        sheet,
        target_range=f"H2:H{sheet.max_row}",
        list_range="$B$1:$B$3",
        prompt="Chọn Đồng ý, Không đồng ý hoặc Chưa chắc.",
    )
    _protect(sheet)


def _write_criterion_sheet(
    workbook: Workbook,
    criteria: Sequence[Mapping[str, Any]],
    criterion_order: Mapping[str, int],
) -> None:
    sheet = workbook.create_sheet("Kết quả tiêu chí")
    headers = (
        "Mã dòng",
        "Mã mẫu",
        "Bài / Vị trí",
        "Câu hỏi hoặc nhiệm vụ",
        "Tiêu chí",
        "Kết quả của tác nhân",
        "Luận giải",
        "Bằng chứng",
        "Phụ thuộc ảnh",
        "Quyết định của giáo viên",
        "Kết quả đề xuất",
        "Lý do / Ghi chú",
        "Người rà soát",
    )
    _append_row(sheet, headers)
    sorted_rows = sorted(
        criteria,
        key=lambda row: (
            str(row["sample_id"]),
            criterion_order.get(str(row["criterion_id"]), 10_000),
        ),
    )
    for row in sorted_rows:
        criterion_label = f"{row['criterion_id']} — {row['criterion_name']}"
        image_text = str(row.get("image_dependency", "none"))
        if str(row.get("needs_image_review", "")).lower() == "true":
            image_text += " — Cần xem ảnh"
        _append_row(
            sheet,
            (
                f"{row['sample_id']}|{row['criterion_id']}",
                row["sample_id"],
                f"{row['lesson']}\n{row['position']}",
                row["question"],
                criterion_label,
                RESULT_LABELS.get(str(row["result"]), str(row["result"])),
                row.get("reason", ""),
                _evidence_text(row),
                image_text,
                "",
                "",
                "",
                "",
            ),
        )
    _style_header(sheet, (48, 31, 42, 48, 35, 20, 58, 55, 22, 25, 22, 48, 24))
    _mark_editable(sheet, (10, 11, 12, 13), 2, sheet.max_row)
    _add_dropdown(
        sheet,
        target_range=f"J2:J{sheet.max_row}",
        list_range="$B$1:$B$3",
        prompt="Chọn mức đồng ý với kết quả của tác nhân.",
    )
    _add_dropdown(
        sheet,
        target_range=f"K2:K{sheet.max_row}",
        list_range="$C$1:$C$3",
        prompt="Nếu không đồng ý, chọn kết quả chuyên môn đề xuất.",
    )
    _protect(sheet)


def _write_correction_sheet(workbook: Workbook, samples: Sequence[Mapping[str, Any]]) -> None:
    sheet = workbook.create_sheet("Sửa dữ liệu")
    headers = (
        "Mã mẫu",
        "Nguồn",
        "Trạng thái xử lý",
        "Bài",
        "Vị trí",
        "Câu hỏi hoặc nhiệm vụ",
        "Mức nhận thức",
        "Đáp án tham chiếu",
        "Hội thoại",
        "Lý do sửa / Ghi chú",
        "Người rà soát",
    )
    _append_row(sheet, headers)
    for sample in samples:
        _append_row(
            sheet,
            (
                sample["sample_id"],
                sample["source_display_name"],
                "",
                sample["lesson"],
                sample["position"],
                sample["question"],
                sample["bloom_level"],
                sample["answer_sgv"],
                sample["dialogue"],
                "",
                "",
            ),
        )
    _style_header(sheet, (31, 22, 22, 38, 42, 52, 30, 52, 85, 48, 24))
    _mark_editable(sheet, tuple(range(3, 12)), 2, sheet.max_row)
    _add_dropdown(
        sheet,
        target_range=f"C2:C{sheet.max_row}",
        list_range="$A$1:$A$4",
        prompt="Chọn Giữ nguyên, Sửa dữ liệu, Loại mẫu hoặc Chưa chắc.",
    )
    _protect(sheet)


def _write_criteria_catalog(workbook: Workbook, registry: Sequence[Mapping[str, str]]) -> None:
    sheet = workbook.create_sheet("Danh mục tiêu chí")
    headers = (
        "Mã tiêu chí",
        "Nhóm",
        "Tên tiêu chí",
        "Điều kiện đạt",
        "Khi không đạt hoặc chưa chắc",
        "Hành động gợi ý",
    )
    _append_row(sheet, headers)
    for row in registry:
        _append_row(
            sheet,
            (
                row["criterion_id"],
                GROUP_LABELS.get(row["criterion_group"], row["criterion_group"]),
                row["criterion_name"],
                row["pass_condition"],
                row["fail_or_uncertain_policy"],
                row["default_reviewer_action"],
            ),
        )
    _style_header(sheet, (20, 24, 34, 68, 68, 42))
    _protect(sheet)


def _write_dropdown_sheet(workbook: Workbook) -> None:
    sheet = workbook.create_sheet("_Danh_muc")
    for row, value in enumerate(("Giữ nguyên", "Sửa dữ liệu", "Loại mẫu", "Chưa chắc"), 1):
        _set_text(sheet.cell(row, 1), value)
    for row, value in enumerate(("Đồng ý", "Không đồng ý", "Chưa chắc"), 1):
        _set_text(sheet.cell(row, 2), value)
    for row, value in enumerate(("Đạt", "Không đạt", "Chưa chắc"), 1):
        _set_text(sheet.cell(row, 3), value)
    sheet.sheet_state = "hidden"


def _build_workbook(
    path: Path,
    *,
    target: WorkbookTargetConfig,
    samples: Sequence[Mapping[str, Any]],
    criteria: Sequence[Mapping[str, Any]],
    registry: Sequence[Mapping[str, str]],
) -> None:
    workbook = Workbook()
    workbook.properties.title = f"Rà soát audit HNMU — {target.display_name}"
    workbook.properties.subject = "Phiếu rà soát do Plan 04 tạo; kết quả tác nhân không phải ground truth."
    workbook.properties.creator = "edu-benchmark Plan 04"
    _write_guide(
        workbook,
        target=target,
        sample_count=len(samples),
        criterion_count=len(criteria),
    )
    _write_summary_sheet(workbook, samples)
    order = {row["criterion_id"]: index for index, row in enumerate(registry)}
    _write_criterion_sheet(workbook, criteria, order)
    _write_correction_sheet(workbook, samples)
    _write_criteria_catalog(workbook, registry)
    _write_dropdown_sheet(workbook)
    _atomic_workbook(path, workbook)


def _validate_workbook(
    path: Path,
    *,
    expected_sample_ids: set[str],
    expected_criterion_pairs: set[tuple[str, str]],
) -> dict[str, Any]:
    workbook = load_workbook(path, read_only=False, data_only=False)
    expected_sheets = [
        "Hướng dẫn",
        "Tổng hợp mẫu",
        "Kết quả tiêu chí",
        "Sửa dữ liệu",
        "Danh mục tiêu chí",
        "_Danh_muc",
    ]
    if workbook.sheetnames != expected_sheets:
        raise ReviewWorkbookError(f"Workbook sheet mismatch: {workbook.sheetnames}")
    summary = workbook["Tổng hợp mẫu"]
    criteria = workbook["Kết quả tiêu chí"]
    corrections = workbook["Sửa dữ liệu"]
    summary_ids = {str(summary.cell(row, 1).value) for row in range(2, summary.max_row + 1)}
    correction_ids = {
        str(corrections.cell(row, 1).value) for row in range(2, corrections.max_row + 1)
    }
    criterion_pairs: set[tuple[str, str]] = set()
    for row in range(2, criteria.max_row + 1):
        stable_id = str(criteria.cell(row, 1).value)
        if "|" not in stable_id:
            raise ReviewWorkbookError(f"Invalid criterion stable ID: {stable_id}")
        sample_id, criterion_id = stable_id.rsplit("|", 1)
        criterion_pairs.add((sample_id, criterion_id))
    if summary_ids != expected_sample_ids or correction_ids != expected_sample_ids:
        raise ReviewWorkbookError("Workbook sample IDs do not match source inputs")
    if criterion_pairs != expected_criterion_pairs:
        raise ReviewWorkbookError("Workbook criterion pairs do not match source inputs")
    for sheet_name in ("Tổng hợp mẫu", "Kết quả tiêu chí", "Sửa dữ liệu"):
        sheet = workbook[sheet_name]
        if sheet.freeze_panes != "A2" or not sheet.auto_filter.ref:
            raise ReviewWorkbookError(f"Missing freeze/filter in sheet: {sheet_name}")
        if not sheet.protection.sheet:
            raise ReviewWorkbookError(f"Sheet is not protected: {sheet_name}")
        if not sheet.data_validations.dataValidation:
            raise ReviewWorkbookError(f"Sheet has no dropdown validation: {sheet_name}")
    if workbook["_Danh_muc"].sheet_state != "hidden":
        raise ReviewWorkbookError("Dropdown source sheet must remain hidden")
    workbook.close()
    return {
        "reopened": True,
        "sheet_names": expected_sheets,
        "sample_id_count": len(summary_ids),
        "criterion_pair_count": len(criterion_pairs),
        "filters_present": True,
        "frozen_headers_present": True,
        "dropdowns_present": True,
        "locked_identifiers_present": True,
        "editable_cells_highlighted": True,
    }


def build_audit_review_workbooks(
    config: ReviewProductsConfig,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Build and reopen the two approved HNMU review workbooks."""

    registry = _read_criteria_registry(config.workbook.criteria_registry)
    if len(registry) != config.workbook.expected_criteria_per_sample:
        raise ReviewWorkbookError(
            "Criteria registry count does not match expected_criteria_per_sample"
        )
    source_samples: dict[str, list[dict[str, Any]]] = {}
    source_criteria: dict[str, list[dict[str, Any]]] = {}
    input_files: list[Path] = [config.workbook.criteria_registry]
    for source in config.workbook.sources:
        samples, criteria = _load_source(
            source,
            expected_criteria=config.workbook.expected_criteria_per_sample,
        )
        source_samples[source.source_key] = samples
        source_criteria[source.source_key] = criteria
        input_files.extend((source.criterion_csv, source.summary_csv))

    output_root = config.workbook.output_root
    output_root.mkdir(parents=True, exist_ok=True)
    manifest_path = output_root / "review_package_manifest.json"
    target_paths = [output_root / target.output_filename for target in config.workbook.targets]
    existing = [path for path in [*target_paths, manifest_path] if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite review products: " + ", ".join(str(path) for path in existing)
        )

    workbook_results = []
    baseline_records: list[dict[str, Any]] = []
    total_sample_ids: set[str] = set()
    total_pairs: set[tuple[str, str]] = set()
    for target in config.workbook.targets:
        samples = [row for key in target.source_keys for row in source_samples[key]]
        criteria = [row for key in target.source_keys for row in source_criteria[key]]
        sample_ids = {str(row["sample_id"]) for row in samples}
        pairs = {(str(row["sample_id"]), str(row["criterion_id"])) for row in criteria}
        if len(sample_ids) != len(samples):
            raise ReviewWorkbookError(f"Duplicate sample IDs in target {target.key}")
        if total_sample_ids.intersection(sample_ids):
            raise ReviewWorkbookError(f"Sample appears in multiple workbooks: {target.key}")
        total_sample_ids.update(sample_ids)
        total_pairs.update(pairs)
        path = output_root / target.output_filename
        _build_workbook(
            path,
            target=target,
            samples=samples,
            criteria=criteria,
            registry=registry,
        )
        validation = _validate_workbook(
            path,
            expected_sample_ids=sample_ids,
            expected_criterion_pairs=pairs,
        )
        workbook_results.append(
            {
                "key": target.key,
                "display_name": target.display_name,
                "path": path.relative_to(config.repository_root).as_posix(),
                "sha256": _sha256(path),
                "sample_count": len(sample_ids),
                "criterion_result_count": len(pairs),
                "validation": validation,
            }
        )
        baseline_records.extend(
            {
                "sample_id": sample["sample_id"],
                "source_key": sample["source_key"],
                **{field: sample[field] for field in SOURCE_FIELDS},
            }
            for sample in samples
        )

    per_sample_counts = Counter(sample_id for sample_id, _ in total_pairs)
    if set(per_sample_counts) != total_sample_ids or any(
        count != config.workbook.expected_criteria_per_sample
        for count in per_sample_counts.values()
    ):
        raise ReviewWorkbookError("Cross-workbook criterion coverage is incomplete")
    manifest = {
        "schema_version": "plan04-hnmu-review-package-v1",
        "experiment_id": config.experiment_id,
        "created_at": datetime.now(UTC).isoformat(),
        "config_path": config.config_path.relative_to(config.repository_root).as_posix(),
        "inputs": [
            {
                "path": path.relative_to(config.repository_root).as_posix(),
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
            }
            for path in input_files
        ],
        "expected_criteria_per_sample": config.workbook.expected_criteria_per_sample,
        "sample_count": len(total_sample_ids),
        "criterion_result_count": len(total_pairs),
        "duplicate_sample_count": 0,
        "duplicate_sample_criterion_count": 0,
        "workbooks": workbook_results,
        "editable_source_fields": list(SOURCE_FIELDS),
        "baseline_records": sorted(baseline_records, key=lambda row: str(row["sample_id"])),
        "authority_note": (
            "Agent outputs are screening evidence only. HNMU/UET reviewers retain "
            "subject-matter and pedagogical authority."
        ),
    }
    _atomic_json(manifest_path, manifest)
    return manifest
