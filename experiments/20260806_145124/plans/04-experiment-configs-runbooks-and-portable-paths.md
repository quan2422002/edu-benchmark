# Plan 04 — Cấu hình thử nghiệm, hướng dẫn vận hành và đường dẫn khả chuyển

Experiment: `20260806_145124`
Trạng thái: `APPROVED — PROJECT LEAD PHÊ DUYỆT NGÀY 2026-08-09`
Phụ thuộc: Plan 01–03 đã hoàn tất

## 1. Mục tiêu

Tách các thông số riêng của từng thử nghiệm khỏi phần xử lý có thể tái sử dụng.
Thay đường dẫn tuyệt đối của máy người phát triển và mã thử nghiệm được ghi cứng
trong mã nguồn bằng cơ chế xác định đường dẫn từ một trong ba nguồn rõ ràng:

- thư mục gốc của kho mã nguồn;
- tệp cấu hình;
- tham số giao diện dòng lệnh (`CLI`).

Mỗi quy trình đại diện phải có một hướng dẫn vận hành (`runbook`) đủ rõ để con
người có thể chuẩn bị, chạy, tiếp tục và kiểm tra kết quả.

## 2. Ranh giới trách nhiệm

- `experiments/<id>/configs/`: lưu mã mô hình, mã và phiên bản gói dữ liệu
  (`artifact`) đầu vào, thiết lập lấy mẫu, giới hạn chi phí, thư mục đầu ra và
  các tham số của lần chạy; không lưu khóa, mã truy cập hoặc thông tin xác thực.
- `experiments/<id>/runbooks/`: lưu điều kiện cần có trước khi chạy, câu lệnh
  chính xác, cách tiếp tục lần chạy bị gián đoạn, cách kiểm tra kết quả, đầu ra
  dự kiến, cách xử lý lỗi, quay lui và dọn dẹp.
- `src/`: chứa logic dùng chung để đọc và kiểm tra cấu hình, xác định đường dẫn
  và thực thi nghiệp vụ.
- `scripts/`: chỉ đọc tham số `CLI`, gọi phần xử lý trong `src/` và trả kết quả
  cho người vận hành.

Mặc định, mỗi kế hoạch có thao tác vận hành chỉ tạo một hướng dẫn vận hành. Chỉ
tách thành nhiều hướng dẫn khi các quy trình có vòng đời thực sự khác nhau.
Hướng dẫn vận hành không được chứa phản hồi thô của mô hình hoặc phần phân tích
kết quả.

## 3. Các quy trình ưu tiên chuyển đổi

Kế hoạch này ưu tiên bốn nhóm quy trình:

1. chấm mức độ bắt buộc của nguyên tắc sư phạm (`requirement scoring`);
2. sinh phản hồi của gia sư;
3. chấm phản hồi, bao gồm xử lý theo lô;
4. phân tích và kiểm tra ngoại tuyến trên toàn bộ 1.400 mẫu ứng viên.

Không cần sửa toàn bộ tệp lệnh lịch sử trong một lần. Trước tiên phải lập danh
sách và phân loại từng tệp lệnh hoặc tệp bọc lệnh (`wrapper`) như sau:

- `active`: đang được sử dụng và thuộc phạm vi chuyển đổi;
- `compatibility`: tạm giữ để tương thích hoặc quay lui;
- `historical-only`: chỉ giữ để truy vết lịch sử, không dùng cho lần chạy mới.

Chỉ những thành phần được xác định là `active` mới mặc nhiên thuộc phạm vi sửa
đổi của Plan 04.

## 4. Thông tin bắt buộc trong cấu hình và tệp kê khai lần chạy

Tệp kê khai lần chạy (`manifest`) phải ghi đủ:

- đường dẫn, phiên bản và mã băm của tệp cấu hình;
- mã, phiên bản và mã băm của gói dữ liệu đầu vào chuẩn dùng chung;
- mã commit của mã nguồn, nếu kho mã nguồn đã có commit tương ứng;
- phiên bản và mã băm của chỉ dẫn hoặc bộ chỉ dẫn (`prompt bundle`);
- nhà cung cấp, mô hình, vùng chạy và các tham số thực tế;
- phiên bản lược đồ dữ liệu đầu ra, thời điểm chạy, lịch sử tiếp tục lần chạy và
  chi phí khi có áp dụng.

