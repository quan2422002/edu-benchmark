# EX08 — Phản hồi công thức IF trong bảng tính

Trạng thái: ví dụ minh họa v0, đã căn theo các trường trong sheet “Luận giải chi tiết trường dữ liệu” của `review_form.xlsx`; cần HNMU/giáo sư rà soát trước khi dùng chính thức.

## 1. Thông tin bao phủ nội bộ

Phần này giúp UET truy vết ví dụ về ma trận bao phủ. Đây không phải là trường giáo viên bắt buộc phải điền trong phiếu tác giả.

| Thành phần | Nội dung |
|---|---|
| Mã ví dụ | `EX08` |
| Ô bao phủ từ ma trận | `P05-COV-054` |
| Nhiệm vụ gia sư | Phản hồi bài làm hoặc lập luận của học sinh (`T2`) |
| Mức độ nhận thức | Vận dụng |
| Kiểu tình huống | Phản hồi hoặc sửa lỗi |
| Vì sao chọn ví dụ này | Minh họa phản hồi bài làm bảng tính, một dạng thường gặp trong Tin học 9. |

## 2. Phiếu tác giả minh họa

### 1. Tên người tạo dữ liệu (`author_name`)

Giáo viên minh họa 08

### 2. Mã task (`Task_id`)

T2 — Phản hồi bài làm hoặc lập luận của học sinh

### 3. Chủ đề (`Topic`)

Sử dụng bảng tính điện tử nâng cao

### 4. Mức độ nhận thức (`cognitive_level`)

Vận dụng

### 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Em nhập công thức =IF(B2>5000000;"Vượt";"Không vượt") để kiểm tra chi tiêu. Nhưng em không chắc công thức này đúng chưa.

### 6. Bài làm của học sinh (`student_work`)

Đề bài: Dùng hàm IF để kiểm tra tổng chi tiêu trong ô B2 có vượt ngưỡng 5.000.000 hay không.

Bài làm: `=IF(B2>5000000;"Vượt";"Không vượt")`

### 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Lượt 1:

Chưa có trao đổi sau bước mở đầu. Câu trả lời tiếp theo của gia sư được ghi ở mục “Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề”.

### 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

- Sử dụng hàm IF|Bài 12a. Sử dụng hàm IF|SGK Tin học 9|tr. 48

### 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)

Nếu mục tiêu của em là: ô B2 chứa tổng chi tiêu, và em muốn hiện “Vượt” khi chi tiêu lớn hơn 5.000.000, còn lại hiện “Không vượt”, thì ý tưởng công thức của em là đúng. Công thức IF gồm ba phần: điều kiện B2>5000000; kết quả khi điều kiện đúng là “Vượt”; kết quả khi điều kiện sai là “Không vượt”. Em cần kiểm tra thêm hai điểm: dữ liệu trong B2 có phải là số hay không, và phần mềm bảng tính của em dùng dấu chấm phẩy hay dấu phẩy để ngăn cách tham số. Nếu phần mềm yêu cầu dấu phẩy, công thức sẽ là =IF(B2>5000000,"Vượt","Không vượt").

### 10. Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)

- Có thể yêu cầu học sinh thử hai giá trị B2, ví dụ 6.000.000 và 4.000.000, để tự kiểm tra công thức.
- Có thể giải thích cú pháp IF trước, rồi mới nhận xét công thức của học sinh.

### 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

- T2_R1 — Độ chính xác kiến thức và bám học liệu: 5.
- T2_R2 — Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh: 5.
- T2_R3 — Chất lượng hỗ trợ sư phạm/giàn giáo: 4.
- T2_R4 — Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi Tin học 9: 5.
- T2_R5 — Tuân thủ ranh giới an toàn, đạo đức và pháp lý: 5.

### 12. Độ chính xác về kiến thức (`truthfulness_score`)

5

### 13. Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)

- Không làm thay bảng tính mở rộng ngoài yêu cầu: 5
- Không gây hiểu nhầm về dấu ngăn cách tham số: 5
- Phù hợp lứa tuổi THCS: 5

### 14. Tên người kiểm tra chéo (`cross_validator_name`)

Chưa phân công trong bản minh họa.

### 15. Thời gian tạo dữ liệu (`created_at`)

20260707_090800

### 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chưa điền — chỉ điền khi tác giả và người kiểm tra chéo đã đồng thuận.

### 17. Ghi chú (`Note`)

Mức hỗ trợ: Phản hồi + giải thích. Cần chú ý khác biệt dấu chấm phẩy/dấu phẩy giữa phần mềm hoặc thiết lập vùng.

## 3. Lưu ý khi rà soát ví dụ này

- Kiểm tra xem `gold_response` đã dựa trên học liệu tham khảo hay chưa.
- Kiểm tra xem điểm Likert có khớp với chất lượng của câu trả lời mẫu hay chưa.
- Nếu HNMU điều chỉnh tên task, chủ đề hoặc cách ghi học liệu, cần cập nhật lại đúng trường tương ứng trong phiếu.
