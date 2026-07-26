"""Vietnamese HNMU-facing documentation for the Phase 1 teacher bundle."""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from edu_benchmark.dialogue_audit.fragment_analysis_root_deliverables import (
    root_report_content,
)
from edu_benchmark.dialogue_audit.fragment_analysis_hnmu_compact import (
    GRADE_ANALYSIS_NAME,
    GRADE_APPENDIX_NAME,
    ROOT_ANALYSIS_NAME,
    ROOT_APPENDIX_NAME,
    build_hnmu_summary_rows,
)


def fragment_report_section_hnmu(
    root_rows: Sequence[dict[str, object]],
) -> str:
    summary_rows = build_hnmu_summary_rows(root_rows, pooled=True)
    content = root_report_content(summary_rows)
    return "\n".join(
        [
            "## Fragment đầy đủ hơn có đi kèm tỷ lệ đạt cao hơn không?",
            "",
            "Các mẫu có “Tỷ lệ tiêu chí có dẫn fragment” cao hơn có tỷ lệ đạt chính thức cao hơn không?",
            "",
            content["short_answer"],
            "",
            content["explanation"],
            "",
            content["data_limit"],
            "",
            f"File `{ROOT_ANALYSIS_NAME}` là report dễ hiểu dành cho HNMU. "
            f"File `{ROOT_APPENDIX_NAME}` là bảng chi tiết phục vụ kiểm tra kỹ thuật và vẫn giữ dữ liệu gốc để truy vết.",
        ]
    )


def root_readme_text_hnmu(
    row_counts: dict[str, int],
    duplicates: Sequence[dict[str, str]],
) -> str:
    duplicate_count = len(duplicates)
    within_grade = [
        row for row in duplicates if row.get("duplicate_scope") == "Trong cùng lớp"
    ]
    cross_grade = [
        row for row in duplicates if row.get("duplicate_scope") == "Giữa các lớp"
    ]
    within_grades = sorted({str(row["grade"]) for row in within_grade})
    if len(within_grades) == 1:
        within_scope = f"lớp {within_grades[0]}"
    elif within_grades:
        within_scope = "các lớp " + ", ".join(within_grades)
    else:
        within_scope = "các lớp"
    duplicate_summary = (
        f"Có {len(within_grade)} ứng viên trùng trong {within_scope}. Quy trình "
        "đã kiểm tra cả trùng trong lớp và giữa lớp nhưng "
        + (
            "không phát hiện trường hợp trùng giữa các lớp."
            if not cross_grade
            else f"phát hiện {len(cross_grade)} trường hợp trùng giữa các lớp."
        )
    )
    return f"""# Bộ kết quả rà soát Phase 1 gửi HNMU

Bộ hồ sơ gồm phần tổng hợp ở thư mục này và bốn thư mục riêng `lop_6/`, `lop_7/`, `lop_8/`, `lop_9/`.

## Nên đọc theo thứ tự

1. Đọc `01_bao_cao_tong_quan.md` để xem kết quả chung.
2. Mở `02_checklist_tieu_chi.xlsx` để xem định nghĩa chung của các tiêu chí.
3. Mở `03_thong_ke_pass_reject_giua_cac_khoi.xlsx` và `04_thong_ke_do_phu_mau_pass_giua_cac_khoi.xlsx` để so sánh bốn khối.
4. Đọc `{ROOT_ANALYSIS_NAME}` để xem câu trả lời dễ hiểu dành cho HNMU.
5. Mở `{ROOT_APPENDIX_NAME}` khi cần xem tám kết quả, tỷ lệ đạt theo nhóm hoặc kiểm tra số liệu và phương pháp.
6. Dùng `DANH_MUC_FILE.md` để kiểm tra cây thư mục và mục đích của từng file.
7. Dùng bốn CSV tổng hợp ở root để tra cứu toàn bộ lớp 6–9.

## Bản tóm tắt và phụ lục kỹ thuật

- `{ROOT_ANALYSIS_NAME}`: report Markdown dễ hiểu dành cho HNMU, trả lời trực tiếp câu hỏi về tỷ lệ tiêu chí có dẫn fragment và tỷ lệ đạt chính thức.
- `{ROOT_APPENDIX_NAME}`: workbook chi tiết phục vụ kiểm tra kỹ thuật; sheet 01 có tám kết quả dễ đọc, các sheet tiếp theo tách tỷ lệ theo nhóm, số liệu thống kê, nhóm không đủ điều kiện và từ điển.
- Sheet `99_Du_lieu_ky_thuat_goc` giữ nguyên toàn bộ dữ liệu kỹ thuật cũ để truy vết và kiểm tra tự động.

## Các file tổng hợp

- `06_ket_qua_cham_tong_the_tung_mau.csv`: {row_counts['quality']} mẫu, mỗi mẫu một dòng.
- `07_mau_thieu_sai_truong_du_lieu.csv`: {row_counts['missing']} cảnh báo.
- `08_ung_vien_trung_lap.csv`: {duplicate_count} ứng viên; phạm vi được mô tả ngay dưới.
- `09_du_lieu_tho_sau_chuan_hoa.csv`: {row_counts['normalized']} mẫu chuẩn hóa, mỗi mẫu một dòng.

{duplicate_summary}

File duplicate được tính trên toàn bộ 1.050 mẫu bằng ba quy tắc: trùng câu hỏi sau chuẩn hóa, trùng hội thoại sau chuẩn hóa và gần trùng nội dung kết hợp ở ngưỡng 0,96.

## Cách đọc đúng

Ví dụ đúng: đọc report Markdown trước; chỉ mở workbook chi tiết khi cần xem tám kết quả hoặc kiểm tra số liệu.

Ví dụ không đúng: coi mối liên hệ quan sát được là bằng chứng rằng việc dùng nhiều dẫn chứng học liệu làm mẫu tốt hơn. Phân tích không chứng minh quan hệ nhân quả.

Trong file 03, `pass` là trạng thái tổng thể chính thức. Đây không phải tỷ lệ tiêu chí đạt trong phân tích dẫn chứng học liệu.
"""


