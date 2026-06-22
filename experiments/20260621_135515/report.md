# Báo cáo triển khai F01

## Trạng thái

`SẴN SÀNG ĐỂ GIÁO VIÊN THẨM ĐỊNH`

F01 đã tạo khung bộ đánh giá ứng viên và gói bàn giao cho giáo viên. Đây chưa
phải bộ đánh giá chính thức, không hoàn thành thay P02–P05 và không thay thế
quyết định chuyên môn của giáo viên Tin học lớp 9.

## Điều chỉnh sau rà soát ngôn ngữ và tham chiếu

Ngày 21/06/2026, F01 được rà soát lại theo ba yêu cầu:

1. tài liệu giáo viên dùng tiếng Việt làm ngôn ngữ chính;
2. hai tài liệu chương trình bắt buộc được lưu trực tiếp trong experiment;
3. mọi mẫu minh họa ánh xạ đúng mã trường trong hợp đồng dữ liệu.

Các thuật ngữ tiếng Anh chỉ còn ở:

- tên bài báo nghiên cứu;
- mã trường kỹ thuật bắt buộc như `student_prompt`;
- tên tệp hoặc mã định danh đã có.

Mỗi mã trường đều có tên và giải thích tiếng Việt trong trang tính
`Du_lieu_vao_ra` và trong phần ghi chú của tài liệu DOCX.

## Hai nguồn chương trình bắt buộc

### Nguồn chuẩn tắc

`curriculum_sources/01-Chuong-trinh-GDPT-mon-Tin-hoc-2018.pdf`

- Chương trình giáo dục phổ thông môn Tin học.
- Ban hành kèm Thông tư 32/2018/TT-BGDĐT.
- Phần lớp 9: trang in 37–40.
- SHA-256:
  `0CDE1D108B90546EE2976B35A19B7ACC56E61A292DA2B27985A73238DB3FB4F4`.

### Nguồn diễn giải

`curriculum_sources/02-Tai-lieu-tim-hieu-Chuong-trinh-mon-Tin-hoc-2019.pdf`

- Tài liệu tìm hiểu Chương trình môn Tin học trong Chương trình GDPT 2018.
- Cơ quan: Bộ Giáo dục và Đào tạo; Trường Đại học Sư phạm Hà Nội.
- SHA-256:
  `54E53D7AD4E3F1E95B749DD771FA85F366DBEC18F6E28D1CC27B2F54778E9478`.

`source_registry.csv` lưu URL gốc, hash, số trang và vai trò nguồn.
`curriculum_reference_matrix.csv` lưu chương, mục, trang và diễn giải được dùng
trong F01.

## Kết quả chính

- Nhật ký tổng quan có 93 dòng: 17 lượt tìm kiếm và 76 tài liệu ứng viên.
- Ma trận bằng chứng có 28 nguồn nghiên cứu cốt lõi.
- Khung có 7 nhóm nhiệm vụ:
  - T01, T03, T05, T06: có bằng chứng nghiên cứu trực tiếp;
  - T02, T04, T07: tạm thời, bằng chứng trực tiếp còn hạn chế.
- Hợp đồng dữ liệu ưu tiên văn bản, giả mã, mã lệnh ngắn, lịch sử trao đổi và
  mô tả sản phẩm có cấu trúc.
- Bảng tiêu chí có 9 chiều, mỗi chiều có mốc riêng từ 0 đến 5.
- “Không áp dụng” được giữ riêng, không quy thành điểm 0.
- Lỗi nghiêm trọng được ghi riêng, không bù bằng điểm cao.
- Không khóa trọng số, điểm tổng hoặc ngưỡng đạt.
- 18 mẫu C01 đã được ánh xạ tới 7 nhiệm vụ.
- Cả 18 mẫu có đầy đủ mã trường đầu vào, lịch sử trao đổi, kết quả, điểm,
  danh sách mã lỗi nghiêm trọng, quyết định, lí do và căn cứ học liệu cụ thể.

## Sản phẩm

### Nguồn chương trình

- `curriculum_sources/README.md`
- `curriculum_sources/source_registry.csv`
- `curriculum_sources/curriculum_reference_matrix.csv`
- hai tệp PDF nguồn bắt buộc

### Tổng quan nghiên cứu

- `literature/review_protocol.md`
- `literature/review_log.csv`
- `literature/evidence_matrix.csv`
- `literature/rapid_review.md`

Các tệp này là tài liệu nghiên cứu nội bộ; tiêu đề bài báo được giữ nguyên để
đối chiếu thư mục.

### Khung bộ đánh giá

- `benchmark/benchmark_framework.xlsx`
- `benchmark/task_specification.md`
- `benchmark/traceability_matrix.csv`

Workbook khung gồm các trang tính:

- `Nhiem_vu`;
- `Du_lieu_vao_ra`;
- `Tieu_chi_cham`;
- `Vai_tro_giao_vien`;
- `Tham_chieu`.

