# Plan 07 — Đồng bộ tài liệu, validation và đóng migration

Experiment: `20260806_145124`
Trạng thái: `DRAFT — AWAITING PLAN 06 COMPLETION AND PROJECT-LEAD APPROVAL`
Phụ thuộc: Plan 01–06

## 1. Mục tiêu

Chứng minh cải tổ hoạt động như một hệ thống hoàn chỉnh, sau đó đồng bộ tài liệu
theo hiện trạng thật và đóng experiment bằng báo cáo ngắn gọn. Plan này không
dùng tài liệu để tuyên bố trước những migration chưa hoàn tất.

## 2. Phạm vi

- Reconcile `README.md`, `ARCHITECTURE.md`, active roadmap và ownership map.
- Viết onboarding cho người và routing instructions cho orchestrator.
- Kiểm link, metadata, registry, import, CLI, config/runbook và retention policy.
- Thực hiện clean-environment/clean-clone drill trong phạm vi không cần secret.
- Lập deprecation list và backlog còn lại thay vì kéo dài experiment vô hạn.
- Tạo final report so sánh kết quả với mục tiêu Roadmap và đóng handoff.

## 3. Tài liệu đích

- `README.md`: cách bắt đầu, artifact chuẩn ở đâu, command offline cốt lõi,
  experiment nào đang active.
- `ARCHITECTURE.md`: component/runtime/ownership hiện có hiệu lực.
- `docs/decisions/`: vì sao kiến trúc chọn như vậy, không phải trạng thái run.
- roadmap: thứ tự/gate và trạng thái cấp cao.
- final report: baseline, thay đổi đã triển khai, validation, ngoại lệ và backlog.

## 4. Validation matrix

Tối thiểu phải kiểm:

- package install/import bằng `benchmark_env`;
- unit/integration test offline và validator schema/link;
- canonical artifact counts/checksums/joins;
- representative CLI preflight từ repo root;
- restore drill cho ít nhất một externalized output nếu Plan 06 có externalize;
- secret scan và large-file scan;
- link từ README → registry → manifest → source provenance;
- không có tài liệu gọi provisional artifact là đã được HNMU/UET xác nhận.

## 5. Các bước triển khai dự kiến

1. Chụp trạng thái sau Plan 06 và danh sách acceptance còn mở.
2. Chạy validation matrix, sửa lỗi thuộc phạm vi migration.
3. Reconcile tài liệu từ bằng chứng đã chạy.
4. Thực hiện clean-environment drill và ghi exact commands/interpreter.
5. Lập backlog có owner/gate cho việc không chặn closeout.
6. Viết `reports/plan07-final.md`, handoff và đề xuất trạng thái experiment.

## 6. Phạm vi ghi dự kiến

- `README.md`, `ARCHITECTURE.md`, `AGENTS.md` nếu routing thực tế thay đổi
- docs/decision và documentation gần component
- test/validator chỉ để sửa lỗi closeout đã xác định
- experiment artifacts Plan 07

## 7. Nghiệm thu

- Một người mới có thể tìm canonical 665/2.028/1.400 và hiểu status trong không
  quá ba lần chuyển link từ README.
- Agent có thể chọn đúng `src`, `scripts`, config, runbook và shared/experiment
  ownership từ tài liệu hiện hành.
- Clean-environment drill offline đạt hoặc mọi phần không đạt có blocker rõ ràng.
- README, ARCHITECTURE và roadmap không mâu thuẫn về plan/status/component.
- Final report nêu cả phần chưa làm, không biến backlog thành completed.
- Không còn plan nào được tự động đánh dấu approved/complete thiếu bằng chứng.

## 8. Rủi ro và rollback

Closeout dễ biến thành một vòng refactor mới. Chỉ sửa defect chặn acceptance;
thay đổi tính năng mới được đưa vào backlog/experiment sau. Tài liệu có thể
rollback theo commit nếu không phản ánh đúng code đã validation.

## 9. Quyết định cần duyệt

- Tiêu chí nào chặn đóng experiment và tiêu chí nào được đưa vào backlog.
- Trạng thái cuối (`completed`, `completed_with_backlog` hoặc trạng thái khác theo
  vocabulary Plan 01).
- Experiment kế tiếp, nếu cần, chỉ được tạo sau final review.
