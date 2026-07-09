# Specialist handoff

- Delegation ID: `p02-benchmark-spec-v0-003`
- Agent: `benchmark-specification-designer`
- Model if spawned: `gpt-5.4-mini`, reasoning `high`
- Status: completed via `single-agent fallback`
- Native thread ID/label: `null` / single-agent parent thread

## Task

Tạo bản nháp rubric, mã lỗi nghiêm trọng, task registry và provenance matrix từ `review_form.xlsx`, evidence snapshot và learning-resource mapping v0.

## Inputs read

- `agents/benchmark-specification-designer/SKILL.md`
- `agents/benchmark-specification-designer/references/benchmark-spec-schema.md`
- `agents/benchmark-specification-designer/references/research-id-convention.md`
- `agents/benchmark-specification-designer/references/rubric-and-serious-error-guidelines.md`
- `agents/benchmark-specification-designer/references/provenance-matrix-guidelines.md`
- `drive_snapshot/files/teacher_packet/review_form.xlsx`
- `drive_snapshot/files/literature_review/evidence_matrix.xlsx`
- `learning_resources/learning_resource_source_map.csv`
- `learning_resources/learning_resource_fragments_v0.csv`

## Outputs created

- `benchmark_spec/benchmark_tasks.csv`
- `benchmark_spec/task_code_registry.csv`
- `benchmark_spec/rubrics.csv`
- `benchmark_spec/rubric_dimensions.csv`
- `benchmark_spec/rubric_specification.md`
- `benchmark_spec/serious_errors.csv`
- `benchmark_spec/serious_error_catalog.md`
- `benchmark_spec/rubric_error_mapping.csv`
- `benchmark_spec/provenance_matrix.csv`
- `benchmark_spec/provenance_matrix_v0.csv`
- `benchmark_spec/benchmark_task_specification.md`
- `benchmark_spec/benchmark_open_questions.md`
- `benchmark_spec/targeted_research_evidence_notes.md`

## Result summary

Đã chuyển task/rubric/mã lỗi từ `review_form.xlsx` thành đặc tả máy đọc được và bản đọc bằng mắt. Chính sách v0 nhấn mạnh: lỗi nghiêm trọng không mặc định làm 0 toàn bộ task; cần xem mapping lỗi–rubric và chờ HNMU chốt chính sách cuối.

## Uncertainty

- T02, T04, T07 có bằng chứng trực tiếp hạn chế.
- Rubric D1–D9 cần HNMU hiệu chuẩn với ví dụ cụ thể.
- Mapping lỗi nghiêm trọng sang rubric là đề xuất v0, chưa phải policy chính thức.
