# Specialist handoff

- Delegation ID: `P05-student-work-type-revision-024`
- Agent: `benchmark-specification-designer-single-agent-fallback`
- Status: `completed`
- Native thread ID/label: `null` — dùng skill trong parent thread, không spawn subagent ẩn.

## Delegation prompt

Bổ sung dạng bài làm của học sinh đã nêu trong P03 vào ma trận bao phủ tổng quát P05, sao cho phần này được thể hiện rõ ràng dù số dạng ban đầu còn ít.

## Follow-up or steer messages

- Không tăng số ô ma trận nếu không cần thiết.
- Tách `student_work_type` khỏi `format_family` để tránh lẫn task của tutor với vật liệu học sinh đưa vào hội thoại.
- Ưu tiên các dạng từ P03: khái niệm, trắc nghiệm, tự luận, sửa lỗi/code, thuật toán/chương trình; bổ sung bảng tính, sản phẩm số và tình huống đạo đức số do SGK Tin học 9 có các vùng này.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260705_215045/roadmap.md`
- `agents/benchmark-specification-designer/SKILL.md`
- `experiments/20260705_215045/plans/03-targeted-paper-review-bloom-tutoring.md`
- `experiments/20260705_215045/reports/P03-literature-synthesis-for-design.md`
- `experiments/20260705_215045/plans/05-case-coverage-and-pilot-allocation.md`
- `experiments/20260705_215045/coverage_design/coverage_axis_values_v0.csv`
- `experiments/20260705_215045/coverage_design/general_coverage_matrix_v0.csv`

## Outputs created

- Updated `experiments/20260705_215045/coverage_design/coverage_axis_values_v0.csv`
- Updated `experiments/20260705_215045/coverage_design/general_coverage_matrix_v0.csv`
- Updated `experiments/20260705_215045/coverage_design/coverage_summary_v0.csv`
- Updated `experiments/20260705_215045/coverage_design/coverage_matrix_readme_v0.md`
- Updated `experiments/20260705_215045/coverage_design/coverage_metrics_v0.md`
- Updated `experiments/20260705_215045/reports/P05-general-coverage-brief.md`
- Updated `experiments/20260705_215045/plans/05-case-coverage-and-pilot-allocation.md`
- Updated `experiments/20260705_215045/plans/06-teacher-examples-and-pilot-packet.md`
- Updated `experiments/20260705_215045/roadmap.md`

## Result summary

P05 now includes a clear `student_work_type` axis. The main matrix still has 96 coverage cells, but each row now includes:

- `primary_student_work_type`
- `secondary_student_work_type`
- `student_work_type_note`

This makes P06 more controllable because examples can now be selected not only by task/topic/cognitive level, but also by the kind of student work being submitted.

## Orchestrator decision

Do not expand the matrix into task × topic × cognitive level × every possible student work type yet. That would create too many artificial combinations. The v0 design keeps one primary and one secondary student-work type per coverage cell.

## Uncertainty

- The exact list of student-work types may need HNMU review after teachers begin writing examples.
- Some topic/task pairs can support multiple student-work types; P05 records a primary/secondary suggestion rather than a final exclusive label.

## Open questions and next human decisions

- Should P06 require at least one example for every `student_work_type`, or only for the common/core ones?
- Should teacher-facing labels use the code `SWTxx`, the Vietnamese label only, or both?
