# Bàn giao requirement-scoring V4 và calibration

- Delegation ID: `EXP-20260727-REQUIREMENT-V4-001`
- Agent: `benchmark-specification-designer` ở chế độ single-agent skill
- Status: `completed`
- Native thread ID/label: không có; không spawn specialist

## Delegation prompt

Siết prompt cho Feedback và Questioning, dùng code phát hiện lập luận điểm
cao còn mang tính tùy chọn, và tạo bộ calibration cân bằng cho đủ sáu
nguyên tắc. Không gọi Vertex AI; bàn giao câu lệnh cho project lead.

## Follow-up or steer messages

Không có.

## Inputs read

- `README.md`, `ARCHITECTURE.md`
- roadmap và Plans 01–02 của experiment active
- `system_prompt_v3.md`
- kết quả và review queue của `pilot_v3/`
- registry sáu nguyên tắc kế thừa
- hướng dẫn canonical của skill `benchmark-specification-designer`

## Outputs created

- `shared/prompts/benchmark_candidate_task_assigning/system_prompt_v4.md`
- `outputs/principle_requirement_scoring/specification_v4.md`
- `outputs/principle_requirement_scoring/specification_manifest_v4.json`
- `outputs/principle_requirement_scoring/calibration_cases_v1.csv`
- code semantic lint, calibration loader/metrics và CLI `calibration`
- handoff này

## Result summary

V4 giữ nguyên tám trường input, schema V2, thang điểm, threshold và cấu
hình generation. Prompt bắt buộc điểm 4–5 nêu `Nhu cầu độc lập:` và
`Nếu bỏ nguyên tắc này:`; Feedback và Questioning có cổng riêng.

Code không dùng regex để tự sửa score. Semantic lint chỉ đưa vào review
các trường hợp có dấu hiệu mâu thuẫn. Bộ calibration có 36 ca: ba
positive và ba near-miss cho từng nguyên tắc. Expected range là tạm thời,
chờ UET review.

Validation dùng:

`/home/quannda/miniconda3/envs/benchmark_env/bin/python`

Test tập trung cho Vertex pipeline đạt 20/20. Validation manifest và bộ
calibration đạt; không có Vertex API call.

## Orchestrator decision

V4 được phép chạy calibration hai lần A/B. Chưa tạo holdout mới và chưa
chạy đủ 2.028 candidate. Sau calibration, UET review các ca ngoài khoảng,
semantic lint và các ca spot check trước khi quyết định holdout.

## Uncertainty

- 36 ca là đối chứng có chủ đích, không đại diện phân bố 2.028 candidate.
- Expected range chưa phải nhãn chuyên gia HNMU.
- Semantic lint ưu tiên phát hiện rủi ro rõ; nó không bao phủ mọi lỗi ngữ
  nghĩa và không thay thế review.

## Open questions and next human decisions

- UET chạy `calibration_v1`.
- UET xác nhận hoặc sửa expected range của các ca bị đưa vào review.
- Sau disposition, xây holdout 40 candidate mới để kiểm khả năng khái
  quát của V4.
- HNMU xác nhận ranh giới sư phạm trong gói task–rubric–ví dụ tích hợp.
