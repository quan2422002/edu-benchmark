# Bàn giao cài đặt Claude judge v2 — Plan 05

- Delegation ID: `EXP-20260729-PLAN05-CLAUDE-JUDGE-V2-001`
- Agent: `benchmark-specification-designer` ở chế độ single-agent
- Status: `completed`
- Native thread ID/label: không có; skill canonical được nạp trong parent thread

## Delegation prompt

Cài đặt lại Claude judge smoke theo contract v2 đã được UET cập nhật trong
Plan 05; chưa gọi API và bàn giao câu lệnh cho người dùng tự chạy.

## Follow-up or steer messages

Không có.

## Inputs read

- `README.md`, `ARCHITECTURE.md`
- `experiments/20260727_170150/roadmap.md`
- `experiments/20260727_170150/plans/05-benchmark-evaluation-configuration.md`
- Rubric, serious-error catalog, candidate/gold/grounding và hai target smoke run
- Skill và rubric/error guideline của `benchmark-specification-designer`

## Outputs created

- `shared/prompts/benchmark_response_judging/system_prompt_v2.md`
- Builder, validator, cổng hậu xử lý và runner v2
- Wrapper chạy một lệnh
  `scripts/benchmark_evaluation/run_claude_judge_smoke_v2.sh`
- Contract blind judge v2 trong `evaluation_schema.json`
- Test Markdown, giao error–rubric, bốn nhánh cổng và runner
- Tài liệu trạng thái/protocol/architecture đã đồng bộ

## Result summary

Preflight tạo đúng 20 phép so sánh trên 10 candidate, dùng Claude Sonnet
4.6 tại `us-east5`, upper bound 1,67376 USD dưới stage cap 2 USD. 55 test
`tests/benchmark_evaluation` pass bằng `benchmark_env`. Không gọi API và
không tạo thư mục run v2.

## Orchestrator decision

Bàn giao wrapper executable có `--execute-api` cho người dùng. Không dùng
lại prompt/output v1 và không tự chuyển sang pilot 240 candidate sau
smoke.

## Uncertainty

Rubric và serious-error catalog vẫn là bản tạm dùng chờ HNMU. Kết quả
Claude chưa tồn tại nên chưa thể đánh giá độ chính xác hoặc đồng thuận.

## Open questions and next human decisions

- Người dùng chạy smoke v2 và kiểm `run_errors.jsonl` nếu có.
- UET xem 20 phán quyết trước khi thiết kế đánh giá mù của con người.

## Cập nhật provider ngày 29/07/2026

Lần chạy Claude thất bại 20/20 do project chưa kích hoạt sản phẩm Anthropic
trên Marketplace; chi phí bằng 0 USD. UET quyết định không tiếp tục thủ tục
Marketplace ở smoke hiện tại và chuyển judge tạm thời sang Gemini 3.5 Flash.
Adapter `gemini_judge.py` cùng wrapper
`run_gemini35_judge_smoke_v2.sh` đã được thêm; preflight đạt đúng 20 phép
so sánh với upper bound 0,85296 USD và chưa gọi Gemini API. Kết quả target
Gemini phải được báo riêng do judge cùng model.

## Cập nhật MAX_TOKENS và retry1 ngày 29/07/2026

Lần Gemini đầu hoàn tất 11/20; chín call còn lại dừng ở `MAX_TOKENS`.
Manifest cũ đã được đánh dấu cost 0,353856 USD là lower bound vì runner cũ
không giữ usage của các response bị cắt. Runner mới dùng thread pool 8
worker; mỗi attempt lỗi in toàn bộ diagnostic JSON ngay trên terminal, gồm
exception, traceback, `finish_reason`, usage và partial response. Chính
record này cũng được ghi vào `run_errors.jsonl`, và failed-attempt usage
được cộng vào cost. Retry1 dùng run directory mới,
`max_output_tokens=8192`, stage cap 2 USD và upper bound 1,77456 USD; 57 test
cùng preflight không gọi API đều pass.
