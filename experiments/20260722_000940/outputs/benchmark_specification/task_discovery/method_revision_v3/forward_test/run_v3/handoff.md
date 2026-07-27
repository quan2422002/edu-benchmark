# Bàn giao run_v3

## Phạm vi

- Coder: `PEDAGOGICAL-PRINCIPLE-ANNOTATOR-FORWARD-V3`
- Mô hình: `gpt-5.4-mini`
- reasoning: `medium`
- Input: `principle_annotation_pass1_input.csv`, `principle_annotation_grounding_input.csv`, `principle_annotation_grounding_manifest.json`
- Allowed writes: chỉ trong `experiments/20260722_000940/outputs/benchmark_specification/task_discovery/method_revision_v3/forward_test/run_v3/`

## Artifact đã tạo

- `principle_annotation_pass1.csv`
- `principle_annotation_pass1_labels.csv`
- `principle_annotation_final.csv`
- `principle_annotation_final_labels.csv`
- `principle_annotation_review_queue.csv`
- `principle_annotation_run_manifest.json`
- `handoff.md`

## Kết quả nhãn cuối

- FT-C01: `EXPLANATION`
- FT-C02: `EXPLANATION`, `FEEDBACK`
- FT-C03: `CHALLENGE`, `PRACTICE`
- FT-C04: `MODELLING`
- FT-C05: `EXPLANATION`

## Thống kê

- Candidate: 5
- Tổng label row: 7
- `EXPLANATION`: 3
- `FEEDBACK`: 1
- `CHALLENGE`: 1
- `PRACTICE`: 2
- `MODELLING`: 1
- `QUESTIONING`: 0

## Grounding

- Tất cả 5 candidate giữ nguyên tập nhãn giữa pass 1 và final.
- Không có coverage gap.
- Không có conflict ngữ nghĩa.
- Không có candidate nào vượt quá 3 nhãn.

## Review queue

- 1 hàng review cho FT-C04 với `principle_boundary_ambiguous`.
- Lý do: ranh giới giữa `MODELLING` và `QUESTIONING` trong ca mở đầu gỡ lỗi còn có thể được UET rà lại.

## Xác thực

- Bundle đã được kiểm tra bằng `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.
- Trạng thái validation: `passed`.

## Độ không chắc chắn

- Ca biên chính là FT-C04. Tôi chọn `MODELLING` đơn lẻ vì phản hồi tối thiểu cần mô tả bước đầu gỡ lỗi là chạy chương trình và quan sát hiện tượng sai đầu tiên.
- Nếu UET muốn nhấn mạnh việc yêu cầu học sinh trả lời lại sau khi quan sát, có thể cân nhắc bổ sung `QUESTIONING`.

## Cần UET quyết định

- Xác nhận liệu FT-C04 có cần giữ `MODELLING` בלבד hay mở rộng thêm `QUESTIONING`.
