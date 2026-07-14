# Chuyển trạng thái từ experiment `20260705_215045`

Ngày tạo: 09/07/2026  
Experiment mới: `20260709_155523`

## 1. Lý do mở experiment mới

Experiment trước tập trung vào nghiên cứu nền, phạm vi học liệu, task/rubric v0, ma trận bao phủ và ví dụ phiếu tác giả. Sau trao đổi ngày 08/07, vai trò của HNMU và luồng dữ liệu đã thay đổi đủ lớn để cần một experiment riêng:

- HNMU tạo hội thoại thô thay vì điền toàn bộ phiếu tác giả;
- UET ánh xạ hội thoại sang định dạng benchmark;
- task và rubric được phát triển ở phía UET;
- cần thêm giao thức sử dụng benchmark và thiết kế thí nghiệm.

Không sửa ngược các artifact của experiment cũ. Chúng được dùng như đầu vào có phiên bản.

## 2. Artifact được dùng tiếp

| Artifact cũ | Vai trò trong experiment mới |
|---|---|
| `teacher_examples/author_form_field_reference_v0.csv` | Danh sách trường đích và quy ước hiện tại của phiếu tác giả. |
| `teacher_examples/hnmu_sample_01_scratch_average_single_response_author_form.md` | Ví dụ ánh xạ một mẫu HNMU theo hướng chấm phản hồi cuối. |
| `teacher_examples/hnmu_sample_01_conversion_notes.md` | Các lưu ý về ranh giới giữa `student_prompt`, `conversation_history` và `gold_response`. |
| `benchmark_design/benchmark_tasks.csv` | Danh sách task v0 theo hành vi gia sư; cần rà soát, không coi là đã chốt. |
| `benchmark_design/rubrics.csv` | Rubric R1–R5 thang Likert 1–5; cần làm rõ cửa sổ quan sát. |
| `benchmark_design/task_design_rationale_v0.md` | Luận giải ban đầu về task. |
| `benchmark_design/rubric_design_rationale_v0.md` | Luận giải ban đầu về rubric. |
| `coverage_design/general_coverage_matrix_v0.csv` | Khung kiểm tra độ phủ, không dùng để ép HNMU tự gán task. |
| `literature_notes/` | Bằng chứng nghiên cứu cho quyết định task/rubric và thiết kế đánh giá. |
| `topic_taxonomy/tin9_sgk_topics_v0.csv` | Danh sách chủ đề/bài học v0 để chuẩn hóa ở phía UET. |

## 3. Artifact không được coi là nguồn chân lý cuối

- 17 ví dụ do UET tạo không thay thế dữ liệu thật của HNMU.
- Task T1–T4 và rubric R1–R5 vẫn ở trạng thái cần rà soát.
- Ma trận bao phủ là công cụ thiết kế, không phải định dạng HNMU phải điền.
- Phiếu tác giả là định dạng đích nội bộ ở giai đoạn mới, không còn là mô tả đầy đủ quy trình làm việc của giáo viên.

## 4. Quyết định được kế thừa

- Chỉ dùng ba mức nhận thức: `Biết`, `Hiểu`, `Vận dụng`.
- `student_prompt` là lời đầu tiên của học sinh.
- `conversation_history` là phần trao đổi tiếp theo, bắt đầu bằng gia sư và kết thúc bằng học sinh.
- `gold_response` là phản hồi cuối mong muốn của gia sư.
- Thiết kế hiện tại ưu tiên chấm phản hồi cuối, đồng thời bảo toàn toàn bộ hội thoại nguồn.
- Nội dung do HNMU cung cấp không được tự ý viết lại.

## 5. Việc chưa kế thừa như một quyết định cuối

- Task chính và quy tắc gán task.
- Cửa sổ quan sát của từng rubric.
- Cách sử dụng trường “Đáp án” trong mẫu thô.
- Cách chấm toàn bộ hội thoại nếu sau này chuyển sang đánh giá đa lượt.
- Danh sách mô hình, số lần chạy và phương pháp tổng hợp kết quả thí nghiệm.

