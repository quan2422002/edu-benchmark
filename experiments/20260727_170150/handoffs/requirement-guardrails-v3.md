# Bàn giao contract requirement-scoring v3

- Delegation ID: `EXP-20260727-REQUIREMENT-V3-001`
- Agent: `benchmark-specification-designer` ở chế độ single-agent skill
- Status: `completed`
- Native thread ID/label: không có; không spawn specialist

## Delegation prompt

Làm rõ system prompt theo năm quy tắc đối chứng đã được UET chấp thuận,
giữ nguyên kết quả pilot v2 và không gọi Vertex AI.

## Follow-up or steer messages

Không có.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260727_170150/roadmap.md`
- plans 01–02 của experiment active
- `system_prompt_v2.md`
- `pedagogical_principles.csv`
- `task_discovery_codebook.md`
- output và nhận định rà soát pilot v2 trong phiên làm việc hiện tại

## Outputs created

- `shared/prompts/benchmark_candidate_task_assigning/system_prompt_v3.md`
- `experiments/20260727_170150/outputs/principle_requirement_scoring/specification_v3.md`
- `experiments/20260727_170150/outputs/principle_requirement_scoring/specification_manifest_v3.json`
- handoff này

## Result summary

V3 giữ nguyên tám trường input, schema v2, thang điểm, threshold và
generation config. Prompt bổ sung cổng đối chứng trước điểm `4`–`5`, quy
tắc “chỉ có thể hữu ích thì tối đa 3” và năm phép phân biệt chống gán tràn.
Runner mặc định ghi vào `pilot_v3/`; `pilot_v1/` và `pilot_v2/` không bị
thay đổi.

Validation:

- test pipeline: 14/14 đạt;
- toàn bộ test dưới `tests/`: 149/149 đạt;
- lệnh `prepare` offline tạo đúng manifest `pilot_version=v3`, prompt v3,
  manifest v3 và schema v2;
- không có Vertex API call.

## Orchestrator decision

Contract v3 được công bố để UET chạy pilot so sánh trên đúng 40 candidate
của v2. Đây là thử nghiệm prompt, chưa phải xác nhận sư phạm cuối cùng.

## Uncertainty

- Pilot v3 chưa chạy nên chưa biết năm guardrail có giảm gán tràn mà không
  làm mất nhãn đúng hay không.
- `Challenge` và `Practice` vẫn có ít positive case trong pilot; độ đúng
  của hai nguyên tắc này chưa thể kết luận chỉ bằng độ lặp lại A/B.

## Open questions and next human decisions

- UET chạy và so sánh pilot v3 với v2.
- UET review các thay đổi vượt ngưỡng, đặc biệt hai mẫu đã được đánh dấu.
- HNMU xác nhận ranh giới sư phạm trong gói task–rubric–ví dụ tích hợp.
