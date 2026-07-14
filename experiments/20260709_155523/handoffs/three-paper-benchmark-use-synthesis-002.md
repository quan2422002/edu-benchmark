# Specialist handoff

- Delegation ID: `EXP-20260709-RESEARCH-002`
- Agent: `research-methodologist` then `benchmark-specification-designer`, loaded in parent thread
- Status: completed
- Native thread ID/label: `single-agent`

## Delegation prompt

Đối chiếu ba nghiên cứu P03 để làm rõ đơn vị đánh giá, vai trò của phản hồi tham chiếu, cách chấm, quan hệ một-nhiều giữa hội thoại HNMU và mẫu benchmark, trường `answer`, và cách xử lý trường thiếu.

## Follow-up or steer messages

Không có.

## Inputs read

- `experiments/20260705_215045/literature_notes/paper_summaries/P03-P001-mathtutorbench.md`
- `experiments/20260705_215045/literature_notes/paper_summaries/P03-P002-kmp-bench.md`
- `experiments/20260705_215045/literature_notes/paper_summaries/P03-P003-tutorbench.md`
- `experiments/20260705_215045/literature_notes/evidence_matrix.csv`
- `experiments/20260705_215045/literature_notes/evidence_to_design_matrix.csv`
- `experiments/20260705_215045/reports/P03-literature-synthesis-for-design.md`
- ba file PDF nguồn tương ứng trong `document/paper/source_paper/`
- `experiments/20260709_155523/reports/meeting-notes-structured-20260708.md`
- `experiments/20260709_155523/roadmap.md`

## Outputs created

- `experiments/20260709_155523/reports/three-paper-benchmark-use-synthesis.md`
- cập nhật `experiments/20260709_155523/reports/meeting-notes-structured-20260708.md`
- cập nhật `experiments/20260709_155523/roadmap.md`

## Result summary

Đã xác nhận KMP-Bench dùng lượt gia sư gốc bị cắt làm phản hồi tham chiếu. MathTutorBench dùng phản hồi giáo viên trong xếp hạng cặp. TutorBench dùng phản hồi gia sư lý tưởng để xây rubric riêng cho từng mẫu. Thiết kế dự án giữ đánh giá một lượt gia sư trong lịch sử định sẵn, cho phép một hội thoại HNMU tạo nhiều mẫu có truy vết, và tách `answer` khỏi `gold_response`.

## Orchestrator decision

Chưa sửa phiếu tác giả hoặc triển khai specialist/mã chuyển đổi. Các thay đổi hiện chỉ là quyết định thiết kế và roadmap; việc triển khai cần plan `APPROVED`.

## Uncertainty

- Chưa chốt có dùng so sánh cặp với `gold_response` trong thí nghiệm đầu.
- Chưa có dữ liệu thật đủ lớn để xác định số lượt gia sư nên lấy từ mỗi hội thoại.
- Chưa kiểm tra độ tin cậy của mô hình giám khảo trên tiếng Việt/Tin học THCS.

## Open questions and next human decisions

- Chốt cách dùng `gold_response` trong chấm điểm.
- Chốt task chính và nhãn hành vi phụ.
- Duyệt việc dùng hai specialist hiện có trước khi cân nhắc tạo specialist mới.

