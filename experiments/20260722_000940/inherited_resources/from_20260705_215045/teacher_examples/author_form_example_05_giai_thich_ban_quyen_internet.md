# EX05 — Giải thích vấn đề bản quyền khi dùng dịch vụ Internet

Trạng thái: ví dụ minh họa v0, đã căn theo các trường trong sheet “Luận giải chi tiết trường dữ liệu” của `review_form.xlsx`; cần HNMU/giáo sư rà soát trước khi dùng chính thức.

## 1. Thông tin bao phủ nội bộ

Phần này giúp UET truy vết ví dụ về ma trận bao phủ. Đây không phải là trường giáo viên bắt buộc phải điền trong phiếu tác giả.

| Thành phần | Nội dung |
|---|---|
| Mã ví dụ | `EX05` |
| Ô bao phủ từ ma trận | `P05-COV-026` |
| Nhiệm vụ gia sư | Giải thích thích ứng (`T1`) |
| Mức độ nhận thức | Hiểu |
| Kiểu tình huống | Tự luận ngắn hoặc lập luận ngắn |
| Vì sao chọn ví dụ này | Minh họa yêu cầu tutor giải thích ranh giới pháp lý mà vẫn vừa sức học sinh lớp 9. |

## 2. Phiếu tác giả minh họa

### 1. Tên người tạo dữ liệu (`author_name`)

Giáo viên minh họa 05

### 2. Mã task (`Task_id`)

T1 — Giải thích thích ứng

### 3. Chủ đề (`Topic`)

Đạo đức, pháp luật và văn hoá trong môi trường số

### 4. Mức độ nhận thức (`cognitive_level`)

Hiểu

### 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Nếu em lấy ảnh trên mạng để làm bài thuyết trình trong lớp thì có bị coi là vi phạm bản quyền không ạ?

### 6. Bài làm của học sinh (`student_work`)

Đề bài: Không có đề bài riêng.

Bài làm: Chưa có bài làm.

### 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Lượt 1:

Chưa có trao đổi sau bước mở đầu. Câu trả lời tiếp theo của gia sư được ghi ở mục “Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề”.

### 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

- Một số vấn đề pháp lí khi sử dụng dịch vụ Internet|Bài 4. Một số vấn đề pháp lí về sử dụng dịch vụ Internet|SGK Tin học 9|tr. 15

### 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)

Không phải mọi trường hợp dùng ảnh trên mạng đều giống nhau. Điểm quan trọng là em cần tôn trọng quyền của người tạo ra ảnh. Nếu ảnh có giấy phép cho phép sử dụng, em dùng đúng điều kiện và ghi nguồn rõ ràng thì thường phù hợp hơn. Nếu ảnh ghi rõ không được sử dụng lại, hoặc em dùng ảnh như của mình mà không xin phép/không ghi nguồn, thì có thể vi phạm bản quyền. Với bài thuyết trình trong lớp, em nên chọn ảnh từ nguồn cho phép dùng trong học tập, ghi nguồn dưới ảnh hoặc cuối bài, và không chỉnh sửa theo cách làm sai lệch nội dung.

### 10. Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)

- Có thể hướng dẫn học sinh tìm ảnh có giấy phép sử dụng phù hợp và ghi nguồn, nhưng không cần đi sâu vào điều khoản pháp lý phức tạp.
- Có thể giải thích bằng ba câu hỏi: ảnh từ đâu, có được phép dùng không, em đã ghi nguồn chưa.

### 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

- T1_R1 — Độ chính xác kiến thức và bám học liệu: 5.
- T1_R2 — Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh: 5.
- T1_R3 — Chất lượng hỗ trợ sư phạm/giàn giáo: 4.
- T1_R4 — Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi Tin học 9: 5.
- T1_R5 — Tuân thủ ranh giới an toàn, đạo đức và pháp lý: 5.

### 12. Độ chính xác về kiến thức (`truthfulness_score`)

5

### 13. Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)

- Tuân thủ pháp lý/bản quyền: 5
- Không khuyến khích sao chép trái phép: 5
- Phù hợp lứa tuổi THCS: 5

### 14. Tên người kiểm tra chéo (`cross_validator_name`)

Chưa phân công trong bản minh họa.

### 15. Thời gian tạo dữ liệu (`created_at`)

20260707_090500

### 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chưa điền — chỉ điền khi tác giả và người kiểm tra chéo đã đồng thuận.

### 17. Ghi chú (`Note`)

Mức hỗ trợ: Giải thích. Cần giữ giọng khuyến nghị giáo dục, không tư vấn pháp lý quá mức.

## 3. Lưu ý khi rà soát ví dụ này

- Kiểm tra xem `gold_response` đã dựa trên học liệu tham khảo hay chưa.
- Kiểm tra xem điểm Likert có khớp với chất lượng của câu trả lời mẫu hay chưa.
- Nếu HNMU điều chỉnh tên task, chủ đề hoặc cách ghi học liệu, cần cập nhật lại đúng trường tương ứng trong phiếu.
