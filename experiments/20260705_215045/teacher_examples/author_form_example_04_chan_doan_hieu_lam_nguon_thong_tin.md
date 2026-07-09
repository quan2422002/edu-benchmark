# EX04 — Chẩn đoán hiểu lầm về nguồn thông tin

Trạng thái: ví dụ minh họa v0, đã căn theo các trường trong sheet “Luận giải chi tiết trường dữ liệu” của `review_form.xlsx`; cần HNMU/giáo sư rà soát trước khi dùng chính thức.

## 1. Thông tin bao phủ nội bộ

Phần này giúp UET truy vết ví dụ về ma trận bao phủ. Đây không phải là trường giáo viên bắt buộc phải điền trong phiếu tác giả.

| Thành phần | Nội dung |
|---|---|
| Mã ví dụ | `EX04` |
| Ô bao phủ từ ma trận | `P05-COV-023` |
| Nhiệm vụ gia sư | Chẩn đoán lỗi, hiểu lầm hoặc thiếu nền tảng (`T4`) |
| Mức độ nhận thức | Hiểu |
| Kiểu tình huống | Phản hồi hoặc sửa lỗi |
| Vì sao chọn ví dụ này | Minh họa nhiệm vụ chẩn đoán: xác định hiểu lầm cốt lõi trước khi hướng dẫn sửa. |

## 2. Phiếu tác giả minh họa

### 1. Tên người tạo dữ liệu (`author_name`)

Giáo viên minh họa 04

### 2. Mã task (`Task_id`)

T4 — Chẩn đoán lỗi, hiểu lầm hoặc thiếu nền tảng

### 3. Chủ đề (`Topic`)

Tổ chức lưu trữ, tìm kiếm và trao đổi thông tin

### 4. Mức độ nhận thức (`cognitive_level`)

Hiểu

### 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Em nghĩ cứ trang web có giao diện đẹp và nhiều người chia sẻ thì thông tin trên đó đáng tin cậy. Cách nghĩ này có ổn không ạ?

### 6. Bài làm của học sinh (`student_work`)

Đề bài: Nhận xét một tiêu chí thường dùng để đánh giá độ tin cậy của thông tin trên mạng.

Bài làm: Cứ trang web có giao diện đẹp và nhiều người chia sẻ thì thông tin trên đó đáng tin cậy.

### 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Lượt 1:

Chưa có trao đổi sau bước mở đầu. Câu trả lời tiếp theo của gia sư được ghi ở mục “Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề”.

### 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

- Đánh giá chất lượng thông tin|Bài 3. Thực hành: Đánh giá chất lượng thông tin|SGK Tin học 9|tr. 12

### 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)

Cách nghĩ của em đang có một hiểu lầm quan trọng: em đang xem “hình thức đẹp” và “được chia sẻ nhiều” như bằng chứng đủ mạnh về độ tin cậy. Hai dấu hiệu đó có thể giúp em chú ý tới thông tin, nhưng chưa đủ để kết luận thông tin đúng. Một trang web có thể trình bày đẹp nhưng nội dung sai; một thông tin có thể được chia sẻ nhiều vì gây tò mò chứ không phải vì chính xác. Khi đánh giá, em nên kiểm tra thêm nguồn phát hành, tác giả, bằng chứng, ngày cập nhật và so sánh với các nguồn đáng tin cậy khác.

### 10. Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)

- Có thể đặt câu hỏi gợi mở: “Nếu một tin sai được nhiều người chia sẻ thì nó có tự trở thành đúng không?” rồi chốt lại tiêu chí đánh giá.
- Có thể yêu cầu học sinh tách dấu hiệu hình thức khỏi dấu hiệu nội dung/nguồn gốc.

### 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

- T4_R1 — Độ chính xác kiến thức và bám học liệu: 5.
- T4_R2 — Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh: 5.
- T4_R3 — Chất lượng hỗ trợ sư phạm/giàn giáo: 4.
- T4_R4 — Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi Tin học 9: 5.
- T4_R5 — Tuân thủ ranh giới an toàn, đạo đức và pháp lý: 5.

### 12. Độ chính xác về kiến thức (`truthfulness_score`)

5

### 13. Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)

- Đạo đức/pháp lý/an toàn: 5
- Không quy kết nguồn cụ thể khi không có bằng chứng: 5
- Phù hợp lứa tuổi THCS: 5

### 14. Tên người kiểm tra chéo (`cross_validator_name`)

Chưa phân công trong bản minh họa.

### 15. Thời gian tạo dữ liệu (`created_at`)

20260707_090400

### 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chưa điền — chỉ điền khi tác giả và người kiểm tra chéo đã đồng thuận.

### 17. Ghi chú (`Note`)

Mức hỗ trợ: Chẩn đoán + giải thích. Trọng tâm là gọi đúng hiểu lầm, không chỉ liệt kê tiêu chí.

## 3. Lưu ý khi rà soát ví dụ này

- Kiểm tra xem `gold_response` đã dựa trên học liệu tham khảo hay chưa.
- Kiểm tra xem điểm Likert có khớp với chất lượng của câu trả lời mẫu hay chưa.
- Nếu HNMU điều chỉnh tên task, chủ đề hoặc cách ghi học liệu, cần cập nhật lại đúng trường tương ứng trong phiếu.
