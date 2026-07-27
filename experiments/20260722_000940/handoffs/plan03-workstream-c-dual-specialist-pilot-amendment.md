# Specialist handoff

- Delegation ID: `PLAN03-C-DUAL-SPECIALIST-PILOT-AMENDMENT-001`
- Agent: `benchmark-specification-designer` với `skill-creator` trong chế độ single-agent
- Status: `completed_with_blocker`
- Native thread ID/label: không có; specialist mới chưa được tạo hoặc chạy

## Delegation prompt

Sửa Workstream C để pilot đúng hai instance của `pedagogical-principle-annotator` chạy đồng thời trên cùng tập 40 mẫu và kiểm tra tính tái lập trước khi scale.

## Follow-up or steer messages

- `SKILL.md`/reference chỉ cần nêu trực tiếp đường dẫn tới tài liệu sáu nguyên tắc và sáu năng lực; không yêu cầu viện dẫn các đường dẫn ở từng dòng annotation.
- Hai instance phải dùng cùng input/tài liệu nhưng ghi vào hai vùng riêng và không nhìn output của nhau.
- Chỉ số AI–AI là tính tái lập liên-instance, không phải độ tin cậy giữa hai người chấm.

## Inputs read

- `README.md`, `ARCHITECTURE.md`, roadmap và Plan 03 hiện hành
- `agents/benchmark-specification-designer/SKILL.md`
- system skill `skill-creator`
- tài liệu sáu nguyên tắc và mô hình sáu năng lực hiện hành

## Outputs created or updated

- sửa Plan 03, roadmap, README và ARCHITECTURE;
- cập nhật paper-update packet và manifest Workstream C;
- tạo handoff và append coordination event.

## Result summary

Plan 03 nay có Cổng C0a để tạo/kiểm định specialist và Cổng C0b để chạy hai instance trên cùng lô 40, so sánh nhãn, đưa toàn bộ bất đồng cho UET và dừng đóng nếu không đạt ngưỡng đăng ký trước. Skill/reference phải nêu rõ đường dẫn tài liệu sáu nguyên tắc, codebook và ba file mô hình sáu năng lực.

## Blocker phát hiện trong khi đồng bộ

File active `outputs/benchmark_specification/task_discovery/task_discovery_codebook.md` hiện giống hệt bản tám nhiệm vụ legacy, SHA-256 `c3a6d242485e1d6e6f6dac5f4ef6235e41350278f4d7e8462c4364ff22b365e7`, trong khi manifest chờ bản sáu nguyên tắc SHA-256 `d87742644cddb5c82030a3bcc7918493336365071e9399118438bcd66ff430b8`. Không ghi đè file vì đây là thay đổi đồng thời ngoài phạm vi an toàn. Cổng C0a phải giữ đóng cho tới khi khôi phục/xác nhận đúng bản.

## Open questions and next human decisions

- Xác nhận hoặc khôi phục codebook sáu nguyên tắc tại đường dẫn active.
- Sau khi integrity gate đạt, cho phép triển khai specialist và pilot hai instance theo C0a–C0b.
