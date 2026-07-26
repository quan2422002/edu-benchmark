"""Build and validate the grade-partitioned HNMU Phase 1 bundle v2."""

from __future__ import annotations

import tempfile
from pathlib import Path

from edu_benchmark.dialogue_audit.teacher_bundle import (
    EXPECTED_CRITERIA_PER_SAMPLE,
    EXPECTED_GRADE_COUNTS,
    BundleData,
    _display_path,
    load_canonical_bundle_data,
)
from edu_benchmark.dialogue_audit.teacher_bundle_v2 import (
    CHECKLIST_FIELDS,
    COVERAGE_HEADERS,
    CRITERIA_HEADERS,
    DUPLICATE_FIELDS,
    MISSING_FIELDS,
    NORMALIZED_FIELDS,
    QUALITY_FIELDS,
    STATUS_HEADERS,
    ChiSquareResult,
    V2BuildSummary,
    _assert_workbook_rows,
    _checklist_rows,
    _chi_square_result,
    _criteria_rows,
    _duplicate_rows,
    _missing_rows,
    _normalized_rows,
    _overview_report,
    _pass_coverage_rows,
    _quality_rows,
    _status_counts,
    _status_rows,
    _validate_csv_exact,
    _write_csv,
    _write_single_sheet_workbook,
)

ROOT_OUTPUT_NAMES = (
    "README.md",
    "01_bao_cao_tong_quan.md",
    "02_checklist_tieu_chi.xlsx",
    "03_thong_ke_pass_reject_giua_cac_khoi.xlsx",
    "04_thong_ke_do_phu_mau_pass_giua_cac_khoi.xlsx",
)
GRADE_OUTPUT_NAMES = (
    "README.md",
    "01_du_lieu_tho_sau_chuan_hoa.csv",
    "02_thong_ke_do_phu_mau_pass.xlsx",
    "03_ket_qua_cham_tong_the_tung_mau.csv",
    "04_ket_qua_cham_chi_tiet_tung_tieu_chi.csv",
    "05_mau_thieu_sai_truong_du_lieu.csv",
    "06_ung_vien_trung_lap.csv",
)


def _filter_grade(rows: list[dict[str, str]], grade: str) -> list[dict[str, str]]:
    return [row for row in rows if row["grade"] == grade]


def _grade_data_rows(data: BundleData, grade: str) -> dict[str, list[dict[str, str]]]:
    return {
        "normalized": _filter_grade(_normalized_rows(data), grade),
        "quality": _filter_grade(_quality_rows(data), grade),
        "checklist": _filter_grade(_checklist_rows(data), grade),
        "missing": _filter_grade(_missing_rows(data), grade),
        "duplicates": _filter_grade(_duplicate_rows(data), grade),
    }


def _grade_coverage_rows(data: BundleData, grade: str) -> list[list[object]]:
    return [row for row in _pass_coverage_rows(data) if row[0] == grade]


def _root_readme_text() -> str:
    return """# Bộ kết quả rà soát Phase 1 gửi HNMU

Bộ hồ sơ được chia thành phần dùng chung ở thư mục này và bốn thư mục riêng cho lớp 6, 7, 8, 9.

## Đọc phần dùng chung

1. Đọc `01_bao_cao_tong_quan.md` để xem quy mô, tỷ lệ trạng thái và kết quả so sánh giữa các khối.
2. Mở `02_checklist_tieu_chi.xlsx` để xem 18 tiêu chí dùng chung.
3. Mở `03_thong_ke_pass_reject_giua_cac_khoi.xlsx` để so sánh số lượng và tỷ lệ trạng thái của bốn khối.
4. Mở `04_thong_ke_do_phu_mau_pass_giua_cac_khoi.xlsx` để so sánh độ phủ được tính lại riêng từ các mẫu đạt.

## Đọc kết quả theo lớp

Chọn đúng một thư mục: `lop_6/`, `lop_7/`, `lop_8/` hoặc `lop_9/`. Mỗi thư mục có cùng bảy file và chỉ chứa dữ liệu của lớp đó.

Trong từng thư mục lớp, đọc file kết quả tổng thể trước. Sau đó dùng cùng `sample_id` để đối chiếu dữ liệu chuẩn hóa và kết quả chi tiết theo tiêu chí. Hai file thiếu/sai trường và ứng viên trùng lặp là thành phần bổ sung; file không có bản ghi vẫn giữ hàng tiêu đề.

Ví dụ đúng: tra một mẫu lớp 8 trong `lop_8/`, rồi dùng cùng `sample_id` ở các file khác trong chính thư mục đó.

Ví dụ không đúng: tìm mẫu lớp 8 trong `lop_9/` hoặc coi trạng thái `failed` là quyết định loại bỏ vĩnh viễn. Giáo viên HNMU/UET vẫn giữ quyền xác nhận chuyên môn.
"""


