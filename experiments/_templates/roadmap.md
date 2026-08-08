# Roadmap — <Tên experiment>

Experiment: `<YYYYMMDD_HHMMSS>`
Trạng thái: `PLANNING — AWAITING PLAN 01 APPROVAL`
Nguồn hiện trạng chính: `<experiment hoặc artifact nguồn>`

## 1. Mục tiêu

Nêu kết quả cuối cùng và giới hạn thẩm quyền của experiment.

## 2. Nguyên tắc triển khai

1. Chỉ triển khai plan có dòng trạng thái `APPROVED`.
2. Duyệt plan theo trình tự trong roadmap.
3. Giữ baseline ổn định sau approval; ghi thay đổi tình thế theo timeline.
4. Không xóa hoặc ghi đè dữ liệu nếu chưa có approval rõ ràng.

## 3. Kiến trúc hoặc workflow đích

Mô tả ngắn bằng prose, bảng hoặc sơ đồ khi quan hệ thực sự cần hình ảnh.

## 4. Trình tự plan

| Thứ tự | Plan | Trạng thái | Gate mở plan kế tiếp |
|---:|---|---|---|
| 01 | [Plan 01](plans/01-<name>.md) | `DRAFT` | <gate> |

## 5. Gate chung

- Approval, phạm vi ghi và rollback được xác nhận trước triển khai.
- Validation, status, coordination event và handoff được hoàn tất trước closeout.

## 6. Ngoài phạm vi

- <Nêu rõ những việc roadmap không cho phép.>

## 7. Cổng dừng hiện tại

Nêu plan duy nhất đang được phép xem xét hoặc triển khai.

