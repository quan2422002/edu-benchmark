# Specialist handoff

- Delegation ID: `PRE-PLAN03-RESEARCH-SINGLE-AGENT-001`
- Agent: `research-methodologist`, loaded by the orchestrator in single-agent mode
- Status: `completed`
- Native thread ID/label: `null`; no specialist subagent was spawned

## Yêu cầu thực hiện

Rà soát lại bốn bài báo kế thừa từ hai experiment trước, tập trung vào định nghĩa nhiệm vụ, tiêu chí chấm, phản hồi tham chiếu/chuẩn, đầu ra của bộ chấm và cách tổng hợp điểm ở cấp mẫu; đối chiếu với 2.028 mẫu ứng viên hiện tại để chuẩn bị sửa bản nháp Plan 03.

## Điều chỉnh trong quá trình thực hiện

Project lead yêu cầu bổ sung một bản tóm tắt chi tiết, có mục tiêu cho từng bài báo và sửa toàn bộ phần trình bày theo chính sách ưu tiên tiếng Việt.

## Đầu vào đã đọc

- `agents/research-methodologist/SKILL.md`
- `agents/research-methodologist/references/review-protocol.md`
- `agents/research-methodologist/references/evidence-schema.md`
- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260722_000940/roadmap.md`
- `experiments/20260722_000940/plans/03-thcs-task-rubric-specification-and-coverage.md`
- bốn PDF trong `document/paper/source_paper/`
- các literature notes/reports kế thừa từ experiment `20260705_215045` và `20260709_155523`
- bản chính thức trực tuyến của bốn bài báo và thẻ dữ liệu công khai của TutorBench

## Đầu ra đã tạo

- `experiments/20260722_000940/literature_notes/pre_plan03_task_rubric_review/review_protocol.md`
- `experiments/20260722_000940/literature_notes/pre_plan03_task_rubric_review/search_log.csv`
- `experiments/20260722_000940/literature_notes/pre_plan03_task_rubric_review/evidence_matrix.csv`
- `experiments/20260722_000940/literature_notes/pre_plan03_task_rubric_review/operational_claim_matrix.csv`
- `experiments/20260722_000940/literature_notes/pre_plan03_task_rubric_review/paper_summaries/TR-P001-mathtutorbench.md`
- `experiments/20260722_000940/literature_notes/pre_plan03_task_rubric_review/paper_summaries/TR-P002-kmp-bench.md`
- `experiments/20260722_000940/literature_notes/pre_plan03_task_rubric_review/paper_summaries/TR-P003-tutorbench.md`
- `experiments/20260722_000940/literature_notes/pre_plan03_task_rubric_review/paper_summaries/TR-P004-vietlegal.md`
- `experiments/20260722_000940/reports/pre-plan03-four-paper-task-rubric-operational-synthesis.md`
- handoff này

## Tóm tắt kết quả

Bốn bài báo dùng nhiệm vụ và tiêu chí chấm ở các tầng khác nhau. Không có căn cứ để giữ nguyên R1–R5 lặp lại ở từng nhiệm vụ như cấu trúc duy nhất. Bản tổng hợp đề xuất một nhiệm vụ chính ở cấp mẫu ứng viên, các kỹ năng phụ, một lõi tiêu chí chung nhỏ, các tiêu chí nguyên tử riêng theo mẫu và cổng lỗi nghiêm trọng tách biệt. `gold_response` là bằng chứng hỗ trợ biên soạn/phản hồi tham chiếu, còn `gold_answer` là neo sự thật; cả hai không phải chuỗi đích để so khớp chính xác.

## Quyết định của điều phối viên

Chưa sửa và chưa triển khai draft Plan 03. Chờ project lead xem báo cáo. Nếu được chấp nhận, Plan 03 cần được redraft trước khi đổi trạng thái sang `APPROVED`.

## Điểm chưa chắc chắn

- KMP-Bench không công bố đầy đủ tên của toàn bộ 22 tiêu chí.
- Công thức TutorBench chưa diễn giải đầy đủ phép chuẩn hóa khi tổng có tiêu chí âm.
- Chất lượng của 665 `gold_response` chưa được chuyên gia xác nhận đủ để dùng trong phép so sánh theo cặp.
- Độ tin cậy của bộ chấm trong tiếng Việt và miền Tin học THCS chưa được đo.

## Câu hỏi mở và quyết định tiếp theo của con người

1. T4 chẩn đoán là nhiệm vụ chính hay kỹ năng phụ?
2. Lõi tiêu chí chung gồm những chiều đánh giá nào?
3. Thí điểm biên soạn và rà soát tiêu chí nên lấy bao nhiêu mẫu ứng viên?
4. Chính sách lỗi nghiêm trọng là rà soát, chặn điểm hay loại?
5. Có thử so sánh theo cặp với `gold_response` sau khi đã chấm tuyệt đối theo từng tiêu chí hay không?
