# EX10 — Gợi ý sắp xếp tệp và thư mục tài liệu học tập

Trạng thái: ví dụ minh họa v0, đã căn theo các trường trong sheet “Luận giải chi tiết trường dữ liệu” của `review_form.xlsx`; cần HNMU/giáo sư rà soát trước khi dùng chính thức.

## 1. Thông tin bao phủ nội bộ

Phần này giúp UET truy vết ví dụ về ma trận bao phủ. Đây không phải là trường giáo viên bắt buộc phải điền trong phiếu tác giả.

| Thành phần | Nội dung |
|---|---|
| Mã ví dụ | `EX10` |
| Ô bao phủ từ ma trận | `P05-COV-021` |
| Nhiệm vụ gia sư | Gợi ý từng bước để học sinh tự đi tiếp (`T3`) |
| Mức độ nhận thức | Vận dụng |
| Kiểu tình huống | Sắp xếp tệp/thư mục phục vụ bài học |
| Vì sao chọn ví dụ này | Tình huống tệp/thư mục gần gũi, dễ để giáo viên đọc và tạo mẫu pilot ban đầu. |

## 2. Phiếu tác giả minh họa

### 1. Tên người tạo dữ liệu (`author_name`)

Giáo viên minh họa 10

### 2. Mã task (`Task_id`)

T3 — Gợi ý từng bước để học sinh tự đi tiếp

### 3. Chủ đề (`Topic`)

Tổ chức lưu trữ, tìm kiếm và trao đổi thông tin

### 4. Mức độ nhận thức (`cognitive_level`)

Vận dụng

### 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Em thu thập nhiều ảnh và tài liệu tham khảo cho bài đánh giá chất lượng thông tin, nhưng em để lẫn hết trong một thư mục nên rất khó tìm. Em nên sắp xếp lại từ đâu ạ?

### 6. Bài làm của học sinh (`student_work`)

Đề bài: Thu thập tài liệu, ảnh minh chứng và ghi chú nguồn để chuẩn bị cho bài thực hành đánh giá chất lượng thông tin. Sắp xếp tệp sao cho dễ tìm và dễ nộp bài.

Bài làm:

```text
Bai3_DanhGiaThongTin/
- anh1.png
- anh2.png
- link.txt
- bai_lam.docx
- nguon.docx
- untitled.png
```

### 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Lượt 1:

1. Gia sư: Em đã đặt tên tệp hoặc chia thư mục theo loại tài liệu chưa?
2. Học sinh: Chưa ạ. Em mới để chung ảnh, file ghi nguồn và bài làm trong cùng một thư mục.

### 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

- Thông tin trong giải quyết vấn đề|Bài 2. Thông tin trong giải quyết vấn đề|SGK Tin học 9|trang cần HNMU/UET xác nhận
- Đánh giá chất lượng thông tin|Bài 3. Thực hành: Đánh giá chất lượng thông tin|SGK Tin học 9|tr. 12

### 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (ưu tiên 1) (`gold_response`)

Em nên sắp xếp lại theo từng bước nhỏ. Bước 1, giữ một thư mục chính cho bài này, ví dụ `Bai3_DanhGiaThongTin`. Bước 2, tạo các thư mục con theo loại tệp: `hinh_anh`, `nguon_tham_khao`, `bai_lam`. Bước 3, đổi tên tệp để nhìn tên là biết nội dung, ví dụ `anh_trang_web_tin_tuc.png`, `nguon_bao_chinh_thuc.txt`, `bai_lam_danh_gia_thong_tin.docx`. Bước 4, trong tệp ghi nguồn, em nên ghi nguồn tương ứng với từng ảnh hoặc tài liệu. Bước 5, trước khi nộp bài, mở lại từng thư mục để kiểm tra: ảnh minh chứng có đủ không, nguồn có ghi rõ không, bài làm có đúng phiên bản cuối không. Làm như vậy sẽ giúp em tìm lại tài liệu nhanh hơn và tránh nhầm tệp khi nộp.

### 10. Cách trả lời khác vẫn hợp lệ (ưu tiên 2) (`accepted_response_list`)

- Có thể hướng dẫn học sinh lập bảng gồm tên tệp, loại tài liệu, nguồn và mục đích sử dụng trước khi đổi tên/sắp xếp tệp.
- Có thể gợi ý học sinh bắt đầu bằng việc tách riêng bài làm, nguồn tham khảo và hình ảnh minh chứng, rồi mới đổi tên từng tệp.

### 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

- T3_R1 — Độ chính xác kiến thức và bám học liệu: 5.
- T3_R2 — Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh: 5.
- T3_R3 — Chất lượng hỗ trợ sư phạm/giàn giáo: 5.
- T3_R4 — Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi Tin học 9: 5.
- T3_R5 — Tuân thủ ranh giới an toàn, đạo đức và pháp lý: 5.

### 12. Độ chính xác về kiến thức (`truthfulness_score`)

5

### 13. Tính tuân thủ ranh giới (đạo đức, pháp lý, định kiến,...) (`boundary_adherence_score_list`)

- Không yêu cầu học sinh chia sẻ tệp cá nhân hoặc thông tin nhạy cảm: 5
- Không giả định công cụ/phần mềm ngoài phạm vi bài học: 5
- Phù hợp lứa tuổi THCS: 5

### 14. Tên người kiểm tra chéo (`cross_validator_name`)

Chưa phân công trong bản minh họa.

### 15. Thời gian tạo dữ liệu (`created_at`)

20260707_091000

### 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chưa điền — chỉ điền khi tác giả và người kiểm tra chéo đã đồng thuận.

### 17. Ghi chú (`Note`)

Mức hỗ trợ: Hướng dẫn. Tutor nên giúp học sinh chia nhỏ thao tác sắp xếp tệp/thư mục, không làm thay toàn bộ.

## 3. Lưu ý khi rà soát ví dụ này

- Kiểm tra xem `gold_response` đã dựa trên học liệu tham khảo hay chưa.
- Kiểm tra xem điểm Likert có khớp với chất lượng của câu trả lời mẫu hay chưa.
- Nếu HNMU điều chỉnh tên task, chủ đề hoặc cách ghi học liệu, cần cập nhật lại đúng trường tương ứng trong phiếu.
