# EX02 — Phản hồi đáp án trắc nghiệm về thiết bị số

Trạng thái: ví dụ minh họa v0, đã căn theo các trường trong sheet “Luận giải chi tiết trường dữ liệu” của `review_form.xlsx`; cần HNMU/giáo sư rà soát trước khi dùng chính thức.

## 1. Thông tin bao phủ nội bộ

Phần này giúp UET truy vết ví dụ về ma trận bao phủ. Đây không phải là trường giáo viên bắt buộc phải điền trong phiếu tác giả.


| Thành phần               | Nội dung                                                                                          |
| -------------------------- | -------------------------------------------------------------------------------------------------- |
| Mã ví dụ                | `EX02`                                                                                             |
| Ô bao phủ từ ma trận   | `P05-COV-004`                                                                                      |
| Nhiệm vụ gia sư         | Phản hồi bài làm hoặc lập luận của học sinh (`T2`)                                        |
| Mức độ nhận thức      | Biết                                                                                              |
| Kiểu tình huống         | Trắc nghiệm có giải thích                                                                     |
| Vì sao chọn ví dụ này | Bổ sung tình huống học sinh chọn đáp án, giúp phiếu không chỉ có câu hỏi tự luận. |

## 2. Phiếu tác giả minh họa

### 1. Tên người tạo dữ liệu (`author_name`)

Giáo viên minh họa 02

### 2. Mã task (`Task_id`)

T2 — Phản hồi bài làm hoặc lập luận của học sinh

### 3. Chủ đề (`Topic`)

Máy tính và cộng đồng

### 4. Mức độ nhận thức (`cognitive_level`)

Biết

### 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Câu hỏi: Thiết bị nào sau đây là thiết bị số? A. Quyển vở B. Máy tính bảng C. Bút chì D. Bảng đen. Em chọn A vì quyển vở cũng lưu thông tin. Em làm vậy đúng không ạ?

### 6. Bài làm của học sinh (`student_work`)

Đề bài: Thiết bị nào sau đây là thiết bị số? A. Quyển vở; B. Máy tính bảng; C. Bút chì; D. Bảng đen.

Bài làm: A. Quyển vở

### 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Lượt 1:

Chưa có trao đổi sau bước mở đầu. Câu trả lời tiếp theo của gia sư được ghi ở mục “Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề”.

### 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

- Thiết bị số và dữ liệu số|Bài 1. Thế giới kĩ thuật số|SGK Tin học 9|trang cần HNMU/UET xác nhận

### 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)

Em có một ý đúng là quyển vở có thể lưu thông tin, nhưng đáp án A chưa đúng với câu hỏi này. “Thiết bị số” là thiết bị có khả năng làm việc với dữ liệu số, ví dụ máy tính bảng, điện thoại thông minh hoặc máy tính. Quyển vở lưu thông tin trên giấy, nhưng không xử lí dữ liệu số như thiết bị số. Vì vậy đáp án phù hợp hơn là B. Máy tính bảng. Lần sau, em hãy phân biệt “vật lưu thông tin” với “thiết bị số xử lí/lưu trữ/trao đổi dữ liệu số”.

### 10. Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)

- Có thể khen học sinh đã chú ý tới yếu tố lưu thông tin, rồi sửa lại rằng lưu thông tin trên giấy chưa đủ để gọi là thiết bị số.
- Có thể yêu cầu học sinh tự so sánh quyển vở và máy tính bảng theo khả năng xử lí dữ liệu số trước khi kết luận.

### 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

- T2_R1 — Độ chính xác kiến thức và bám học liệu: 5.
- T2_R2 — Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh: 5.
- T2_R3 — Chất lượng hỗ trợ sư phạm/giàn giáo: 4.
- T2_R4 — Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi Tin học 9: 5.
- T2_R5 — Tuân thủ ranh giới an toàn, đạo đức và pháp lý: 5.

### 12. Độ chính xác về kiến thức (`truthfulness_score`)

5

### 13. Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)

- Đạo đức/pháp lý/an toàn: 5
- Không làm học sinh mất tự tin: 5
- Phù hợp lứa tuổi THCS: 5

### 14. Tên người kiểm tra chéo (`cross_validator_name`)

Chưa phân công trong bản minh họa.

### 15. Thời gian tạo dữ liệu (`created_at`)

20260707_090200

### 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chưa điền — chỉ điền khi tác giả và người kiểm tra chéo đã đồng thuận.

### 17. Ghi chú (`Note`)

Mức hỗ trợ: Giải thích + gợi ý nhẹ. Cần phản hồi vào lí do học sinh chọn sai, không chỉ báo đáp án đúng.

## 3. Lưu ý khi rà soát ví dụ này

- Kiểm tra xem `gold_response` đã dựa trên học liệu tham khảo hay chưa.
- Kiểm tra xem điểm Likert có khớp với chất lượng của câu trả lời mẫu hay chưa.
- Nếu HNMU điều chỉnh tên task, chủ đề hoặc cách ghi học liệu, cần cập nhật lại đúng trường tương ứng trong phiếu.
