# Plan 03 — Task/rubric specification và coverage Tin học THCS

Experiment: `20260722_000940`  
Trạng thái: `DRAFT` — chưa được duyệt, không triển khai  
Ngày lập: 23/07/2026  
Phụ thuộc: Plan 02 hoàn thành và có full candidate/disposition output

## 1. Mục tiêu

Plan 03 chuyển bộ task/rubric v0 thiên về Tin học 9 thành specification v1 dùng cho toàn miền Tin học THCS lớp 6–9, sau đó tạo gợi ý task/rubric cho từng candidate và thống kê coverage quan sát được.

Plan này không xác nhận task/rubric thay HNMU. Mọi gợi ý semantic đều là provisional và phải có trạng thái, confidence, rationale và đường review.

## 2. Phân loại phát biểu theo căn cứ

Plan 03 phải dùng ba loại:

- `evidence`: kế thừa trực tiếp từ nghiên cứu, learning-resource registry hoặc dữ liệu candidate;
- `inference`: suy luận thiết kế của UET/agent từ evidence;
- `teacher_decision_needed`: ranh giới task, rubric hoặc serious-error cần HNMU/UET chốt.

Không được đổi một inference thành “đã xác nhận” chỉ vì pipeline gán được nhãn.

## 3. Input chỉ đọc

### Từ Plan 02

- `outputs/benchmark_conversion/full_v0/benchmark_candidate_splits.csv`
- `outputs/benchmark_conversion/full_v0/conversion_trace.csv`
- `outputs/benchmark_conversion/full_v0/conversion_dispositions.csv`
- `reports/plan02-full-multi-candidate-conversion-summary.md`

Plan 02 hiện có 665 disposition cấp raw sample đều là `converted`, tương ứng 2.028 candidate trước filtering. Chỉ candidate thuộc `sample_id` có `conversion_disposition = converted` được đưa vào assignment. Family đang `need_human_review` không được coi là input sạch.

### Specification kế thừa

- `inherited_resources/from_20260705_215045/benchmark_design/benchmark_tasks.csv`
- `inherited_resources/from_20260705_215045/benchmark_design/rubrics.csv`
- `inherited_resources/from_20260705_215045/benchmark_design/task_design_rationale_v0.md`
- `inherited_resources/from_20260705_215045/benchmark_design/rubric_design_rationale_v0.md`
- `experiments/20260705_215045/literature_notes/evidence_matrix.csv`
- `experiments/20260705_215045/literature_notes/evidence_to_design_matrix.csv`
- `experiments/20260705_215045/literature_notes/paper_selection_registry.csv`
- `experiments/20260705_215045/reports/P03-literature-synthesis-for-design.md`

Các ID `P03-P*` và `P03-C*` là ID lịch sử của experiment nguồn. Plan 03 phải tạo bảng alias tới research ID canonical theo convention của specialist, chỉ khi nguồn đủ chắc. Không invent DOI/arXiv ID cho nguồn chưa xác minh.

### Học liệu và coverage

- `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv`
- `shared/learning_resources/fragments/learning_resource_fragments.csv`
- `shared/learning_resources/agent_context/hnmu_cognitive_level_method_canonical.md`
- `shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md`
- coverage design v0 kế thừa từ experiment `20260705_215045` chỉ để tham khảo cấu trúc.

## 4. Specification v1 cần tạo

### 4.1. `benchmark_tasks.csv`

Giữ 4 task T1–T4 làm candidate starting point, nhưng:

- thay toàn bộ giới hạn “Tin học 9” bằng phạm vi Tin học THCS 6–9 khi evidence cho phép;
- không đổi ID T1–T4 nếu semantics không đổi;
- nếu T4 trở thành secondary label, phải có migration record thay vì sửa âm thầm;
- dùng schema:
  `task_id, task_name, definition, scope, input_requirements, output_requirements, status, research_ids, learning_material_ids, teacher_decision_needed`.

Status chỉ dùng:

- `draft`
- `needs_uet_review`
- `needs_hnmu_review`
- `confirmed`
- `retired`

Không có task nào được gắn `confirmed` nếu chưa có quyết định của đúng authority.

### 4.2. `rubrics.csv`

- Giữ R1–R5 theo task làm starting point.
- Mỗi rubric phải đo hành vi quan sát được từ response.
- Thay phạm vi Tin học 9 bằng Tin học THCS 6–9.
- Không suy luận learning gain từ chất lượng một response.
- Schema:
  `rubric_id, task_id, criterion, observable_evidence, score_levels, status`.

### 4.3. `serious_errors.csv`

Tạo catalog v0 với schema:

