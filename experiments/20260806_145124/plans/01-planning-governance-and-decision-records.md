# Plan 01 — Quản trị plan và bản ghi quyết định

Experiment: `20260806_145124`
Trạng thái: `APPROVED — 2026-08-06 — PROJECT LEAD`
Phụ thuộc: không

## 1. Mục tiêu

Thiết lập một quy trình plan cô đọng: con người đọc baseline và timeline;
máy đọc status cùng quan hệ chi tiết. Quy trình phải chấp nhận việc triển khai
thực tế phát sinh thay đổi mà không viết lại lịch sử hoặc biến plan thành nhật
ký dài hàng nghìn dòng.

## 2. Phạm vi được duyệt khi plan chuyển sang `APPROVED`

- Chuẩn hóa template cho roadmap, plan, status, amendment, final report,
  runbook, coordination event và handoff.
- Tạo ADR cho ba quyết định dài hạn:
  - ranh giới `src/`–`scripts/`;
  - promotion artifact từ experiment sang `shared/`;
  - baseline/status/amendment và retention output.
- Bổ sung validator nhẹ cho metadata/status/link và artifact budget.
- Cập nhật hướng dẫn agent để plan mới dùng chuẩn này; không hồi tố viết lại
  toàn bộ experiment cũ.

## 3. Mô hình tài liệu

```text
plans/NN-<name>.md             baseline; ổn định sau approval
plans/NN-status.yaml           trạng thái máy đọc; thay đổi khi thực thi
decisions/planNN-amendments.md timeline thay đổi tình thế
reports/planNN-final.md         kết quả chốt so với baseline
```

`NN-status.yaml` chỉ giữ trường tối thiểu: plan ID, trạng thái, baseline path,
thời điểm cập nhật, current step, last amendment, gate và artifact chính.
Quan hệ chi tiết là tùy chọn cho máy đọc, không trở thành phần bắt buộc người
duyệt phải học.

Amendment được đánh số khi phát sinh, không lập sẵn danh sách work package.
Mỗi mục chỉ trả lời: khi nào, quyết định gì, vì sao, ảnh hưởng gì, ai duyệt.

## 4. Artifact budget

Mặc định cho mỗi plan:

- một baseline plan;
- một status YAML;
- một amendment log chỉ khi có thay đổi;
- một runbook khi có thao tác vận hành;
- một final report và một handoff tại gate;
- output máy đọc chỉ khi code hoặc reviewer thực sự tiêu thụ.

File mới vượt budget phải được giải thích trong plan/amendment. Không tạo cùng
một nội dung dưới dạng raw, normalized, report và snapshot nếu có thể dựng lại.

## 5. Các bước triển khai dự kiến

1. Inventory template, quy tắc status và lối ghi coordination hiện hữu.
2. Chốt vocabulary trạng thái nhỏ, có mapping cho trạng thái lịch sử.
3. Viết template/schema/validator và ADR.
4. Áp dụng thử vào chính experiment `20260806_145124`.
5. Cập nhật `AGENTS.md`, `README.md`, `ARCHITECTURE.md` ở mức cần thiết.
6. Chạy validation; lập báo cáo khác biệt trước/sau.

## 6. Phạm vi ghi dự kiến

- `experiments/_templates/`
- `docs/decisions/`
- `scripts/` hoặc `src/edu_benchmark/` cho validator nhỏ đã được chốt
- `tests/` tương ứng
- `experiments/20260806_145124/`
- `AGENTS.md`, `README.md`, `ARCHITECTURE.md`

Không sửa baseline plan của experiment cũ chỉ để đồng nhất hình thức.

## 7. Nghiệm thu

- Một người đọc biết plan nào trước/sau từ roadmap mà không đọc metadata máy.
- Một validator xác định được plan được phép triển khai hay chưa.
- Thay đổi tình thế có thể thêm bằng `Pxx-A001` mà không sửa baseline.
- Schema không ép xác định trước số bước/amendment.
- Template/hướng dẫn không mâu thuẫn với quy tắc `APPROVED` trong `AGENTS.md`.
- Plan 02–07 của experiment này có thể chuyển sang quy trình mới mà không tạo
  thêm đồ thị quan hệ dành cho con người.

## 8. Rủi ro và rollback

Rủi ro chính là tạo thêm giấy tờ thay vì giảm chúng. Nếu thử nghiệm vượt artifact
budget hoặc làm việc duyệt khó hơn, rollback bằng cách giữ roadmap + plan +
handoff hiện hành và không áp template mới sang experiment khác.

## 9. Quyết định cần duyệt

Project lead duyệt hoặc yêu cầu sửa Plan 01. Duyệt Plan 01 chỉ cho phép triển
khai cơ chế quản trị trên; không cho phép bắt đầu packaging hay di chuyển dữ liệu.
