# Plan 07 — Đồng bộ tài liệu, kiểm chứng và hoàn tất quá trình cải tổ

Thử nghiệm: `20260806_145124`
Trạng thái: `APPROVED — 2026-08-13 — PROJECT LEAD`
Phụ thuộc: Plan 01–06

## 1. Mục tiêu

Chứng minh toàn bộ quá trình cải tổ hoạt động như một hệ thống hoàn chỉnh, đồng
bộ tài liệu theo đúng hiện trạng và kết thúc thử nghiệm bằng một báo cáo cô
đọng. Kế hoạch này không dùng tài liệu để tuyên bố trước những thay đổi chưa được
triển khai hoặc chưa qua kiểm chứng.

## 2. Phạm vi

- Đối chiếu và đồng bộ `README.md`, `ARCHITECTURE.md`, lộ trình đang hoạt động và
  bảng phân định quyền sở hữu.
- Viết hướng dẫn bắt đầu cho người dùng và chỉ dẫn định tuyến nhiệm vụ cho agent
  điều phối.
- Kiểm tra liên kết, thông tin mô tả, sổ đăng ký, khả năng nhập mô-đun, CLI, tệp
  cấu hình, hướng dẫn vận hành và chính sách lưu giữ.
- Thử nghiệm trên môi trường sạch và bản sao Git mới trong phạm vi không cần
  thông tin xác thực.
- Lập danh sách thành phần dự kiến ngừng sử dụng và công việc tồn đọng, tránh kéo
  dài thử nghiệm hiện tại vô hạn.
- Tạo báo cáo cuối để đối chiếu kết quả với mục tiêu của lộ trình và hoàn tất tài
  liệu bàn giao.

## 3. Tài liệu đích

- `README.md`: hướng dẫn bắt đầu, vị trí sản phẩm chuẩn, các lệnh ngoại tuyến cốt
  lõi và thử nghiệm đang hoạt động.
- `ARCHITECTURE.md`: thành phần, cơ chế chạy và quyền sở hữu đang có hiệu lực.
- `docs/decisions/`: lý do của các quyết định kiến trúc, không dùng để ghi trạng
  thái của từng lần chạy.
- Lộ trình: thứ tự triển khai, cổng kiểm soát và trạng thái cấp cao.
- Báo cáo cuối: hiện trạng ban đầu, thay đổi đã triển khai, kết quả kiểm chứng,
  ngoại lệ và công việc tồn đọng.

## 4. Ma trận kiểm chứng

Tối thiểu phải kiểm tra:

- cài đặt gói và khả năng nhập mô-đun bằng `benchmark_env`;
- kiểm thử đơn vị, kiểm thử tích hợp ngoại tuyến và công cụ kiểm tra lược đồ/liên
  kết;
- số lượng, mã kiểm tra và phép nối của các sản phẩm chuẩn;
- bước kiểm tra điều kiện trước khi chạy của các CLI đại diện từ thư mục gốc kho
  mã nguồn;
- thử phục hồi ít nhất một đầu ra được chuyển sang kho ngoài nếu Plan 06 có thực
  hiện việc chuyển này;
- quét thông tin nhạy cảm và tệp dung lượng lớn;
- chuỗi liên kết từ `README.md` đến sổ đăng ký, tệp kê khai và nguồn gốc dữ liệu;
- không có tài liệu nào gọi sản phẩm tạm thời là nội dung đã được HNMU/UET xác
  nhận.

## 5. Các bước triển khai dự kiến

1. Ghi nhận trạng thái sau Plan 06 và danh sách tiêu chí nghiệm thu còn mở.
2. Chạy ma trận kiểm chứng và sửa các lỗi thuộc phạm vi quá trình cải tổ.
3. Đồng bộ tài liệu dựa trên bằng chứng đã kiểm chứng.
4. Thử nghiệm trên môi trường sạch, ghi chính xác lệnh đã chạy và trình thông dịch
   được sử dụng.
5. Lập danh sách công việc tồn đọng, kèm người chịu trách nhiệm và cổng kiểm soát,
   cho những việc không cản trở hoàn tất thử nghiệm.
6. Viết `reports/plan07-final.md`, tài liệu bàn giao và đề xuất trạng thái cuối của
   thử nghiệm.

## 6. Phạm vi ghi dự kiến

- `README.md`, `ARCHITECTURE.md` và `AGENTS.md` nếu cơ chế định tuyến thực tế thay
  đổi;
- `docs/decisions/` và tài liệu nằm gần thành phần liên quan;
- kiểm thử hoặc công cụ kiểm tra, nhưng chỉ để sửa lỗi đã xác định đang chặn việc
  hoàn tất;
- các sản phẩm quản trị của Plan 07 trong thử nghiệm `20260806_145124`.

## 7. Nghiệm thu

- Một người mới có thể tìm được các tập chuẩn 665/2.028/1.400 và hiểu trạng thái
  của chúng trong không quá ba lần chuyển liên kết từ `README.md`.
- Agent điều phối có thể chọn đúng `src/`, `scripts/`, tệp cấu hình, hướng dẫn vận
  hành và ranh giới sở hữu giữa `shared/` với `experiments/` từ tài liệu hiện
  hành.
- Thử nghiệm ngoại tuyến trên môi trường sạch đạt; nếu không đạt, mọi trở ngại
  chặn phải được ghi rõ cùng bằng chứng.
- `README.md`, `ARCHITECTURE.md` và lộ trình không mâu thuẫn về trạng thái kế hoạch,
  thành phần hoặc quyền sở hữu.
- Báo cáo cuối nêu rõ cả phần chưa làm, không biến công việc tồn đọng thành nội
  dung đã hoàn thành.
- Không có kế hoạch nào được tự động đánh dấu `approved` hoặc `completed` khi thiếu
  phê duyệt hay bằng chứng.

## 8. Rủi ro và cách quay lui

Giai đoạn hoàn tất dễ biến thành một vòng cải tổ mới. Chỉ sửa những lỗi trực tiếp
chặn tiêu chí nghiệm thu; thay đổi tính năng mới phải được đưa vào danh sách công
việc tồn đọng hoặc một thử nghiệm sau. Có thể quay lui thay đổi tài liệu qua lịch
sử Git nếu tài liệu không phản ánh đúng phần mã đã được kiểm chứng.

## 9. Quyết định cần duyệt

- Tiêu chí nào chặn việc hoàn tất thử nghiệm và tiêu chí nào được đưa vào danh
  sách công việc tồn đọng.
- Trạng thái cuối phải dùng đúng tập giá trị của Plan 01. Nếu mục tiêu đã hoàn
  thành nhưng vẫn còn công việc không chặn, dùng `completed` và ghi công việc đó
  riêng trong báo cáo; không tạo trạng thái mới như `completed_with_backlog`.
- Chỉ tạo thử nghiệm kế tiếp sau khi báo cáo cuối của thử nghiệm hiện tại được
  duyệt.
