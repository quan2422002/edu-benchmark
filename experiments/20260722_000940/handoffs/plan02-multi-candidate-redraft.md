# Specialist handoff

- Delegation ID: `PLAN02-REDRAFT-SINGLE-AGENT-001`
- Agent: orchestrator, single-agent mode; loaded `benchmark-specification-designer`
- Status: completed
- Native thread ID/label: không áp dụng

## Delegation prompt

Không có specialist delegation. Người phụ trách dự án yêu cầu xác nhận Plan 01 đã hoàn thành và cập nhật Plan 02 theo contract multi-candidate vừa trao đổi.

## Follow-up or steer messages

Phạm vi được giới hạn ở đúng 665 raw dialogue `pass`. Mỗi lượt AI tạo một candidate; lượt HS cuối không được dùng trong benchmark candidate; không thêm outcome column; task/rubric filtering thuộc Plan 03.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260722_000940/roadmap.md`
- Plan 01, report Plan 01 và output conversion hiện hành
- Plan 02 cũ
- `experiments/20260709_155523/reports/three-paper-benchmark-use-synthesis.md`
- `experiments/20260705_215045/literature_notes/paper_summaries/P03-P002-kmp-bench.md`
- canonical skill và schema/rubric/provenance references của `benchmark-specification-designer`

## Outputs created

- viết lại `plans/02-split-policy-and-full-benchmark-conversion.md` ở trạng thái `DRAFT`;
- cập nhật `roadmap.md`, `README.md` và `ARCHITECTURE.md` để phản ánh contract dự kiến;
- tạo handoff này và append coordination event.

## Result summary

Plan 02 cũ phân nhánh 368 strict-compatible và 297 trailing-HS, đồng thời giới hạn một candidate trên raw dialogue. Bản mới thay bằng `each_tutor_turn`: 665 raw dialogue `pass` dự kiến sinh 2.028 candidate sơ bộ, candidate content nằm trong CSV gọn và provenance/correction nằm trong trace riêng. Migration pilot 20 raw dialogue là gate bắt buộc trước full conversion.

## Orchestrator decision

Giữ Plan 02 ở trạng thái `DRAFT`; không triển khai code hay tạo output Plan 02 trước khi người phụ trách dự án review và đổi plan sang `APPROVED`.

Phân loại căn cứ:

- bằng chứng nghiên cứu trực tiếp: đánh giá một tutor response trong context cố định và dùng tutor turn làm reference;
- suy luận/quyết định thiết kế dự án: tạo candidate ở mọi lượt AI, schema gọn, candidate-family grouping;
- thẩm quyền con người ở plan sau: task/rubric suitability, chất lượng sư phạm và quyết định giữ/loại cuối.

## Uncertainty

Pool 2.028 candidate là baseline kỹ thuật trước assignment/audit. Chưa biết bao nhiêu candidate sẽ khớp task/rubric hoặc đạt chuẩn benchmark sau Plan 03–05.

## Open questions and next human decisions

1. Người phụ trách dự án duyệt hoặc yêu cầu sửa Plan 02.
2. Sau khi duyệt, ghi D02-01 và chạy migration pilot trước full conversion.
3. Khi review Plan 03, chốt assignment disposition và cách tính family-level coverage/weighting.
