# Handoff — So sánh calibration bằng Gemini 3.5 Flash

- Delegation ID: `EXP-20260727-GEMINI35-MEDIUM-001`
- Agent: `benchmark-specification-designer` ở chế độ single-agent
- Status: `completed`
- Native thread ID/label: không có; không spawn specialist

## Delegation prompt

Giữ nguyên system prompt V4 và 36 ca calibration, chỉ chuyển model cùng
generate/thinking config sang Gemini 3.5 Flash; không gọi API và bàn giao
câu lệnh cho project lead tự chạy.

## Follow-up or steer messages

- UET khóa model `gemini-3.5-flash`.
- Không gửi `temperature`, `top_p` hoặc `top_k`.
- Dùng `thinking_level=MEDIUM`, `include_thoughts=false`; không gửi
  `thinking_budget`.
- Giữ `max_output_tokens=4096`, seed `20260727`, prompt V4, schema V2 và
  cùng 36 ca.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260727_170150/roadmap.md`
- `experiments/20260727_170150/plans/02-vertex-ai-requirement-scoring-pilot.md`
- `shared/prompts/benchmark_candidate_task_assigning/system_prompt_v4.md`
- `experiments/20260727_170150/outputs/principle_requirement_scoring/calibration_cases_v1.csv`
- `experiments/20260727_170150/outputs/principle_requirement_scoring/calibration_v1/`

## Outputs created

- Runtime và CLI đã cập nhật dưới `src/vertex_ai_call/`.
- Kiểm thử hồi quy đã bổ sung tại
  `tests/vertex_ai_call/test_requirement_scoring.py`.
- Bundle mới được khóa tên
  `calibration_gemini35_medium_v1`; bundle `calibration_v1` không bị sửa.

## Result summary

Runner tạo `GenerateContentConfig` theo kiểu có điều kiện. Với Gemini 3.x,
code không đưa sampling legacy hoặc `thinking_budget` vào request và đóng
lỗi nếu người chạy cố trộn hai hợp đồng. Manifest vẫn ghi các giá trị
`null` để chứng minh tham số bị bỏ. `--bundle-name` chỉ nhận tên thư mục
con an toàn, giúp các lần so sánh không ghi đè nhau.

## Orchestrator decision

Không gọi Vertex AI trong lượt cài đặt. Project lead sở hữu lệnh chạy và
UET sẽ so sánh kết quả mới với baseline Gemini 2.5 Flash.

## Uncertainty

Expected range của 36 ca vẫn là giả thuyết UET tạm thời, không phải nhãn
HNMU. Việc model mới qua gate kỹ thuật không tự chứng minh tính hợp lệ sư
phạm.

## Open questions and next human decisions

- Chạy bundle Gemini 3.5 Flash và review kết quả.
- Quyết định có chuyển sang holdout 40 candidate hay cần hiệu chỉnh tiếp.
