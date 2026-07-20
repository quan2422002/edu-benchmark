# Dữ liệu hội thoại thô HNMU

Thư mục này lưu dữ liệu hội thoại thô do đội ngũ giáo viên HNMU gửi cho dự án.

## Quy tắc sử dụng

1. Không sửa trực tiếp các file Excel gốc trong thư mục này.
2. Mọi bước đọc, kiểm toán, chuẩn hóa hoặc chuyển đổi phải tạo bản dẫn xuất ở nơi khác và giữ truy vết về file gốc.
3. Mỗi batch dữ liệu phải được đăng ký trong `manifest.csv`.
4. Nếu sau này cần sắp xếp lại file gốc vào thư mục con theo batch, cần làm bằng một plan riêng hoặc một bước đã được duyệt rõ ràng.

## Batch hiện tại

Hiện tại có các batch đã được đăng ký trong `manifest.csv`:

- `20260714_initial`: `Lớp 6.xlsx`, `Lớp 7.xlsx`;
- `20260718_grade8_9`: `Lớp 8.xlsx`, `Lớp 9.xlsx`.

Các file này được giữ nguyên tại vị trí hiện có để tránh làm gãy các đường dẫn hoặc thao tác đang dùng. `manifest.csv` là nguồn ghi nhận chính thức cho các batch này.

## Quan hệ với các plan sau

- Plan 04 sẽ đọc dữ liệu từ đây để kiểm toán độ phủ, thiếu trường, nhất quán và trùng/gần trùng.
- Plan 06 sẽ chỉ chuyển đổi các mẫu đã qua kiểm toán thành mẫu benchmark hoàn chỉnh.
