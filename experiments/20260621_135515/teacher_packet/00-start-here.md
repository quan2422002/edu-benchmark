# Bắt đầu tại đây

> **Trạng thái:** Toàn bộ nhiệm vụ, tiêu chí và mẫu trong gói này đều là
> **tạm thời, chờ giáo viên thẩm định**. Đây chưa phải bộ đánh giá chính thức.

## Mục đích

Gói tài liệu giúp giáo viên đề xuất tình huống, rà soát phản hồi, chấm thử
tiêu chí, phát hiện điểm chưa rõ và ghi bất đồng để phân xử.

Giáo viên giữ quyền quyết định về tính đúng chuyên môn, mức độ phù hợp lớp 9
và tính phù hợp sư phạm.

## Hai tài liệu chương trình bắt buộc

1. `curriculum_sources/01-Chuong-trinh-GDPT-mon-Tin-hoc-2018.pdf`:
   nguồn chương trình chuẩn tắc, ban hành kèm Thông tư 32/2018/TT-BGDĐT.
2. `curriculum_sources/02-Tai-lieu-tim-hieu-Chuong-trinh-mon-Tin-hoc-2019.pdf`:
   tài liệu diễn giải của Bộ Giáo dục và Đào tạo và Trường Đại học Sư phạm Hà Nội.

Khi có khác biệt, tài liệu thứ nhất có thẩm quyền cao hơn. Danh mục vị trí
tham chiếu lớp 9 nằm trong `curriculum_sources/curriculum_reference_matrix.csv`.

## Bảy nhóm nhiệm vụ ứng viên

| Mã | Nhóm nhiệm vụ | Mức độ bằng chứng |
|---|---|---|
| T01 | Giải thích khái niệm theo mức hiểu của học sinh | Có bằng chứng trực tiếp |
| T02 | Hỗ trợ quyết định về thông tin và hành vi số | **Tạm thời – bằng chứng trực tiếp còn hạn chế** |
| T03 | Phản hồi lập luận của học sinh | Có bằng chứng trực tiếp |
| T04 | Lập kế hoạch và góp ý sản phẩm số hoặc mô phỏng | **Tạm thời – bằng chứng trực tiếp còn hạn chế** |
| T05 | Hỗ trợ xây dựng thuật toán bằng gợi ý từng bước | Có bằng chứng trực tiếp |
| T06 | Chẩn đoán và hỗ trợ sửa thuật toán hoặc chương trình | Có bằng chứng trực tiếp |
| T07 | Khám phá nghề nghiệp không định kiến | **Tạm thời – bằng chứng trực tiếp còn hạn chế** |

## Thứ tự làm việc

1. Đọc trang này.
2. Đọc `research-to-benchmark-logic.md` để hiểu vì sao từ chương trình,
   nghiên cứu và học liệu lại hình thành các nhiệm vụ, tiêu chí và mẫu.
3. Đọc phần vai trò của mình trong `author-and-review-guide.md`.
4. Xem đủ 18 mẫu trong `examples.md`; dùng `example_source_registry.csv` để
   đối chiếu bài học, vị trí bài tập và tệp học liệu gốc.
5. Ghi phần việc vào `review_form.xlsx`.
6. Ghi điểm chưa chắc chắn vào trang tính `Cau_hoi_mo`.

## Nguyên tắc bắt buộc

- Không dùng thông tin nhận dạng của học sinh thật.
- Tác giả không tự phê duyệt mẫu mình viết.
- Người thẩm định không sửa âm thầm nội dung của tác giả.
- Điểm số phải kèm lí do ngắn dựa trên điều quan sát được.
- Chỉ dùng “Không áp dụng” khi tiêu chí thực sự không áp dụng.
- Lỗi nghiêm trọng được ghi riêng và không thể bù bằng điểm khác.
- Có lỗi nghiêm trọng **không có nghĩa là tự động cho 0 ở toàn bộ tiêu chí**.
  Người thẩm định vẫn chấm từng tiêu chí theo điều quan sát được, rồi ghi mã
  lỗi nghiêm trọng riêng. Phản hồi có lỗi nghiêm trọng không được xem là mẫu
  đạt yêu cầu cho tới khi lỗi đó được sửa hoặc được người phân xử quyết định.
- Lịch sử trao đổi được ghi theo từng lượt: số lượt, người nói và nội dung.
- Mã lỗi nghiêm trọng được chọn trong trang tính `Ma_loi_nghiem_trong`;
  không có lỗi thì dùng danh sách rỗng `[]`.
- Bất đồng được giữ nguyên để người phân xử xem xét.

## Thang đánh giá

`0` Không thể chấp nhận; `1` Rất yếu; `2` Yếu; `3` Đạt tối thiểu;
`4` Tốt; `5` Rất tốt; `N/A` Không áp dụng.

## Ghi chú về thuật ngữ

“Bộ đánh giá” là cách gọi tiếng Việt dùng trong gói giáo viên. Thuật ngữ
tiếng Anh “benchmark” chỉ được giữ trong tên dự án hoặc tên tệp đã có.
Các mã trường dữ liệu bằng tiếng Anh được giữ nguyên để hệ thống đối chiếu,
nhưng luôn có tên và giải thích tiếng Việt trong trang tính `Du_lieu_vao_ra`.