def _grade_readme_text(data: BundleData, grade: str) -> str:
    rows = _grade_data_rows(data, grade)
    coverage = _grade_coverage_rows(data, grade)
    counts = _status_counts(data)[grade]
    non_pass = counts["need_human_review"] + counts["failed"]
    return f"""# Kết quả rà soát lớp {grade}

Thư mục này chỉ chứa dữ liệu lớp {grade}. Có {len(rows['normalized'])} mẫu chuẩn hóa.

## Số bản ghi

- `01_du_lieu_tho_sau_chuan_hoa.csv`: {len(rows['normalized'])} bản ghi.
- `02_thong_ke_do_phu_mau_pass.xlsx`: {len(coverage)} dòng thống kê.
- `03_ket_qua_cham_tong_the_tung_mau.csv`: {len(rows['quality'])} bản ghi.
- `04_ket_qua_cham_chi_tiet_tung_tieu_chi.csv`: {len(rows['checklist'])} bản ghi.
- `05_mau_thieu_sai_truong_du_lieu.csv`: {len(rows['missing'])} bản ghi.
- `06_ung_vien_trung_lap.csv`: {len(rows['duplicates'])} bản ghi.

## Trạng thái

- `pass`: {counts['pass']} mẫu.
- `need_human_review`: {counts['need_human_review']} mẫu.
- `failed`: {counts['failed']} mẫu.
- `non_pass`: {non_pass} mẫu.

Đọc file 03 để xem trạng thái tổng thể. Dùng cùng `sample_id` trong file 01 và 04 để xem đầy đủ nội dung và từng tiêu chí. File 05 và 06 có thể có 0 bản ghi; khi đó hàng tiêu đề vẫn được giữ.

Ví dụ đúng: một phản hồi về lớp {grade} ghi rõ `sample_id`, nội dung cần xem lại và lý do.

Ví dụ không đúng: dùng một dòng của lớp khác để nhận xét cho lớp {grade}. Mọi dòng dữ liệu trong thư mục này phải có `grade = {grade}`.
"""


def _overview_text(data: BundleData) -> str:
    return _overview_report(data).replace(
        "Độ phủ trong file 05",
        "Độ phủ trong file 04 ở thư mục gốc và file 02 trong từng thư mục lớp",
    )


def _all_output_paths(bundle_dir: Path) -> tuple[Path, ...]:
    paths = [bundle_dir / name for name in ROOT_OUTPUT_NAMES]
    for grade in EXPECTED_GRADE_COUNTS:
        paths.extend(bundle_dir / f"lop_{grade}" / name for name in GRADE_OUTPUT_NAMES)
    return tuple(paths)


