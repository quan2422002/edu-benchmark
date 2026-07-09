# Ghi chú chuyển đổi mẫu HNMU 01 sang phiếu tác giả

Trạng thái: ghi chú làm việc cho UET; cập nhật theo hướng **chỉ chấm phản hồi cuối của gia sư**. Không dùng hướng chấm toàn bộ hội thoại trong bản này.

## 1. Nguyên tắc chuyển đổi đang dùng

Mẫu HNMU có một hội thoại hoàn chỉnh. Khi chuyển sang phiếu tác giả theo hướng chấm phản hồi cuối, không đưa toàn bộ hội thoại vào một trường duy nhất. Thay vào đó, ghép hội thoại theo ba phần đúng như sheet “quy ước” trong `review_form.xlsx`:

1. `student_prompt` + `student_work`: bước đầu tiên trong lượt hội thoại, nêu vấn đề ban đầu và bài làm/ngữ cảnh ban đầu của học sinh;
2. `conversation_history`: các bước tương tác giữa gia sư và học sinh sau khi đã có vấn đề ban đầu; phần này bắt đầu bằng gia sư và kết thúc bằng học sinh;
3. `gold_response`: bước hội thoại cuối cùng của cả lượt, thuộc về gia sư.

Cách làm này giúp người chấm biết rõ vấn đề ban đầu là gì, gia sư đã tương tác thế nào trước đó, và phản hồi cuối cần đánh giá là phản hồi nào.

## 2. Ánh xạ từ mẫu HNMU sang phiếu tác giả

| Thành phần trong mẫu HNMU | Đưa vào trường nào | Ghi chú |
|---|---|---|
| Sách giáo khoa Tin học 6 | `reference_curriculumn_list` | Giữ nguyên thông tin nguồn. |
| Chủ đề: Giải quyết vấn đề với sự hỗ trợ của máy tính | `Topic` | Giữ nguyên tên chủ đề trong mẫu. |
| Bài 17 – Chương trình máy tính trang 71/SGK | `reference_curriculumn_list` | Giữ nguyên tên bài và trang. |
| Nội dung câu hỏi: Tạo được chương trình Scratch tính trung bình cộng của ba số. | `student_work` | Ghi ở phần đề bài. |
| Mức độ: Vận dụng (Tạo được) | `cognitive_level` | Ghi là “Vận dụng”. |
| Đáp án: Khởi tạo biến a, b, c và TBC. Đặt TBC thành `(a + b + c) / 3`. | Có thể bổ sung thành trường riêng nếu cần | Không ép vào `gold_response`, vì `gold_response` trong cách chấm này là phản hồi cuối của gia sư. |
| Lượt học sinh ban đầu: “Em muốn sửa bài tính tổng 2 số...” | `student_prompt` | Đây là tuyên bố ban đầu của học sinh về vấn đề đang gặp phải. |
| Các lượt hội thoại sau tuyên bố ban đầu, từ “Đã có biến...” đến “Em lấy khối...” | `conversation_history` | Bắt đầu bằng gia sư và kết thúc bằng học sinh. |
| Lượt gia sư: “Tuyệt cú mèo!...” | `gold_response` | Đây là phản hồi cuối cần chấm. |
| Các kỹ thuật dàn giáo | `Note` | Giữ nguyên danh sách kỹ thuật trong mẫu gốc. |

## 3. Vì sao không dùng hướng chấm toàn bộ hội thoại ở bản này?

Theo phản hồi hiện tại, ưu tiên là chấm câu phản hồi cuối của gia sư. Vì vậy:

- không dùng `conversation_history` như nơi chứa toàn bộ hội thoại cần chấm;
- không tự thêm phản hồi khác ngoài câu phản hồi cuối trong mẫu gốc;
- không tự suy diễn thêm bước giải, bước chạy thử, điểm rubric hoặc câu trả lời hợp lệ khác.
- không coi `student_prompt` là lượt học sinh cuối; `student_prompt` vẫn là tuyên bố ban đầu của học sinh.

File chính nên đọc là:

- `teacher_examples/hnmu_sample_01_scratch_average_single_response_author_form.md`

## 4. Trường có thể cần bổ sung sau

Nếu muốn giữ sát mẫu HNMU hơn mà không làm lệch vai trò của `student_prompt` và `gold_response`, có thể cân nhắc thêm hai trường:

| Trường đề xuất | Vai trò |
|---|---|
| Nội dung câu hỏi | Ghi đề bài/nhiệm vụ chuyên môn mà học sinh đang làm. |
| Đáp án cốt lõi | Ghi đáp án chuyên môn ngắn gọn do giáo viên cung cấp. |

Hai trường này khác với `gold_response`: `gold_response` là phản hồi mẫu của gia sư ở lượt cần chấm, còn “Đáp án cốt lõi” là lời giải chuyên môn dùng để đối chiếu.
