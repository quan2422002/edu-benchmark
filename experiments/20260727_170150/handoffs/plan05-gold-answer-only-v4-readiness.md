# Specialist handoff

- Delegation ID: Không áp dụng
- Agent: root dùng skill `benchmark-specification-designer`
- Status: Hoàn thành cài đặt và preflight offline; chưa gọi API
- Native thread ID/label: single-agent implementation

## Delegation prompt

Không có delegation. UET yêu cầu bỏ fragment khỏi prompt judge, dùng
`gold_answer` làm neo tính đúng chuyên môn và giữ các nhánh cũ hoạt động.

## Follow-up or steer messages

UET ưu tiên thay đổi cô lập, không ghi đè output v2/v3 và không làm hỏng
runner/provider hiện tại.

## Inputs read

- `README.md`, `ARCHITECTURE.md`, active roadmap và Plan 05
- `agents/benchmark-specification-designer/SKILL.md`
- rubric/error guidelines và `outputs/benchmark_rubric/rubrics.csv`
- builder, runner, provider callers, prompt v3 và test Plan 05
- hai bundle rubric-only-v3 90/90 để kiểm tương thích hash

## Outputs created

- `shared/prompts/benchmark_response_judging/system_prompt_gold_answer_only_v4.md`
- `scripts/benchmark_evaluation/run_gold_answer_only_v4_judge_pilot_30.sh`
- contract `gold-answer-only-v4` trong builder/runner/provider hiện có
- regression test v4 trong `tests/benchmark_evaluation/`
- cập nhật Plan 05, roadmap, README và ARCHITECTURE

## Result summary

V4 kế thừa `rubric-only-v3`, không đọc conversion evidence hoặc fragment
registry, không dựng mục `Căn cứ học liệu`, giữ evidence IDs rỗng và ghi
`learning_evidence_included=false`. `RUB-GEN-ACC` giữ nguyên ID nhưng dùng
tên/anchor hiển thị riêng dựa trên `gold_answer`, chấp nhận cách làm tương
đương và yêu cầu `Tie` khi đáp án không đủ phân xử. V2/v3 không đổi prompt:
preflight trên hai bundle v3 hiện có nhận đủ 90 record mỗi judge với request
hash khớp. Wrapper v4 preflight đạt 90 phép so sánh cho Gemini và 90 cho GPT,
không gọi API.
Lần chạy trả phí đầu tiên giữ 88/90 record Gemini; recovery đã qua 86
regression test và preflight đúng 88 existing + 2 pending. Alias tên tiêu
chí chỉ bật cho v4; Gemini dùng 12.288 token khi recovery còn GPT giữ 8.192.

## Orchestrator decision

Giữ v2/v3 làm provenance và dùng output directory mới cho v4. Chỉ chạy API
khi người dùng chủ động đặt `EXECUTE_API=1`.

## Uncertainty

`gold_answer` chưa được HNMU audit đầy đủ ở cấp candidate. V4 loại nhiễu từ
fragment nhưng chuyển phạm vi khẳng định sang độ phù hợp với đáp án chuẩn,
không phải xác minh trực tiếp theo SGK/SGV.

## Open questions and next human decisions

- Chạy hai judge v4 trên đúng pilot 30 mẫu.
- So sánh v3–v4 và Gemini–GPT, ưu tiên `RUB-GEN-ACC`, số Tie, agreement và
  các mẫu đổi phán quyết trước khi cân nhắc full judge.
