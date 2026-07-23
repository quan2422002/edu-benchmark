# Plan 04 — Evidence và quality audit cho benchmark candidate

Experiment: `20260722_000940`  
Trạng thái: `DRAFT` — chưa được duyệt, không triển khai  
Ngày lập: 23/07/2026  
Phụ thuộc: Plan 03 hoàn thành

## 1. Mục tiêu

Plan 04 kiểm từng benchmark candidate sau conversion và task/rubric assignment để trả lời:

1. candidate có đúng schema và truy vết không;
2. điểm cắt `student_prompt`/`conversation_history`/`gold_response` có đúng không;
3. `gold_answer` và `gold_response` có được học liệu hỗ trợ không;
4. task/rubric có áp dụng được không;
5. candidate có leakage, trùng/gần trùng hoặc lỗi nghiêm trọng không;
6. candidate đủ điều kiện nào: `pass`, `need_human_review`, hay `failed`.

Đây là audit candidate, không phải raw-dialogue audit và không phải chấm response của model.

## 2. Input chỉ đọc

### Candidate và trace

- `outputs/benchmark_conversion/full_v0/benchmark_candidate_splits.csv`
- `outputs/benchmark_conversion/full_v0/conversion_trace.csv`
- `outputs/benchmark_conversion/full_v0/conversion_dispositions.csv`

### Task/rubric/specification

- `outputs/benchmark_specification/spec_v1/benchmark_tasks.csv`
- `outputs/benchmark_specification/spec_v1/rubrics.csv`
- `outputs/benchmark_specification/spec_v1/serious_errors.csv`
- `outputs/benchmark_specification/spec_v1/provenance_matrix.csv`
- `outputs/benchmark_specification/candidate_assignment/benchmark_candidate_task_rubric_suggestions.csv`

### Checklist và học liệu

- `inherited_resources/from_20260709_155523/checklists/benchmark-candidate-quality-checklist-v0.md`
- `shared/learning_resources/fragments/learning_resource_fragments.csv`
- `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv`
- `shared/learning_resources/indexes/learning_resources_v0.sqlite`
- raw-audit evidence được giữ trong candidate chỉ làm provenance, không tự động coi là candidate evidence đã xác nhận.

## 3. Chuẩn hóa checklist candidate v1 trước khi audit

Checklist kế thừa còn dùng một số tên cũ như `benchmark_sample_id`, `raw_sample_id`, `answer`, `fail`, `needs_human_review`. Plan 04 phải tạo bản v1 dẫn xuất, không sửa snapshot.

Tên canonical:

- `benchmark_candidate_id`
- `sample_id`
- `gold_answer`
- `candidate_quality_decision`: `pass`, `need_human_review`, `failed`
- criterion result: `pass`, `uncertain`, `fail`, `not_applicable`

Nhóm tiêu chí v1 tối thiểu:

- `BEN-STR-*`: schema, split và trace;
- `BEN-TASK-*`: task/input/leakage;
- `BEN-RUB-*`: rubric và khả năng chấm;
- `BEN-EVD-*`: evidence học liệu;
- `BEN-PED-*`: chất lượng sư phạm/gold response;
- `BEN-DUP-*`: trùng/gần trùng;
- `BEN-SER-*`: serious errors từ Plan 03.

Mỗi criterion phải ghi rõ:

- kiểm bằng code, retrieval, agent hay con người;
- điều kiện `pass`/`uncertain`/`fail`;
- evidence field được phép dùng;
- default action;
- authority cần xác nhận.

## 4. Candidate-level evidence contract

Plan 04 không tái sử dụng tên `evidence_fragment_ids` của phase 1 với nghĩa mới.

### 4.1. Bảng link chi tiết

Tạo `candidate_evidence_links.csv`, mỗi dòng là một liên kết:

- `benchmark_candidate_id`
- `fragment_id`
- `target_field`: `question`, `gold_answer`, `gold_response`, `task_context`
- `support_status`: `supports`, `partial_support`, `conflicts`, `irrelevant`
- `match_reason`
- `confidence_score`
- `selection_method`
- `evidence_review_required`: boolean `true`/`false`

Fragment ID phải tồn tại trong registry/fragment table. Không invent ID.

### 4.2. Trường tổng hợp

`candidate_content_evidence_fragment_ids` là JSON-list union của các link có `support_status = supports`.

Trường này:

