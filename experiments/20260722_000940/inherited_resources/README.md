# Tài nguyên kế thừa cho experiment `20260722_000940`

Thư mục này chứa bản copy/snapshot của các tài nguyên cần dùng trực tiếp trong giai đoạn 2: chuyển dữ liệu thô đã `pass` thành ứng viên mẫu benchmark và kiểm chất lượng ứng viên.

Nguyên tắc:

1. Đây là bản snapshot để làm việc thuận tiện trong experiment mới.
2. Nguồn gốc/canonical vẫn được ghi rõ ở từng mục.
3. Không copy dữ liệu nặng hoặc tài nguyên dùng chung đã nằm ở `shared/`.
4. Nếu file nguồn ở experiment cũ được sửa sau này, cần copy lại có chủ đích; không giả định snapshot này tự đồng bộ.

## 1. Từ experiment `20260705_215045`

Vai trò: kế thừa thiết kế benchmark v0.

### `from_20260705_215045/benchmark_design/`

Nguồn gốc: `experiments/20260705_215045/benchmark_design/`

Nội dung:

- `benchmark_tasks.csv`: 4 task hành vi gia sư v0.
- `rubrics.csv`: 20 rubric v0, 5 tiêu chí cho mỗi task, thang Likert 1–5.
- `task_design_rationale_v0.md`: luận giải thiết kế task.
- `rubric_design_rationale_v0.md`: luận giải thiết kế rubric.

Vai trò trong experiment mới: dùng làm nền để gán task/rubric sơ bộ cho ứng viên benchmark.

### `from_20260705_215045/coverage_design/`

Nguồn gốc: `experiments/20260705_215045/coverage_design/`

Nội dung:

- `general_coverage_matrix_v0.csv`: ma trận bao phủ tổng quát.
- `coverage_axis_values_v0.csv`: danh mục giá trị của các trục bao phủ.
- `coverage_summary_v0.csv`: tóm tắt coverage v0.
- `coverage_matrix_readme_v0.md`: giải thích cách đọc ma trận.
- `coverage_metrics_v0.md`: gợi ý metric theo dõi độ phủ.

Vai trò trong experiment mới: dùng để kiểm xem các ứng viên benchmark sau chuyển đổi phủ được chủ đề/task/mức nhận thức/dạng bài như thế nào.

### `from_20260705_215045/teacher_examples/`

Nguồn gốc: `experiments/20260705_215045/teacher_examples/`

Nội dung: các ví dụ phiếu tác giả, ví dụ hội thoại nhiều lượt và ghi chú chuyển đổi mẫu HNMU.

Vai trò trong experiment mới: chỉ dùng làm mẫu tham khảo cách trình bày/kiểm tra logic chuyển đổi, không coi là dữ liệu thật.

Lưu ý về ví dụ chuyển đổi mẫu HNMU 01:

- `hnmu_sample_01_scratch_average_full_dialogue_author_form.md` có trạng thái `superseded`; không dùng làm ví dụ chính vì file này thuộc hướng cũ chấm toàn bộ hội thoại.
- `hnmu_sample_01_scratch_average_single_response_author_form.md` là bản tham khảo chính hiện tại, theo hướng chấm phản hồi cuối của gia sư.
- `hnmu_sample_01_conversion_notes.md` giải thích quy ước tách `student_prompt`, `conversation_history`, `gold_response` và giữ `Đáp án` riêng.

## 2. Từ experiment `20260709_155523`

Vai trò: kế thừa kết quả giai đoạn 1 — đánh giá chất lượng dữ liệu hội thoại thô.

### `from_20260709_155523/raw_audit_grade6_7/`

Nguồn gốc:

- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/normalized_dialogue_rows.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/quality_check_suggestions.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/raw_dialogue_checklist_results.repaired.csv`

Vai trò trong experiment mới:

- `normalized_dialogue_rows.csv`: bảng dữ liệu thô lớp 6–7 đã chuẩn hóa.
- `quality_check_suggestions.csv`: file chính ở cấp mẫu để lọc `quality_decision = pass`.
- `raw_dialogue_checklist_results.repaired.csv`: kết quả chi tiết theo từng tiêu chí, dùng khi cần truy ngược lý do.

### `from_20260709_155523/raw_audit_grade8_9/`

Nguồn gốc:

- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/normalized_dialogue_rows.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/quality_check_suggestions.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv`

Vai trò trong experiment mới:

- `normalized_dialogue_rows.csv`: bảng dữ liệu thô lớp 8–9 đã chuẩn hóa.
- `quality_check_suggestions.csv`: file chính ở cấp mẫu để lọc `quality_decision = pass`.
- `raw_dialogue_checklist_results.regex_repaired.csv`: kết quả chi tiết theo từng tiêu chí, dùng khi cần truy ngược lý do.

### `from_20260709_155523/checklists/`

Nguồn gốc: `experiments/20260709_155523/reports/`

Nội dung:

- `benchmark-candidate-quality-checklist-v0.md`: checklist chính cho giai đoạn 2, dùng sau khi mẫu thô đã được chuyển thành ứng viên benchmark.
- `raw-dialogue-quality-checklist-v0.md`: checklist dữ liệu thô, giữ để truy vết logic giai đoạn 1.
- `raw-dialogue-audit-criteria-v0.csv`: registry tiêu chí dữ liệu thô ở cấp từng mẫu.

Vai trò trong experiment mới: dùng `benchmark-candidate-quality-checklist-v0.md` làm checklist vận hành chính; hai file raw-dialogue chỉ dùng để đối chiếu giai đoạn 1.

### `from_20260709_155523/reports/`

Nguồn gốc: `experiments/20260709_155523/reports/`

Nội dung:

- `bao-cao-gui-hnmu-ket-qua-ra-soat-du-lieu-hoi-thoai-lop-6-9-20260719.md`
- `hnmu-dialogue-audit-batch-20260717.md`
- `hnmu-dialogue-audit-batch-grade8-9-20260719.md`

Vai trò trong experiment mới: dùng để hiểu bối cảnh và số liệu tổng hợp của giai đoạn 1.

## 3. Tài nguyên dùng chung không copy vào đây

Các tài nguyên sau vẫn dùng từ `shared/`, không copy để tránh nhân bản nặng và lệch nguồn:

- `shared/raw_data/HNMU-teacher_dialog_samples/manifest.csv`
- `shared/learning_resources/fragments/learning_resource_fragments.csv`
- `shared/learning_resources/indexes/learning_resources_v0.sqlite`
- `shared/learning_resources/registries/ocr_text_manifest.csv`
- `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv`
- `shared/learning_resources/agent_context/README.md`
- `shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md`
- `shared/learning_resources/agent_context/hnmu_cognitive_level_method_canonical.md`

Những file này là nguồn chung của toàn dự án. Experiment mới chỉ nên đọc chúng, không sửa trực tiếp nếu chưa có plan riêng.
