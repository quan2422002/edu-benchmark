# Plan 06 — Chuyển hội thoại thô HNMU thành mẫu benchmark hoàn chỉnh

Experiment: `20260709_155523`
Trạng thái: `DRAFT` — chưa triển khai.
Ngày lập: 14/07/2026

## 1. Mục tiêu

Chuyển dữ liệu hội thoại thô HNMU đã qua kiểm toán thành mẫu benchmark hoàn chỉnh, có thể dùng trong các thử nghiệm đánh giá gia sư AI sau này.

Plan này lấp khoảng trống giữa Plan 04 và Plan 05:

```text
Dữ liệu thô HNMU đã audit
        ↓
Ánh xạ sang phiếu tác giả / cấu trúc benchmark
        ↓
Mẫu benchmark hoàn chỉnh có truy vết
        ↓
Plan 05 đánh giá khả năng áp dụng và phân biệt
```

## 2. Điều kiện bắt đầu

Cần có:

1. Batch HNMU đã qua Plan 04.
2. Danh sách mẫu đủ điều kiện chuyển đổi thử.
3. Checklist chất lượng và kết quả audit cho từng mẫu.
4. Học liệu registry v0 từ Plan 03, hoặc ít nhất mapping sơ bộ theo `Bài` và `Vị trí`.
5. Task/rubric v0 từ experiment `20260705_215045` hoặc bản cập nhật được UET chấp nhận.

## 3. Nguyên tắc

1. Không sửa nội dung hội thoại gốc.
2. Mọi mẫu benchmark phải truy vết được về file gốc, sheet, dòng gốc và batch.
3. Nếu agent điền trường còn thiếu, phải lưu `confidence_score`, lý do và trạng thái cần xác nhận.
4. `Đáp án` phải tách khỏi `gold_response`.
5. `gold_response` là phản hồi mong muốn của gia sư trong bối cảnh đã cho, không phải chỉ là đáp án cuối.
6. Một hội thoại thô có thể tạo nhiều mẫu benchmark nếu cắt ở nhiều lượt gia sư, miễn là truy vết rõ.
7. Nếu không chắc task/rubric, mẫu phải vào hàng đợi UET/HNMU xác nhận, không tự chốt.

## 4. Luồng chuyển đổi đề xuất

### Bước 1 — Chuẩn hóa bảng đầu vào dẫn xuất

Đầu vào:

- File Excel HNMU gốc.
- Kết quả Plan 04: `quality_check_results.csv`, `hnmu_review_queue.csv`, báo cáo độ phủ/trùng lặp.

Code thực hiện:

- Đọc dữ liệu từ bản gốc.
- Gắn mã dòng dẫn xuất, ví dụ `raw_sample_id`.
- Ghép với kết quả audit.
- Chỉ lấy mẫu đạt điều kiện hoặc mẫu được UET cho phép chuyển đổi thử.

Output dự kiến:

- `outputs/benchmark_conversion/conversion_input_candidates.csv`

### Bước 2 — Ánh xạ cột HNMU sang trường phiếu tác giả

Mapping sơ bộ:

| Cột HNMU | Trường benchmark/phiếu tác giả dự kiến | Ghi chú |
| --- | --- | --- |
| `Bài` | bài học / learning resource reference | Cần mapping với registry học liệu. |
| `Vị trí` | vị trí học liệu | Có thể là mục/trang SGK; cần chuẩn hóa. |
| `Câu hỏi` | `student_prompt` hoặc đề bài/yêu cầu ban đầu | Cần xét cùng hội thoại. |
| `Mức Bloom` | mức nhận thức | Giữ nguyên nhãn gốc và có thể chuẩn hóa về 3 mức. |
| `Đáp án (SGV)` | `Đáp án` | Không trộn vào `gold_response`. |
| `Hội thoại gia sư (Theo phương pháp Dàn giáo)` | nguồn để tách `student_prompt`, `conversation_history`, `gold_response` | Không sửa nội dung gốc. |

Output dự kiến:

- `outputs/benchmark_conversion/author_form_mapped_candidates.csv`

