# Specialist handoff

- Delegation ID: `PLAN03-C-SPECIALIST-PLAN-AMENDMENT-001`
- Agent: `benchmark-specification-designer` với `skill-creator` trong chế độ single-agent
- Status: `completed`
- Native thread ID/label: không có; chưa tạo hoặc chạy specialist mới

## Delegation prompt

Bổ sung việc tạo một specialist riêng để gán sáu nguyên tắc sư phạm vào Workstream C của Plan 03.

## Follow-up or steer messages

- Specialist chỉ áp dụng codebook, không sở hữu hoặc sửa codebook.
- Phải tách vật lý context vòng 1 khỏi gold/reference vòng 2.
- Chưa mã hóa lô 40 trong thay đổi plan này.

## Inputs read

- `README.md`, `ARCHITECTURE.md`, roadmap và Plan 03 hiện hành
- `agents/benchmark-specification-designer/SKILL.md`
- system skill `skill-creator`
- quy ước specialist/adapters/tests hiện có trong repository

## Outputs created

- sửa `plans/03-thcs-task-rubric-specification-and-coverage.md`;
- sửa `roadmap.md`, `README.md`, `ARCHITECTURE.md`;
- cập nhật manifest trạng thái Workstream C và paper-update packet;
- tạo handoff và append coordination event này.

## Result summary

Plan 03 có thêm Bước 8.3.2 và Cổng C0 để tạo `pedagogical-principle-annotator`. Plan chỉ rõ cấu trúc skill/adapter, model `gpt-5.4-mini` reasoning `medium`, ownership tách khỏi agent thiết kế, hai input context/reference, ba output pass1/final/review queue, validator/test, forward test và quyền quyết định UET/HNMU.

## Orchestrator decision

Trạng thái chuyển từ `WORKSTREAM_C_READY_FOR_PRINCIPLE_CODING` thành `WORKSTREAM_C_SPECIALIST_CREATION_PENDING`. Specialist phải được tạo và đạt Cổng C0 trước khi bất kỳ dòng nào trong lô 40 được tính là nhãn chính thức.

## Uncertainty

- Specialist chưa được tạo hoặc forward-test.
- Schema chi tiết của review queue sẽ được khóa khi triển khai C0.
- Việc tách agent thiết kế và agent gán nhãn không tạo ra hai người chấm độc lập nếu cùng dùng một họ LLM.

## Open questions and next human decisions

- Người phụ trách dự án cho phép triển khai Cổng C0 theo plan đã bổ sung.
- UET duyệt bộ ví dụ biên dùng cho forward test trước lô 40.
