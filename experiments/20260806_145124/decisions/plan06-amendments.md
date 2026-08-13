# Nhật ký điều chỉnh Plan 06

Experiment: `20260806_145124`
Kế hoạch gốc: `plans/06-output-retention-deduplication-and-repository-hygiene.md`

## P06-A001 — Giữ dữ liệu tại ngữ cảnh gốc và không xóa các nhóm đã rà soát

- Thời điểm: `2026-08-13T16:01:47+07:00`
- Người duyệt: `project_lead`
- Quyết định:
  - giữ 45 tệp JSONL sinh/chấm mô hình tại đúng đường dẫn trong experiment
    `20260727_170150`, dùng hai quy tắc `.gitignore` giới hạn theo đúng họ đầu ra;
    không dùng Git LFS và không gom dữ liệu sang một thư mục mới trong `shared/`;
  - giữ các đầu ra OCR thử nghiệm và bản sao học liệu lịch sử tại đường dẫn
    experiment hiện tại; các quy tắc bỏ qua đã có tiếp tục ngăn chúng đi vào Git;
  - không xóa SQLite học liệu có thể dựng lại, 16 tệp trung gian/bản sao lưu và
    `main.xdv`; tệp đang được Git theo dõi tiếp tục được theo dõi;
  - giữ nguyên sáu bản chụp lịch sử trùng byte, tổng 15.883.404 byte. Chúng đã
    nằm trên các nhánh remote, mỗi tệp chỉ từ 1.391.127 đến 5.079.433 byte và
    không gây lỗi giới hạn 100 MB của GitHub.
- Lý do: vị trí trong experiment mang ngữ cảnh về vai trò và nguồn gốc của tệp;
  gom dữ liệu vào một kho dùng chung sẽ làm việc đọc lại khó hơn. Các JSONL lớn
  không cần được đồng bộ qua GitHub, còn các tệp nhỏ đã được theo dõi không tạo
  rủi ro push tương tự.
- Ảnh hưởng:
  - `.gitignore` phải mô tả rõ tên và vai trò của 45 JSONL;
  - tệp kê khai lưu giữ đổi các nhóm đã duyệt sang hành động `keep` và trạng thái
    `plan_approved`;
  - dung lượng giải phóng vẫn bằng 0; không thực hiện xóa, di chuyển, bỏ theo dõi,
    dùng LFS hoặc viết lại lịch sử.
- Không thay đổi: ba PDF bản thảo cục bộ chưa thuộc quyết định này và tiếp tục
  được giữ nguyên; benchmark, rubric, kết quả khoa học và quyền phê duyệt của
  UET/HNMU không thay đổi.

## P06-A002 — Làm mới kiểm kê sau commit và không công bố thông tin ngoài phạm vi

- Thời điểm: `2026-08-13T16:37:31+07:00`
- Người duyệt: `project_lead`
- Quyết định:
  - làm mới ba sản phẩm máy đọc sau khi mã nguồn Plan 06 đã được Git theo dõi để
    trạng thái Git và số liệu trong báo cáo phản ánh đúng commit đích;
  - không ghi đường dẫn, dung lượng riêng lẻ hoặc SHA-256 của tệp chưa được Git
    theo dõi và không thuộc nhóm lưu giữ đã cấu hình;
  - bỏ nhóm PDF bản thảo khỏi cấu hình lưu giữ vì đây là thay đổi của người dùng
    ngoài phạm vi Plan 06, không phải sản phẩm cần Plan 06 quản lý.
- Lý do: sản phẩm kiểm kê đã ghi bốn tệp triển khai là chưa được theo dõi do được
  sinh trước commit, đồng thời công bố thông tin mô tả của bốn tệp người dùng ngoài
  phạm vi. Bản kiểm kê được commit không được mang thông tin chi tiết của các tệp
  cục bộ không liên quan.
- Ảnh hưởng:
  - tệp chưa được theo dõi và ngoài phạm vi chỉ còn số lượng cùng tổng dung lượng
    trong tệp kê khai; nội dung, tên và mã kiểm tra không được ghi;
  - số liệu kiểm kê, báo cáo và bàn giao được đồng bộ theo trạng thái sau commit;
  - không xóa, di chuyển, sửa nội dung, bỏ theo dõi hoặc thêm các tệp người dùng
    vào `.gitignore`.
- Không thay đổi: chính sách giữ 45 JSONL, đầu ra OCR, học liệu, SQLite, các bản
  chụp lịch sử và tệp trung gian vẫn tuân theo P06-A001.
