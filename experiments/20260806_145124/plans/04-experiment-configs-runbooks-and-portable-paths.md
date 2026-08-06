# Plan 04 — Config, runbook và path khả chuyển

Experiment: `20260806_145124`
Trạng thái: `DRAFT — AWAITING PLAN 03 COMPLETION AND PROJECT-LEAD APPROVAL`
Phụ thuộc: Plan 01–03

## 1. Mục tiêu

Tách cấu hình của từng experiment khỏi logic dùng lại và thay path tuyệt đối/
experiment ID hard-code bằng path được resolve rõ ràng từ repo root, config hoặc
CLI. Mỗi pipeline đại diện phải có một runbook đủ để con người vận hành.

## 2. Ranh giới

- `experiments/<id>/configs/`: model ID, dataset artifact ID/version, sampling,
  budget, output location và các tham số run; không chứa secret.
- `experiments/<id>/runbooks/`: precondition, exact command, resume, validate,
  expected output, failure/rollback và cleanup.
- `src/`: load/validate config và logic thực thi tái sử dụng.
- `scripts/`: parse CLI và gọi thư viện.

Một runbook mặc định cho mỗi plan có thao tác vận hành; chỉ tách thêm khi lifecycle
thực sự khác. Không lưu raw response hoặc phân tích kết quả trong runbook.

## 3. Phạm vi migration ưu tiên

- requirement scoring;
- tutor response generation;
- response judging/batch processing;
- analysis/validation offline của full 1.400.

Không cần sửa mọi script lịch sử trong một lượt. Inventory phân loại
`active`, `compatibility`, `historical-only` trước khi chọn target.

## 4. Hợp đồng config

Manifest của run phải ghi:

- config path/version/hash;
- canonical input artifact ID/version/hash;
- code commit nếu có;
- prompt/bundle version/hash;
- provider/model/location và tham số thực tế;
- output schema/version, timestamps, resume history và cost khi áp dụng.

Secret chỉ được lấy từ ADC/environment/secret manager đã quy định, không serialize
vào config, manifest, log hay handoff.

## 5. Các bước triển khai dự kiến

1. Quét absolute path, experiment ID và config constant trong code/wrapper.
2. Chọn schema config nhỏ cho từng pipeline ưu tiên.
3. Viết resolver repo root/canonical artifact và validator fail-closed.
4. Tạo config + runbook cho một run đại diện trước, rồi mở rộng có kiểm soát.
5. Chạy preflight offline từ repo root và một working directory khác.
6. So sánh request manifest/derived input với baseline, không gọi paid API.
7. Đánh dấu wrapper cũ compatibility/historical thay vì xóa ngay.

## 6. Phạm vi ghi dự kiến

- `experiments/20260806_145124/configs/` và `runbooks/`
- config tham chiếu cho active experiment khi được inventory cho phép
- package config/path modules, CLI mỏng và tests
- wrapper active có absolute path
- docs liên quan

## 7. Nghiệm thu

- Không có absolute path của máy người phát triển trong active runbook/wrapper.
- Preflight đại diện chạy từ ít nhất hai working directory và resolve cùng input.
- Config/manifest không chứa token, credential hay nội dung ADC.
- Thay experiment/config không yêu cầu sửa hằng số trong library.
- Resume chỉ xử lý pending ID và ghi lịch sử rõ ràng.
- Derived input/hash bằng baseline hoặc khác biệt được giải thích và duyệt.

## 8. Rủi ro và rollback

Path migration có thể âm thầm trỏ sang snapshot khác. Resolver phải fail-closed
trên checksum/count sai. Wrapper cũ được giữ trong thời gian compatibility để
rollback sau khi equivalence test thất bại.

## 9. Quyết định cần duyệt

- Pipeline nào là active và phải migrate trước.
- Format config chính (`yaml`, `toml` hoặc `json`) sau khi cân nhắc dependency.
- Thời hạn giữ compatibility wrapper.
