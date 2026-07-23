# Specialist handoff

- Delegation ID: `PLANS02-05-SINGLE-AGENT-001`
- Agent: orchestrator, single-agent mode; loaded `benchmark-specification-designer` and `teacher-collaboration-designer` skills
- Status: completed
- Native thread ID/label: không áp dụng

## Delegation prompt

Không có specialist delegation. Người phụ trách dự án yêu cầu soạn trước các plan tiếp theo trong khi review kết quả Plan 01.

## Follow-up or steer messages

Không có steer. Chỉ soạn tài liệu Plan 02–05 ở trạng thái `DRAFT`; không triển khai code, không chạy specialist và không tạo benchmark specification/teacher packet thật.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260722_000940/roadmap.md`
- Plan 01 và report Plan 01
- checklist benchmark candidate v0
- task/rubric/rationale và research matrices kế thừa
- learning-resource registry/fragment headers
- canonical skills và references của `benchmark-specification-designer`
- canonical skills và references của `teacher-collaboration-designer`

## Outputs created

- `plans/02-split-policy-and-full-benchmark-conversion.md`
- `plans/03-thcs-task-rubric-specification-and-coverage.md`
- `plans/04-benchmark-candidate-evidence-and-quality-audit.md`
- `plans/05-benchmark-pilot-and-hnmu-uet-review.md`
- cập nhật `roadmap.md` để ghi trạng thái, dependency và link.

## Result summary

Plan 02 đặt D02-01 trước full conversion và buộc disposition đủ 665 mẫu. Plan 03 migrate task/rubric sang THCS 6–9, thêm serious-error/provenance/research-ID alias và coverage. Plan 04 định nghĩa evidence cấp candidate tách khỏi raw-audit evidence và audit strict. Plan 05 tách packet-ready khỏi review-completed, có reviewer/adjudicator authority và không cho code tự điền quyết định người.

## Orchestrator decision

Giữ cả bốn plan ở trạng thái `DRAFT`. Không plan nào được triển khai trước khi người phụ trách review và đổi trạng thái thành `APPROVED`. Plan 02 vẫn cần quyết định split policy.

## Uncertainty

Chưa chốt policy cho 297 raw dialogue kết thúc bằng `HS`, quy mô/staffing pilot HNMU, release threshold và execution protocol cho semantic assignment/audit toàn batch. Hai lỗi vai trò khác đã được người phụ trách dự án quyết định sửa qua correction overlay sau handoff ban đầu.

## Open questions and next human decisions

1. Chọn phương án A/B/C tại D02-01.
2. Có duyệt một `benchmark-specification-designer` instance trong Plan 03/04 không?
3. Chốt kích thước, số reviewer và adjudication rule của Plan 05.