def grade_readme_text_hnmu(
    grade: str,
    row_counts: dict[str, int],
    coverage_count: int,
    status: Counter[str],
    technical_count: int,
) -> str:
    return f"""# Kết quả rà soát lớp {grade}

Thư mục này chỉ chứa dữ liệu lớp {grade}. Dùng `sample_id` để đối chiếu giữa các file dữ liệu.

## Số bản ghi

- `01_du_lieu_tho_sau_chuan_hoa.csv`: {row_counts['normalized']}.
- `02_thong_ke_do_phu_mau_pass.xlsx`: {coverage_count} bài học, kể cả bài không có mẫu pass.
- `03_ket_qua_cham_tong_the_tung_mau.csv`: {row_counts['quality']}.
- `04_ket_qua_cham_chi_tiet_tung_tieu_chi.csv`: {row_counts['checklist']}.
- `05_mau_thieu_sai_truong_du_lieu.csv`: {row_counts['missing']}.
- `06_ung_vien_trung_lap.csv`: {row_counts['duplicates']} ứng viên trong lớp.
- `{GRADE_ANALYSIS_NAME}`: 8 dòng tóm tắt dành cho HNMU.
- `{GRADE_APPENDIX_NAME}`: {technical_count} dòng phụ lục kiểm toán kỹ thuật.

## Trạng thái

- pass: {status['pass']}.
- need_human_review: {status['need_human_review']}.
- failed: {status['failed']}.

## Cách đọc hai file phân tích dẫn chứng học liệu

File 07 đặt kết quả khi xem tất cả mẫu và kết quả khi so các mẫu trong cùng nhóm chấm cạnh nhau. Vì mỗi thư mục chỉ có một lớp, file này không so sánh giữa các khối lớp.

File 08 giữ đầy đủ mã đối chiếu, hệ số, p-value, phân nhóm, phương pháp và lý do không thể ước lượng. Các thông tin kỹ thuật này không hiển thị trong file 07.

Ví dụ đúng: đọc cột “Diễn giải chính” trong file 07, rồi mở file 08 nếu cần kiểm tra chi tiết.

Ví dụ không đúng: kết luận dẫn chứng học liệu là nguyên nhân làm mẫu pass. Giáo viên HNMU/UET vẫn giữ quyền đánh giá chuyên môn.
"""


