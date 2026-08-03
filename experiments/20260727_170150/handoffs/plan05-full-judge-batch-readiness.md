# Bàn giao full judge bằng Batch API — Plan 05

- Change ID: `EXP-20260730-PLAN05-FULL-JUDGE-BATCH-001`
- Chế độ: single-agent implementation
- Trạng thái: full batch và recovery đã hoàn tất

## Phạm vi

Cài đường full judge cho 1.400 candidate × ba target × hai judge bằng
contract `gold-answer-only-v4`. Gemini 3.5 Flash dùng Vertex AI Batch qua
GCS; GPT-5.4-mini dùng OpenAI Batch `/v1/responses`.

## Input đã khóa

- Ba target full, mỗi target đủ 1.400 response.
- Hai bundle calibration v4, mỗi judge đủ 90 judgment.
- Candidate manifest 1.400 ID, rubric, requirement run, system prompt v4 và
  evaluation schema hiện hành.

## Output/code tạo mới

- `src/edu_benchmark/benchmark_evaluation/batch_judge.py`
- `scripts/benchmark_evaluation/run_batch_judge.py`
- `scripts/benchmark_evaluation/run_full_1400_judge_batch.sh`
- `tests/benchmark_evaluation/test_batch_judge.py`
- `outputs/benchmark_evaluation/full_1400_v1/judge_full_batch_gold_answer_only_v4/`

## Hợp đồng vận hành

- Runner synchronous cũ không bị thay đổi.
- Hai provider có manifest, input, raw output, budget và final JSONL riêng.
- `prepare`, `submit`, `status`, `watch`, `collect`, `retry-submit` tách biệt
  và có thể resume; retry chỉ gửi lại đúng ID lỗi, tối đa một lần.
- Final bundle chỉ chuyển `completed` khi đủ 4.200 record, đúng request hash,
  đúng rubric và không chứa fragment học liệu.
- Budget dùng p95 usage của pilot v4, giá batch và hệ số an toàn 1,10; ngân
  sách Vertex và OpenAI không trộn lẫn.

## Kiểm tra đã thực hiện trước khi người dùng yêu cầu dừng chạy

- 17 test liên quan batch/OpenAI/judge runner đạt.
- Syntax shell/Python và `git diff --check` đạt.
- Preflight offline dựng đúng 4.200 dòng mỗi provider, 74 MB Gemini và 77 MB
  OpenAI; không upload, không gọi provider và không phát sinh phí.
- Dự toán: Gemini 132,44616 USD; GPT 46,52802 USD.

Sau khi người dùng làm rõ chỉ cần code, không chạy, không có lệnh pipeline
hoặc API nào khác được thực hiện.

## Kết quả cuối

- Gemini: 4.200/4.200 judgment hợp lệ; 10 biến thể tên tiêu chí được hậu
  xử lý cục bộ và hai request `MAX_TOKENS` được retry ở 9.000 token.
- GPT-5.4-mini: 4.200/4.200 judgment hợp lệ.
- Cả hai manifest có `status = completed`, không còn ID lỗi và giữ riêng
  provenance/cost theo provider.
