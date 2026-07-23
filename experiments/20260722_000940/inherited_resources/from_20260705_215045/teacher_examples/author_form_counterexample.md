# Phản ví dụ — Mẫu phiếu tác giả cần sửa

Trạng thái: phản ví dụ minh họa v0. Mục đích là giúp giáo viên thấy một mẫu có vẻ “có nội dung” nhưng chưa đạt vì không điền đúng các trường của phiếu tác giả.

## 1. Phiếu tác giả minh họa chưa đạt

### 1. Tên người tạo dữ liệu (`author_name`)

Giáo viên minh họa lỗi

### 2. Mã task (`Task_id`)

Chưa rõ

### 3. Chủ đề (`Topic`)

Tin học

### 4. Mức độ nhận thức (`cognitive_level`)

Chưa rõ

### 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Học sinh chưa hiểu bài, gia sư giải thích cho dễ hiểu.

### 6. Bài làm của học sinh (`student_work`)

Đề bài: Tin học.

Bài làm: Chưa ghi nội dung bài làm cụ thể.

### 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Không ghi rõ lượt/bước hội thoại.

### 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

SGK Tin học 9.

### 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)

Gia sư trả lời thật dễ hiểu, có ví dụ.

### 10. Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)

Không ghi.

### 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

Không ghi.

### 12. Độ chính xác về kiến thức (`truthfulness_score`)

Không ghi.

### 13. Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)

Không ghi.

### 14. Tên người kiểm tra chéo (`cross_validator_name`)

Chưa phân công.

### 15. Thời gian tạo dữ liệu (`created_at`)

20260707_093000

### 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chưa điền.

### 17. Ghi chú (`Note`)

Mẫu còn quá chung.

## 2. Vì sao mẫu này cần sửa

- `Mã task` không khớp danh sách task đã chốt tạm thời, nên không biết đang kiểm tra năng lực gia sư nào.
- `Chủ đề` quá rộng; cần ghi đúng chủ đề/bài học trong SGK Tin học 9.
- `student_prompt` không phải lời học sinh cụ thể, nên không tạo được tình huống đánh giá rõ ràng.
- `Bài làm của học sinh` không ghi đề bài và bài làm cụ thể, nên người rà soát không biết học sinh đang làm nhiệm vụ nào và sai/đúng ở đâu.
- `reference_curriculumn_list` không chỉ rõ bài/mục/trang, nên `gold_response` không có căn cứ kiểm tra.
- `gold_response` chỉ mô tả “trả lời dễ hiểu”, chưa phải câu trả lời mẫu có thể dùng để đối chiếu.
- `rubric_score_list`, `truthfulness_score` và `boundary_adherence_score_list` bị bỏ trống, nên người rà soát không biết kỳ vọng chất lượng là gì.

## 2. Vì sao mẫu này cần sửa

- `Mã task` không khớp danh sách task đã chốt tạm thời, nên không biết đang kiểm tra năng lực gia sư nào.
- `Mức độ nhận thức` không nằm trong ba giá trị Biết, Hiểu, Vận dụng, nên không kiểm soát được độ khó nhận thức của mẫu.
- `Chủ đề` quá rộng; cần ghi đúng chủ đề/bài học trong SGK Tin học 9.
- `student_prompt` không phải lời học sinh cụ thể, nên không tạo được tình huống đánh giá rõ ràng.
- `Bài làm của học sinh` không ghi đề bài và bài làm cụ thể, nên người rà soát không biết học sinh đang làm nhiệm vụ nào và sai/đúng ở đâu.
- `reference_curriculumn_list` không chỉ rõ bài/mục/trang, nên `gold_response` không có căn cứ kiểm tra.
- `gold_response` chỉ mô tả “trả lời dễ hiểu”, chưa phải câu trả lời mẫu có thể dùng để đối chiếu.
- `rubric_score_list`, `truthfulness_score` và `boundary_adherence_score_list` bị bỏ trống, nên người rà soát không biết kỳ vọng chất lượng là gì.

## 3. Cách sửa nhanh

Chọn một task cụ thể, một chủ đề/bài học cụ thể, chọn mức độ nhận thức trong ba giá trị Biết, Hiểu, Vận dụng, viết lại đúng lời học sinh, chỉ rõ học liệu tham khảo, sau đó viết câu trả lời mẫu của gia sư và điểm Likert theo từng tiêu chí.
