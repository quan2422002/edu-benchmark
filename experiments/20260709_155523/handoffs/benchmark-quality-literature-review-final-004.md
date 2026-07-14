# Specialist handoff

- Delegation ID: `research-methodologist-single-agent-20260714-final-004`
- Agent: `research-methodologist` trong chế độ single-agent ở luồng cha; không spawn specialist riêng.
- Status: hoàn thành Plan 01.
- Native thread ID/label: `null`

## Delegation prompt

Hoàn thiện nốt Plan 01 sau khi roadmap được cập nhật theo dữ liệu HNMU mới. Trọng tâm bổ sung là checklist kiểm định chất lượng benchmark/dữ liệu v0 để Plan 04 có thể dùng khi kiểm batch hội thoại HNMU.

## Follow-up or steer messages

- Người dùng yêu cầu hoàn thiện Plan 01.
- Người điều phối xác định các output cũ đã có: tóm tắt 4 paper, ma trận bằng chứng, báo cáo tổng hợp, slide.
- Phần còn thiếu theo plan cập nhật là `reports/benchmark-quality-checklist-v0.md` và handoff hoàn tất.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260709_155523/roadmap.md`
- `experiments/20260709_155523/plans/01-benchmark-quality-literature-review.md`
- `agents/research-methodologist/SKILL.md`
- `experiments/20260709_155523/reports/benchmark-quality-literature-synthesis.md`
- `experiments/20260709_155523/literature_benchmark_quality/benchmark_quality_evidence_matrix.csv`
- `experiments/20260709_155523/handoffs/benchmark-quality-literature-review-003.md`

Các nguồn paper đã được đọc ở lượt triển khai trước của Plan 01 và được ghi lại trong handoff `benchmark-quality-literature-review-003.md`.

## Outputs created

- `experiments/20260709_155523/reports/benchmark-quality-checklist-v0.md`
- `experiments/20260709_155523/handoffs/benchmark-quality-literature-review-final-004.md`

## Outputs updated

- `experiments/20260709_155523/reports/benchmark-quality-literature-synthesis.md`

Cập nhật này thêm mục “Output vận hành đã bổ sung ngày 14/07/2026” và sửa lỗi gõ đường dẫn `shared/learning_renguồns/` thành `shared/learning_resources/`.

## Result summary

Plan 01 hiện đã có đủ các output chính:

1. Tóm tắt chi tiết 4 paper.
2. Ma trận bằng chứng về cách các paper chứng minh chất lượng bộ đánh giá.
3. Báo cáo tổng hợp khung đánh giá benchmark cho dự án.
4. Checklist kiểm định chất lượng v0 để Plan 04 dùng cho batch HNMU.
5. Handoff cuối ghi rõ kết quả, giới hạn và quyết định còn mở.

Checklist v0 chuyển bằng chứng từ 4 paper thành tiêu chí vận hành gồm:

- kiểm độ phủ cấp batch;
- kiểm thiếu trường/định dạng;
- kiểm nhất quán câu hỏi–đáp án–hội thoại;
- kiểm chất lượng sư phạm của hội thoại;
- kiểm trùng/gần trùng;
- kiểm khả năng chuyển đổi sang `student_prompt`, `conversation_history`, `gold_response`, `Đáp án`;
- quy tắc `quality_decision`, `confidence_score`, `needs_sgv_verification` và hàng đợi HNMU/UET kiểm lại.

## Orchestrator decision

Plan 01 được xem là hoàn thành ở mức tài liệu nghiên cứu và checklist vận hành. Không triển khai code trong Plan 01; code audit thuộc Plan 04. Không tự final các quyết định chuyên môn; các điểm cần xác nhận được chuyển sang HNMU/UET.

## Uncertainty

- Checklist v0 dựa trên 3 paper gia sư thuộc Toán/STEM và 1 paper tiếng Việt thuộc Luật; cần HNMU xác nhận khi chuyển sang Tin học THCS.
- Khi chưa crawl/OCR SGV, kiểm `Đáp án (SGV)` chỉ là sơ bộ và nên gắn cờ `needs_sgv_verification`.
- Ngưỡng `confidence_score` hiện là đề xuất vận hành, cần hiệu chỉnh sau khi chạy batch thật.

## Open questions and next human decisions

1. UET có được loại tạm mẫu trùng/gần trùng khỏi batch chuyển đổi thử không?
2. HNMU có thể kiểm tra chéo một tập nhỏ để đo độ đồng thuận không?
3. Ngưỡng `confidence_score` nào đủ để không cần HNMU xem lại?
4. Khi phản hồi gia sư trong hội thoại gốc chưa lý tưởng, UET có được đề xuất bản `gold_response` chỉnh sửa để HNMU duyệt không?
5. Có cần chờ SGV được crawl/OCR trước khi chuyển đổi mẫu có cờ `needs_sgv_verification` không?
