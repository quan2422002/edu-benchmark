# Specialist handoff

- Delegation ID: `P05-general-coverage-matrix-023`
- Agent: `benchmark-specification-designer-single-agent-fallback`
- Status: `completed`
- Native thread ID/label: `null` — dùng skill trong parent thread, không spawn subagent ẩn.

## Delegation prompt

Triển khai P05 theo yêu cầu mới: các câu hỏi mở từ P04 được coi là tạm chốt; 20 mẫu pilot chỉ là con số tượng trưng; cần tạo ma trận tổng quát để nhìn mức độ bao phủ của benchmark trước khi sang P06.

## Follow-up or steer messages

- Không khóa vào đúng 20 mẫu.
- Dùng task/rubric P04 đã có.
- Dùng 3 mức nhận thức từ P02: Biết, Hiểu, Vận dụng.
- Dùng chủ đề SGK Tin học 9 từ P02.
- P06 sẽ chọn lát cắt ví dụ từ ma trận P05.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260705_215045/roadmap.md`
- `agents/benchmark-specification-designer/SKILL.md`
- `experiments/20260705_215045/plans/05-case-coverage-and-pilot-allocation.md`
- `experiments/20260705_215045/plans/06-teacher-examples-and-pilot-packet.md`
- `experiments/20260705_215045/benchmark_design/benchmark_tasks.csv`
- `experiments/20260705_215045/benchmark_design/rubrics.csv`
- `experiments/20260705_215045/topic_taxonomy/tin9_sgk_topics_v0.csv`
- `experiments/20260705_215045/reports/P04-task-rubric-open-questions.md`

## Outputs created

- `experiments/20260705_215045/coverage_design/coverage_axis_values_v0.csv`
- `experiments/20260705_215045/coverage_design/general_coverage_matrix_v0.csv`
- `experiments/20260705_215045/coverage_design/coverage_summary_v0.csv`
- `experiments/20260705_215045/coverage_design/coverage_matrix_readme_v0.md`
- `experiments/20260705_215045/coverage_design/coverage_metrics_v0.md`
- `experiments/20260705_215045/reports/P05-general-coverage-brief.md`
- `experiments/20260705_215045/plans/05-case-coverage-and-pilot-allocation.md`
- `experiments/20260705_215045/plans/06-teacher-examples-and-pilot-packet.md`
- `experiments/20260705_215045/roadmap.md`
- `README.md`

## Result summary

P05 đã chuyển từ tư duy “phân bổ đúng 20 mẫu pilot” sang ma trận bao phủ tổng quát. Artifact chính là `general_coverage_matrix_v0.csv` với 96 ô bao phủ: 4 task × 3 mức nhận thức × 8 cụm chủ đề SGK Tin học 9.

Ma trận có nhãn ưu tiên:

- `core`: nên lấy mẫu trước;
- `recommended`: nên lấy nếu cần cân bằng thêm;
- `optional`: bổ sung sau;
- `deferred`: tạm để sau.

P06 plan đã được chỉnh để dùng ma trận P05, không còn phụ thuộc vào file phân bổ 20 mẫu và không dùng `Vận dụng cao` trong v0.

## Orchestrator decision

Các câu hỏi mở P04 được coi là tạm chốt theo chỉ đạo “cứ làm đi, có gì bổ sung sau”. Nếu HNMU/giáo sư phản hồi khác, nên tạo revision/migration plan để cập nhật quy tắc hoặc mức ưu tiên của P05, không sửa ngầm artifact đã chốt.

## Uncertainty

- Tên chủ đề từ SGK Tin học 9 vẫn dựa trên OCR mục lục, cần HNMU/UET rà soát.
- Một số ô bao phủ tự nhiên hơn các ô khác; vì vậy P05 dùng `coverage_priority`, không coi mọi ô ngang nhau.
- Nhóm định dạng hiện là trục thiết kế, chưa phải schema cuối cùng của phiếu tác giả.

## Open questions and next human decisions

- Quân muốn P06 chọn bao nhiêu ví dụ đầu tiên từ các ô `core`?
- P06 nên ưu tiên ví dụ “đẹp, dễ hiểu” hay cố tình có thêm tình huống khó để giáo viên thấy biên của rubric?
- Nếu HNMU phản hồi lại P04, ta có cập nhật P05 ngay hay chờ sau pilot?
