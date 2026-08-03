# Handoff — Bundle instruction gia sư có phiên bản

- Delegation ID: `EXP-20260728-PLAN05-INSTRUCTION-BUNDLE-V1-001`
- Agent: `benchmark-specification-designer` ở chế độ single-agent
- Status: `completed`
- Native thread ID/label: không có

## Delegation prompt

Đưa tên tiếng Việt và cấu trúc nhiều dòng vào từng yêu cầu sư phạm; lưu
instruction theo phiên bản để có thể cải tiến sau smoke/pilot.

## Follow-up or steer messages

Không có.

## Inputs read

- `experiments/20260727_170150/plans/05-benchmark-evaluation-configuration.md`
- `experiments/20260727_170150/outputs/benchmark_evaluation/`
- `src/edu_benchmark/benchmark_evaluation/`
- `shared/prompts/benchmark_candidate_task_assigning/`

## Outputs created

- `shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v1.yaml`
- `src/edu_benchmark/benchmark_evaluation/instruction_bundle.py`
- Code, test và bốn artifact cấu hình Plan 05 đã được đồng bộ.
- Run smoke nằm cùng phase tại
  `outputs/benchmark_evaluation/smoke_gemini35_instruction_v1/`.

## Result summary

Bundle `v1` là nguồn instruction duy nhất. Sáu yêu cầu có tên tiếng Việt
và bốn mục con xuống dòng. Registry là view phục vụ review; manifest và
response lưu version/hash bundle, còn resume bằng bundle khác bị chặn.
Mười response smoke giữ nguyên; mỗi record đã được bổ sung system prompt,
user prompt và toàn bộ message mà không gọi lại API.

## Orchestrator decision

Smoke Gemini đã hoàn thành. Cấu hình và run hiện dùng chung một gốc
`outputs/benchmark_evaluation/`; không cần chạy lại 10 candidate. UET có
thể review trực tiếp request và response trong cùng record JSONL.

## Uncertainty

Instruction vẫn là bản tạm dùng, chờ HNMU review sau khi có kết quả smoke.

## Open questions and next human decisions

- UET xem kết quả smoke của bundle `v1`.
- HNMU xác nhận cách diễn giải sáu yêu cầu sư phạm.
