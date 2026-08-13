# Plan 06 — Quản lý đầu ra, khử trùng lặp và vệ sinh kho mã nguồn

Experiment: `20260806_145124`
Trạng thái: `APPROVED — 2026-08-12 — PROJECT LEAD`
Phụ thuộc: Plan 01–05

## 1. Mục tiêu

Giảm số lượng tệp và dung lượng Git mà không làm mất nguồn gốc dữ liệu, khả năng
tái lập hoặc sản phẩm duy nhất. Kế hoạch này đặc biệt xử lý các tệp JSONL lớn,
bản chụp lặp, tệp tạm, nhật ký chạy và đầu ra có thể dựng lại.

## 2. Phân lớp sản phẩm


| Phân lớp                                            | Ví dụ                                                                               | Chính sách đích                                                                                             |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Sản phẩm dùng chung chuẩn                         | Sổ đăng ký, tập lựa chọn và đặc tả đã được đưa vào kho dùng chung | Theo dõi theo phiên bản trong Git nếu quyền truy cập và dung lượng cho phép                           |
| Tệp kê khai phục vụ tái lập                     | Cấu hình, mã kiểm tra, số lượng, chi phí và lược đồ                      | Theo dõi trong Git                                                                                             |
| Báo cáo dành cho người đọc                     | Phân tích, kết luận tại cổng duyệt và báo cáo cuối                         | Theo dõi trong Git và giữ cô đọng                                                                         |
| Đầu ra thô hoặc đầu ra lớn của nhà cung cấp | Đầu vào/đầu ra theo lô và tệp JSONL lớn của lần chạy                      | Bỏ qua trong Git hoặc chuyển sang kho đối tượng bên ngoài; theo dõi địa chỉ lưu và mã kiểm tra |
| Sản phẩm dẫn xuất có thể dựng lại             | Bảng kết nối dữ liệu, bộ nhớ đệm và yêu cầu được sinh tự động       | Không theo dõi trong Git nếu có thể dựng lại một cách xác định                                      |
| Tệp tạm thời                                       | `.orig`, nhật ký chạy, tệp tạm và bộ nhớ đệm `xdv`                          | Bỏ qua trong Git; chỉ dọn sau khi được duyệt                                                             |
| Bằng chứng lịch sử duy nhất                      | Bằng chứng cũ không còn thành phần nào sử dụng trực tiếp                  | Lưu trữ kèm tệp kê khai; không xóa chỉ dựa trên tên hoặc cảm nhận                                 |

Git LFS chỉ được cân nhắc khi dự án thực sự cần quản lý phiên bản của dữ liệu
lớn ngay trong Git; không dùng Git LFS để thay thế việc phân loại đầu ra thô,
sản phẩm dẫn xuất và sản phẩm chuẩn.

## 3. Quy tắc an toàn

- Lập bảng kiểm kê dung lượng, mã kiểm tra, trạng thái được/không được Git theo dõi
  và mọi nơi đang tham chiếu trước khi dọn dẹp.
- Xác nhận việc đưa sản phẩm vào kho dùng chung và chuyển các thành phần sử dụng
  sang đường dẫn mới đã hoàn tất.
- Tạo bản lưu trữ hoặc bản sao lưu, ghi địa chỉ lưu và kiểm chứng mã kiểm tra trước
  khi bỏ bản nằm trong kho mã nguồn.
- Mọi thao tác xóa hoặc viết lại lịch sử Git là một quyết định phá hủy riêng,
  cần người phụ trách dự án phê duyệt chính xác đường dẫn đích và cách khôi phục.
- Kế hoạch được `APPROVED` không mặc nhiên cho phép `git filter-repo`, xóa kho
  từ xa (`remote`) hoặc xóa toàn bộ đầu ra cũ.

## 4. Các bước triển khai dự kiến

1. Lập bảng kiểm kê theo dung lượng, loại tệp, mã kiểm tra, thành phần sử dụng và
   trạng thái hiện tại.
2. Phát hiện nội dung trùng lặp và các tệp có thể dựng lại.
3. Đề xuất bảng chính sách lưu giữ cho từng đường dẫn đích, kèm dung lượng dự
   kiến có thể giải phóng.
4. Trình duyệt riêng từng hành động: giữ nguyên (`keep`), đưa vào kho dùng chung
   (`promote`), chuyển ra kho ngoài (`externalize`), lưu trữ (`archive`) hoặc xóa
   (`delete`).
5. Cập nhật `.gitignore` theo đúng từng thư mục đầu ra; không dùng mẫu
   `*.jsonl` cho toàn bộ kho mã nguồn.
6. Thực hiện các hành động đã được duyệt theo từng nhóm nhỏ và kiểm chứng sau
   mỗi nhóm.
7. Chạy kiểm thử, kiểm tra liên kết và mã kiểm tra, sau đó ghi tệp kê khai của
   lần dọn dẹp.

## 5. Phạm vi ghi dự kiến

- `.gitignore`, tài liệu về chính sách lưu giữ và địa chỉ của kho lưu trữ;
- đầu ra và bản chụp của thử nghiệm, nhưng chỉ sau khi từng đường dẫn đích được
  phê duyệt rõ ràng;
- công cụ và kiểm thử phục vụ việc kiểm kê, khử trùng lặp và dọn dẹp;
- các sản phẩm quản trị của Kế hoạch 06.

Viết lại lịch sử Git không nằm trong phạm vi mặc định của kế hoạch.

## 6. Nghiệm thu

- Không còn tệp được Git theo dõi vượt giới hạn 100 MB của GitHub trong commit
  đích.
- Các tệp JSONL cần thiết cho mã nguồn hoặc kiểm thử không bị `.gitignore` loại
  bỏ bởi một mẫu áp dụng cho toàn bộ kho mã nguồn.
- Mỗi dữ liệu được chuyển ra kho ngoài đều có địa chỉ lưu, mã kiểm tra, lược đồ, số
  lượng bản ghi và hướng dẫn phục hồi.
- Các sản phẩm dùng chung và sản phẩm chuẩn vẫn truy cập được qua sổ đăng ký.
- Việc loại bỏ nội dung trùng lặp không làm hỏng thành phần sử dụng hoặc liên
  kết trong tài liệu.
- Báo cáo trước và sau khi thực hiện nêu rõ số lượng tệp, dung lượng được Git
  theo dõi và dung lượng đã giải phóng.

## 7. Rủi ro và cách quay lui

Đây là kế hoạch có rủi ro cao nhất vì có khả năng làm mất dữ liệu. Trước khi có
phê duyệt riêng cho các thao tác thay đổi dữ liệu, mặc định chỉ được lập bảng
kiểm kê và chuẩn bị phương án chuyển dữ liệu ra ngoài. Chỉ được bỏ bản trong kho
mã nguồn sau khi bản sao đã được xác minh. Nếu mã kiểm tra không khớp hoặc phép
thử phục hồi thất bại, phải dừng việc dọn dẹp và giữ nguyên tệp nguồn.

## 8. Quyết định cần duyệt

- Kho bên ngoài hoặc kho lưu trữ chính thức và thời hạn lưu giữ dữ liệu.
- Danh sách chính xác các đường dẫn được phép xóa, nếu có.
- Có cần xử lý tệp lớn đã nằm trong commit chưa đẩy lên kho từ xa bằng cách viết
  lại lịch sử hay chỉ sửa các commit cục bộ cụ thể. Đây là quyết định cần được
  phê duyệt riêng, không thuộc quyền triển khai được cấp bởi việc duyệt chung kế
  hoạch.
