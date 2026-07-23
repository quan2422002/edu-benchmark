# Mẫu HNMU 01 — Phiếu tác giả dạng chấm phản hồi cuối

Trạng thái: ví dụ chuyển đổi bám sát mẫu minh họa của giáo viên HNMU; chỉ dùng để kiểm tra cách biểu diễn dữ liệu theo hướng **chấm phản hồi cuối của gia sư**. Chưa phải mẫu benchmark chính thức.

Nguyên tắc của file này: không thêm bước giải, không tự chấm điểm, không mở rộng nội dung ngoài mẫu gốc. Phần hội thoại hoàn chỉnh được ghép theo đúng quy ước trong `review_form.xlsx`:

1. `student_prompt` + `student_work`: tuyên bố ban đầu của học sinh và bài làm/ngữ cảnh ban đầu;
2. `conversation_history`: các bước tương tác giữa học sinh và gia sư sau tuyên bố ban đầu, bắt đầu bằng gia sư và kết thúc bằng học sinh;
3. `gold_response`: câu trả lời mong muốn cuối cùng của gia sư, dựa trên `student_prompt`, `student_work` và `conversation_history`.

## 1. Thông tin từ mẫu gốc HNMU

| Trường trong mẫu gốc | Nội dung |
|---|---|
| Sách | Sách giáo khoa Tin học 6 |
| Chủ đề | Giải quyết vấn đề với sự hỗ trợ của máy tính |
| Tên bài | Bài 17 – Chương trình máy tính trang 71/SGK |
| Nội dung câu hỏi | Tạo được chương trình Scratch tính trung bình cộng của ba số. |
| Mức độ | Vận dụng (Tạo được) |
| Đáp án | Khởi tạo biến `a`, `b`, `c` và `TBC`. Đặt `TBC` thành `(a + b + c) / 3`. |
| Các kỹ thuật dàn giáo | Gợi mở tư duy; Đánh dấu đặc điểm kĩ thuật; Rút dần hỗ trợ |

## 2. Phiếu tác giả minh họa

### 1. Tên người tạo dữ liệu (`author_name`)

Giáo viên HNMU minh họa

### 2. Mã task (`Task_id`)

T3 — Gợi ý từng bước để học sinh tự đi tiếp

### 3. Chủ đề (`Topic`)

Giải quyết vấn đề với sự hỗ trợ của máy tính

### 4. Mức độ nhận thức (`cognitive_level`)

Vận dụng

### 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Em muốn sửa bài tính tổng 2 số thành tính trung bình cộng 3 số thì thao tác thế nào trên Scratch ạ?

### 6. Bài làm của học sinh (`student_work`)

Đề bài: Tạo được chương trình Scratch tính trung bình cộng của ba số.

Bài làm: Học sinh đang có bài tính tổng 2 số và muốn sửa thành bài tính trung bình cộng 3 số. Mẫu gốc không cung cấp ảnh hoặc mô tả đầy đủ các khối lệnh hiện có.

### 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Lượt 1:

1. Gia sư: Đã có biến `a`, `b` rồi. Để nhập 3 số, em cần tạo thêm biến nào và làm thao tác gì?
2. Học sinh: Cần tạo thêm biến `c` và dùng lệnh hỏi để nhập giá trị cho `c` ạ.
3. Gia sư: Rất đúng. Trên Scratch, khối phép cộng `() + ()` chỉ có 2 lỗ trống. Để cộng 3 biến `a + b + c`, em phải lồng ghép 2 khối phép cộng đó vào nhau như thế nào?
4. Học sinh: Em lấy khối `(a + b)` nhét vào lỗ trống đầu tiên của khối thứ hai, thành `((a + b) + c)`. Rồi nhét tất cả vào khối phép chia `/ 3`.

### 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

- Bài 17 – Chương trình máy tính trang 71/SGK|Sách giáo khoa Tin học 6

### 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)

Tuyệt cú mèo! Kĩ năng lồng ghép khối lệnh của em cực kì nhạy bén. Hãy mở Scratch lên và chạy thử ngay nào!

### 10. Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)

Chưa mở rộng trong bản bám sát mẫu gốc. Tạm thời chỉ coi phản hồi có nội dung tương đương `gold_response` là phản hồi hợp lệ.

### 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

Chưa chấm trong mẫu gốc. Trường này cần được HNMU/UET chấm sau nếu dùng mẫu này làm dữ liệu thử nghiệm.

### 12. Độ chính xác về kiến thức (`truthfulness_score`)

Chưa chấm trong mẫu gốc.

### 13. Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)

Chưa chấm trong mẫu gốc.

### 14. Tên người kiểm tra chéo (`cross_validator_name`)

Chưa có trong mẫu gốc.

### 15. Thời gian tạo dữ liệu (`created_at`)

Chưa có trong mẫu gốc.

### 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chưa có trong mẫu gốc.

### 17. Ghi chú (`Note`)

Các kỹ thuật dàn giáo trong mẫu gốc:

- Gợi mở tư duy
- Đánh dấu đặc điểm kĩ thuật
- Rút dần hỗ trợ

## 3. Hội thoại hoàn chỉnh sau khi ghép các trường

Phần này chỉ dùng để kiểm tra việc ghép trường, không phải trường mới trong phiếu tác giả.

1. Học sinh (`student_prompt`): Em muốn sửa bài tính tổng 2 số thành tính trung bình cộng 3 số thì thao tác thế nào trên Scratch ạ?
2. Gia sư (`conversation_history`): Đã có biến `a`, `b` rồi. Để nhập 3 số, em cần tạo thêm biến nào và làm thao tác gì?
3. Học sinh (`conversation_history`): Cần tạo thêm biến `c` và dùng lệnh hỏi để nhập giá trị cho `c` ạ.
4. Gia sư (`conversation_history`): Rất đúng. Trên Scratch, khối phép cộng `() + ()` chỉ có 2 lỗ trống. Để cộng 3 biến `a + b + c`, em phải lồng ghép 2 khối phép cộng đó vào nhau như thế nào?
5. Học sinh (`conversation_history`): Em lấy khối `(a + b)` nhét vào lỗ trống đầu tiên của khối thứ hai, thành `((a + b) + c)`. Rồi nhét tất cả vào khối phép chia `/ 3`.
6. Gia sư (`gold_response`): Tuyệt cú mèo! Kĩ năng lồng ghép khối lệnh của em cực kì nhạy bén. Hãy mở Scratch lên và chạy thử ngay nào!

## 4. Điểm cần xác nhận

- Với cách chấm phản hồi cuối, `student_prompt` vẫn là tuyên bố ban đầu của học sinh về vấn đề đang gặp phải.
- `conversation_history` chứa các bước tương tác sau tuyên bố ban đầu, bắt đầu bằng gia sư và kết thúc bằng học sinh.
- `gold_response` là phản hồi cuối của gia sư cần chấm.
- Nếu HNMU muốn giữ thêm trường “Nội dung câu hỏi” và “Đáp án” như trong mẫu gốc, có thể bổ sung hai trường riêng thay vì ép vào `student_prompt` hoặc `gold_response`.
