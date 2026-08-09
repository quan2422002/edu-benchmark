# Amendments — Plan 04

Experiment: `20260806_145124`
Baseline: `plans/04-experiment-configs-runbooks-and-portable-paths.md`

## P04-A001 — Chọn quy trình đại diện, định dạng cấu hình và thời hạn tương thích

- Thời điểm: `2026-08-09T10:43:56+07:00`
- Người duyệt: orchestrator, trong phạm vi Plan 04 đã được project lead duyệt
- Quyết định:
  - chọn quy trình phân tích Section V trên bộ 1.400 mẫu làm quy trình `active`
    được chuyển đổi đầu tiên;
  - dùng YAML làm định dạng cấu hình chính;
  - giữ các wrapper sinh và chấm full đã hoàn tất ở trạng thái `compatibility`
    hoặc `historical-only`; không xóa trong Plan 04;
  - giữ wrapper tương thích ít nhất đến gate đóng migration của Plan 07;
  - kiểm chứng lần chạy mới bằng ba input đã khóa và so sánh ngữ nghĩa với
    output Section V hiện có, cho phép duy nhất khác biệt đường dẫn tuyệt đối
    được chuẩn hóa thành đường dẫn tương đối theo repository.
- Lý do:
  - Section V là quy trình hiện hành có thể chạy hoàn toàn offline, không cần
    credential hoặc API trả phí;
  - output baseline và mã băm của ba input đều đã có, nên có thể kiểm chứng
    tương đương từ nhiều thư mục làm việc;
  - `PyYAML` đã là dependency trực tiếp của package, vì vậy YAML không làm tăng
    dependency;
  - các wrapper trả phí đã hoàn tất nhiệm vụ lịch sử và chứa trạng thái phục hồi
    riêng; chuyển đổi hàng loạt ngay trong Plan 04 làm tăng rủi ro ngoài gate
    đại diện.
- Ảnh hưởng: Plan 04 cài đặt hợp đồng cấu hình, bộ xác định đường dẫn, preflight,
  CLI và runbook cho Section V; inventory ghi rõ trạng thái của các pipeline còn
  lại để Plan 05–07 tiếp tục xử lý.
- Không thay đổi: dữ liệu benchmark, phán quyết model, thống kê Section V,
  wrapper lịch sử, credential, output trả phí hoặc phạm vi của Plan 05–07.
