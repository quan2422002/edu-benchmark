# Bàn giao tầng grounding câu hỏi nguồn của Workstream C

- Delegation ID: `PLAN03-C-SOURCE-GROUNDING-001`
- Agent: `benchmark-specification-designer` ở chế độ single-agent trong parent thread
- Status: `completed`
- Native thread ID/label: không có; không spawn specialist mới

## Delegation prompt

Vật hóa câu hỏi nguồn cho từng benchmark candidate bằng code để specialist không phải tự truy ngược hội thoại thô.

## Follow-up or steer messages

Không có.

## Inputs read

- `experiments/20260722_000940/outputs/benchmark_conversion/full_v0/benchmark_candidate_splits.csv`
- `experiments/20260722_000940/inherited_resources/from_20260709_155523/raw_audit_grade6_7/normalized_dialogue_rows.csv`
- `experiments/20260722_000940/inherited_resources/from_20260709_155523/raw_audit_grade8_9/normalized_dialogue_rows.csv`

## Outputs created

- `src/edu_benchmark/benchmark_specification/principle_grounding.py`
- `scripts/benchmark_specification/build_principle_grounding_pool.py`
- `tests/benchmark_specification/test_principle_grounding.py`
- `experiments/20260722_000940/outputs/benchmark_specification/task_discovery/method_revision_v3/candidate_principle_grounding_pool.csv`
- `experiments/20260722_000940/outputs/benchmark_specification/task_discovery/method_revision_v3/candidate_principle_grounding_pool_manifest.json`

## Result summary

- Đã ghép đủ 2.028 candidate vào đúng một trong 1.050 hội thoại nguồn qua `sample_id`.
- 2.028 candidate thuộc 665 family nguồn; không thiếu `source_question`.
- Join đóng khi lỗi nếu thiếu/trùng `sample_id`, câu hỏi nguồn rỗng hoặc metadata/`gold_answer` không khớp.
- Grounding pool chỉ có 10 cột được phép dùng và không chứa `gold_response`.
- Bảng candidate chính của Plan 02 không bị thay đổi.

## Orchestrator decision

Lần chạy specialist tiếp theo phải cắt input grounding từ pool v3; specialist không tự mở hai snapshot nguồn. Hai input reference chứa `gold_response` của lần C0b đầu tiên chỉ còn là artifact chẩn đoán lịch sử.

## Uncertainty

Schema output tập nguyên tắc không thứ tự của bản sửa phương pháp v3 chưa được triển khai trong thay đổi này.

## Open questions and next human decisions

- Không có quyết định UET mới cho tầng join.
- Cần hoàn tất schema tập nhãn và lô phân tầng 6–9 trước khi chạy specialist lại.
