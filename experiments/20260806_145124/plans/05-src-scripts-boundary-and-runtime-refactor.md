# Plan 05 — Tách ranh giới `src/` và `scripts/`

Experiment: `20260806_145124`
Trạng thái: `DRAFT — AWAITING PLAN 04 COMPLETION AND PROJECT-LEAD APPROVAL`
Phụ thuộc: Plan 01–04

## 1. Mục tiêu

Loại bỏ sự nhập nhằng chức năng giữa `src/` và `scripts/`: thư viện chịu trách
nhiệm cho logic có thể test/tái sử dụng; script chỉ làm giao diện dòng lệnh và
điều phối một thao tác cụ thể.

## 2. Quy tắc ownership đích

`src/edu_benchmark/` chứa:

- model/domain types, schema và validator;
- transformation, scoring, aggregation và analysis;
- provider adapter, retry/resume/budget policy dùng lại;
- config/path loading không gắn một experiment cụ thể.

`scripts/` chứa:

- `argparse`/CLI help và lựa chọn subcommand;
- load config, gọi đúng hàm library, ánh xạ exit code;
- thông báo tiến độ cấp command.

Script không giữ prompt, thuật toán nghiệp vụ, provider lifecycle phức tạp,
absolute path hoặc experiment ID. Mục tiêu tham khảo là khoảng 100–150 dòng cho
CLI mới, nhưng cohesion/testability quan trọng hơn giới hạn cơ học.

## 3. Migration ưu tiên

- Hợp nhất `src/vertex_ai_call/` vào namespace phù hợp, dự kiến
  `src/edu_benchmark/requirement_scoring/` và provider modules liên quan.
- Tách runner evaluation/judge lớn thành domain service, provider adapter,
  persistence/resume và CLI.
- Dùng code dùng chung cho validation/join/manifest thay vì bản sao trong nhiều
  script.
- Giữ thin compatibility wrapper cho command đã được runbook hoặc người dùng gọi.

Tên module cuối cùng phải dựa trên import/call graph ở đầu plan, không áp đặt chỉ
từ tên thư mục hiện tại.

## 4. Các bước triển khai dự kiến

1. Lập inventory file, LOC, import/call graph, command và consumer.
2. Phân loại từng file: library, CLI, experiment-specific hoặc historical.
3. Chốt public API và compatibility matrix trước khi move.
4. Refactor từng vertical slice; test trước/sau mỗi slice.
5. Chuyển runbook/config sang entry point mới.
6. Deprecate wrapper cũ có thông báo; chưa xóa trong plan nếu chưa hết window.
7. Cập nhật kiến trúc và ownership map sau khi code thực sự ổn định.

## 5. Phạm vi ghi dự kiến

- `src/edu_benchmark/`
- `src/vertex_ai_call/` trong phạm vi migration đã duyệt
- `scripts/`
- `tests/`
- packaging entry points nếu cần
- configs/runbooks/docs và artifact Plan 05

## 6. Nghiệm thu

- Logic nghiệp vụ chính có thể gọi trực tiếp từ package mà không chạy subprocess.
- CLI đại diện chủ yếu parse/dispatch và có unit/integration test.
- Không có prompt/config experiment bị copy vào source constant.
- Compatibility commands đã công bố vẫn chạy hoặc có migration message rõ ràng.
- Offline equivalence test giữ nguyên candidate ordering, request hash, output
  schema và metric cho fixture đại diện.
- Active module ownership được phản ánh trong `ARCHITECTURE.md`.

## 7. Rủi ro và rollback

Move hàng loạt dễ làm mất lịch sử hành vi và phá command cá nhân. Migration theo
vertical slice, giữ import shim/CLI wrapper có thời hạn và không xóa file nguồn
cho đến khi consumer audit đạt.

## 8. Quyết định cần duyệt

- Public CLI names và compatibility window.
- Module boundary cuối cùng sau inventory.
- Script historical nào chỉ ghi tài liệu, script nào cần migrate thật.