def _build_partitioned_files(data: BundleData, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=False)
    (directory / ROOT_OUTPUT_NAMES[0]).write_text(_root_readme_text(), encoding="utf-8")
    (directory / ROOT_OUTPUT_NAMES[1]).write_text(_overview_text(data), encoding="utf-8")
    _write_single_sheet_workbook(
        directory / ROOT_OUTPUT_NAMES[2],
        "checklist_tieu_chi",
        CRITERIA_HEADERS,
        _criteria_rows(data),
        {1: 22, 2: 24, 3: 55, 4: 22, 5: 16},
    )
    _write_single_sheet_workbook(
        directory / ROOT_OUTPUT_NAMES[3],
        "pass_reject_giua_cac_khoi",
        STATUS_HEADERS,
        _status_rows(data),
        {1: 10, 2: 16, 3: 24, 4: 34, 5: 14, 6: 16, 7: 18},
        percentage_columns=(6,),
    )
    _write_single_sheet_workbook(
        directory / ROOT_OUTPUT_NAMES[4],
        "do_phu_pass_giua_cac_khoi",
        COVERAGE_HEADERS,
        _pass_coverage_rows(data),
        {1: 10, 2: 16, 3: 20, 4: 22, 5: 22, 6: 65, 7: 14, 8: 22, 9: 20},
        percentage_columns=(8,),
    )

    for grade in EXPECTED_GRADE_COUNTS:
        grade_dir = directory / f"lop_{grade}"
        grade_dir.mkdir()
        rows = _grade_data_rows(data, grade)
        coverage = _grade_coverage_rows(data, grade)
        (grade_dir / GRADE_OUTPUT_NAMES[0]).write_text(
            _grade_readme_text(data, grade),
            encoding="utf-8",
        )
        _write_csv(grade_dir / GRADE_OUTPUT_NAMES[1], NORMALIZED_FIELDS, rows["normalized"])
        _write_single_sheet_workbook(
            grade_dir / GRADE_OUTPUT_NAMES[2],
            "do_phu_mau_pass",
            COVERAGE_HEADERS,
            coverage,
            {1: 10, 2: 16, 3: 20, 4: 22, 5: 22, 6: 65, 7: 14, 8: 22, 9: 20},
            percentage_columns=(8,),
        )
        _write_csv(grade_dir / GRADE_OUTPUT_NAMES[3], QUALITY_FIELDS, rows["quality"])
        _write_csv(grade_dir / GRADE_OUTPUT_NAMES[4], CHECKLIST_FIELDS, rows["checklist"])
        _write_csv(grade_dir / GRADE_OUTPUT_NAMES[5], MISSING_FIELDS, rows["missing"])
        _write_csv(grade_dir / GRADE_OUTPUT_NAMES[6], DUPLICATE_FIELDS, rows["duplicates"])


