# Mẫu phiếu tác giả

Mẫu này bám theo version mới của `review_form.xlsx`, trong đó `Mức độ nhận thức` là trường bắt buộc của phiếu tác giả. Thầy cô có thể sao chép từng mục dưới đây để viết một mẫu dữ liệu mới.

## 1. Tên người tạo dữ liệu (`author_name`)

Ghi họ tên đầy đủ của người tạo mẫu.

## 2. Mã task (`Task_id`)

Chọn một mã task đã được UET/HNMU thống nhất tạm thời, ví dụ: T1, T2, T3 hoặc T4 trong bản thiết kế hiện tại. Nếu phiếu mới của HNMU dùng mã T01–T07, UET cần ánh xạ trước khi nhập dữ liệu chính thức.

## 3. Chủ đề (`Topic`)

Ghi chủ đề/bài học trong SGK Tin học 9. Nếu chưa chắc tên chuẩn, ghi tên gần nhất và thêm ghi chú cần xác nhận.

## 4. Mức độ nhận thức (`cognitive_level`)

Chọn một trong ba giá trị: Biết, Hiểu, Vận dụng.

## 5. Yêu cầu của học sinh về kiến thức thuộc chủ đề (`student_prompt`)

Viết đúng lời học sinh hỏi hoặc yêu cầu gia sư hỗ trợ.

## 6. Bài làm của học sinh (`student_work`)

Ghi đề bài và bài làm của học sinh. Không thêm lời giải thích ngoài hai phần này.

Cách ghi gọn:

```text
Đề bài: ...

Bài làm: ...
```

Ở phần `Bài làm`, ghi đúng nội dung học sinh đã viết/chọn/làm. Ví dụ: ghi `A. Quyển vở, vì...`, không ghi lại thành “học sinh chọn A vì...”. Nếu là công thức hoặc mã lệnh, ghi nguyên công thức hoặc mã lệnh. Nếu là ảnh, dùng ảnh theo phiếu.

Nếu học sinh chưa làm, ghi:

```text
Đề bài: ...

Bài làm: Chưa có bài làm.
```

## 7. Lịch sử trao đổi giữa học sinh và gia sư (`conversation_history`)

Ghi các trao đổi diễn ra sau bước mở đầu. Bước mở đầu của học sinh đã nằm ở mục 5 (`student_prompt`) và mục 6 (`student_work`), nên không lặp lại câu hỏi hoặc bài làm đó ở mục này.

Nếu đã có trao đổi sau bước mở đầu, bước đầu tiên trong mục này nên là gia sư và bước cuối cùng nên là học sinh. Ví dụ:

```text
Lượt 1:

1. Gia sư: Em đã thử kiểm tra phần nào trước chưa?
2. Học sinh: Em mới kiểm tra đề bài, nhưng chưa biết lỗi nằm ở đâu.
```

Nếu chưa có trao đổi sau bước mở đầu, ghi:

```text
Lượt 1:

Chưa có trao đổi sau bước mở đầu.
```

Câu trả lời tiếp theo hoặc câu trả lời cuối cùng của gia sư được viết ở mục 9.

## 8. Danh sách học liệu tham khảo (`reference_curriculumn_list`)

Ghi theo dạng:

- Mục trong bài|Tên bài|Tên sách|Trang

Ví dụ:

- Sử dụng hàm IF|Bài 12a. Sử dụng hàm IF|SGK Tin học 9|tr. 48

## 9. Đáp án cho câu hỏi Yêu cầu của học sinh về kiến thức thuộc chủ đề (`gold_response`)

Viết câu trả lời mẫu của gia sư. Câu trả lời này phải dựa trên danh sách học liệu tham khảo và phù hợp với câu hỏi/lịch sử hội thoại.

## 10. Cách trả lời khác vẫn hợp lệ (`accepted_response_list`)

Ghi các cách trả lời khác vẫn chấp nhận được, mỗi cách là một gạch đầu dòng.

## 11. Điểm đánh giá theo thang đo Likert (`rubric_score_list`)

Ghi điểm 1–5 cho từng tiêu chí của task. Ví dụ:

- T2_R1 — Độ chính xác kiến thức và bám học liệu: 5.
- T2_R2 — Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh: 5.
- T2_R3 — Chất lượng hỗ trợ sư phạm/giàn giáo: 4.
- T2_R4 — Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi Tin học 9: 5.
- T2_R5 — Tuân thủ ranh giới an toàn, đạo đức và pháp lý: 5.

## 12. Độ chính xác về kiến thức (`truthfulness_score`)

Ghi điểm 1–5 cho độ chính xác của câu trả lời mẫu khi đối chiếu với học liệu tham khảo.

## 13. Tính tuân thủ ranh giới (`boundary_adherence_score_list`)

Ghi điểm 1–5 cho các ranh giới liên quan. Ví dụ:

- Đạo đức/pháp lý/an toàn: 5.
- Không khuyến khích gian lận hoặc làm thay quá mức: 5.
- Phù hợp lứa tuổi THCS: 5.

## 14. Tên người kiểm tra chéo (`cross_validator_name`)

Có thể để trống/chưa phân công ở giai đoạn tác giả. Chỉ điền khi đã có người kiểm tra chéo.

## 15. Thời gian tạo dữ liệu (`created_at`)

Ghi theo dạng `YYYYMMDD_HHMMSS`, ví dụ `20260707_090000`.

## 16. Thời gian hoàn thành dữ liệu (`completed_at`)

Chỉ điền khi tác giả và người kiểm tra chéo đã đồng thuận rằng mẫu hoàn thành. Nếu chưa, ghi “Chưa điền”.

## 17. Ghi chú (`Note`)

Ghi các lưu ý khi tạo mẫu. Nếu liên quan đến hỗ trợ sư phạm, nên dùng nhãn tiếng Việt như: Gợi mở, Giải thích, Gợi ý, Hướng dẫn, Làm mẫu.
