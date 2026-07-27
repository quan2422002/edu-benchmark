# Bàn giao bổ sung điều hướng tài liệu trong skill

- Delegation ID: `PLAN03-SKILL-DOCUMENT-ROUTING-001`
- Agent: `benchmark-specification-designer` với `skill-creator` trong chế độ single-agent
- Status: `completed`
- Native thread ID/label: không có; không mở subagent

## Delegation prompt

Làm rõ rằng các tài liệu quan trọng chỉ cần được nêu bằng đường dẫn trong skill hoặc tài liệu tham chiếu; không cần gộp chúng thành một nguồn viện dẫn hay sao chép nội dung.

## Follow-up or steer messages

- Ví dụ áp dụng hiện tại gồm tài liệu mô tả sáu nguyên tắc sư phạm và mô hình sáu năng lực gia sư.
- Đường dẫn chỉ phục vụ điều hướng.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `agents/benchmark-specification-designer/SKILL.md`
- system skill `skill-creator`
- `experiments/20260722_000940/plans/03-thcs-task-rubric-specification-and-coverage.md`
- các artifact canonical của sáu nguyên tắc và sáu năng lực

## Outputs created

- cập nhật `agents/benchmark-specification-designer/SKILL.md`;
- cập nhật yêu cầu tạo `pedagogical-principle-annotator` trong Plan 03;
- tạo handoff và append coordination event này.

## Result summary

Skill thiết kế đặc tả hiện nêu trực tiếp ba đường dẫn: bảng sáu nguyên tắc, tài liệu mô hình sáu năng lực và bảng định nghĩa/anchor năng lực. Plan 03 yêu cầu specialist mới cũng phải nêu các đường dẫn đó trong `SKILL.md` hoặc tài liệu tham chiếu được liên kết trực tiếp.

Nội dung mới nói rõ đây là bản đồ điều hướng, không phải tuyên bố hai hệ là cùng một khái niệm đo lường hoặc cùng một nguồn căn cứ. Không sao chép định nghĩa vào skill.

## Orchestrator decision

Chấp nhận chỉnh sửa ở mức điều hướng tài liệu. Không thay đổi kiến trúc một nhiệm vụ–sáu nguyên tắc–sáu năng lực và chưa tạo specialist mới.

## Uncertainty

Không có bất định về đường dẫn hiện tại. Nếu experiment hoặc vị trí artifact canonical thay đổi, skill và manifest phải được cập nhật đồng thời.

## Open questions and next human decisions

- Người phụ trách dự án quyết định thời điểm triển khai Cổng C0 và tạo `pedagogical-principle-annotator`.