def _markdown_line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def validate_partitioned_phase1_teacher_bundle_v2(
    experiment_dir: Path,
    bundle_dir: Path,
    *,
    expected_source_hashes: dict[Path, str] | None = None,
) -> dict[str, object]:
    """Validate the shared root and all four grade-only directories."""

    data = load_canonical_bundle_data(experiment_dir)
    if expected_source_hashes is not None and data.source_hashes != expected_source_hashes:
        raise ValueError("Canonical source hashes changed during partitioned v2 build")
    if not bundle_dir.is_dir():
        raise FileNotFoundError(f"Missing partitioned v2 bundle: {bundle_dir}")

    expected_root_entries = set(ROOT_OUTPUT_NAMES) | {
        f"lop_{grade}" for grade in EXPECTED_GRADE_COUNTS
    }
    actual_root_entries = {path.name for path in bundle_dir.iterdir()}
    if actual_root_entries != expected_root_entries:
        raise ValueError(
            f"Unexpected root entries: missing={sorted(expected_root_entries - actual_root_entries)}, "
            f"extra={sorted(actual_root_entries - expected_root_entries)}"
        )

    criteria_rows = _criteria_rows(data)
    status_rows = _status_rows(data)
    coverage_rows = _pass_coverage_rows(data)
    _assert_workbook_rows(
        bundle_dir / ROOT_OUTPUT_NAMES[2],
        "checklist_tieu_chi",
        CRITERIA_HEADERS,
        criteria_rows,
    )
    _assert_workbook_rows(
        bundle_dir / ROOT_OUTPUT_NAMES[3],
        "pass_reject_giua_cac_khoi",
        STATUS_HEADERS,
        status_rows,
    )
    _assert_workbook_rows(
        bundle_dir / ROOT_OUTPUT_NAMES[4],
        "do_phu_pass_giua_cac_khoi",
        COVERAGE_HEADERS,
        coverage_rows,
    )
    if {row[0] for row in coverage_rows} != set(EXPECTED_GRADE_COUNTS):
        raise ValueError("Root pass coverage does not compare all four grades")
    for grade in EXPECTED_GRADE_COUNTS:
        if not all(
            any(row[0] == grade and row[2] == dimension for row in coverage_rows)
            for dimension in ("topic", "lesson", "bloom_band")
        ):
            raise ValueError(f"Root pass coverage misses a dimension for grade {grade}")

    root_readme = (bundle_dir / ROOT_OUTPUT_NAMES[0]).read_text(encoding="utf-8")
    for grade in EXPECTED_GRADE_COUNTS:
        if f"lop_{grade}/" not in root_readme:
            raise ValueError(f"Root README does not route teachers to lop_{grade}")
    overview = (bundle_dir / ROOT_OUTPUT_NAMES[1]).read_text(encoding="utf-8")
    for marker in ("Chi-square:", "Cramér’s V:", "Phụ lục — Nội dung báo cáo canonical"):
        if marker not in overview:
            raise ValueError(f"Overview report is missing: {marker}")

    all_normalized_ids: list[str] = []
    all_quality_ids: list[str] = []
    all_pairs: list[tuple[str, str]] = []
    file_row_counts: dict[str, int] = {
        ROOT_OUTPUT_NAMES[0]: _markdown_line_count(bundle_dir / ROOT_OUTPUT_NAMES[0]),
        ROOT_OUTPUT_NAMES[1]: _markdown_line_count(bundle_dir / ROOT_OUTPUT_NAMES[1]),
        ROOT_OUTPUT_NAMES[2]: len(criteria_rows),
        ROOT_OUTPUT_NAMES[3]: len(status_rows),
        ROOT_OUTPUT_NAMES[4]: len(coverage_rows),
    }

    for grade, expected_count in EXPECTED_GRADE_COUNTS.items():
        grade_dir = bundle_dir / f"lop_{grade}"
        actual_grade_entries = {path.name for path in grade_dir.iterdir()}
        if actual_grade_entries != set(GRADE_OUTPUT_NAMES):
            raise ValueError(
                f"lop_{grade} file set differs: "
                f"missing={sorted(set(GRADE_OUTPUT_NAMES) - actual_grade_entries)}, "
                f"extra={sorted(actual_grade_entries - set(GRADE_OUTPUT_NAMES))}"
            )
        expected = _grade_data_rows(data, grade)
        normalized = _validate_csv_exact(
            grade_dir / GRADE_OUTPUT_NAMES[1], NORMALIZED_FIELDS, expected["normalized"]
        )
        quality = _validate_csv_exact(
            grade_dir / GRADE_OUTPUT_NAMES[3], QUALITY_FIELDS, expected["quality"]
        )
        checklist = _validate_csv_exact(
            grade_dir / GRADE_OUTPUT_NAMES[4], CHECKLIST_FIELDS, expected["checklist"]
        )
        missing = _validate_csv_exact(
            grade_dir / GRADE_OUTPUT_NAMES[5], MISSING_FIELDS, expected["missing"]
        )
        duplicates = _validate_csv_exact(
            grade_dir / GRADE_OUTPUT_NAMES[6], DUPLICATE_FIELDS, expected["duplicates"]
        )
        grade_coverage = _grade_coverage_rows(data, grade)
        _assert_workbook_rows(
            grade_dir / GRADE_OUTPUT_NAMES[2],
            "do_phu_mau_pass",
            COVERAGE_HEADERS,
            grade_coverage,
        )

        if len(normalized) != expected_count or len(quality) != expected_count:
            raise ValueError(f"lop_{grade} has the wrong sample count")
        if any(row["grade"] != grade for row in normalized + quality + checklist + missing + duplicates):
            raise ValueError(f"lop_{grade} contains a row from another grade")
        if any(not row["source_file"] for row in normalized + quality + checklist + missing):
            raise ValueError(f"lop_{grade} loses source_file provenance")
        if any(
            not row["source_file_a"] or not row["source_file_b"]
            for row in duplicates
        ):
            raise ValueError(f"lop_{grade} duplicate rows lose source_file provenance")

        normalized_ids = [row["sample_id"] for row in normalized]
        quality_ids = [row["sample_id"] for row in quality]
        pairs = [(row["sample_id"], row["criterion_id"]) for row in checklist]
        if len(set(normalized_ids)) != expected_count or set(normalized_ids) != set(quality_ids):
            raise ValueError(f"lop_{grade} loses or duplicates sample_id values")
        if len(pairs) != expected_count * EXPECTED_CRITERIA_PER_SAMPLE or len(set(pairs)) != len(pairs):
            raise ValueError(f"lop_{grade} has missing or duplicate criterion keys")

        grade_readme = (grade_dir / GRADE_OUTPUT_NAMES[0]).read_text(encoding="utf-8")
        required_counts = (
            len(normalized),
            len(grade_coverage),
            len(quality),
            len(checklist),
            len(missing),
            len(duplicates),
        )
        if not all(f": {count} " in grade_readme for count in required_counts):
            raise ValueError(f"lop_{grade} README does not state every row count")

        all_normalized_ids.extend(normalized_ids)
        all_quality_ids.extend(quality_ids)
        all_pairs.extend(pairs)
        prefix = f"lop_{grade}/"
        file_row_counts.update(
            {
                prefix + GRADE_OUTPUT_NAMES[0]: _markdown_line_count(
                    grade_dir / GRADE_OUTPUT_NAMES[0]
                ),
                prefix + GRADE_OUTPUT_NAMES[1]: len(normalized),
                prefix + GRADE_OUTPUT_NAMES[2]: len(grade_coverage),
                prefix + GRADE_OUTPUT_NAMES[3]: len(quality),
                prefix + GRADE_OUTPUT_NAMES[4]: len(checklist),
                prefix + GRADE_OUTPUT_NAMES[5]: len(missing),
                prefix + GRADE_OUTPUT_NAMES[6]: len(duplicates),
            }
        )

    expected_ids = set(data.normalized_by_id)
    if (
        len(all_normalized_ids) != 1050
        or len(set(all_normalized_ids)) != 1050
        or set(all_normalized_ids) != expected_ids
        or len(all_quality_ids) != 1050
        or set(all_quality_ids) != expected_ids
    ):
        raise ValueError("Four grade directories do not partition all 1,050 samples")
    if len(all_pairs) != 1050 * EXPECTED_CRITERIA_PER_SAMPLE or len(set(all_pairs)) != len(all_pairs):
        raise ValueError("Four grade directories do not partition all criterion keys")

    return {
        "status": "ok",
        "output_paths": [path.as_posix() for path in _all_output_paths(bundle_dir)],
        "grade_counts": dict(EXPECTED_GRADE_COUNTS),
        "status_counts": _status_counts(data),
        "checklist_row_count": len(all_pairs),
        "missing_row_count": len(data.missing_rows),
        "duplicate_row_count": len(data.duplicate_rows),
        "chi_square": _chi_square_result(data).__dict__,
        "source_count": len(data.source_hashes),
        "source_hashes": {
            _display_path(path): digest for path, digest in data.source_hashes.items()
        },
        "read_paths": sorted(_display_path(path) for path in data.read_paths),
        "file_row_counts": file_row_counts,
    }