Khóa, mã truy cập (`token`) và thông tin xác thực chỉ được đọc từ cơ chế đã quy định, chẳng hạn Application Default Credentials (`ADC`), biến môi trường hoặc kho quản lý bí mật. Không được ghi các giá trị này vào cấu hình, `manifest`, nhật ký hoặc tài liệu bàn giao.

## 5. Các bước triển khai dự kiến

1. Lập danh sách đường dẫn tuyệt đối, mã thử nghiệm và hằng số cấu hình đang
   được ghi cứng trong mã nguồn hoặc tệp bọc lệnh.
2. Xác định lược đồ cấu hình tối thiểu cho từng quy trình ưu tiên.
3. Xây dựng bộ xác định đường dẫn và bộ kiểm tra. Bộ kiểm tra phải dừng ngay khi
   không xác định được nguồn duy nhất hoặc khi mã băm và số lượng bản ghi sai.
4. Tạo cấu hình và hướng dẫn vận hành cho một lần chạy đại diện, kiểm chứng
   trước khi mở rộng sang quy trình tiếp theo.
5. Chạy bước kiểm tra trước khi thực thi (`preflight`) từ thư mục gốc của
   kho mã nguồn và từ ít nhất một thư mục làm việc khác.
6. So sánh `manifest` yêu cầu và dữ liệu đầu vào được tạo ra với mốc đối chiếu
   (`baseline`). Bước kiểm chứng này không gọi API trả phí.
7. Đánh dấu tệp bọc lệnh cũ là `compatibility` hoặc `historical-only` thay vì
   xóa ngay.

## 6. Phạm vi tệp dự kiến được phép sửa

- `experiments/20260806_145124/configs/` và
  `experiments/20260806_145124/runbooks/`;
- cấu hình tham chiếu của thử nghiệm đang hoạt động, sau khi bước lập danh sách
  xác nhận nó thuộc phạm vi;
- mô-đun đọc cấu hình và xác định đường dẫn trong gói Python, `CLI` mỏng và các
  phép kiểm thử liên quan;
- tệp bọc lệnh đang hoạt động có chứa đường dẫn tuyệt đối;
- tài liệu trực tiếp liên quan đến quy trình được chuyển đổi.

Kế hoạch này không cho phép xóa tệp bọc lệnh lịch sử hoặc gọi API trả phí.

## 7. Tiêu chí nghiệm thu

- Hướng dẫn vận hành và tệp bọc lệnh đang hoạt động không chứa đường dẫn tuyệt
  đối của máy người phát triển.
- Bước `preflight` đại diện chạy được từ ít nhất hai thư mục làm việc và xác
  định đúng cùng một gói dữ liệu đầu vào.
- Cấu hình và `manifest` không chứa mã truy cập, thông tin xác thực hoặc nội
  dung `ADC`.
- Đổi thử nghiệm hoặc tệp cấu hình không yêu cầu sửa hằng số trong thư viện.
- Khi tiếp tục một lần chạy, hệ thống chỉ xử lý những ID chưa hoàn tất và ghi
  rõ lịch sử tiếp tục.
- Dữ liệu đầu vào được tạo ra và mã băm phải giống mốc đối chiếu. Mọi khác biệt
  phải được giải thích và được người phụ trách dự án duyệt.

## 8. Rủi ro và cách quay lui

Việc thay đổi cách xác định đường dẫn có thể âm thầm trỏ sang một bản chụp dữ
liệu khác. Vì vậy, bộ xác định đường dẫn phải dừng và báo lỗi khi mã băm hoặc số
lượng bản ghi không khớp, thay vì tự chọn một nguồn gần đúng.

Tệp bọc lệnh cũ được giữ tạm ở trạng thái `compatibility`. Nếu phép kiểm tra
tương đương thất bại, người vận hành quay lại tệp cũ và kết quả mới không được
coi là kết quả thay thế mốc đối chiếu.

## 9. Các quyết định cần người phụ trách dự án duyệt

- Quy trình nào đang là `active` và phải được chuyển đổi trước.
- Định dạng cấu hình chính: YAML (`.yaml`), TOML (`.toml`) hay JSON (`.json`).
- Thời gian giữ tệp bọc lệnh ở trạng thái `compatibility` trước khi xem xét loại
  bỏ.
