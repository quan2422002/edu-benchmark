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

## P04-A002 — Hoàn thiện inventory và bảo toàn manifest đã hoàn tất

- Thời điểm: `2026-08-09T17:37:50+07:00`
- Người duyệt: project lead yêu cầu xử lý nốt sau khi audit Plan 04
- Quyết định:
  - mở rộng inventory hiện có để phân loại toàn bộ entrypoint Python/shell của
    bốn quy trình ưu tiên, nhưng không chuyển đổi, chạy lại hoặc xóa các
    entrypoint lịch sử;
  - `preflight` không ghi đè một run manifest đã có trạng thái `completed`;
  - `validate` phải tính lại preflight fingerprint và đối chiếu config, input,
    output, code provenance, resume, equivalence, secret scan và result hash với
    manifest đã lưu;
  - bổ sung test cho inventory đầy đủ, bảo toàn manifest, code drift và manifest
    provenance bị sửa.
- Lý do: audit closeout phát hiện inventory mới bao phủ 9 entrypoint và
  `preflight` có thể hạ manifest `completed` về `preflight_passed`; đồng thời
  `validate` chưa phát hiện code provenance thay đổi sau lần chạy.
- Ảnh hưởng: Plan 04 giữ nguyên một machine-output inventory và một run manifest,
  không tăng artifact budget; output Section V được dựng lại offline để cập nhật
  fingerprint sau khi runtime thay đổi.
- Không thay đổi: dữ liệu benchmark, phép tính Section V, baseline ngữ nghĩa,
  wrapper lịch sử, provider, credential hoặc phạm vi Plan 05.

## P04-A003 — Hoàn thiện điều kiện pass của preflight

- Thời điểm: `2026-08-10T00:09:15+07:00`
- Người duyệt: project lead yêu cầu cài đặt hoàn chỉnh sau khi rà trạng thái
  `preflight_passed`
- Quyết định:
  - dùng một validator contract chung trước cả `preflight` và `run`;
  - chỉ cho phép `preflight_passed` sau khi pipeline, execution, đúng ba input
    role/format, output schema, resume policy, parameter và provenance offline
    đều hợp lệ;
  - bắt buộc runner được ghi trong `provenance.code_paths` để fingerprint bao
    phủ cả entrypoint;
  - lỗi CLI trả JSON có trạng thái `<command>_failed` và exit code `2`;
  - khi bảo toàn manifest `completed`, preflight công bố riêng manifest đó đang
    khớp (`matched_preserved`) hay đã cũ (`stale_preserved`) so với fingerprint
    hiện tại.
- Lý do: các kiểm tra `pipeline_id` và parameter trước đây chỉ chạy trong
  `run`, nên một config không thể thực thi vẫn có thể nhận
  `preflight_passed`; cờ bảo toàn manifest cũng chưa nói manifest cũ có khớp
  contract hiện tại hay không.
- Ảnh hưởng: cấu hình Section V đăng ký thêm compatibility entrypoint vào code
  provenance; run offline được dựng lại để khóa config/fingerprint mới. Không
  tạo thêm loại artifact.
- Không thay đổi: input benchmark, phép tính và semantic hash Section V,
  provider, credential, wrapper lịch sử hoặc phạm vi Plan 05.
