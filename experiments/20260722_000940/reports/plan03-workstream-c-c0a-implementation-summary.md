# Báo cáo triển khai Workstream C — C0a trước forward test

Ngày: 27/07/2026  
Trạng thái: **hạ tầng và kiểm thử tĩnh đã đạt; dừng đúng cổng UET trước forward test và pilot hai specialist**.

## Kết quả đã hoàn thành

- Tạo specialist `pedagogical-principle-annotator` với skill canonical, hợp đồng hai lượt, adapter Codex/Claude và liên kết discovery.
- Khóa model `gpt-5.4-mini`, reasoning `medium`; specialist chỉ được đề xuất nhãn, không sửa codebook, không ghi `confirmed` và không đọc output của instance còn lại.
- Tạo module và ba CLI cho: tách input context/reference, khóa hash năm tài liệu canonical, validate từng bundle, đăng ký trước ngưỡng và so sánh hai run xác định.
- Tạo lô pilot 40 với hai file vật lý riêng. View vòng 1 không có `gold_response`, `gold_answer` hoặc evidence ẩn; hai view có cùng 40 cặp ID theo cùng thứ tự.
- Tạo reference manifest với `ordered_id_sha256=7559aa497a0227c221725ebd2c9df60867aceeb93fa8dc8fe37ec2a62f6058e3`.
- Tạo packet UET gồm năm ví dụ biên, đề xuất ngưỡng C0b và file gán mù 20 mẫu đầu.

## Validation

- Skill creator `quick_validate.py`: đạt.
- Kiểm thử tập trung C0a: 15/15 đạt.
- Toàn bộ `tests/agents` và `tests/benchmark_specification`: 68/68 đạt.
- Toàn bộ repository: 125/125 đạt.
- Python dùng để validate: `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.

## Những gì chưa được làm

- Chưa chạy forward test, vì năm ví dụ biên phải được UET xem trước.
- Chưa spawn hai specialist A/B và chưa tạo nhãn AI chính thức.
- Chưa so sánh A–B, vì ngưỡng phải được UET đăng ký trước và UET phải hoàn tất nhãn mù 20 mẫu trước khi xem output AI.
- `formal_principle_annotation_count` vẫn bằng 0.

## Cổng UET hiện tại

UET cần xử lý packet `outputs/benchmark_specification/teacher_review_packets/workstream_c_c0_gate/` và file `outputs/benchmark_specification/task_discovery/principle_calibration.csv`. Sau khi ba quyết định được khóa, orchestrator mới được chạy forward test và spawn đúng hai native specialist thread.

## Giới hạn

Cơ chế vùng ghi riêng được thực thi bằng hợp đồng delegation, đường dẫn riêng và validator. Repository không tuyên bố có ACL hệ điều hành để cấm tuyệt đối một agent đọc thư mục kia; tính cô lập còn dựa trên native-thread prompt và kiểm tra artifact/handoff. Chỉ số A–B sau này là tính tái lập AI liên-instance, không phải độ tin cậy giữa hai người chấm.
