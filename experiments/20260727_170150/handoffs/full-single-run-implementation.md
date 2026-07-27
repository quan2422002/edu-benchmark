# Handoff — Full single-run requirement-scoring

- Delegation ID: `EXP-20260727-FULL-SINGLE-RUN-001`
- Agent: `benchmark-specification-designer` ở chế độ single-agent
- Status: `completed`
- Native thread ID/label: không có; không spawn specialist

## Delegation prompt

Dừng calibration, chốt Gemini 3.5 Flash với cấu hình hiện tại, cài một
full run cho 2.028 candidate, tăng concurrency lên 20, không gọi API và
lập plan thống kê–phân tích hậu chạy.

## Follow-up or steer messages

- UET chấp nhận giới hạn độ lặp lại của calibration.
- Full output chỉ có một run và tiếp tục là đề xuất của model.
- Project lead tự chạy lệnh bàn giao.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260727_170150/roadmap.md`
- `experiments/20260727_170150/plans/02-vertex-ai-requirement-scoring-pilot.md`
- grounding pool 2.028 candidate
- hai calibration bundle Gemini 2.5/3.5 Flash

## Outputs created

- Lệnh `full` trong `src/vertex_ai_call/run_requirement_scoring.py`.
- Kiểm thử full single-run trong
  `tests/vertex_ai_call/test_requirement_scoring.py`.
- Plan 03 tại `plans/03-full-run-statistics-and-analysis.md`.
- Tài liệu trạng thái và kiến trúc đã đồng bộ.

## Result summary

Runner đọc trực tiếp grounding pool, không tạo `pilot_input.csv`, tạo
manifest chỉ có run `full`, dùng concurrency 20 và request ceiling 2500.
Mỗi response được ghi tăng dần vào `run_full.jsonl`; candidate lỗi chỉ
retry sau lượt quét. Khi đủ 2.028 record và 12.168 score, validator đóng
bundle ở trạng thái `completed_awaiting_analysis`.

## Orchestrator decision

Không gọi Vertex AI trong lượt cài đặt. Bundle active là
`full_gemini35_medium_v1`; Plan 03 chưa được triển khai khi chưa có UET
duyệt và full bundle hoàn chỉnh.

## Uncertainty

Một run không đo được agreement, repeatability hoặc accuracy. Kết quả
không được gọi là ground truth và vẫn cần UET/HNMU review ở các bước sau.

## Open questions and next human decisions

- Project lead chạy full bundle và xác nhận không còn failure.
- UET review/duyệt Plan 03 trước khi triển khai phân tích.
