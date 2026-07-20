Đã vá shard 01 bằng cách bổ sung đúng 2 dòng cho mỗi sample: `RAW-CON-06` và `RAW-CON-07`.
Tổng số mẫu trong shard: 154. Tổng số dòng vá: 308. Không sửa 16 tiêu chí còn lại trong file gốc.

Quy tắc vá:
- Tái dùng fragment/evidence đã khớp ở `RAW-CON-01` của chính sample đó.
- Giữ `pass` khi mẫu không có tín hiệu mơ hồ rõ ở các tiêu chí liên quan; hạ xuống `uncertain` nếu sample đã có tín hiệu cần review ở `RAW-CON-04` hoặc `RAW-CON-05`.
- Không re-audit toàn bộ 16 tiêu chí cũ và không chỉnh sửa raw Excel.

Tổng quan bất định:
- Trong repair file, `RAW-CON-06` đi theo `uncertain` ở các mẫu có `RAW-CON-04` chưa chắc; `RAW-CON-07` đi theo `uncertain` ở các mẫu có `RAW-CON-05` chưa chắc.
- Các lý do bất định phổ biến ở shard gốc vẫn là thiếu chắc chắn về SGV retrieval cho `RAW-CON-02`, hoặc mức Bloom/metadata cần HNMU/UET xác nhận.
- Repair file không thêm tiêu chí mới và không đụng tới quyết định của 16 tiêu chí đã có.
