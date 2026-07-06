# Specialist handoff

- Delegation ID: `p02-roadmap-and-modular-plans-002`
- Agents used in single-agent fallback: `learning-resource-curator`, `research-methodologist`, `benchmark-specification-designer`, `teacher-collaboration-designer`
- Status: completed via `single-agent fallback`
- Native thread ID/label: `null` / parent thread

## Task

Cập nhật experiment `20260705_215045` theo phản hồi của người phụ trách dự án: học liệu chủ đạo là SGK/SGV trên trang tập huấn, rủi ro coverage cần kiểm soát bằng chuẩn hóa chủ đề xuyên suốt SGK Tin học THCS, và cần viết roadmap/plan độc lập không chồng chéo.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260620_115236/roadmap.md`
- `experiments/20260705_215045/reports/meeting-notes-structured-20260705.md`
- `agents/learning-resource-curator/SKILL.md`
- `agents/research-methodologist/SKILL.md`
- `agents/benchmark-specification-designer/SKILL.md`
- `agents/teacher-collaboration-designer/SKILL.md`

## Outputs created/updated

- `experiments/20260705_215045/roadmap.md`
- `experiments/20260705_215045/plans/01-bloom-task-rubric-example-sprint.md` — marked `SUPERSEDED_DRAFT`
- `experiments/20260705_215045/plans/02-source-scope-topic-taxonomy.md`
- `experiments/20260705_215045/plans/03-targeted-paper-review-bloom-tutoring.md`
- `experiments/20260705_215045/plans/04-bloom-task-taxonomy-and-compact-rubric.md`
- `experiments/20260705_215045/plans/05-case-coverage-and-pilot-allocation.md`
- `experiments/20260705_215045/plans/06-teacher-examples-and-pilot-packet.md`
- `experiments/20260705_215045/plans/07-pilot-sample-intake-and-design-check.md`
- `experiments/20260705_215045/reports/meeting-notes-structured-20260705.md`
- `experiments/20260705_215045/metadata.yaml`
- `README.md` — updated active planning roadmap pointer

## Result summary

Đã tách plan monolithic thành roadmap và 6 plan độc lập. P02/P03 có thể chạy song song; P04 chỉ chốt sau P02/P03; P05–P07 đi tuần tự từ coverage đến ví dụ giáo viên và phân tích 20 mẫu pilot. Mỗi plan có vùng artifact riêng để hạn chế sửa chồng chéo. README cũng được cập nhật tối thiểu để trỏ người đọc tới roadmap đang active.

## Key design decision

Học liệu chủ đạo được ghi rõ là SGK/SGV Tin học THCS trên trang tập huấn. Rủi ro coverage được đưa về P02: chuẩn hóa topic taxonomy xuyên suốt SGK/SGV trước khi đo độ phủ.

## Uncertainty

- Chưa triển khai các plan; toàn bộ đang ở trạng thái `DRAFT`.
- Chưa snapshot đầy đủ SGK/SGV từ trang tập huấn trong experiment này.
- Chưa đọc sâu MathTutorBench/VietLegal trong experiment này.

## Validation

Chạy artifact-level validation bằng `benchmark_env` Python và `pytest tests/agents -q`.
