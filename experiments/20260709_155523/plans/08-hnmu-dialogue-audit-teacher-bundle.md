# Plan 08 — Đóng gói kết quả kiểm toán hội thoại HNMU cho giáo viên

Experiment: `20260709_155523`
Trạng thái: `APPROVED`
Ngày duyệt: 20/07/2026
Người duyệt: project lead
Người thực hiện: Codex ở chế độ single-agent

## 1. Mục tiêu

Đóng gói lại các output canonical đã có của Plan 04 thành bốn workbook dễ đọc cho giáo viên HNMU, tương ứng lớp 6, 7, 8 và 9. Đây chỉ là bước trình bày lại kết quả; không chạy lại experiment, không tái tạo specialist audit và không thay đổi quyết định chuyên môn.

## 2. Ràng buộc

- Không sửa bất kỳ output nguồn nào.
- Không đọc `shared/**`, không truy cập Google Drive và không dereference giá trị trong cột `source_file`.
- Giữ nguyên `source_file` và `source_row_number` trong workbook để truy vết.
- Chỉ đọc đúng 15 file canonical trong allowlist của plan.
- Không dùng pilot, per-shard, pre-repair, backup, regex-repair/debug hoặc output cơ học trung gian.
- Dùng trực tiếp `/home/dknguyen/miniconda3/envs/edu_ai/bin/python` cho pip, build, test và validation.
- Không stage, commit, push, upload hoặc chạy `rclone` trước khi project lead review kết quả local.

## 3. Allowlist đầu vào

Batch lớp 6–7:

1. `outputs/hnmu_dialogue_audit/normalized_dialogue_rows.csv`
2. `outputs/hnmu_dialogue_audit/coverage_summary.csv`
3. `outputs/hnmu_dialogue_audit/missing_field_report.csv`
4. `outputs/hnmu_dialogue_audit/duplicate_candidates.csv`
5. `outputs/hnmu_dialogue_audit/agent_shard_audit/merged/quality_check_suggestions.csv`
6. `outputs/hnmu_dialogue_audit/agent_shard_audit/merged/hnmu_review_queue_suggestions.csv`
7. `outputs/hnmu_dialogue_audit/agent_shard_audit/merged/raw_dialogue_checklist_results.repaired.csv`

Batch lớp 8–9:

8. `outputs/hnmu_dialogue_audit_grade8_9/normalized_dialogue_rows.csv`
9. `outputs/hnmu_dialogue_audit_grade8_9/coverage_summary.csv`
10. `outputs/hnmu_dialogue_audit_grade8_9/missing_field_report.csv`
11. `outputs/hnmu_dialogue_audit_grade8_9/duplicate_candidates.csv`
12. `outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/quality_check_suggestions.csv`
13. `outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/hnmu_review_queue_suggestions.csv`
14. `outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv`

Báo cáo diễn giải:

15. `outputs/hnmu_dialogue_audit/reports/bao-cao-gui-hnmu-ket-qua-ra-soat-du-lieu-hoi-thoai-lop-6-9-20260719.md`

## 4. Output và code được phép thay đổi

- `src/edu_benchmark/dialogue_audit/`
- `scripts/dialogue_audit/`
- `tests/dialogue_audit/`
- `experiments/20260709_155523/deliverables/hnmu_dialogue_audit_phase1/`
- `experiments/20260709_155523/plans/08-hnmu-dialogue-audit-teacher-bundle.md`
- `experiments/20260709_155523/roadmap.md`
- `experiments/20260709_155523/metadata.yaml`
- `experiments/20260709_155523/coordination/delegations.jsonl`
- `experiments/20260709_155523/handoffs/`
- `requirements.txt`
- `.gitignore`
- `README.md`
- `ARCHITECTURE.md`
- `src/edu_benchmark/README.md`

## 5. Deliverable

Tạo bốn workbook local dưới `deliverables/hnmu_dialogue_audit_phase1/lop_6` đến `lop_9`. Mỗi workbook có đúng bảy sheet: `00_Huong_dan`, `01_Tong_quan`, `02_Can_ra_soat`, `03_Da_dat`, `04_Do_phu`, `PL_Chi_tiet_tieu_chi`, `PL_Nguon_du_lieu`.

README tiếng Việt được theo dõi trong Git. Workbook `.xlsx` được ignore và chỉ sinh local trên server. `PL_Nguon_du_lieu` chỉ liệt kê 15 file allowlist mà builder thực sự đọc.

## 6. Tiêu chí hoàn thành

- Bốn lớp tạo thành phân hoạch đúng 1.050 mẫu: 238, 224, 280 và 308.
- Không mất, trùng hoặc sai lớp; `grade`, `source_file` và workbook đích đồng thuận.
- Checklist có đúng 18 tiêu chí/mẫu và khóa `(sample_id, criterion_id)` duy nhất.
- Hàng đợi có đúng 132, 92, 71 và 90 mẫu theo lớp.
- SHA-256 của 15 nguồn không thay đổi.
- Validator mở lại workbook và đối chiếu đầy đủ ID, câu hỏi, đáp án, hội thoại, `source_file` và dòng nguồn.
- Không có thao tác đọc ngoài allowlist trong builder.
- Test và validation chạy bằng interpreter tuyệt đối của `edu_ai`.
- Sau validation, dừng để project lead review trước mọi thao tác Git hoặc upload bên ngoài.
