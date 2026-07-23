# EX16 — Gợi ý nhiều bước để viết công thức IF trong bảng tính

Trạng thái: ví dụ minh họa bổ sung v0, tập trung vào hội thoại nhiều bước; cần HNMU/giáo sư rà soát trước khi dùng chính thức.

## 1. Thông tin bao phủ nội bộ

Phần này giúp UET truy vết ví dụ về ma trận bao phủ. Đây không phải là trường giáo viên bắt buộc phải điền trong phiếu tác giả.

| Thành phần | Nội dung |
|---|---|
| Mã ví dụ | `EX16` |
| Ô bao phủ từ ma trận | `P05-COV-057` |
| Nhiệm vụ gia sư | T3 — Gợi ý từng bước để học sinh tự đi tiếp |
| Mức độ nhận thức | Vận dụng |
| Kiểu tình huống | Học sinh chưa biết ghép điều kiện và hai kết quả trong hàm IF. |
| Vì sao chọn ví dụ này | Minh họa giàn giáo nhiều bước ở bảng tính: gia sư không đưa công thức ngay mà lần lượt hỏi điều kiện, kết quả khi đúng và kết quả khi sai. |

## 2. Phiếu tác giả minh họa

### 1. Tên người tạo dữ liệu (`author_name`)

Giáo viên minh họa 16

### 2. Mã task (`Task_id`)

T3 — Gợi ý từng bước để học sinh tự đi tiếp

### 3. Chủ đề (`Topic`)

Sử dụng bảng tính điện tử nâng cao

### 4. Mức độ nhận thức (`cognitive_level`)

Vận dụng

### 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Em cần dùng hàm IF để hiện “Đạt” nếu điểm từ 5 trở lên, còn lại hiện “Chưa đạt”, nhưng em chưa biết bắt đầu viết công thức như thế nào.

### 6. Bài làm của học sinh (`student_work`)

Đề bài: Cho điểm kiểm tra ở ô B2. Dùng hàm IF để hiện “Đạt” nếu điểm từ 5 trở lên, ngược lại hiện “Chưa đạt”.

Bài làm: Chưa có bài làm.

### 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Lượt 1:

1. Gia sư: Trước hết, em thử xác định điều kiện cần kiểm tra trong ô B2 là gì?
2. Học sinh: Điểm trong B2 phải lớn hơn hoặc bằng 5 ạ.
3. Gia sư: Tốt. Nếu điều kiện đó đúng thì ô kết quả cần hiện chữ gì, và nếu sai thì hiện chữ gì?
4. Học sinh: Đúng thì hiện “Đạt”, sai thì hiện “Chưa đạt”. Em còn lúng túng thứ tự các phần trong hàm IF.

### 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

- Sử dụng hàm IF|Bài 12a. Sử dụng hàm IF|SGK Tin học 9|tr. 48

### 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)

Em đã xác định đúng ba phần quan trọng rồi. Với hàm IF, em ghép theo thứ tự: điều kiện cần kiểm tra, giá trị khi điều kiện đúng, giá trị khi điều kiện sai. Trong bài này, điều kiện là `B2>=5`; khi đúng thì hiện “Đạt”; khi sai thì hiện “Chưa đạt”. Vì vậy công thức có thể viết là `=IF(B2>=5;"Đạt";"Chưa đạt")`. Sau khi nhập công thức, em nên thử với vài điểm khác nhau, ví dụ B2 = 4 thì kết quả phải là “Chưa đạt”, B2 = 5 hoặc 7 thì kết quả phải là “Đạt”.

### 10. Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)

- Có thể tiếp tục gợi mở bằng khung `=IF(điều kiện; giá trị nếu đúng; giá trị nếu sai)` rồi để học sinh tự điền.
- Có thể nhắc học sinh kiểm tra dấu phân cách theo phần mềm hoặc thiết lập máy đang dùng.

### 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

- T3_R1 — Độ chính xác kiến thức và bám học liệu: 5.
- T3_R2 — Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh: 5.
- T3_R3 — Chất lượng hỗ trợ sư phạm/giàn giáo: 5.
- T3_R4 — Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi Tin học 9: 5.
- T3_R5 — Tuân thủ ranh giới an toàn, đạo đức và pháp lý: 5.

### 12. Độ chính xác về kiến thức (`truthfulness_score`)

5

### 13. Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)

- Không làm phức tạp bài bằng hàm lồng nhau không cần thiết: 5
- Không bỏ qua bước tự kiểm tra bằng dữ liệu thử: 4
- Phù hợp lứa tuổi THCS: 5

### 14. Tên người kiểm tra chéo (`cross_validator_name`)

Chưa phân công trong bản minh họa.

### 15. Thời gian tạo dữ liệu (`created_at`)

20260708_100000

### 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chưa điền — chỉ điền khi tác giả và người kiểm tra chéo đã đồng thuận.

### 17. Ghi chú (`Note`)

Mức hỗ trợ: Gợi ý + hướng dẫn. Tutor chia công thức IF thành ba phần để học sinh tự ghép trước khi thấy công thức hoàn chỉnh.

## 3. Lưu ý khi rà soát ví dụ này

- Kiểm tra xem `conversation_history` đã bắt đầu bằng gia sư và kết thúc bằng học sinh hay chưa.
- Kiểm tra xem `gold_response` đã dùng đúng thông tin học sinh cung cấp ở các bước trước hay chưa.
- Nếu HNMU điều chỉnh tên task, chủ đề hoặc cách ghi học liệu, cần cập nhật lại đúng trường tương ứng trong phiếu.
