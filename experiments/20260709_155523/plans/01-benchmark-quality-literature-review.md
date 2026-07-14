# Plan 01 — Đọc paper về cách đánh giá chất lượng benchmark

Experiment: `20260709_155523`
Trạng thái: `HOÀN THÀNH` — được Quân yêu cầu triển khai ngày 12/07/2026; hoàn thành ngày 14/07/2026.
Ngày lập: 11/07/2026
Ngày cập nhật: 14/07/2026

## 1. Mục tiêu

Đọc lại các paper cốt lõi với câu hỏi mới:

> Các paper đánh giá chất lượng của chính benchmark như thế nào?

Trọng tâm không phải là “benchmark được dùng để chấm model ra sao”, mà là “paper đã chứng minh benchmark của họ đáng tin, đủ phủ, đúng, đa dạng và có khả năng phân biệt năng lực model như thế nào”.

Sau cập nhật ngày 14/07/2026, Plan 01 cần có thêm một output cuối: checklist kiểm định chất lượng v0 cho dữ liệu HNMU. Checklist này là cầu nối từ phần đọc paper sang Plan 04, không phải code kiểm toán.

## 2. Nguồn cần đọc

Không cần search web cho 4 paper bắt buộc. Tất cả paper cần đọc trong plan này đã được Quân lưu sẵn ở thư mục local:

```text
document/paper/source_paper/
```

Bắt buộc đọc kỹ 4 file local sau:

1. `document/paper/source_paper/2502.18940v2.pdf` — `MathTutorBench: A Benchmark for Measuring Open-ended Pedagogical Capabilities of LLM Tutors`.
2. `document/paper/source_paper/18426-AAAI26.ShiW-NLP.pdf` — `From Solver to Tutor: Evaluating the Pedagogical Intelligence of LLMs with KMP-Bench`.
3. `document/paper/source_paper/2510.02663v1.pdf` — `TutorBench: A Benchmark To Assess Tutoring Capabilities Of Large Language Models`.
4. `document/paper/source_paper/2512.14554v5.pdf` — `Benchmarking Vietnamese Legal Knowledge of Large Language Models` / VietLegal/V-Legal.

Có thể dùng lại tóm tắt từ `experiments/20260705_215045/literature_notes/`, nhưng không được chỉ copy. Cần đọc lại các PDF local với mục tiêu mới.

Các PDF khác trong `document/paper/source_paper/` chỉ dùng làm nguồn bổ sung nếu Quân yêu cầu hoặc nếu cần đối chiếu rõ ràng; không tự mở rộng phạm vi plan từ 4 paper thành một literature review lớn hơn.

## 3. Câu hỏi đọc bắt buộc

Với mỗi paper, cần trả lời:

1. Benchmark được tạo từ nguồn dữ liệu nào?
2. Paper kiểm tra độ phủ của benchmark bằng cách nào?
3. Paper kiểm tra độ chính xác hoặc chất lượng dữ liệu bằng cách nào?
4. Paper kiểm tra độ khó, độ đa dạng hoặc phân tầng task như thế nào?
5. Paper có kiểm tra độ tin cậy giữa người chấm không?
6. Paper có chứng minh benchmark phân biệt được model/tutor mạnh-yếu không?
7. Có sử dụng reference response/gold response không, và dùng để làm gì?
8. Những tiêu chí nào có thể chuyển hóa sang benchmark gia sư Tin học THCS của ta?
9. Những tiêu chí nào không phù hợp hoặc cần HNMU xác nhận?

## 4. Output dự kiến và lý do tạo

### 4.1. `literature_benchmark_quality/paper_summaries/`

Vai trò: chứa tóm tắt chi tiết từng paper theo đúng câu hỏi đọc ở trên.
Lý do tạo: mỗi paper cần một file riêng để dễ kiểm tra, tránh nhảy thẳng sang tổng hợp rồi mất căn cứ.

### 4.2. `literature_benchmark_quality/benchmark_quality_evidence_matrix.csv`

Vai trò: bảng hóa bằng chứng từ từng paper theo các tiêu chí đánh giá benchmark.
Lý do tạo: giúp thấy tiêu chí nào có căn cứ từ paper nào, tiêu chí nào chỉ là suy luận của UET.

### 4.3. `reports/benchmark-quality-literature-synthesis.md`

Vai trò: báo cáo tổng hợp tiếng Việt cho Quân/giáo sư/HNMU.
Lý do tạo: đây là tài liệu quyết định ta sẽ đánh giá benchmark theo khung nào.

### 4.4. `reports/benchmark-quality-checklist-v0.md`

Vai trò: checklist kiểm định chất lượng dữ liệu/bộ benchmark v0, dùng làm đầu vào trực tiếp cho Plan 04.
Lý do tạo: các paper không chỉ để trích dẫn trong bài báo; chúng phải được chuyển thành tiêu chí vận hành được khi kiểm dữ liệu HNMU.

Checklist tối thiểu phải có các nhóm:

- Độ phủ: kiến thức/học liệu, mức nhận thức, dạng bài, hành vi gia sư.
- Độ chính xác và nhất quán: câu hỏi, đáp án, bài học, vị trí SGK, hội thoại có khớp nhau không.
- Chất lượng sư phạm: hội thoại có giàn giáo không, có nhảy thẳng đáp án không, có lượt thừa không có giá trị không.
- Trùng/gần trùng.
- Khả năng dùng làm mẫu benchmark: có thể cắt thành `student_prompt`, `conversation_history`, `gold_response`, `Đáp án` không.
- Trường hợp cần HNMU xác nhận.
- Quy tắc điểm tự tin (`confidence_score`) và ngưỡng trả về người kiểm tra.

Checklist phải phân rõ:

- Tiêu chí code có thể kiểm cơ học.
- Tiêu chí agent có thể gợi ý/đánh giá ngữ nghĩa.
- Tiêu chí bắt buộc HNMU/UET xác nhận.

### 4.5. `handoffs/benchmark-quality-literature-review-xxx.md`

Vai trò: ghi lại nguồn đọc, output, kết luận và câu hỏi còn mở.
Lý do tạo: đảm bảo traceability giữa literature review và các plan sau.

## 5. Tiêu chí hoàn thành

Plan hoàn thành khi có:

1. Tóm tắt chi tiết cho 4 paper.
2. Evidence matrix về cách đánh giá benchmark.
3. Báo cáo tổng hợp khung đánh giá benchmark đề xuất cho dự án.
4. Checklist kiểm định chất lượng v0, đủ để Plan 04 chuyển thành logic audit.
5. Danh sách tiêu chí có thể dùng ngay, tiêu chí cần sửa, tiêu chí cần HNMU/giáo sư xác nhận.

## 6. Ngoài phạm vi

- Không code pipeline.
- Không chấm dữ liệu HNMU.
- Không tự quyết định benchmark cuối cùng tốt hay chưa.
- Không thay đổi task/rubric hiện có nếu chưa có quyết định riêng.
