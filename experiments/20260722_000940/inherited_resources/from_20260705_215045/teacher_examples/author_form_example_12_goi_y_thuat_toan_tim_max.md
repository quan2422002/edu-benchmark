# EX12 — Gợi ý thuật toán tìm số lớn nhất

Trạng thái: ví dụ minh họa v0, đã căn theo các trường trong sheet “Luận giải chi tiết trường dữ liệu” của `review_form.xlsx`; cần HNMU/giáo sư rà soát trước khi dùng chính thức.

## 1. Thông tin bao phủ nội bộ

Phần này giúp UET truy vết ví dụ về ma trận bao phủ. Đây không phải là trường giáo viên bắt buộc phải điền trong phiếu tác giả.


| Thành phần                             | Nội dung                                                                                   |
| ---------------------------------------- | ------------------------------------------------------------------------------------------- |
| Mã ví dụ                              | `EX12`                                                                                      |
| Ô bao phủ từ ma trận                 | `P05-COV-081`                                                                               |
| Nhiệm vụ gia sư                       | Gợi ý từng bước để học sinh tự đi tiếp (`T3`)                                    |
| Mức độ nhận thức                    | Vận dụng                                                                                  |
| Kiểu tình huống                       | Lập trình, thuật toán hoặc bài toán tin học                                         |
| Vì sao chọn ví dụ này               | Minh họa giàn giáo ở mức thuật toán, trước khi chuyển sang viết chương trình. |

## 2. Phiếu tác giả minh họa

### 1. Tên người tạo dữ liệu (`author_name`)

Giáo viên minh họa 12

### 2. Mã task (`Task_id`)

T3 — Gợi ý từng bước để học sinh tự đi tiếp

### 3. Chủ đề (`Topic`)

Giải quyết vấn đề với sự trợ giúp của máy tính

### 4. Mức độ nhận thức (`cognitive_level`)

Vận dụng

### 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Em cần tìm số lớn nhất trong một dãy số nhưng không biết nghĩ thuật toán từ đâu.

### 6. Bài làm của học sinh (`student_work`)

Đề bài: Tìm số lớn nhất trong một dãy số.

Bài làm: Chưa có bài làm.

### 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Lượt 1:

1. Gia sư: Nếu dãy chỉ có một số thì số lớn nhất là số nào?
2. Học sinh: Là chính số đó ạ, nhưng nếu có nhiều số thì em bị rối.

### 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

- Bài toán tin học và cách mô tả thuật toán|Bài 15. Bài toán tin học|SGK Tin học 9|tr. 79

### 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)

Em hãy nghĩ theo cách “giữ số lớn nhất tạm thời”. Bước 1, giả sử số đầu tiên đang là số lớn nhất tạm thời. Bước 2, đọc số tiếp theo trong dãy. Bước 3, so sánh số vừa đọc với số lớn nhất tạm thời. Nếu số mới lớn hơn, em cập nhật số lớn nhất tạm thời bằng số mới; nếu không, giữ nguyên. Bước 4, lặp lại đến khi hết dãy. Khi đó, số lớn nhất tạm thời chính là kết quả. Em thử áp dụng với dãy 4, 7, 2, 9: ban đầu lớn nhất là 4, gặp 7 thì đổi thành 7, gặp 2 thì giữ 7, gặp 9 thì đổi thành 9.

### 10. Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)

- Có thể dùng câu hỏi gợi mở theo từng bước thay vì nêu đủ thuật toán ngay, nếu lịch sử hội thoại chưa chạm giới hạn.
- Có thể yêu cầu học sinh mô phỏng bằng bảng gồm “số đang xét” và “lớn nhất tạm thời”.

### 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

- T3_R1 — Độ chính xác kiến thức và bám học liệu: 5.
- T3_R2 — Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh: 5.
- T3_R3 — Chất lượng hỗ trợ sư phạm/giàn giáo: 5.
- T3_R4 — Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi Tin học 9: 5.
- T3_R5 — Tuân thủ ranh giới an toàn, đạo đức và pháp lý: 5.

### 12. Độ chính xác về kiến thức (`truthfulness_score`)

5

### 13. Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)

- Không nhảy ngay sang code khi học sinh đang cần thuật toán: 5
- Không làm thay toàn bộ nếu còn lượt gợi mở: 4
- Phù hợp lứa tuổi THCS: 5

### 14. Tên người kiểm tra chéo (`cross_validator_name`)

Chưa phân công trong bản minh họa.

### 15. Thời gian tạo dữ liệu (`created_at`)

20260707_091200

### 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chưa điền — chỉ điền khi tác giả và người kiểm tra chéo đã đồng thuận.

### 17. Ghi chú (`Note`)

Mức hỗ trợ: Gợi ý + hướng dẫn. Nếu chưa chạm giới hạn hội thoại, có thể giảm mức hỗ trợ bằng cách hỏi gợi mở trước.

## 3. Lưu ý khi rà soát ví dụ này

- Kiểm tra xem `gold_response` đã dựa trên học liệu tham khảo hay chưa.
- Kiểm tra xem điểm Likert có khớp với chất lượng của câu trả lời mẫu hay chưa.
- Nếu HNMU điều chỉnh tên task, chủ đề hoặc cách ghi học liệu, cần cập nhật lại đúng trường tương ứng trong phiếu.
