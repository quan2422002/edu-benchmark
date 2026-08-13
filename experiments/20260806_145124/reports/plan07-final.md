# Báo cáo cuối Plan 07 — Đồng bộ tài liệu và hoàn tất quá trình cải tổ

Thử nghiệm: `20260806_145124`
Kế hoạch: `P07`
Trạng thái kết luận: `completed`

## 1. Kết luận

Plan 07 đã hoàn tất và đóng thử nghiệm cải tổ. Tài liệu hiện dẫn người đọc từ
`README.md` đến sổ đăng ký cùng tệp kê khai của các tập 18/665/2.028/1.400; agent
điều phối có quy tắc tập trung để chọn đúng `src/`, `scripts/`, `shared/`,
`experiments/` và `docs/decisions/`. Bản chụp Git dự kiến đã dựng và cài gói wheel,
sau đó vượt cả hai phạm vi kiểm thử ngoại tuyến.

Không có API nhà cung cấp nào được gọi, không có dữ liệu benchmark được sửa và
không có thay đổi bản thảo/tệp người dùng ngoài phạm vi nào được đưa vào sản phẩm
Plan 07.

## 2. Lỗi được phát hiện và sửa

Lượt kiểm tra bản chụp đầu tiên phát hiện hai lỗi mà bản cài editable trong thư mục làm việc
không biểu hiện:

1. kiểm thử đóng gói chỉ chấp nhận mô-đun nằm dưới `src/`, nên từ chối gói wheel đã
   được cài đúng dưới `site-packages`;
2. chức năng chấm yêu cầu nguyên tắc suy ra gốc kho mã nguồn từ `__file__` của
   package, khiến gói wheel tìm nguồn đặc tả dưới thư mục Conda.

Plan 07 đã sửa kiểm thử để chấp nhận cả bản cài editable và wheel, đồng thời
truyền `repository_root` đã được bộ đọc cấu hình kiểm chứng vào quy trình chấm
yêu cầu nguyên tắc. Không thêm `sys.path`, đường dẫn máy cá nhân hoặc bản sao
logic vào CLI.

Ngoài ra, `pytest.ini` trùng với cấu hình trong `pyproject.toml` đã được loại bỏ,
và thông tin đóng gói sinh tự động `src/*.egg-info/` được bỏ qua bằng quy tắc có
mục tiêu.

## 3. Tài liệu và định tuyến

- `README.md` có mục bắt đầu ngắn dẫn trực tiếp đến kho benchmark dùng chung,
  kiến trúc, quy tắc agent và lộ trình.
- `shared/benchmark/README.md` có liên kết trực tiếp đến sổ đăng ký và bảy tệp kê khai.
- `AGENTS.md` quy định ranh giới sở hữu:
  - `src/edu_benchmark/`: logic dùng lại;
  - `scripts/`: CLI mỏng;
  - `shared/`: sản phẩm ổn định có phiên bản và thông tin thẩm quyền;
  - `experiments/<id>/`: cấu hình, lần chạy, báo cáo và bàn giao;
  - `docs/decisions/`: lý do kiến trúc bền vững.
- `ARCHITECTURE.md` không còn mục “Future P05/P06” mâu thuẫn với code đã tồn tại
  và không mô tả rubric tạm thời như ground truth.

## 4. Kết quả kiểm chứng

Chi tiết nằm tại `outputs/plan07/validation_matrix.csv`. Các kết quả chính:

- toàn bộ kiểm thử trong thư mục làm việc: `308 passed`;
- bản chụp tự chứa: `260 passed`;
- bản chụp lõi: `133 passed`;
- công cụ kiểm tra quản trị: đạt;
- sổ đăng ký dùng chung: 18 tiêu chí, 665 hội thoại, 2.028 ứng viên, 1.400 được chọn,
  628 cần UET xem lại và 0 bị chặn;
- bước kiểm tra trước khi chạy từ `/tmp`: đạt và giữ nguyên tệp kê khai hoàn tất khớp;
- nhập mô-đun từ gói wheel dưới `site-packages`: đạt;
- `pip check`: không có gói phụ thuộc bị hỏng;
- 105 liên kết cục bộ trong 34 tài liệu hiện hành: không có liên kết hỏng;
- quét toàn bộ đường dẫn trong bản chụp Git dự kiến: không phát hiện khóa riêng tư hoặc khóa API
  thực tế; chuỗi mẫu cấm trong validator được phân loại là dương tính giả;
- không có tệp Git theo dõi hoặc blob trong `HEAD` vượt 100 MiB;
- `git diff --check`: đạt.

Trình thông dịch dùng cho toàn bộ lệnh Python:
`/home/quannda/miniconda3/envs/benchmark_env/bin/python`.

## 5. Đối chiếu nghiệm thu

- Tìm 665/2.028/1.400 trong không quá ba lần chuyển liên kết: đạt.
- Agent chọn đúng ranh giới thư mục từ tài liệu hiện hành: đạt và có test khóa.
- Kiểm chứng môi trường/snapshot sạch ngoại tuyến: đạt sau khi sửa hai lỗi
  portability.
- `README.md`, `ARCHITECTURE.md` và lộ trình thống nhất trạng thái/thành phần: đạt.
- Công việc chưa làm được tách riêng, không được đánh dấu hoàn tất: đạt.
- Không có plan nào thiếu phê duyệt mà bị đóng: đạt.
- Phục hồi đầu ra chuyển ra kho ngoài: không áp dụng vì Plan 06 không thực hiện
  chuyển dữ liệu ra ngoài.

## 6. Công việc tồn đọng không chặn

Danh sách máy đọc nằm tại `outputs/plan07/closeout_backlog.csv`:

- HNMU/UET xác nhận nội dung benchmark, rubric và diễn giải đánh giá;
- khóa phụ thuộc bắc cầu đa nền tảng;
- kiểm thử cơ chế chạy Claude và cải thiện khả năng quan sát agent trong IDE;
- chọn kho sao lưu bền vững cho dữ liệu lớn đang giữ cục bộ;
- chạy GitHub Actions sau khi nhánh được push hoặc mở pull request.

Các mục này không phủ định kết quả cải tổ repository, nhưng phải qua cổng duyệt
riêng trước khi triển khai.

## 7. Trạng thái cuối

Thử nghiệm `20260806_145124` được kết thúc với trạng thái `completed`. Không tự
động tạo hoặc phê duyệt thử nghiệm kế tiếp.