- khác rỗng khi có ít nhất một fragment đã được audit là hỗ trợ trực tiếp nội dung candidate;
- bằng `[]` khi retrieval không tìm được, link chỉ partial/conflict/irrelevant, hoặc chưa audit xong;
- không phụ thuộc máy móc vào `candidate_quality_decision`;
- nếu rỗng với candidate cần kiến thức/học liệu, criterion evidence phải `uncertain` hoặc `fail` theo checklist, không được auto-pass.

### 4.3. Quan hệ với raw-audit evidence

- `raw_audit_blocking_evidence_fragment_ids`: evidence chặn cấp raw sample phase 1.
- `raw_audit_all_evidence_fragment_ids`: toàn bộ evidence agent dùng khi audit raw sample.
- `candidate_content_evidence_fragment_ids`: evidence đã kiểm ở cấp candidate cho nội dung sau split.

Ba trường không được join/rename để giả vờ cùng semantics.

## 5. Audit output schema

### 5.1. Criterion-level

`candidate_checklist_results.csv`:

- `benchmark_candidate_id`
- `criterion_id`
- `criterion_group`
- `result`
- `confidence_score`
- `criterion_evidence_fragment_ids`
- `reason`
- `suggested_reviewer_action`
- `checked_by`
- `checked_at`
- `audit_shard_id`
- `check_method`

Mỗi candidate phải có đúng một dòng cho mỗi criterion bắt buộc.

### 5.2. Candidate-level

`candidate_quality_suggestions.csv`:

- `benchmark_candidate_id`
- `sample_id`
- `candidate_quality_decision`
- `confidence_score`
- `blocking_criterion_ids`
- `failure_reasons`
- `candidate_content_evidence_fragment_ids`
- `suggested_reviewer_action`
- `needs_hnmu_review`
- `needs_uet_review`
- `checked_by`
- `checked_at`
- `audit_version`

Aggregation strict:

- có `fail` → `failed`;
- không có `fail`, có `uncertain` → `need_human_review`;
- còn lại → `pass`.

Confidence:

- `failed`: min confidence của dòng `fail`;
- `need_human_review`: min confidence của dòng `uncertain`;
- `pass`: min confidence của mọi criterion applicable.

### 5.3. Review queue

`candidate_review_queue.csv` có:

- candidate ID;
- priority;
- blocking criteria;
- câu hỏi review cụ thể;
- evidence/source links;
- owner đề xuất: UET hay HNMU;
- status.

## 6. Deterministic checks và semantic checks

### 6.1. Code bắt buộc chạy cho toàn bộ candidate

- schema/enum/required fields;
- candidate ↔ raw trace hai chiều;
- split content so với raw dialogue;
- `gold_answer` so với `answer_sgv`;
- task/rubric foreign keys;
- evidence fragment existence;
- exact duplicate;
- normalized near-duplicate candidates;
- lexical leakage giữa input và `gold_answer`;
- repeated-template gold responses;
- checklist completeness và strict aggregation.

Code chỉ gắn cờ near-duplicate/leakage; không tự kết luận semantic severity nếu rule chưa đủ.

### 6.2. Retrieval-assisted checks

- truy xuất fragment theo grade/lesson/question/`gold_answer`;
- ưu tiên fragment candidate/raw provenance đã có nhưng phải re-check relevance;
- ghi toàn bộ candidate evidence link;
- xung đột SGK/SGV vào review queue.

### 6.3. Agent-assisted checks

Nếu plan được duyệt, được dùng một `benchmark-specification-designer` instance để rà provisional:

- split correctness khi code không đủ;
- task/rubric applicability;
- evidence support;
- gold response usefulness và serious-error indicators.

Model pinned `gpt-5.4-mini`, reasoning `high`. Một native observable thread xử lý các shard tuần tự; không spawn nhiều instance nếu chưa được user phê duyệt fan-out. Mỗi shard ghi thư mục staging riêng và có manifest.

Agent không:

- đánh dấu HNMU đã xác nhận;
- sửa gold response;
- invent evidence;
- chấm model response;
- thay quyết định chuyên môn của giáo viên.

Mọi semantic `pass` là agent-assisted provisional cho đến Plan 05/HNMU review.

## 7. Thay đổi code cụ thể

### 7.1. `src/edu_benchmark/benchmark_quality/`

Tạo/mở rộng:

- `schema.py`: checklist/result/decision contracts;
- `checklist_registry.py`: load/validate checklist v1;
- `candidate_evidence.py`: evidence links và aggregation;
- `structural_checks.py`: schema, trace, split;
- `leakage.py`: lexical leakage features;
- `duplicates.py`: exact/near duplicate clusters;
- `checklist_aggregation.py`: strict candidate-level aggregation;
- `review_queue.py`: queue/priority;
- `pipeline.py`: shard, merge, validate và write output.

