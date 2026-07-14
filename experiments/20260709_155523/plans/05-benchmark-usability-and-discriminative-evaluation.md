# Plan 05 — Đánh giá khả năng áp dụng và phân biệt của benchmark

Experiment: `20260709_155523`
Trạng thái: `DRAFT` — chưa triển khai.
Ngày lập: 11/07/2026
Ngày cập nhật: 14/07/2026

## 1. Mục tiêu

Lên kế hoạch kiểm tra tiêu chí thứ ba mà giáo sư nêu: benchmark phải có khả năng đánh giá gia sư một cách toàn diện và phân biệt được tutor tốt, tutor trung bình và tutor kém.

Plan này là việc sau, chỉ triển khai khi đã có mẫu benchmark hoàn chỉnh từ Plan 06. Plan 05 không làm việc trực tiếp với dữ liệu thô HNMU.

## 2. Điều kiện bắt đầu

Cần có:

1. Dữ liệu hội thoại HNMU đã qua kiểm toán ở Plan 04.
2. Mẫu benchmark đã được chuyển đổi ở Plan 06 và truy vết được.
3. Task/rubric đủ ổn định.
4. Giao thức đầu vào model rõ ràng.
5. Cách chấm điểm đã được HNMU/UET chấp nhận.
6. Có tập nhỏ được UET/HNMU xác nhận để làm điểm neo ban đầu.

## 3. Câu hỏi cần trả lời

1. Benchmark có làm lộ khác biệt giữa tutor tốt, trung bình và kém không?
2. Điểm rubric có phân hóa hay bị dồn vào một mức?
3. Các task khác nhau có tạo ra độ khó khác nhau không?
4. Mô hình mạnh hơn có điểm cao hơn một cách hợp lý không?
5. Human reviewer có đồng thuận khi chấm một tập nhỏ không?
6. Có mẫu nào rubric không đủ phân biệt hoặc gây nhầm lẫn không?
7. Mẫu nào có vấn đề do chuyển đổi từ dữ liệu thô, dù dữ liệu thô đã qua audit?

## 4. Thiết kế thử nghiệm sơ bộ

Có thể dùng ba nhóm phản hồi:

1. Phản hồi tốt: lấy từ reference/gold response do HNMU hoặc UET duyệt.
2. Phản hồi trung bình: model mạnh nhưng không được cung cấp học liệu đầy đủ, hoặc phản hồi có thiếu sót nhẹ.
3. Phản hồi kém: phản hồi lộ đáp án quá sớm, sai học liệu, không giàn giáo, hoặc không bám yêu cầu học sinh.

Lưu ý: phản hồi kém phải được tạo và dùng cẩn thận, không làm nhiễm dữ liệu chính thức.

## 5. Output dự kiến

- `reports/benchmark-discriminative-evaluation-design.md`
- bảng thiết kế thử nghiệm
- bảng phân tích phân bố điểm
- danh sách task/rubric cần sửa nếu không phân hóa
- handoff cho giai đoạn paper/experiment

## 6. Ngoài phạm vi

- Không chạy trước khi có benchmark samples hoàn chỉnh.
- Không thay thế đánh giá của HNMU.
- Không dùng model judge làm nguồn chân lý nếu chưa hiệu chỉnh bằng người chấm.
- Không sửa dữ liệu thô HNMU.