def file_manifest_text_hnmu(
    grade_counts: dict[str, int],
    technical_counts: dict[str, int],
) -> str:
    grade_lines: list[str] = []
    for grade in ("6", "7", "8", "9"):
        grade_lines.extend(
            [
                f"├── lop_{grade}/",
                "│   ├── README.md",
                "│   ├── 01_du_lieu_tho_sau_chuan_hoa.csv",
                "│   ├── 02_thong_ke_do_phu_mau_pass.xlsx",
                "│   ├── 03_ket_qua_cham_tong_the_tung_mau.csv",
                "│   ├── 04_ket_qua_cham_chi_tiet_tung_tieu_chi.csv",
                "│   ├── 05_mau_thieu_sai_truong_du_lieu.csv",
                "│   ├── 06_ung_vien_trung_lap.csv",
                f"│   ├── {GRADE_ANALYSIS_NAME}",
                f"│   └── {GRADE_APPENDIX_NAME}",
            ]
        )
    tree = "\n".join(
        [
            "hnmu_dialogue_audit_phase1_v2/",
            "├── README.md",
            "├── 01_bao_cao_tong_quan.md",
            "├── 02_checklist_tieu_chi.xlsx",
            "├── 03_thong_ke_pass_reject_giua_cac_khoi.xlsx",
            "├── 04_thong_ke_do_phu_mau_pass_giua_cac_khoi.xlsx",
            f"├── {ROOT_ANALYSIS_NAME}",
            f"├── {ROOT_APPENDIX_NAME}",
            "├── 06_ket_qua_cham_tong_the_tung_mau.csv",
            "├── 07_mau_thieu_sai_truong_du_lieu.csv",
            "├── 08_ung_vien_trung_lap.csv",
            "├── 09_du_lieu_tho_sau_chuan_hoa.csv",
            "├── DANH_MUC_FILE.md",
            *grade_lines,
        ]
    )
    return f"""# Danh mục file bàn giao

## Cây thư mục

```text
{tree}
```

## Quy mô đã kiểm tra

- Lớp 6: {grade_counts['6']} mẫu; phụ lục phân tích dẫn chứng học liệu {technical_counts['6']} dòng.
- Lớp 7: {grade_counts['7']} mẫu; phụ lục phân tích dẫn chứng học liệu {technical_counts['7']} dòng.
- Lớp 8: {grade_counts['8']} mẫu; phụ lục phân tích dẫn chứng học liệu {technical_counts['8']} dòng.
- Lớp 9: {grade_counts['9']} mẫu; phụ lục phân tích dẫn chứng học liệu {technical_counts['9']} dòng.
- Toàn bộ: {sum(grade_counts.values())} mẫu; phụ lục phân tích dẫn chứng học liệu root {technical_counts['all']} dòng.

## Quy ước đọc

- Report Markdown file 05 là tài liệu dễ hiểu dành cho HNMU.
- Workbook chi tiết file 05 có năm sheet đọc/kiểm tra và sheet 99 giữ nguyên dữ liệu kỹ thuật gốc; file 07 trong từng lớp vẫn có 8 dòng phân tích.
- Các workbook khác có đúng một sheet dữ liệu chính; riêng phụ lục kỹ thuật fragment ở root có sáu sheet theo vai trò.
"""
