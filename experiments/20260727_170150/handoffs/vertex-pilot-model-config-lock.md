# Handoff — Khóa cấu hình model cho pilot Vertex AI

- Delegation ID: `EXP-20260727-MODEL-CONFIG-LOCK-001`
- Agent: `benchmark-specification-designer` ở chế độ single-agent
- Status: completed
- Native thread ID/label: không có

## Delegation prompt

Khóa pilot ở `gemini-2.5-flash`, tắt thinking và giữ generate config ban
đầu để ưu tiên tính ổn định; không chạy API.

## Follow-up or steer messages

Project lead quyết định dùng `thinking_budget=0`, `temperature=0`,
`top_p=1`, `max_output_tokens=4096` và `seed=20260727`.

## Inputs read

- `experiments/20260727_170150/plans/02-vertex-ai-requirement-scoring-pilot.md`
- `src/vertex_ai_call/requirement_scoring.py`
- `src/vertex_ai_call/vertex_client.py`
- `src/vertex_ai_call/run_requirement_scoring.py`
- `tests/vertex_ai_call/test_requirement_scoring.py`

## Outputs created

- Cập nhật runner, request hash, manifest và test để gửi/ghi
  `thinking_budget=0`.
- Đồng bộ Plan 02, README, architecture và lệnh bàn giao.
- Đồng bộ hash system prompt hiện hành trong specification manifest.

## Result summary

Cấu hình ảnh hưởng response đã được khóa tường minh. `tests/` đạt 146 test
bằng `/home/quannda/miniconda3/envs/benchmark_env/bin/python`; không có
request nào được gửi đến Vertex AI. Không dùng kết quả của `pytest` ở
repository root vì lệnh đó thu thập nhầm test nội bộ trong thư mục
`google-cloud-sdk/` cục bộ; phạm vi đúng của dự án là `tests/`.

## Orchestrator decision

Giữ hai run A/B cùng model, generate config và seed để đo khả năng lặp lại
của phép chấm ổn định.

## Uncertainty

Chất lượng và độ ổn định thực tế chỉ có thể đánh giá sau khi project lead
chạy pilot và UET review kết quả.

## Open questions and next human decisions

- Project lead chạy pilot bằng lệnh đã bàn giao.
- UET quyết định giữ hoặc sửa cấu hình sau khi review pilot.
