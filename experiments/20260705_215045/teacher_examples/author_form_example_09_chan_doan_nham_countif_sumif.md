# EX09 — Chẩn đoán nhầm lẫn giữa COUNTIF và SUMIF

Trạng thái: ví dụ minh họa v0, đã căn theo các trường trong sheet “Luận giải chi tiết trường dữ liệu” của `review_form.xlsx`; cần HNMU/giáo sư rà soát trước khi dùng chính thức.

## 1. Thông tin bao phủ nội bộ

Phần này giúp UET truy vết ví dụ về ma trận bao phủ. Đây không phải là trường giáo viên bắt buộc phải điền trong phiếu tác giả.


| Thành phần               | Nội dung                                                                   |
| -------------------------- | --------------------------------------------------------------------------- |
| Mã ví dụ                | `EX09`                                                                      |
| Ô bao phủ từ ma trận   | `P05-COV-059`                                                               |
| Nhiệm vụ gia sư         | Chẩn đoán lỗi, hiểu lầm hoặc thiếu nền tảng (`T4`)                |
| Mức độ nhận thức      | Hiểu                                                                       |
| Kiểu tình huống         | Phản hồi hoặc sửa lỗi                                                  |
| Vì sao chọn ví dụ này | Minh họa lỗi hiểu nhầm chức năng của hai hàm bảng tính gần nhau. |

## 2. Phiếu tác giả minh họa

### 1. Tên người tạo dữ liệu (`author_name`)

Giáo viên minh họa 09

### 2. Mã task (`Task_id`)

T4 — Chẩn đoán lỗi, hiểu lầm hoặc thiếu nền tảng

### 3. Chủ đề (`Topic`)

Sử dụng bảng tính điện tử nâng cao

### 4. Mức độ nhận thức (`cognitive_level`)

Hiểu

### 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Em có bảng chi tiêu bên dưới. Em muốn tính tổng tiền của các khoản “Ăn uống”, nhưng công thức em dùng chỉ ra kết quả 3. Em không hiểu sai ở đâu.

### 6. Bài làm của học sinh (`student_work`)

Đề bài: Cho bảng chi tiêu sau. Hãy tính tổng số tiền của các khoản thuộc loại “Ăn uống”.


| Hàng | Loại khoản chi | Số tiền |
| ----- | ---------------- | --------: |
| 2     | Ăn uống        |     30000 |
| 3     | Đi lại         |     15000 |
| 4     | Ăn uống        |     25000 |
| 5     | Sách vở        |     40000 |
| 6     | Ăn uống        |     20000 |

Bài làm: `=COUNTIF(A2:A6;"Ăn uống")`

### 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Lượt 1:

Chưa có trao đổi sau bước mở đầu. Câu trả lời tiếp theo của gia sư được ghi ở mục “Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề”.

### 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

- Sử dụng hàm COUNTIF|Bài 10a. Sử dụng hàm COUNTIF|SGK Tin học 9|tr. 41
- Sử dụng hàm SUMIF|Bài 11a. Sử dụng hàm SUMIF|SGK Tin học 9|tr. 45

### 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)

Lỗi chính của em là dùng nhầm mục đích của hàm. `COUNTIF(A2:A6;"Ăn uống")` dùng để đếm có bao nhiêu dòng có loại khoản chi là “Ăn uống”, nên kết quả 3 là số khoản “Ăn uống”, không phải tổng tiền. Vì đề bài yêu cầu cộng số tiền, em cần dùng `SUMIF`: vùng điều kiện là A2:A6, điều kiện là “Ăn uống”, vùng cần cộng là B2:B6. Công thức phù hợp là `=SUMIF(A2:A6;"Ăn uống";B2:B6)`. Với bảng này, tổng tiền là 30000 + 25000 + 20000 = 75000.

### 10. Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)

- Có thể trước hết hỏi học sinh: “Kết quả 3 đang là số khoản hay tổng số tiền?” để học sinh tự nhận ra khác biệt COUNTIF và SUMIF.
- Có thể giải thích ngắn: COUNTIF trả về số lượng, SUMIF trả về tổng giá trị thỏa điều kiện.

### 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

- T4_R1 — Độ chính xác kiến thức và bám học liệu: 5.
- T4_R2 — Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh: 5.
- T4_R3 — Chất lượng hỗ trợ sư phạm/giàn giáo: 4.
- T4_R4 — Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi Tin học 9: 5.
- T4_R5 — Tuân thủ ranh giới an toàn, đạo đức và pháp lý: 5.

### 12. Độ chính xác về kiến thức (`truthfulness_score`)

5

### 13. Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)

- Không tạo thêm dữ liệu nhạy cảm về tài chính cá nhân: 5
- Không áp công thức khi chưa xác định vùng dữ liệu: 4
- Phù hợp lứa tuổi THCS: 5

### 14. Tên người kiểm tra chéo (`cross_validator_name`)

Chưa phân công trong bản minh họa.

### 15. Thời gian tạo dữ liệu (`created_at`)

20260707_090900

### 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chưa điền — chỉ điền khi tác giả và người kiểm tra chéo đã đồng thuận.

### 17. Ghi chú (`Note`)

Mức hỗ trợ: Chẩn đoán + gợi ý. Cần nêu rõ bản chất lỗi là nhầm mục đích đếm và tính tổng.

## 3. Lưu ý khi rà soát ví dụ này

- Kiểm tra xem `gold_response` đã dựa trên học liệu tham khảo hay chưa.
- Kiểm tra xem điểm Likert có khớp với chất lượng của câu trả lời mẫu hay chưa.
- Nếu HNMU điều chỉnh tên task, chủ đề hoặc cách ghi học liệu, cần cập nhật lại đúng trường tương ứng trong phiếu.
