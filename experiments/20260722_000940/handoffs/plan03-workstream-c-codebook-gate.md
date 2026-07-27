> **ĐÃ BỊ THAY THẾ NGÀY 26/07/2026.** Handoff này chỉ mô tả nhánh tám nhiệm vụ lịch sử. Toàn bộ artifact liên quan đã chuyển tới `outputs/benchmark_specification/legacy/eight_task_candidate_branch/`; không còn cổng UET nào chờ duyệt nhánh này. Kiến trúc hiện hành dùng một nhiệm vụ, sáu nguyên tắc KMP và sáu năng lực.

# Bàn giao Cổng C1 — Workstream C

- Delegation ID: `PLAN03-C-CODEBOOK-GATE-001`
- Agent: `benchmark-specification-designer` trong chế độ single-agent; áp dụng thêm skill `teacher-collaboration-designer`
- Status: `waiting_uet_review`
- Native thread ID/label: không có; không mở subagent

## Delegation prompt

Triển khai Workstream C theo Plan 03 đã duyệt và dừng khi đến phần cần đại diện UET rà soát.

## Follow-up or steer messages

Không có. Phạm vi được khóa ở Bước C1 vì plan yêu cầu UET duyệt sổ tay mã hóa trước khi AI mã hóa chính thức lô 40 đầu tiên.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260722_000940/roadmap.md`
- `experiments/20260722_000940/plans/03-thcs-task-rubric-specification-and-coverage.md`
- `agents/benchmark-specification-designer/SKILL.md` và các reference liên quan
- `agents/teacher-collaboration-designer/SKILL.md` và các reference liên quan
- `experiments/20260722_000940/literature_notes/pre_plan03_task_rubric_review/`
- `experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/`
- `experiments/20260722_000940/outputs/benchmark_specification/task_discovery/`
- `experiments/20260722_000940/outputs/benchmark_specification/specialist_draft/task_discovery/`

## Outputs created

- `outputs/benchmark_specification/task_discovery/benchmark_tasks.csv`
- `outputs/benchmark_specification/task_discovery/task_discovery_codebook.md`
- `outputs/benchmark_specification/task_discovery/task_candidate_matrix.csv`
- `outputs/benchmark_specification/teacher_review_packets/workstream_c_codebook_gate/`
- `outputs/benchmark_specification/plan03_workstream_c_c1_manifest.json`
- bộ kiểm tra và bài kiểm thử cho cổng sổ tay trong `src/edu_benchmark/benchmark_specification/teacher_packet.py` và `tests/benchmark_specification/test_teacher_packet.py`

## Result summary

Bước C1 đã tạo tám nhiệm vụ hạt giống ở trạng thái `needs_uet_review`, bảy quy tắc ranh giới, ví dụ đạt, phản ví dụ và một trường hợp chưa phân loại. Căn cứ nghiên cứu được trình bày cùng giới hạn, đặc biệt không mặc nhiên coi `TASK-DIAG`, `TASK-MODEL` và `TASK-PRACTICE` là nhiệm vụ độc lập.

Gói UET có tám dòng quyết định nhiệm vụ, bảy dòng quyết định ranh giới và một quyết định toàn sổ tay. Bộ kiểm tra đóng khi lỗi nếu thiếu nhiệm vụ, thiếu ranh giới, sai cấu trúc, điền dở quyết định ban đầu hoặc dùng mã người rà soát không hợp lệ.

Số ứng viên mã hóa chính thức là 0. Hai mươi nhãn thử có trước C1 được giữ để truy vết nhưng manifest loại chúng khỏi kết quả mã hóa, hiệu chỉnh, độ phủ và bão hòa.

## Orchestrator decision

Dừng tại cổng UET đúng yêu cầu. Không mở Bước C2 và không mã hóa lô 40 trước khi `UET-REVIEWER-01` duyệt hoặc yêu cầu sửa sổ tay.

## Uncertainty

- `TASK-DIAG` có căn cứ cho hành vi chẩn đoán, nhưng chưa chắc tạo một nhiệm vụ độc lập trong phản hồi mở.
- `TASK-MODEL` có thể là chiến lược của giải thích hoặc dàn giáo.
- `TASK-PRACTICE` có căn cứ lý thuyết nhưng chưa có số liệu bao phủ chính thức.
- Các ví dụ `DIAG`, `MODEL`, `PRACTICE` hiện là ví dụ minh họa; lô khám phá phải kiểm chúng trên ứng viên thật.

## Open questions and next human decisions

1. UET giữ, sửa, gộp hay chuyển từng nhiệm vụ hạt giống thành hành vi phụ?
2. Bảy ranh giới đã đủ rõ để dùng mà không dựa vào `gold_response` chưa?
3. UET có cho phép mở lô 40 đầu tiên, cho phép có điều kiện hay yêu cầu sửa sổ tay trước?
