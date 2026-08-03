# Bàn giao recovery Gemini baseline bị cắt — Plan 05

- Mã công việc: `EXP-20260729-PLAN05-GEMINI1536-RECOVERY-001`
- Mã follow-up: `EXP-20260729-PLAN05-GEMINI2048-FOLLOWUP-001`
- Chế độ: `benchmark-specification-designer` nạp trong parent thread, single-agent
- Trạng thái: `followup_2048_ready_for_user_api_run`

## Sự cố đã xác nhận

Lượt full Gemini baseline ghi đủ 1.400 record, trong đó 964 `completed` và
436 `needs_review` do `MAX_TOKENS`; 0 API exception. Cap 1.024 không đủ khi
Gemini 3.5 Flash dùng MEDIUM thinking. Runner trả mã 2 đúng fail-closed và
wrapper dừng trước Llama/LearnLM. Chi phí ước tính của lượt đầu là
11,2495365 USD.

## Recovery đã cài

- Khóa đúng 436 ID từ `completion_issue=output_truncated`.
- Giữ model, prompt, seed, bundle và MEDIUM thinking.
- Lượt 1 tăng `max_output_tokens` từ 1.024 lên 1.536 và hoàn thành 417/436 mẫu.
- Follow-up chỉ khóa 19 mẫu còn `MAX_TOKENS`, tăng cap lên 2.048 và tái sử dụng 417 kết quả hợp lệ.
- Gọi API trong staging tạm `/tmp`, không tạo thư mục recovery trong experiment.
- Chỉ merge khi 417 + 19 đều hoàn chỉnh; nếu còn cờ, source không đổi.
- Dựng lại JSONL và thay thế file nguyên tử; manifest ghi hash, tập ID, token cap và chi phí từng lượt trong `recovery_history`; staging bị xóa sau merge.

## Output

- `src/edu_benchmark/benchmark_evaluation/recovery.py`
- `scripts/benchmark_evaluation/recover_truncated_targets.py`
- `scripts/benchmark_evaluation/run_recover_gemini35_1536.sh`
- `scripts/benchmark_evaluation/run_recover_gemini35_followup_2048.sh`
- staging tạm `/tmp/edu-benchmark-plan05-gemini-recovery-1536` chỉ tồn tại đến khi merge thành công

## Cổng chi phí

Recovery 1.536 đã dùng 4,7877885 USD, đưa mốc tạm thời lên 72,557325 USD.
Cận trên follow-up 19 mẫu ở cap 2.048, gồm tối đa hai retry, là 1,307124
USD; vẫn nằm dưới hard cap 250 USD khi giữ dự phòng 25 USD.

## Bước người dùng

Chạy wrapper follow-up 2.048 với `EXECUTE_API=1`. Wrapper tự khóa 19 ID,
finalize đủ 436 recovery record, merge vào baseline và xóa staging. Sau đó
kiểm baseline phải đạt 1.400/1.400 `completed`; chưa resume Llama/LearnLM
nếu wrapper vẫn trả mã 2.
