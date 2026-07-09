# P06 — Tóm tắt chỉnh sửa ví dụ theo phiếu tác giả

## 1. Kết quả chính

Đã cập nhật bộ ví dụ P06 theo version mới của `review_form.xlsx`. Mỗi ví dụ hiện là một mẫu phiếu tác giả có đủ các trường, bao gồm trường bắt buộc mới `Mức độ nhận thức` (`cognitive_level`).

## 2. File mới/cập nhật

- `teacher_examples/author_form_field_reference_v0.csv`: bảng tham chiếu các trường trong phiếu tác giả, trích từ `review_form.xlsx`.
- `teacher_examples/author_form_example_*.md`: 13 mẫu phiếu tác giả hoàn chỉnh.
- `teacher_examples/author_form_counterexample.md`: phản ví dụ theo đúng các trường của phiếu.
- `teacher_examples/example_coverage_summary.md`: tóm tắt độ phủ và cách dùng bộ ví dụ.
- `teacher_packet/04-examples.md`: bản tóm tắt ví dụ để gửi giáo viên đọc nhanh.
- `teacher_packet/05-author-template.md`: mẫu điền phiếu tác giả theo đúng trường dữ liệu.

## 3. Cách hiểu bản chỉnh sửa

Ma trận bao phủ vẫn được dùng để chọn tình huống đại diện. Tuy nhiên, khi chuyển sang ví dụ cho giáo viên, đơn vị chính không còn là “ô bao phủ” mà là “một phiếu tác giả có đủ trường”. Vì vậy mỗi ví dụ hiện có hai lớp:

1. Thông tin bao phủ nội bộ: dùng để UET truy vết task, mức nhận thức, chủ đề và các nhãn phân loại thiết kế nếu cần.
2. Phiếu tác giả minh họa: dùng để giáo viên thấy cần điền gì ở từng trường chính thức.

## 4. Quy ước `student_work`

Sau phản hồi ngày 08/07/2026, trường `Bài làm của học sinh` được làm rõ: đề bài vẫn nằm trong trường này, cùng với bài làm của học sinh. Phần bài làm phải ghi đúng nội dung học sinh đã viết/chọn/làm, không diễn giải lại bằng lời của người tạo mẫu.

## 5. Lưu ý còn mở

- Tên chủ đề và trang học liệu vẫn cần HNMU/UET rà soát vì hiện dựa trên mục lục/OCR v0 của SGK Tin học 9.
- Khi HNMU chốt lại mã task hoặc cách ghi học liệu, cần cập nhật trực tiếp các trường `Task_id`, `Topic` và `reference_curriculumn_list`.
- Các điểm Likert trong ví dụ là điểm kỳ vọng cho câu trả lời mẫu, chưa phải kết quả chấm phản hồi thật của AI tutor.

## 6. Cập nhật EX09/EX10 - 08/07/2026

- EX09 bổ sung bảng chi tiêu cụ thể và công thức sai cụ thể để giáo viên thấy rõ lỗi cần chẩn đoán.
- EX10 thay ví dụ dựng video bằng ví dụ sắp xếp tệp/thư mục tài liệu học tập vì tình huống này nhẹ hơn và dễ tạo mẫu pilot hơn.
## 7. Cập nhật quy ước trình tự hội thoại - 08/07/2026

- Đã căn lại các ví dụ theo sheet “quy ước” của `review_form.xlsx` mới.
- `student_prompt` + `student_work` được xem là bước mở đầu của học sinh, nên không lặp lại bước này trong `conversation_history`.
- Với ví dụ chưa có trao đổi sau bước mở đầu, `conversation_history` ghi “Chưa có trao đổi sau bước mở đầu”.
- Với ví dụ đã có trao đổi tiếp theo, `conversation_history` bắt đầu bằng gia sư và kết thúc bằng học sinh; `gold_response` là phản hồi cuối cùng của gia sư.