`error_id, description, suggested_action, affected_rubric_ids, status, confirmation_owner`

Candidate serious errors tối thiểu cần xem xét:

- sai kiến thức tự tin và nghiêm trọng;
- bịa nguồn/học liệu;
- hướng dẫn không an toàn hoặc vi phạm đạo đức/pháp lý;
- làm thay làm hỏng task giàn giáo;
- bỏ qua thiếu nền tảng rõ;
- rò đáp án làm mất giá trị đánh giá.

Suggested action chỉ là đề xuất `review`, `revision`, `exclusion`, hoặc `score_cap`; policy cuối cần HNMU/UET xác nhận.

### 4.4. `provenance_matrix.csv`

Mỗi task, rubric và serious error có một dòng:

`item_id, item_type, research_ids, learning_material_ids, rationale, status`

Không invent research ID hoặc learning-material ID. Nếu chưa có căn cứ thì để trống đúng cột, đặt status cần review và nêu gap.

Tạo thêm `research_id_aliases.csv`:

- `source_research_id`
- `canonical_research_id`
- `source_type`
- `source_locator`
- `verification_status`
- `notes`

Claim ID `P03-C*` không được giả làm source research ID. Provenance có thể dẫn claim qua rationale, nhưng `research_ids` phải trỏ tới source ID canonical đã được verify.

### 4.5. Open questions

`benchmark_open_questions.md` tối thiểu phải hỏi:

1. T4 là primary task hay secondary label?
2. R1–R5 có dùng đủ cho cả lớp 6–9?
3. Serious-error nào dẫn tới exclusion hay score cap?
4. Task/rubric nào cần ví dụ riêng cho code, bảng tính, thuật toán và sản phẩm số?

## 5. Candidate task/rubric suggestion schema

`benchmark_candidate_task_rubric_suggestions.csv` có:

- `benchmark_candidate_id`
- `sample_id`
- `suggested_primary_task_id`
- `suggested_secondary_task_ids`
- `suggested_rubric_ids`
- `task_confidence_score`
- `task_rationale`
- `assignment_method`
- `spec_version`
- `assignment_review_required`: boolean `true`/`false`
- `assignment_review_reason`

Rule:

- mức nhận thức không được dùng làm task;
- task phải phản ánh hành vi gia sư mà input tạo cơ hội đánh giá;
- rubric IDs phải thuộc task spec đã biết;
- candidate mơ hồ không được ép vào task; dùng review queue;
- không tạo candidate-level quality decision trong Plan 03.

## 6. Coverage contract cho THCS 6–9

Coverage là coverage quan sát được của candidate, không phải tuyên bố đã bao phủ toàn chương trình.

Trục bắt buộc:

- `grade`: 6, 7, 8, 9;
- `topic_id`/`lesson_id` từ registry;
- `primary_task_id`;
- `cognitive_band`: `Biết`, `Hiểu`, `Vận dụng`;
- `turn_count_bin`;
- `split_strategy`;
- `assignment_review_status`.

Không tạo full Cartesian product khổng lồ làm mặc định. Xuất bảng long-form cho cell quan sát được và bảng gap theo target được người phụ trách chốt.

Coverage report phải tách:

- raw candidate count;
- candidate đã gán task đủ confidence;
- candidate cần review;
- coverage trước và sau khi loại ambiguous assignment;
- lesson/topic chưa có candidate.

## 7. Thay đổi code cụ thể

### 7.1. Package specification

Tạo dưới `src/edu_benchmark/benchmark_specification/`:

- `schema.py`: schema/enum/foreign-key validation;
- `migration.py`: chuyển v0 Tin học 9 thành draft v1 THCS mà không sửa source;
- `provenance.py`: kiểm known IDs và provenance completeness;
- `research_ids.py`: validate/migrate source IDs và alias table;
- `serious_errors.py`: validator catalog;
- `assignment.py`: contract và deterministic feature extraction cho task suggestion;
- `coverage.py`: long-form coverage và gap summary;
- `pipeline.py`: orchestration.

### 7.2. CLI

Tạo:

- `scripts/benchmark_specification/build_thcs_spec_v1.py`
- `scripts/benchmark_specification/assign_candidate_tasks.py`
- `scripts/benchmark_specification/build_candidate_coverage.py`

### 7.3. Specialist use khi plan được duyệt

Được phép dùng đúng một `benchmark-specification-designer` cho synthesis specification v1:

- model pinned: `gpt-5.4-mini`;
- reasoning: `high`;
- input: research artifacts, learning-resource registries, task/rubric v0 và một sample candidate nhỏ;
- allowed writes: thư mục staging riêng
  `outputs/benchmark_specification/specialist_draft/`;
