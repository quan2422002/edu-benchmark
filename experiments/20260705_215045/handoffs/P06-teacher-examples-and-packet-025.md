# Specialist handoff

- Delegation ID: `P06-teacher-examples-and-packet-025`
- Agent: `teacher-collaboration-designer-single-agent-fallback`
- Status: `completed`
- Native thread ID/label: `null` — dùng skill trong parent thread, không spawn subagent ẩn.

## Delegation prompt

Tạo đủ ví dụ dựa trên ma trận bao phủ để chuẩn bị bước sinh ví dụ/phiếu tác giả cho giáo viên HNMU.

## Follow-up or steer messages

- Không tạo đủ 96 ví dụ trong đợt này.
- Chọn lát cắt đại diện phủ đủ nhiệm vụ gia sư, mức nhận thức, chủ đề SGK Tin học 9 và dạng bài làm/câu hỏi của học sinh.
- Giữ ngôn ngữ dễ hiểu, ưu tiên tiếng Việt, đánh dấu nội dung là minh họa v0 cần HNMU rà soát.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260705_215045/roadmap.md`
- `agents/teacher-collaboration-designer/SKILL.md`
- `agents/teacher-collaboration-designer/references/plain-language-guidelines.md`
- `agents/teacher-collaboration-designer/references/task-card-schema.md`
- `experiments/20260705_215045/coverage_design/general_coverage_matrix_v0.csv`
- `experiments/20260705_215045/coverage_design/coverage_axis_values_v0.csv`
- `experiments/20260705_215045/benchmark_design/benchmark_tasks.csv`
- `experiments/20260705_215045/benchmark_design/rubrics.csv`
- `experiments/20260705_215045/topic_taxonomy/tin9_sgk_topics_v0.csv`

## Outputs created

- `experiments/20260705_215045/teacher_examples/selected_coverage_cells_v0.csv`
- `experiments/20260705_215045/teacher_examples/author_form_example_*.md`
- `experiments/20260705_215045/teacher_examples/author_form_counterexample.md`
- `experiments/20260705_215045/teacher_examples/example_coverage_summary.md`
- `experiments/20260705_215045/teacher_packet/`
- `experiments/20260705_215045/reports/P06-teacher-examples-and-packet-summary.md`

## Result summary

Đã tạo 13 ví dụ minh họa và một gói hướng dẫn/rà soát cho giáo viên. Bộ ví dụ phủ đủ 4 nhiệm vụ gia sư, 3 mức nhận thức, 8 cụm chủ đề SGK Tin học 9 và 9 dạng bài làm/câu hỏi của học sinh.

## Orchestrator decision

Bản này là lát cắt đại diện, không phải dataset chính thức. Không mở rộng lên 96 ví dụ trong cùng bước để tránh tạo dữ liệu giả quá rộng trước khi HNMU rà soát.

## Uncertainty

- Nội dung ví dụ dựa trên mục lục và kiến thức SGK Tin học 9 ở mức khái quát, chưa gắn đoạn học liệu nhỏ từ OCR toàn văn.
- Tên chủ đề/bài học vẫn cần HNMU xác nhận.
- Cần HNMU đánh giá xem ngôn ngữ ví dụ có tự nhiên với giáo viên hay chưa.

## Open questions and next human decisions

- Có nên gửi toàn bộ 13 ví dụ cho HNMU ngay hay chọn 5–6 ví dụ tiêu biểu trước?
- Có cần thêm ví dụ riêng cho Scratch hay tạm thời ưu tiên Python theo phạm vi Tin học 9 hiện tại?
- Có nên yêu cầu mỗi giáo viên tạo mẫu theo một chủ đề khác nhau để tăng độ phủ?
