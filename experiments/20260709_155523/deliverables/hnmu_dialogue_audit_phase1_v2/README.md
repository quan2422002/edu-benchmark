# Bộ kết quả rà soát Phase 1 gửi HNMU

Bộ hồ sơ gồm phần tổng hợp ở thư mục này và bốn thư mục riêng `lop_6/`, `lop_7/`, `lop_8/`, `lop_9/`.

## Nên đọc theo thứ tự

1. Đọc `01_bao_cao_tong_quan.md` để xem kết quả chung.
2. Mở `02_checklist_tieu_chi.xlsx` để xem định nghĩa chung của các tiêu chí.
3. Mở `03_thong_ke_pass_reject_giua_cac_khoi.xlsx` và `04_thong_ke_do_phu_mau_pass_giua_cac_khoi.xlsx` để so sánh bốn khối.
4. Đọc `05_report_fragment_va_ty_le_dat.md` để xem câu trả lời dễ hiểu dành cho HNMU.
5. Mở `05_phu_luc_ky_thuat_phan_tich_fragment.xlsx` khi cần xem tám kết quả, tỷ lệ đạt theo nhóm hoặc kiểm tra số liệu và phương pháp.
6. Dùng `DANH_MUC_FILE.md` để kiểm tra cây thư mục và mục đích của từng file.
7. Dùng bốn CSV tổng hợp ở root để tra cứu toàn bộ lớp 6–9.

## Bản tóm tắt và phụ lục kỹ thuật

- `05_report_fragment_va_ty_le_dat.md`: report Markdown dễ hiểu dành cho HNMU, trả lời trực tiếp câu hỏi về tỷ lệ tiêu chí có dẫn fragment và tỷ lệ đạt chính thức.
- `05_phu_luc_ky_thuat_phan_tich_fragment.xlsx`: workbook chi tiết phục vụ kiểm tra kỹ thuật; sheet 01 có tám kết quả dễ đọc, các sheet tiếp theo tách tỷ lệ theo nhóm, số liệu thống kê, nhóm không đủ điều kiện và từ điển.
- Sheet `99_Du_lieu_ky_thuat_goc` giữ nguyên toàn bộ dữ liệu kỹ thuật cũ để truy vết và kiểm tra tự động.

## Các file tổng hợp

- `06_ket_qua_cham_tong_the_tung_mau.csv`: 1050 mẫu, mỗi mẫu một dòng.
- `07_mau_thieu_sai_truong_du_lieu.csv`: 22 cảnh báo.
- `08_ung_vien_trung_lap.csv`: 1 ứng viên; phạm vi được mô tả ngay dưới.
- `09_du_lieu_tho_sau_chuan_hoa.csv`: 1050 mẫu chuẩn hóa, mỗi mẫu một dòng.

Có 1 ứng viên trùng trong lớp 9. Quy trình đã kiểm tra cả trùng trong lớp và giữa lớp nhưng không phát hiện trường hợp trùng giữa các lớp.

File duplicate được tính trên toàn bộ 1.050 mẫu bằng ba quy tắc: trùng câu hỏi sau chuẩn hóa, trùng hội thoại sau chuẩn hóa và gần trùng nội dung kết hợp ở ngưỡng 0,96.

## Cách đọc đúng

Ví dụ đúng: đọc report Markdown trước; chỉ mở workbook chi tiết khi cần xem tám kết quả hoặc kiểm tra số liệu.

Ví dụ không đúng: coi mối liên hệ quan sát được là bằng chứng rằng việc dùng nhiều dẫn chứng học liệu làm mẫu tốt hơn. Phân tích không chứng minh quan hệ nhân quả.

Trong file 03, `pass` là trạng thái tổng thể chính thức. Đây không phải tỷ lệ tiêu chí đạt trong phân tích dẫn chứng học liệu.