### 7.2. CLI

Tạo:

- `scripts/benchmark_quality/build_candidate_checklist_v1.py`
- `scripts/benchmark_quality/run_candidate_deterministic_checks.py`
- `scripts/benchmark_quality/prepare_candidate_audit_shards.py`
- `scripts/benchmark_quality/merge_candidate_audit.py`
- `scripts/benchmark_quality/validate_candidate_audit.py`

### 7.3. Tests

Tạo `tests/benchmark_quality/`:

- `test_candidate_schema.py`
- `test_candidate_evidence.py`
- `test_structural_checks.py`
- `test_leakage.py`
- `test_duplicates.py`
- `test_candidate_checklist_aggregation.py`
- `test_candidate_audit_pipeline.py`

Test tối thiểu:

1. canonical labels only;
2. criterion count đầy đủ;
3. evidence link fragment ID tồn tại;
4. raw evidence không auto-promote thành candidate evidence;
5. support union đúng và deterministic;
6. strict aggregation đúng;
7. task/rubric foreign keys;
8. trace/split mismatch bị fail hoặc review theo registry;
9. lexical leakage chỉ là flag trước semantic decision;
10. duplicate cluster stable;
11. shard overlap/missing ID bị reject;
12. merged output bao phủ toàn bộ candidate population;
13. unknown candidate/criterion ID bị reject;
14. output chạy lại deterministic.

## 8. Quy trình thực hiện

1. Tạo checklist v1 dẫn xuất và schema docs.
2. Chạy deterministic checks toàn batch.
3. Build candidate evidence links bằng retrieval.
4. Tạo audit shards không chồng lấn.
5. Chạy một specialist instance tuần tự nếu execution được phê duyệt.
6. Merge criterion results; không cho agent summary ghi đè detailed source of truth.
7. Aggregate strict candidate decisions.
8. Tạo review queue, summary và handoff.
9. Validate toàn bộ row count, completeness, IDs và provenance.

## 9. Output dự kiến

### Checklist/spec

- `outputs/benchmark_candidate_audit/checklists/benchmark-candidate-quality-checklist-v1.md`
- `outputs/benchmark_candidate_audit/checklists/benchmark-candidate-audit-criteria-v1.csv`

### Audit

`outputs/benchmark_candidate_audit/full_v0/`

- `candidate_evidence_links.csv`
- `candidate_checklist_results.csv`
- `candidate_quality_suggestions.csv`
- `candidate_review_queue.csv`
- `candidate_duplicate_clusters.csv`
- `candidate_leakage_flags.csv`
- `audit_validation_summary.json`

### Report/handoff

- `reports/plan04-benchmark-candidate-audit-summary.md`
- `handoffs/plan04-benchmark-candidate-audit.md`
- coordination events append-only.

## 10. Allowed writes

Khi được duyệt:

- `src/edu_benchmark/benchmark_quality/`
- `scripts/benchmark_quality/`
- `tests/benchmark_quality/`
- `experiments/20260722_000940/outputs/benchmark_candidate_audit/`
- `experiments/20260722_000940/reports/plan04-*`
- `experiments/20260722_000940/handoffs/plan04-*`
- coordination logs append-only;
- `README.md`, `ARCHITECTURE.md` khi status/component thay đổi.

Không sửa candidate Plan 02, specification Plan 03, snapshot/raw data hoặc shared fragments/registry.

## 11. Cổng hoàn thành

1. Checklist v1 có canonical schema và quyết định.
2. Mỗi candidate có đủ criterion rows hoặc được ghi rõ audit error.
3. Candidate evidence có link chi tiết, fragment tồn tại và semantics riêng.
4. Detailed checklist là source of truth cho summary.
5. Không candidate nào auto-pass khi còn criterion bắt buộc chưa audit.
6. Duplicate/leakage flags bao phủ toàn batch.
7. Mọi `need_human_review`/`failed` có blocking criterion và reason.
8. Audit merge không missing/duplicate candidate.
9. Test/validator pass bằng `benchmark_env`.
10. Report phân biệt agent provisional result với HNMU-confirmed decision.

## 12. Ngoài phạm vi

- Không sửa candidate content.
- Không chọn final pilot.
- Không yêu cầu HNMU review toàn batch trong plan này.
- Không chấm model.
- Không commit.