### Gói giáo viên

- `teacher_packet/00-start-here.md`
- `teacher_packet/author-and-review-guide.md`
- `teacher_packet/examples.md`
- `teacher_packet/review_form.xlsx`

Workbook giáo viên gồm:

- `Huong_dan`;
- `Tom_tat_nhiem_vu`;
- `Phieu_tac_gia`;
- `Phieu_tham_dinh`;
- `Hieu_chuan`;
- `Cau_hoi_mo`.

### Tài liệu bàn giao

- `deliverables/Khung_benchmark_Tin_hoc_9.docx`

DOCX dùng tiếng Việt làm ngôn ngữ chính, giải thích hai nguồn chương trình,
bảy nhiệm vụ, hợp đồng dữ liệu, bảng tiêu chí, quy trình giáo viên và đủ 18 mẫu
đã ánh xạ trường dữ liệu.


## Điều chỉnh bộ ví dụ sau góp ý

- `teacher_packet/examples.md` nay trình bày đầy đủ C01-S001 đến C01-S018.
- Mọi mẫu đều dựa trên bài tập hoặc hoạt động cụ thể trong học liệu giáo viên.
- Mọi mẫu đều có `conversation_history` dạng danh sách lượt thực.
- Mọi mẫu đều có `critical_failure_flags` dạng danh sách mã; sáu mẫu minh hoạ
  phản hồi có lỗi nghiêm trọng để phục vụ hiệu chuẩn.
- `teacher_packet/example_source_registry.csv` lưu đường dẫn, vị trí bài tập,
  mã mẫu sử dụng và SHA-256 của từng học liệu được trích dùng.

## Kiểm tra

Python:

`D:\conda-envs\benchmark_env\python.exe`

Các bước đã đạt:

- bộ kiểm tra ma trận bằng chứng;
- kiểm tra trực tiếp cấu trúc workbook và tài liệu;
- 28 nguồn nghiên cứu, 7 nhiệm vụ, 9 tiêu chí và 18 dòng truy vết;
- không có mã tham chiếu mồ côi;
- mọi tiêu chí có đủ mốc 0–5;
- các danh sách chọn điểm/quyết định tồn tại trong phiếu giáo viên;
- hai tệp PDF chương trình có đúng số trang 85 và 57;
- DOCX bản trước khi mở rộng ví dụ đã được render và kiểm tra trực quan đủ 10
  trang. Sau khi bổ sung đủ 18 mẫu, cấu trúc và nội dung DOCX đã được kiểm tra
  bằng `python-docx`, nhưng chưa hoàn tất vòng render trực quan mới: trình render
  đóng gói thiếu `pdf2image`, còn Word COM bị treo khi xuất PDF trong phiên này;
- workbook đã qua kiểm tra cấu trúc, nội dung, độ rộng cột, xuống dòng, cố định
  hàng tiêu đề và danh sách chọn bằng `openpyxl`;
- workbook nguồn ban đầu giữ nguyên SHA-256:
  `2CDAF31FF65B2BA65A4C167E97AAF9568A13795E14E39B847CE13C3D4E654001`;
- 17 bài kiểm tra agent đã đạt ở vòng triển khai trước.

Excel trên máy hiện báo giấy phép ứng dụng đã hết hạn khi gọi chức năng xuất
ảnh/PDF. Vì vậy vòng này không thể tạo ảnh trực quan mới của workbook bằng
Excel; đây là hạn chế của môi trường ứng dụng, không phải lỗi đọc tệp.

## Hạn chế

- Đây là tổng quan nhanh mở rộng, không phải tổng quan hệ thống đầy đủ.
- Chưa có bộ đánh giá gia sư Tin học lớp 9 tiếng Việt đã được kiểm định.
- T02, T04 và T07 thiếu bằng chứng trực tiếp.
- Thang 0–5 chưa được giáo viên hiệu chuẩn và không được gọi là thang Likert
  chuẩn.
- Phần lớn bằng chứng gia sư là tiếng Anh và môn Toán.
- Bằng chứng lập trình chủ yếu ở bậc đại học.
- Môi trường lập trình và điều kiện lớp học địa phương chưa được xác nhận.
- Công cụ chấm tự động bằng tiếng Việt chưa được kiểm định theo từng tiêu chí.

## Việc giáo viên cần thực hiện

1. Xác nhận phạm vi và thuật ngữ lớp 9.
2. Quyết định giữ, sửa hoặc loại từng nhiệm vụ/mẫu.
3. Hiệu chuẩn mốc điểm 0–5 trên một tập mẫu chung.
4. Xác nhận lỗi nghiêm trọng và các cách trả lời hợp lệ.
5. Ghi bất đồng và quyết định phân xử trong `review_form.xlsx`.

Chỉ sau các bước này, nhiệm vụ hoặc mẫu mới có thể chuyển sang trạng thái đã
được giáo viên thẩm định.
