# Bàn giao pilot judge OpenAI GPT-5.4 mini — Plan 05

- Delegation ID: không có; triển khai single-agent theo yêu cầu UET
- Agent: root
- Status: preflight ready; chưa gọi API
- Native thread ID/label: phiên làm việc hiện tại

## Yêu cầu triển khai

Bổ sung hạ tầng chạy lại đúng 90 phép chấm cost-pilot bằng
`gpt-5.4-mini`, đồng thời không làm thay đổi đường chạy Gemini, Llama hoặc
Claude hiện có.

## Input đã đọc

- Plan 05 và roadmap experiment `20260727_170150`.
- Ba bundle target full, manifest cost-pilot 30 mẫu, system prompt v2,
  rubric, lỗi nghiêm trọng và learning fragments hiện hành.
- Tài liệu OpenAI về snapshot `gpt-5.4-mini-2026-03-17`, Responses API và
  Structured Outputs.

## Output đã tạo

- `src/edu_benchmark/benchmark_evaluation/openai_judge.py`
- `scripts/benchmark_evaluation/run_openai_gpt54_mini_judge_pilot.sh`
- `tests/benchmark_evaluation/test_openai_judge.py`
- Nhánh provider `openai` tối thiểu trong runner judge chung.
- Cập nhật Plan 05, roadmap, README, architecture, dependency và
  `.gitignore`.

## Kết quả

Caller OpenAI dùng Responses API, system/user tách biệt, Structured Outputs
nghiêm ngặt, `reasoning.effort=medium`, `store=false`, không truyền
temperature và khóa snapshot model. SDK không tự retry; runner chung sở hữu
retry, progress, JSONL tăng dần, error log, resume và budget gate.

Output mới được cô lập tại
`full_1400_v1/judge_cost_pilot_30/judge_openai_gpt54_mini_medium_v1/`.
Preflight xác nhận đúng 30 candidate, 90 comparison, 0 existing và 90
pending; cận trên gồm mọi retry là 11,97828 USD. Không có API request nào
được gửi trong lúc triển khai.

## Kiểm định

- Python: `/home/quannda/miniconda3/envs/benchmark_env/bin/python`
- Unit và regression: 81 test `tests/benchmark_evaluation` đạt.
- Wrapper shell qua `bash -n` và preflight offline đạt.
- `src/.env` đã được Git bỏ qua; credential không vào hash/manifest.

## Giới hạn và quyết định tiếp theo

- Structured Outputs mới được kiểm bằng SDK giả lập và preflight; lần API
  thật đầu tiên vẫn có thể phát hiện khác biệt provider cần xử lý.
- Người dùng chạy wrapper với `EXECUTE_API=1`, sau đó so sánh OpenAI–Gemini
  theo rubric, serious-error anchors, overall và chi phí thực tế.
