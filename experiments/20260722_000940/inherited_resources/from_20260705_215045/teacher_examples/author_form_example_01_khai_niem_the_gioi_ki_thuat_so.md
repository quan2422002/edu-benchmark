# EX01 — Giải thích khái niệm thế giới kĩ thuật số

Trạng thái: ví dụ minh họa v0, đã căn theo các trường trong sheet “Luận giải chi tiết trường dữ liệu” của `review_form.xlsx`; cần HNMU/giáo sư rà soát trước khi dùng chính thức.

## 1. Thông tin bao phủ nội bộ

Phần này giúp UET truy vết ví dụ về ma trận bao phủ. Đây không phải là trường giáo viên bắt buộc phải điền trong phiếu tác giả.

| Thành phần | Nội dung |
|---|---|
| Mã ví dụ | `EX01` |
| Ô bao phủ từ ma trận | `P05-COV-001` |
| Nhiệm vụ gia sư | Giải thích thích ứng (`T1`) |
| Mức độ nhận thức | Biết |
| Kiểu tình huống | Câu hỏi khái niệm/lý thuyết |
| Vì sao chọn ví dụ này | Ví dụ đơn giản để giáo viên thấy cách viết mẫu giải thích khái niệm ở mức Biết. |

## 2. Phiếu tác giả minh họa

### 1. Tên người tạo dữ liệu (`author_name`)

Giáo viên minh họa 01

### 2. Mã task (`Task_id`)

T1 — Giải thích thích ứng

### 3. Chủ đề (`Topic`)

Máy tính và cộng đồng

### 4. Mức độ nhận thức (`cognitive_level`)

Biết

### 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Cô ơi, “thế giới kĩ thuật số” có phải chỉ là Internet không ạ?

### 6. Bài làm của học sinh (`student_work`)

Đề bài: Không có đề bài riêng.

Bài làm: Chưa có bài làm.

### 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Lượt 1:

Chưa có trao đổi sau bước mở đầu. Câu trả lời tiếp theo của gia sư được ghi ở mục “Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề”.

### 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

- Khái niệm thế giới kĩ thuật số|Bài 1. Thế giới kĩ thuật số|SGK Tin học 9|trang cần HNMU/UET xác nhận

### 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)

Không hẳn em nhé. Internet là một phần rất quan trọng của thế giới kĩ thuật số, nhưng không phải toàn bộ. Thế giới kĩ thuật số còn gồm các thiết bị số như điện thoại, máy tính bảng, máy tính; dữ liệu số như ảnh, video, tệp học tập; các dịch vụ số như học trực tuyến, bản đồ số, thư điện tử; và cách con người trao đổi, học tập, làm việc trong môi trường số. Em có thể nhớ ngắn gọn: Internet là mạng kết nối, còn thế giới kĩ thuật số là không gian rộng hơn, nơi thiết bị, dữ liệu, phần mềm, dịch vụ và con người cùng tương tác.

### 10. Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)

- Có thể giải thích bằng ví dụ gần gũi như lưu ảnh trên điện thoại, học trực tuyến hoặc dùng bản đồ số, miễn là nêu rõ Internet chỉ là một phần của thế giới kĩ thuật số.
- Có thể trả lời ngắn hơn nếu học sinh chỉ cần phân biệt khái niệm, nhưng không được đồng nhất thế giới kĩ thuật số với Internet.

### 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

- T1_R1 — Độ chính xác kiến thức và bám học liệu: 5.
- T1_R2 — Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh: 5.
- T1_R3 — Chất lượng hỗ trợ sư phạm/giàn giáo: 4.
- T1_R4 — Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi Tin học 9: 5.
- T1_R5 — Tuân thủ ranh giới an toàn, đạo đức và pháp lý: 5.

### 12. Độ chính xác về kiến thức (`truthfulness_score`)

5

### 13. Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)

- Đạo đức/pháp lý/an toàn: 5
- Không mở rộng lan man ngoài Tin học 9: 5
- Phù hợp lứa tuổi THCS: 5

### 14. Tên người kiểm tra chéo (`cross_validator_name`)

Chưa phân công trong bản minh họa.

### 15. Thời gian tạo dữ liệu (`created_at`)

20260707_090100

### 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chưa điền — chỉ điền khi tác giả và người kiểm tra chéo đã đồng thuận.

### 17. Ghi chú (`Note`)

Mức hỗ trợ: Giải thích. Mẫu nhấn mạnh phân biệt khái niệm, không biến thành bài giảng dài.

## 3. Lưu ý khi rà soát ví dụ này

- Kiểm tra xem `gold_response` đã dựa trên học liệu tham khảo hay chưa.
- Kiểm tra xem điểm Likert có khớp với chất lượng của câu trả lời mẫu hay chưa.
- Nếu HNMU điều chỉnh tên task, chủ đề hoặc cách ghi học liệu, cần cập nhật lại đúng trường tương ứng trong phiếu.
