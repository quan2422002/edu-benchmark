# Bàn giao cấu hình LearnLM-oriented — Plan 05

- Delegation ID: `EXP-20260729-PLAN05-LEARNLM-PROMPT-001`
- Agent: `benchmark-specification-designer` ở chế độ single-agent
- Status: `completed_without_api_calls`
- Native thread ID/label: không có; skill canonical được nạp trong parent thread

## Delegation prompt

Bổ sung khả năng LearnLM của Gemini vào cùng pilot 80 mẫu, không thay đổi
manifest hoặc gọi API.

## Follow-up or steer messages

Người dùng yêu cầu chạy LearnLM cùng Gemini baseline và Llama hiện có.

## Inputs read

- Plan 05, roadmap active, pilot manifest và hai wrapper pilot
- Tài liệu LearnLM chính thức và LearnLM Partner Prompt Guide của Google
- Bundle instruction v2, target runner và judge runner

## Outputs created

- `shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v3_learnlm.yaml`
- Wrapper target có cấu hình `target_gemini35_learnlm_prompted`
- Wrapper judge nhận ba target run và tạo 240 phép so sánh
- Test, protocol, Plan 05, roadmap, README và architecture được đồng bộ

## Result summary

LearnLM không phải model hoặc API mode riêng; Google đã tích hợp các khả
năng này vào Gemini. Pilot dùng cùng `gemini-3.5-flash` và cùng cấu hình
sinh, chỉ thay system-instruction bundle để tạo một prompt ablation. Bundle
mới giữ nguyên sáu yêu cầu KMP và không được kích hoạt nguyên tắc có
`requirement_score < 4`. Cận trên pilot gồm retry là 49,851744 USD.

## Orchestrator decision

Báo kết quả theo ba `target_run_id`; không gọi cấu hình LearnLM là model thứ
ba hoặc model chuyên biệt và không gộp hai run Gemini theo `model_id`.

## Uncertainty

Hiệu quả LearnLM-oriented prompt trên dữ liệu Tin học THCS chỉ được biết sau
pilot. Khoảng trống model chuyên biệt vẫn chưa được lấp.

## Open questions and next human decisions

- Project lead chạy wrapper target, sau đó chạy wrapper judge khi đủ 240 response.
- So sánh Gemini baseline với Gemini+LearnLM-oriented như prompt ablation.
