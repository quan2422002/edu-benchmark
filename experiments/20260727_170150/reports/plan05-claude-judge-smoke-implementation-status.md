# Trạng thái judge smoke v2 — Plan 05

Ngày: 29/07/2026

Contract chấm mù v2 đã được giữ nguyên: 20 phép so sánh trên 10 candidate,
chỉ kích hoạt bốn tiêu chí chung và ba tiêu chí cho mỗi nguyên tắc có
`requirement_score >= 4`. Prompt dùng Markdown, ẩn danh và tráo hai
response; code lưu cả phán quyết thô lẫn phán quyết sau cổng lỗi.

Lần chạy Claude Sonnet 4.6 thất bại 20/20 với HTTP 404 vì project
`edu-benchmark` chưa kích hoạt sản phẩm Anthropic trên Google Cloud
Marketplace. Không request nào sinh phán quyết và chi phí thực tế bằng
0 USD. Model ID cùng region đều hợp lệ; đây không phải lỗi prompt, parser
hoặc rubric.

Theo quyết định UET, judge tạm thời chuyển sang `gemini-3.5-flash` trên
endpoint `global`. Cấu hình không đặt temperature/top-p/top-k, dùng
`thinking_level=MEDIUM`, `include_thoughts=false`, seed `20260728`,
lần đầu dùng `max_output_tokens=3072`, concurrency 2 và retry tối đa 2. Giá Standard
đưa vào budget gate là 1,50 USD input và 9 USD output trên một triệu token.
Lần chạy đầu hoàn tất 11/20 và có chín lỗi `MAX_TOKENS`. Con số
0,353856 USD trong manifest cũ chỉ là lower bound vì usage của chín response
bị cắt chưa được runner cũ lưu lại. Retry1 tăng giới hạn lên 8.192 token,
dùng `ThreadPoolExecutor` với 8 worker, stage cap 2 USD và upper bound
1,77456 USD. Khi một attempt lỗi, terminal in ngay toàn bộ diagnostic JSON,
gồm exception, traceback, `finish_reason`, usage và partial response; chính
record đó đồng thời được ghi vào `run_errors.jsonl`. Preflight đạt và chưa
gọi lại API.

Transport Gemini nằm tại
`src/edu_benchmark/benchmark_evaluation/gemini_judge.py`. Runner chung vẫn
là `scripts/benchmark_evaluation/run_claude_judge_smoke.py` để bảo toàn
provenance, còn lệnh ngắn mới nằm tại
`scripts/benchmark_evaluation/run_gemini35_judge_smoke_v2.sh`.

Hạn chế bắt buộc phải báo cáo: Gemini 3.5 Flash vừa là judge vừa là một
trong các tutor target. Kết quả của target Gemini phải được tách riêng và
không được dùng một mình để kết luận thứ hạng. Tập phân tầng do con người
chấm mù vẫn là cổng kiểm định judge trước khi scale.