- expected output: draft task/rubric/serious-error/provenance và open questions.

Orchestrator validate và merge sang `spec_v1/`. Không fan-out nhiều instance nếu chưa có phê duyệt riêng. Specialist không xác nhận thay HNMU.

Việc semantic assignment toàn batch cần một execution protocol riêng trong plan implementation:

- deterministic rules chỉ gán khi có dấu hiệu rõ;
- trường hợp mơ hồ vào review queue;
- nếu muốn chạy LLM semantic assignment toàn batch, phải ghi rõ model, shard, chi phí, allowed writes và merge plan trước khi chạy; approval Plan 03 không mặc nhiên cho phép fan-out không giới hạn.

### 7.4. Tests

Tạo `tests/benchmark_specification/`:

- `test_schema.py`
- `test_spec_migration.py`
- `test_provenance.py`
- `test_assignment.py`
- `test_coverage.py`
- `test_specification_pipeline.py`

Test tối thiểu:

1. task/rubric/error IDs unique;
2. rubric task foreign key hợp lệ;
3. serious-error affected rubric IDs hợp lệ;
4. không còn scope hard-coded chỉ Tin học 9 trong spec v1;
5. status đúng enum;
6. unknown research/learning IDs bị gắn lỗi;
7. task assignment không dùng cognitive level làm task;
8. ambiguous candidate vào review queue;
9. mọi converted candidate có assignment hoặc review disposition;
10. coverage tổng khớp số candidate theo từng lớp;
11. output deterministic với cùng input;
12. validator của skill pass.

## 8. Quy trình thực hiện

1. Snapshot/hash input Plan 02 và specification v0.
2. Migrate specification sang draft THCS v1.
3. Chạy một specialist synthesis theo contract ở mục 7.3 nếu được phê duyệt trong execution announcement.
4. Validate task/rubric/serious-error/provenance.
5. Extract feature deterministic cho toàn candidate.
6. Tạo task/rubric suggestions và review queue.
7. Build coverage long-form và gap report.
8. Viết open questions, report và handoff.

Không được chờ HNMU rồi tự đánh dấu plan “không hoàn thành”. Plan có thể hoàn thành ở trạng thái specification/suggestions provisional nếu mọi item cần quyết định đã được ghi rõ.

## 9. Output dự kiến

### Specification

`outputs/benchmark_specification/spec_v1/`

- `benchmark_tasks.csv`
- `rubrics.csv`
- `serious_errors.csv`
- `provenance_matrix.csv`
- `research_id_aliases.csv`
- `benchmark_open_questions.md`
- `spec_validation_report.json`

### Assignment và coverage

`outputs/benchmark_specification/candidate_assignment/`

- `benchmark_candidate_task_rubric_suggestions.csv`
- `task_rubric_review_queue.csv`
- `candidate_coverage_long.csv`
- `coverage_summary.csv`
- `coverage_gaps.csv`

### Report/handoff

- `reports/plan03-thcs-task-rubric-and-coverage-summary.md`
- `handoffs/plan03-thcs-task-rubric-and-coverage.md`
- coordination events append-only.

## 10. Allowed writes

Khi được duyệt, Plan 03 chỉ được ghi vào:

- `src/edu_benchmark/benchmark_specification/`
- `scripts/benchmark_specification/`
- `tests/benchmark_specification/`
- `experiments/20260722_000940/outputs/benchmark_specification/`
- `experiments/20260722_000940/reports/plan03-*`
- `experiments/20260722_000940/handoffs/plan03-*`
- coordination logs append-only;
- `README.md` và `ARCHITECTURE.md` khi component/status thay đổi.

Không sửa specification kế thừa, output conversion Plan 01/02, research artifacts hoặc shared learning-resource registry.

## 11. Cổng hoàn thành

1. Spec v1 dùng phạm vi Tin học THCS lớp 6–9.
2. Task/rubric/error/provenance schema và foreign keys hợp lệ.
3. Không có ID evidence bịa hoặc không tồn tại.
4. Mọi unsupported item có status/open question.
5. Mọi converted candidate có suggestion hoặc review disposition.
6. Coverage tổng khớp candidate population và tách rõ ambiguous rows.
7. Không có task/rubric nào được agent tự đánh dấu `confirmed`.
8. Tests và validator pass bằng `benchmark_env`.
9. Report ghi rõ evidence, inference và teacher decisions needed.

## 12. Ngoài phạm vi

- Không audit chất lượng candidate.
- Không xác nhận candidate-level evidence.
- Không cho HNMU chấm candidate trong plan này.
- Không chấm model.
- Không commit.
