# EX06 — Phản hồi tình huống chia sẻ mật khẩu

Trạng thái: ví dụ minh họa v0, đã căn theo các trường trong sheet “Luận giải chi tiết trường dữ liệu” của `review_form.xlsx`; cần HNMU/giáo sư rà soát trước khi dùng chính thức.

## 1. Thông tin bao phủ nội bộ

Phần này giúp UET truy vết ví dụ về ma trận bao phủ. Đây không phải là trường giáo viên bắt buộc phải điền trong phiếu tác giả.

| Thành phần | Nội dung |
|---|---|
| Mã ví dụ | `EX06` |
| Ô bao phủ từ ma trận | `P05-COV-030` |
| Nhiệm vụ gia sư | Phản hồi bài làm hoặc lập luận của học sinh (`T2`) |
| Mức độ nhận thức | Vận dụng |
| Kiểu tình huống | Tự luận ngắn hoặc lập luận ngắn |
| Vì sao chọn ví dụ này | Minh họa phản hồi một quyết định thực tế của học sinh trong môi trường số. |

## 2. Phiếu tác giả minh họa

### 1. Tên người tạo dữ liệu (`author_name`)

Giáo viên minh họa 06

### 2. Mã task (`Task_id`)

T2 — Phản hồi bài làm hoặc lập luận của học sinh

### 3. Chủ đề (`Topic`)

Đạo đức, pháp luật và văn hoá trong môi trường số

### 4. Mức độ nhận thức (`cognitive_level`)

Vận dụng

### 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Bạn em mượn tài khoản học tập của em để vào xem bài. Em định gửi luôn mật khẩu cho bạn vì bạn thân mà. Làm vậy có sao không?

### 6. Bài làm của học sinh (`student_work`)

Đề bài: Bạn em mượn tài khoản học tập để vào xem bài. Hãy nêu em nên xử lý thế nào và giải thích vì sao.

Bài làm: Em định gửi mật khẩu cho bạn vì bạn thân thì có thể tin tưởng.

### 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Lượt 1:

Chưa có trao đổi sau bước mở đầu. Câu trả lời tiếp theo của gia sư được ghi ở mục “Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề”.

### 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

- Một số vấn đề pháp lí khi sử dụng dịch vụ Internet|Bài 4. Một số vấn đề pháp lí về sử dụng dịch vụ Internet|SGK Tin học 9|tr. 15

### 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)

Ý định giúp bạn của em là tốt, nhưng gửi mật khẩu là không nên. Mật khẩu là thông tin bảo vệ tài khoản của em; nếu chia sẻ, em có thể mất quyền kiểm soát tài khoản, lộ thông tin cá nhân, hoặc tài khoản bị dùng cho việc em không mong muốn. Cách an toàn hơn là em hướng dẫn bạn cách tự đăng nhập bằng tài khoản của bạn ấy, gửi đường link bài học công khai nếu được phép, hoặc hỏi giáo viên xem có cách cấp quyền truy cập phù hợp không. Như vậy em vẫn giúp bạn mà không làm mất an toàn tài khoản.

### 10. Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)

- Có thể yêu cầu học sinh nêu rủi ro của việc chia sẻ mật khẩu trước, rồi mới đề xuất cách giúp bạn an toàn hơn.
- Có thể nhấn mạnh nguyên tắc: không chia sẻ mật khẩu, kể cả với bạn thân; hãy dùng cách chia sẻ tài liệu được hệ thống cho phép.

### 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

- T2_R1 — Độ chính xác kiến thức và bám học liệu: 5.
- T2_R2 — Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh: 5.
- T2_R3 — Chất lượng hỗ trợ sư phạm/giàn giáo: 4.
- T2_R4 — Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi Tin học 9: 5.
- T2_R5 — Tuân thủ ranh giới an toàn, đạo đức và pháp lý: 5.

### 12. Độ chính xác về kiến thức (`truthfulness_score`)

5

### 13. Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)

- An toàn tài khoản/cá nhân: 5
- Không khuyến khích vi phạm quy định hệ thống: 5
- Phù hợp lứa tuổi THCS: 5

### 14. Tên người kiểm tra chéo (`cross_validator_name`)

Chưa phân công trong bản minh họa.

### 15. Thời gian tạo dữ liệu (`created_at`)

20260707_090600

### 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chưa điền — chỉ điền khi tác giả và người kiểm tra chéo đã đồng thuận.

### 17. Ghi chú (`Note`)

Mức hỗ trợ: Giải thích + hướng dẫn. Tutor cần công nhận thiện chí giúp bạn nhưng vẫn chốt rõ không chia sẻ mật khẩu.

## 3. Lưu ý khi rà soát ví dụ này

- Kiểm tra xem `gold_response` đã dựa trên học liệu tham khảo hay chưa.
- Kiểm tra xem điểm Likert có khớp với chất lượng của câu trả lời mẫu hay chưa.
- Nếu HNMU điều chỉnh tên task, chủ đề hoặc cách ghi học liệu, cần cập nhật lại đúng trường tương ứng trong phiếu.
