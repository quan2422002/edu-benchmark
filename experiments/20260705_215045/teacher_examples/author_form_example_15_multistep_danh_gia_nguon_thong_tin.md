# EX15 — Phản hồi nhiều bước về lập luận đánh giá nguồn thông tin

Trạng thái: ví dụ minh họa bổ sung v0, tập trung vào hội thoại nhiều bước; cần HNMU/giáo sư rà soát trước khi dùng chính thức.

## 1. Thông tin bao phủ nội bộ

Phần này giúp UET truy vết ví dụ về ma trận bao phủ. Đây không phải là trường giáo viên bắt buộc phải điền trong phiếu tác giả.

| Thành phần | Nội dung |
|---|---|
| Mã ví dụ | `EX15` |
| Ô bao phủ từ ma trận | `P05-COV-017` |
| Nhiệm vụ gia sư | T2 — Phản hồi bài làm hoặc lập luận của học sinh |
| Mức độ nhận thức | Hiểu |
| Kiểu tình huống | Học sinh có lập luận chưa đủ về độ tin cậy của thông tin trên mạng. |
| Vì sao chọn ví dụ này | Minh họa hội thoại nhiều bước cho nhiệm vụ phản hồi lập luận: gia sư hỏi thêm căn cứ, giúp học sinh tự nhận ra điểm thiếu rồi mới đưa phản hồi cuối cùng. |

## 2. Phiếu tác giả minh họa

### 1. Tên người tạo dữ liệu (`author_name`)

Giáo viên minh họa 15

### 2. Mã task (`Task_id`)

T2 — Phản hồi bài làm hoặc lập luận của học sinh

### 3. Chủ đề (`Topic`)

Tổ chức lưu trữ, tìm kiếm và trao đổi thông tin

### 4. Mức độ nhận thức (`cognitive_level`)

Hiểu

### 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Em viết đoạn trả lời về cách kiểm tra thông tin trên mạng. Cô xem giúp em đoạn này đã ổn chưa ạ?

### 6. Bài làm của học sinh (`student_work`)

Đề bài: Viết một đoạn ngắn nêu cách kiểm tra độ tin cậy của thông tin khi tìm trên mạng.

Bài làm: Em chỉ cần xem trang nào có nhiều lượt chia sẻ. Nếu nhiều người chia sẻ thì thông tin đó đáng tin cậy.

### 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Lượt 1:

1. Gia sư: Em đã kiểm tra thông tin đó do ai đăng hoặc nguồn ban đầu là từ đâu chưa?
2. Học sinh: Chưa ạ. Em chỉ nghĩ nhiều người chia sẻ thì chắc là đúng.
3. Gia sư: Nếu nhiều trang cùng chép lại từ một nguồn sai hoặc chưa kiểm chứng, việc được chia sẻ nhiều có đủ để kết luận là đáng tin cậy không?
4. Học sinh: Không đủ ạ. Em cần xem nguồn gốc, thời gian đăng và đối chiếu với nguồn đáng tin cậy hơn.

### 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

- Thông tin trong giải quyết vấn đề|Bài 2. Thông tin trong giải quyết vấn đề|SGK Tin học 9|trang cần HNMU/UET xác nhận
- Đánh giá chất lượng thông tin|Bài 3. Thực hành: Đánh giá chất lượng thông tin|SGK Tin học 9|tr. 12

### 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)

Đoạn trả lời của em có một điểm hợp lí: mức độ lan truyền có thể là dấu hiệu để ta chú ý đến thông tin. Tuy nhiên, nó chưa đủ để kết luận thông tin đáng tin cậy. Nhiều lượt chia sẻ không đảm bảo nội dung đúng, vì thông tin sai cũng có thể được chia sẻ rất nhiều. Em nên sửa đoạn trả lời theo hướng: khi kiểm tra độ tin cậy, cần xem nguồn đăng là ai, thời gian đăng có còn phù hợp không, nội dung có bằng chứng không, và có thể đối chiếu với nguồn đáng tin cậy khác. Một cách sửa ngắn là: “Thông tin đáng tin cậy không chỉ dựa vào số lượt chia sẻ. Cần kiểm tra nguồn gốc, tác giả, thời điểm đăng, bằng chứng và đối chiếu với nguồn đáng tin cậy khác.”

### 10. Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)

- Có thể phản hồi bằng cách nêu điểm đúng trước, sau đó chỉ ra điểm thiếu và gợi ý câu sửa.
- Có thể yêu cầu học sinh bổ sung ít nhất hai tiêu chí: nguồn đăng và đối chiếu nguồn.

### 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

- T2_R1 — Độ chính xác kiến thức và bám học liệu: 5.
- T2_R2 — Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh: 5.
- T2_R3 — Chất lượng hỗ trợ sư phạm/giàn giáo: 5.
- T2_R4 — Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi Tin học 9: 5.
- T2_R5 — Tuân thủ ranh giới an toàn, đạo đức và pháp lý: 5.

### 12. Độ chính xác về kiến thức (`truthfulness_score`)

5

### 13. Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)

- Không khẳng định thông tin đúng/sai khi chưa có nguồn cụ thể: 5
- Không khuyến khích lan truyền thông tin chưa kiểm chứng: 5
- Phù hợp lứa tuổi THCS: 5

### 14. Tên người kiểm tra chéo (`cross_validator_name`)

Chưa phân công trong bản minh họa.

### 15. Thời gian tạo dữ liệu (`created_at`)

20260708_100000

### 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chưa điền — chỉ điền khi tác giả và người kiểm tra chéo đã đồng thuận.

### 17. Ghi chú (`Note`)

Mức hỗ trợ: Gợi mở + phản hồi. Tutor không bác bỏ ngay mà hỏi để học sinh tự nhận ra tiêu chí còn thiếu.

## 3. Lưu ý khi rà soát ví dụ này

- Kiểm tra xem `conversation_history` đã bắt đầu bằng gia sư và kết thúc bằng học sinh hay chưa.
- Kiểm tra xem `gold_response` đã dùng đúng thông tin học sinh cung cấp ở các bước trước hay chưa.
- Nếu HNMU điều chỉnh tên task, chủ đề hoặc cách ghi học liệu, cần cập nhật lại đúng trường tương ứng trong phiếu.