### Bước 3 — Tách hội thoại thành mẫu benchmark

Quy ước:

- `student_prompt`: tuyên bố/yêu cầu ban đầu của học sinh về vấn đề đang gặp phải.
- `conversation_history`: lịch sử hội thoại sau yêu cầu ban đầu, trước phản hồi gia sư mục tiêu.
- `gold_response`: phản hồi mong muốn của gia sư dựa trên `student_prompt` và `conversation_history`.
- `Đáp án`: đáp án đúng cho đề bài/câu hỏi, tách riêng khỏi phản hồi gia sư.

Một hội thoại có thể tạo:

- một mẫu nếu chỉ chấm phản hồi cuối;
- nhiều mẫu nếu cắt ở nhiều lượt gia sư có giá trị đánh giá.

Code có thể tách cấu trúc theo nhãn `HS:` và `AI:`. Agent chỉ hỗ trợ khi format mơ hồ hoặc cần xác định lượt nào có giá trị sư phạm.

Output dự kiến:

- `outputs/benchmark_conversion/dialogue_split_candidates.csv`

### Bước 4 — Gán task, rubric và trường còn thiếu

Thành phần sử dụng:

- Code: kiểm schema, giữ truy vết, tạo bảng dẫn xuất.
- `benchmark-specification-designer`: gợi ý task/rubric dựa trên nhiệm vụ gia sư, mức nhận thức, dạng bài và hội thoại.
- `learning-resource-curator`: gợi ý học liệu/chủ đề nếu mapping `Bài`/`Vị trí` chưa rõ.
- UET/HNMU: xác nhận các mẫu không chắc.

Mọi trường do agent gợi ý cần có:

- `suggested_value`
- `confidence_score`
- `rationale`
- `needs_human_review`

Output dự kiến:

- `outputs/benchmark_conversion/benchmark_sample_candidates.csv`
- `outputs/benchmark_conversion/human_review_needed.csv`

### Bước 5 — Xuất mẫu benchmark v0

Chỉ xuất các mẫu:

- đã qua Plan 04;
- tách hội thoại đúng quy ước;
- có truy vết gốc;
- không có lỗi nghiêm trọng chưa xử lý;
- task/rubric đủ tự tin hoặc đã được UET/HNMU xác nhận.

Output dự kiến:

- `outputs/benchmark_conversion/benchmark_samples_v0.csv`
- `reports/raw-dialogue-to-benchmark-conversion-v0.md`
- handoff cho Plan 05.

## 5. Vai trò của từng thành phần

### 5.1. Code

- Đọc dữ liệu.
- Kiểm schema.
- Tách hội thoại theo pattern có thể tái lập.
- Ghép kết quả audit.
- Tạo ID và bảng truy vết.
- Xuất CSV/JSON dẫn xuất.

### 5.2. Agent

- Gợi ý task/rubric khi cần hiểu ngữ nghĩa.
- Gợi ý học liệu/chủ đề khi mapping chưa chắc.
- Đánh dấu mẫu cần người xác nhận.
- Viết lý do cho quyết định gợi ý.

### 5.3. HNMU/UET

- Xác nhận nội dung chuyên môn.
- Xác nhận các mẫu agent/code không đủ chắc.
- Quyết định mẫu nào được vào benchmark v0.

## 6. Tiêu chí hoàn thành

Plan hoàn thành khi có:

1. Bảng ứng viên chuyển đổi từ batch HNMU đã audit.
2. Logic tách `student_prompt`, `conversation_history`, `gold_response`, `Đáp án` chạy được trên batch thử.
3. Bảng mẫu benchmark v0 có truy vết gốc.
4. Bảng mẫu cần người xác nhận.
5. Báo cáo nêu rõ tỷ lệ chuyển đổi thành công, lỗi thường gặp và đề xuất sửa quy trình.

## 7. Ngoài phạm vi

- Không sửa file Excel gốc.
- Không chấm model.
- Không kết luận benchmark tốt/xấu; việc đó thuộc Plan 05.
- Không tự final task/rubric nếu HNMU/UET chưa chốt.
