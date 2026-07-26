# Kết quả rà soát lớp 9

Thư mục này chỉ chứa dữ liệu lớp 9. Dùng `sample_id` để đối chiếu giữa các file dữ liệu.

## Số bản ghi

- `01_du_lieu_tho_sau_chuan_hoa.csv`: 308.
- `02_thong_ke_do_phu_mau_pass.xlsx`: 22 bài học, kể cả bài không có mẫu pass.
- `03_ket_qua_cham_tong_the_tung_mau.csv`: 308.
- `04_ket_qua_cham_chi_tiet_tung_tieu_chi.csv`: 5544.
- `05_mau_thieu_sai_truong_du_lieu.csv`: 19.
- `06_ung_vien_trung_lap.csv`: 1 ứng viên trong lớp.
- `07_phan_tich_fragment_va_ket_qua_cham.xlsx`: 8 dòng tóm tắt dành cho HNMU.
- `08_phu_luc_ky_thuat_phan_tich_fragment.xlsx`: 63 dòng phụ lục kiểm toán kỹ thuật.

## Trạng thái

- pass: 218.
- need_human_review: 90.
- failed: 0.

## Cách đọc hai file phân tích dẫn chứng học liệu

File 07 đặt kết quả khi xem tất cả mẫu và kết quả khi so các mẫu trong cùng nhóm chấm cạnh nhau. Vì mỗi thư mục chỉ có một lớp, file này không so sánh giữa các khối lớp.

File 08 giữ đầy đủ mã đối chiếu, hệ số, p-value, phân nhóm, phương pháp và lý do không thể ước lượng. Các thông tin kỹ thuật này không hiển thị trong file 07.

Ví dụ đúng: đọc cột “Diễn giải chính” trong file 07, rồi mở file 08 nếu cần kiểm tra chi tiết.

Ví dụ không đúng: kết luận dẫn chứng học liệu là nguyên nhân làm mẫu pass. Giáo viên HNMU/UET vẫn giữ quyền đánh giá chuyên môn.
