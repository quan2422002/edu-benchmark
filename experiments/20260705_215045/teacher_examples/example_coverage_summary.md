# Tóm tắt bộ ví dụ phiếu tác giả v0

Bộ ví dụ đã được chỉnh lại để bám vào version mới của `review_form.xlsx`, trong đó `Mức độ nhận thức` là trường bắt buộc của phiếu tác giả.

## 1. Điểm thay đổi quan trọng

Trước đây, mỗi ví dụ chủ yếu là một tình huống theo ma trận bao phủ. Bản này chuyển mỗi ví dụ thành một mẫu phiếu tác giả có đủ các trường:

- Tên người tạo dữ liệu (`author_name`)
- Mã task (`Task_id`)
- Chủ đề (`Topic`)
- Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)
- Bài làm của học sinh (`student_work`)
- Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)
- Danh sách học liệu tham khảo (`reference_curriculumn_list`)
- Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)
- Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)
- Điểm đánh giá theo thang đo Likert, gồm nhiều chiều, như danh sách ở dưới
- tuân thủ tiến trình sư phạm (ví dụ: phương pháp giàn giáo) (`rubric_score_list`)
- Độ chính xác về kiến thức (`truthfulness_score`)
- Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)
- Tên người kiểm tra chéo (`cross_validator_name`)
- Thời gian tạo dữ liệu (`created_at`)
- Thời gian hoàn thành dữ liệu (`completed_at`)
- Ghi chú (`Note`)

Thông tin về ô bao phủ và mức độ nhận thức vẫn được giữ để UET truy vết thiết kế; các nhãn phân loại nội bộ không thay thế các trường chính của phiếu tác giả.

## 2. Độ phủ của bộ ví dụ

- Số ví dụ đạt: 13 ví dụ + 1 phản ví dụ.
- Mỗi ví dụ hiện có trường `cognitive_level` với một trong ba giá trị: Biết, Hiểu, Vận dụng.
- Nhiệm vụ gia sư: đủ 4 loại đang dùng trong thiết kế v0.
- Mức độ nhận thức: đủ Biết, Hiểu, Vận dụng.
- Chủ đề SGK Tin học 9: phủ các cụm chính đang có trong ma trận v0.
- Loại đề bài/bài làm được minh họa: có trắc nghiệm, tự luận, tình huống đạo đức số, bảng tính, sản phẩm số, thuật toán và Python.

## 3. Cách dùng với HNMU

- Dùng `author_form_field_reference_v0.csv` để đối chiếu ý nghĩa từng trường.
- Dùng `author_form_example_*.md` làm mẫu điền phiếu.
- Dùng `author_form_counterexample.md` để chỉ ra lỗi phổ biến cần tránh.
- Khi HNMU xác nhận lại tên task/chủ đề/học liệu, cập nhật trực tiếp các trường tương ứng trong từng ví dụ.

## 4. Giới hạn hiện tại

- Học liệu tham khảo mới bám theo bài/trang từ mục lục SGK Tin học 9; chưa có mã đoạn học liệu nhỏ sau OCR toàn văn.
- Tất cả ví dụ vẫn là minh họa v0, cần HNMU/giáo sư rà soát chuyên môn trước khi dùng chính thức.

## 5. Quy ước mới cho `student_work`

Trường `Bài làm của học sinh` gồm đề bài và bài làm. Phần bài làm phải ghi đúng nội dung học sinh đã viết/chọn/làm, không diễn giải lại bằng lời của người tạo mẫu. Ghi ngắn gọn theo dạng `Đề bài: ...` và `Bài làm: ...`. Nếu học sinh chưa làm, ghi `Bài làm: Chưa có bài làm.`

## 6. Cập nhật ví dụ 09 và 10

- EX09 đã bổ sung bảng chi tiêu cụ thể để lỗi COUNTIF/SUMIF có căn cứ rõ.
- EX10 đã thay ví dụ video bằng ví dụ sắp xếp tệp/thư mục tài liệu học tập, dễ dùng hơn cho pilot ban đầu.