def build_partitioned_phase1_teacher_bundle_v2(
    experiment_dir: Path,
    bundle_dir: Path,
) -> V2BuildSummary:
    """Build the partitioned v2 bundle atomically and refuse overwrite."""

    if bundle_dir.exists():
        raise FileExistsError(f"V2 bundle already exists; refusing to overwrite: {bundle_dir}")
    data = load_canonical_bundle_data(experiment_dir)
    initial_hashes = dict(data.source_hashes)
    bundle_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".hnmu-teacher-bundle-v2-partitioned-",
        dir=bundle_dir.parent,
    ) as temp:
        staged = Path(temp) / "bundle"
        _build_partitioned_files(data, staged)
        validate_partitioned_phase1_teacher_bundle_v2(
            experiment_dir,
            staged,
            expected_source_hashes=initial_hashes,
        )
        staged.replace(bundle_dir)

    validation = validate_partitioned_phase1_teacher_bundle_v2(
        experiment_dir,
        bundle_dir,
        expected_source_hashes=initial_hashes,
    )
    return V2BuildSummary(
        output_paths=_all_output_paths(bundle_dir),
        grade_counts=dict(EXPECTED_GRADE_COUNTS),
        status_counts=validation["status_counts"],
        chi_square=ChiSquareResult(**validation["chi_square"]),
        source_hashes=validation["source_hashes"],
        read_paths=tuple(validation["read_paths"]),
    )
