# Dữ liệu hội thoại thô HNMU

Thư mục này lưu dữ liệu hội thoại thô do đội ngũ giáo viên HNMU gửi cho dự án.

## Quy tắc sử dụng

1. Không sửa trực tiếp các file Excel gốc trong thư mục này.
2. Mọi bước đọc, kiểm toán, chuẩn hóa hoặc chuyển đổi phải tạo bản dẫn xuất ở nơi khác và giữ truy vết về file gốc.
3. Mỗi batch dữ liệu phải được đăng ký trong `manifest.csv`.
4. Nếu sau này cần sắp xếp lại file gốc vào thư mục con theo batch, cần làm bằng một plan riêng hoặc một bước đã được duyệt rõ ràng.

## Batch hiện tại

Hiện tại có batch ban đầu gồm:

- `Lớp 6.xlsx`
- `Lớp 7.xlsx`

Hai file này được giữ nguyên tại vị trí hiện có để tránh làm gãy các đường dẫn hoặc thao tác đang dùng. `manifest.csv` là nguồn ghi nhận chính thức cho batch này.

## Quan hệ với các plan sau

- Plan 04 sẽ đọc dữ liệu từ đây để kiểm toán độ phủ, thiếu trường, nhất quán và trùng/gần trùng.
- Plan 06 sẽ chỉ chuyển đổi các mẫu đã qua kiểm toán thành mẫu benchmark hoàn chỉnh.
