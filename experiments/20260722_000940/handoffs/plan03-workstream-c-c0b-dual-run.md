# Bàn giao Workstream C0b — pilot hai specialist

- Delegation ID: `PLAN03-C-C0B-ANNOTATOR-A-001`, `PLAN03-C-C0B-ANNOTATOR-B-001`
- Specialist: `pedagogical-principle-annotator`
- Trạng thái: hai bundle hoàn tất; Cổng C0b không đạt
- Native thread: `/root/plan03_c0b_annotator_a`, `/root/plan03_c0b_annotator_b`

## Nhiệm vụ

Hai instance mã hóa độc lập cùng lô 40 bằng workflow hai vòng, cùng model `gpt-5.4-mini`, reasoning `medium`, cùng manifest/hash và hai vùng ghi riêng.

## Input

- `outputs/benchmark_specification/task_discovery/principle_annotation_pass1_input.csv`
- `outputs/benchmark_specification/task_discovery/principle_annotation_reference_input.csv`
- `outputs/benchmark_specification/task_discovery/principle_annotation_reference_manifest.json`
- `outputs/benchmark_specification/task_discovery/dual_run_thresholds.json`

## Output

- `outputs/benchmark_specification/task_discovery/dual_run/annotator_a/`
- `outputs/benchmark_specification/task_discovery/dual_run/annotator_b/`
- `outputs/benchmark_specification/task_discovery/dual_run_comparison.csv`
- `outputs/benchmark_specification/task_discovery/dual_run_confusion_matrix.csv`
- `outputs/benchmark_specification/task_discovery/dual_run_reproducibility_summary.json`
- `outputs/benchmark_specification/teacher_review_packets/workstream_c_c0b/`
- `reports/plan03-workstream-c-c0b-dual-run-summary.md`

## Kết quả

- A: 40 dòng hợp lệ, 18 thay đổi sau reference, 0 conflict, 0 coverage gap.
- B: 40 dòng hợp lệ, 14 thay đổi sau reference, 0 conflict, 0 coverage gap.
- Trùng nguyên tắc chính: 0,55.
- Trùng cặp chính–phụ: 0,55.
- Jaccard trung bình: 0,55.
- Trùng khoảng trống: 1,00.
- Trùng tác động reference: 0,70.

Bốn trong năm chỉ số không đạt ngưỡng UET. C0b không đạt và C1 chưa được mở.

## Sự cố và gia cố

Bundle B ban đầu có một lỗi nhất quán giữa thay đổi nhãn và `reference_effect`. Validator đã chặn; specialist B sửa bundle rồi chạy lại đạt. Hàm so sánh đã được bổ sung bước tự validate cả hai bundle để không thể tạo metric từ bundle lỗi.

## Quyết định của orchestrator

Không coi nhãn A hoặc B là ground truth. Tạo packet 29 dòng gồm 21 trường hợp có bất đồng và 8 trường hợp đồng thuận kiểm tra để UET review. Sau review mới sửa ranh giới/skill và chạy lại C0b.

## Bất định

Lô pilot gồm toàn bộ mẫu lớp 6 do cách lấy offset hiện tại. Kết quả chưa đại diện lớp 7–9. Gói tài liệu canonical cũng tạo chi phí đọc lớn; tối ưu gói vận hành chỉ được thực hiện sau khi giữ kết quả này làm baseline.

## Quyết định tiếp theo của UET

Điền các cột `uet_*` trong `teacher_review_packets/workstream_c_c0b/dual_run_uet_review.csv`. Không cần gán mù và không cần review 11 dòng ngoài packet ở vòng này.
