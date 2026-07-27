# Cổng UET trước pilot hai specialist — Workstream C

Trạng thái: **UET đã duyệt ví dụ và khóa đủ năm ngưỡng; miễn bước gán mù; cho phép chạy forward test rồi chạy A/B**.

## Quyết định UET ngày 27/07/2026

- Duyệt cả năm ví dụ biên dùng cho forward test.
- Khóa ngưỡng: nguyên tắc chính `1.00`; cặp chính–phụ `0.90`; Jaccard `0.90`; coverage gap `1.00`; tác động của reference `0.90`.
- Miễn việc gán mù 20 mẫu vì không đủ thời gian.
- UET chỉ review và phân xử sau khi đã có output A/B.

## Phạm vi review sau run

UET sẽ nhận một packet đã tổng hợp và cần xem:

1. mọi bất đồng A–B;
2. mọi coverage gap;
3. mọi xung đột giữa context và reference;
4. mọi đề xuất sửa ranh giới nguyên tắc;
5. ít nhất 8 trường hợp A/B đồng thuận được chọn xác định.

UET có quyền `accept`, `revise`, `reject` hoặc yêu cầu sửa codebook rồi chạy lại. Nhãn của agent luôn là đề xuất `needs_uet_review`, không phải nhãn đã xác nhận.

## Giới hạn diễn giải

Các metric A–B chỉ đo tính tái lập giữa hai lần chạy AI cùng cấu hình. Không có metric UET–AI trong pilot này và không được gọi kết quả A–B là độ tin cậy giữa hai người chấm.
