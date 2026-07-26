# Bàn giao đóng gói kết quả Phase 1 cho giáo viên HNMU

- Mã công việc: `hnmu-dialogue-audit-teacher-bundle-049`
- Chế độ thực hiện: single-agent/orchestrator; không chạy specialist audit
- Trạng thái: hoàn thành, đã kiểm tra, chờ người dùng duyệt bundle local
- Runtime: `/home/dknguyen/miniconda3/envs/edu_ai/bin/python`

## Phạm vi

Đóng gói lại đúng 15 output canonical của Plan 04 thành bốn workbook có cùng cấu trúc cho lớp 6, 7, 8 và 9. Công việc không chạy lại experiment, không tái tạo specialist audit, không đọc `shared/**` và không truy cập Google Drive.

## Đầu vào đã đọc

Builder chỉ đọc 15 đường dẫn được khai báo trong allowlist của `teacher_bundle.py`:

- 7 file canonical thuộc `outputs/hnmu_dialogue_audit/` cho lớp 6–7;
- 7 file canonical thuộc `outputs/hnmu_dialogue_audit_grade8_9/` cho lớp 8–9;
- 1 báo cáo tổng hợp `bao-cao-gui-hnmu-ket-qua-ra-soat-du-lieu-hoi-thoai-lop-6-9-20260719.md`.

Danh sách đầy đủ, SHA-256 và số bản ghi được ghi trong sheet `PL_Nguon_du_lieu` của từng workbook. Giá trị `source_file` được giữ nguyên để truy vết nhưng không được builder mở hoặc đưa vào danh sách nguồn đã đọc.

## Đầu ra đã tạo

- `experiments/20260709_155523/deliverables/hnmu_dialogue_audit_phase1/README.md`
- `experiments/20260709_155523/deliverables/hnmu_dialogue_audit_phase1/lop_6/README.md` và `01_ket_qua_ra_soat_lop_6.xlsx`
- `experiments/20260709_155523/deliverables/hnmu_dialogue_audit_phase1/lop_7/README.md` và `01_ket_qua_ra_soat_lop_7.xlsx`
- `experiments/20260709_155523/deliverables/hnmu_dialogue_audit_phase1/lop_8/README.md` và `01_ket_qua_ra_soat_lop_8.xlsx`
- `experiments/20260709_155523/deliverables/hnmu_dialogue_audit_phase1/lop_9/README.md` và `01_ket_qua_ra_soat_lop_9.xlsx`

## Kết quả kiểm tra

- Validator mở lại cả bốn workbook: đạt.
- Phân hoạch mẫu: lớp 6 = 238, lớp 7 = 224, lớp 8 = 280, lớp 9 = 308; tổng 1.050.
- Hàng đợi cần rà soát: 132, 92, 71 và 90; tổng 385.
- Mỗi mẫu có đúng 18 tiêu chí checklist và khóa `(sample_id, criterion_id)` duy nhất.
- `PL_Nguon_du_lieu` có đúng 15 nguồn canonical với SHA-256 khớp sau build.
- Test tích hợp giám sát `Path.open` và dừng nếu có thao tác đọc dưới `shared/**`: đạt.
- Lệnh test: `9 passed in 115.07s` cho `test_teacher_bundle.py` và `test_checklist_aggregation.py`.

## Quyết định triển khai

Workbook được giữ là output local theo `.gitignore`; README, builder, validator, test và tài liệu repository có thể được review riêng. Không thực hiện `git add`, commit, push, upload hoặc `rclone` trong công việc này.

## Điểm cần người dùng quyết định

- Duyệt nội dung và cách trình bày của bốn workbook trước khi bàn giao HNMU.
- Sau khi duyệt, người dùng tự upload bundle lên Google Drive hoặc cấp phép riêng cho bước Git nếu cần.
