# Roadmap — Giai đoạn 2: xây dựng mẫu benchmark từ dữ liệu thô đã pass

Experiment: `20260722_000940`  
Trạng thái: `ACTIVE`  
Nguồn kế thừa chính: `20260709_155523` và `20260705_215045`

## 1. Mục tiêu của experiment

Experiment này bắt đầu sau khi tạm đóng giai đoạn 1: đánh giá chất lượng dữ liệu hội thoại thô HNMU.

Mục tiêu của giai đoạn 2 là:

1. Chọn các mẫu hội thoại thô đã `pass` ở giai đoạn 1.
2. Chuyển chúng thành ứng viên mẫu benchmark có cấu trúc.
3. Gán hoặc kiểm tra các trường benchmark quan trọng như `student_prompt`, `conversation_history`, `gold_response`, `gold_answer`, task, rubric, mức nhận thức, dạng bài và học liệu tham chiếu.
4. Đánh giá chất lượng của ứng viên mẫu benchmark trước khi dùng để chấm mô hình.
5. Chuẩn bị một tập mẫu đủ sạch, có truy vết, có thể đưa cho HNMU/UET rà soát hoặc dùng cho thử nghiệm đánh giá mô hình sau này.

### 1.1. Phạm vi môn học đã chốt

Từ ngày 23/07/2026, phạm vi của benchmark là **môn Tin học THCS lớp 6–9**. Lớp 6–8 không còn chỉ được xem là tiền kiến thức phụ cho lớp 9.

Ma trận 96 ô từ experiment `20260705_215045` vẫn được kế thừa để tham khảo cấu trúc task, mức nhận thức và dạng bài, nhưng không phải ma trận coverage đầy đủ cho phạm vi mới. Coverage giai đoạn 2 phải được thống kê trên cả bốn lớp dựa vào dữ liệu HNMU và registry chủ đề/bài học THCS trong `shared/learning_resources/`.

## 2. Đầu vào kế thừa

### 2.1. Từ experiment `20260709_155523`

Experiment trước cung cấp các đầu vào bắt buộc cho giai đoạn 2:

- dữ liệu hội thoại thô đã chuẩn hóa ở cấp dòng;
- kết quả đánh giá dữ liệu thô theo checklist;
- danh sách mẫu `pass`, `need_human_review`, `failed`;
- checklist riêng cho ứng viên mẫu benchmark;
- học liệu SGK/SGV đã OCR, chia fragment và lập chỉ mục truy xuất;
- công cụ truy xuất học liệu bằng full-text search;
- quy tắc tổng hợp kết quả từ tiêu chí chi tiết lên quyết định cấp mẫu.

Đầu vào ưu tiên cho chuyển đổi là:

- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/quality_check_suggestions.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/quality_check_suggestions.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/raw_dialogue_checklist_results.repaired.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/normalized_dialogue_rows.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/normalized_dialogue_rows.csv`
- `experiments/20260709_155523/reports/benchmark-candidate-quality-checklist-v0.md`
- `shared/learning_resources/fragments/learning_resource_fragments.csv`
- `shared/learning_resources/indexes/learning_resources_v0.sqlite`

### 2.2. Từ experiment `20260705_215045`

Experiment `20260705_215045` cung cấp phần thiết kế benchmark ban đầu:

- 4 task hành vi gia sư v0;
- 5 nhóm rubric cho mỗi task, dùng thang Likert 1–5;
- ma trận bao phủ v0 thiên về Tin học 9, dùng để tham khảo cấu trúc trục chứ không đại diện đầy đủ cho coverage Tin học THCS lớp 6–9;
- các ví dụ phiếu tác giả/ứng viên mẫu benchmark để tham khảo cách trình bày.

Đầu vào kế thừa chính:

- `experiments/20260705_215045/benchmark_design/benchmark_tasks.csv`
- `experiments/20260705_215045/benchmark_design/rubrics.csv`
- `experiments/20260705_215045/benchmark_design/task_design_rationale_v0.md`
- `experiments/20260705_215045/benchmark_design/rubric_design_rationale_v0.md`
- `experiments/20260705_215045/coverage_design/general_coverage_matrix_v0.csv`
- `experiments/20260705_215045/coverage_design/coverage_axis_values_v0.csv`
- `experiments/20260705_215045/teacher_examples/`

## 3. Kết quả giai đoạn 1 có thể dùng ngay

Tổng cộng giai đoạn 1 đã rà soát 1.050 mẫu hội thoại thô lớp 6–9.

Theo kết quả rà sâu bằng checklist:

| Nhóm dữ liệu | Tổng mẫu | Pass | Cần người xem lại | Failed |
|---|---:|---:|---:|---:|
| Lớp 6–7 | 462 | 238 | 222 | 2 |
| Lớp 8–9 | 588 | 427 | 160 | 1 |
| Tổng | 1.050 | 665 | 382 | 3 |

Trong giai đoạn 2, chỉ nên lấy nhóm `pass` làm đầu vào mặc định. Nhóm `need_human_review` chỉ đưa vào nếu UET/HNMU quyết định xử lý bổ sung hoặc cần mẫu để phân tích lỗi.

## 4. Cách chia plan trong giai đoạn 2

Experiment này không giao toàn bộ phase 2 cho một plan duy nhất. Các plan được chia theo cổng kiểm soát sau:

| Plan | Trạng thái | Phạm vi | Scale | Output/chốt chính | Phụ thuộc |
|---|---|---|---:|---|---|
| [Plan 01 — Contract và pilot conversion](plans/01-audited-raw-dialogue-to-benchmark-candidate-conversion.md) | `COMPLETED` | Chốt schema, semantics evidence, code chọn input và tách hội thoại; chạy pilot deterministic | 665 input, 40 candidate pilot | Code conversion v0, schema v0, pilot, lỗi và trace | Dữ liệu phase 1 |
| [Plan 02 — Multi-candidate conversion từ mọi lượt gia sư](plans/02-split-policy-and-full-benchmark-conversion.md) | `DRAFT`, chờ duyệt | Migrate contract Plan 01 sang một candidate cho mỗi lượt AI; chạy pilot rồi full conversion | 665 raw sample `pass` → dự kiến 2.028 candidate sơ bộ | D02-01, migration pilot, candidate file gọn, trace, raw-sample summary và error queue | Plan 01 |
| [Plan 03 — Task/rubric specification và coverage THCS](plans/03-thcs-task-rubric-specification-and-coverage.md) | `DRAFT` | Migrate spec sang THCS 6–9, gán task/rubric cho pool sơ bộ và ghi disposition giữ/loại có truy vết | Dự kiến 2.028 candidate trước filtering | Spec v1, serious errors, provenance, assignment/disposition/review queue, coverage | Plan 02 |
| [Plan 04 — Evidence và audit benchmark candidate](plans/04-benchmark-candidate-evidence-and-quality-audit.md) | `DRAFT` | Kiểm schema, evidence, task/rubric, `gold_answer`, `gold_response`, leakage, trùng/gần trùng và giá trị đánh giá | Toàn bộ candidate | Evidence links, checklist chi tiết, `candidate_quality_suggestions.csv`, review queue | Plan 03 |
| [Plan 05 — Pilot benchmark và HNMU/UET review](plans/05-benchmark-pilot-and-hnmu-uet-review.md) | `DRAFT` | Chọn candidate đạt yêu cầu, chuẩn bị packet, review độc lập và phân xử | Tập con sau audit; đề xuất 40 | Pilot v0, teacher packet, review/adjudication, readiness report | Plan 04 |

Plan 01 là pilot nhỏ để kiểm contract và code path; không gán task/rubric trên toàn bộ dữ liệu, không audit chất lượng toàn bộ candidate và không thay thế các plan 02–05.

### 4.1. Tình trạng sau Plan 01

Plan 01 đã tạo 665 conversion inputs hợp lệ và 40 candidate pilot, 10 mẫu mỗi lớp. Hai lỗi vai trò không xen kẽ đã được người phụ trách dự án quyết định sửa qua overlay có hash; snapshot kế thừa không thay đổi. Sau correction, 665/665 hội thoại bắt đầu bằng HS và xen kẽ HS/AI hợp lệ; không có mẫu `pass` nào bắt đầu bằng AI.

Người phụ trách dự án đã định hướng Plan 02 theo contract mới: một raw dialogue tạo một candidate cho mỗi lượt AI. `student_prompt` luôn là lượt HS đầu, history là prefix trước target AI, và mọi suffix sau target đều bị bỏ qua. Do đó, việc 297 hội thoại kết thúc bằng HS không còn tạo một nhánh split policy riêng; lượt HS cuối không xuất hiện trong candidate và không cần cột outcome.

Preflight deterministic trên đúng 665 mẫu `pass` cho thấy contract này sẽ tạo tối đa 2.028 candidate sơ bộ: lớp 6 có 279, lớp 7 có 438, lớp 8 có 557 và lớp 9 có 754. Plan 02 vẫn phải ở trạng thái `DRAFT` cho đến khi người phụ trách duyệt plan, sau đó chạy migration pilot trước full conversion.

## 5. Hướng triển khai giai đoạn 2

### Giai đoạn 2.1 — Chọn đầu vào chuyển đổi

Mục tiêu:

- ghép `quality_check_suggestions.csv` với `normalized_dialogue_rows.csv`;
- lọc các mẫu `pass`;
- giữ đầy đủ truy vết tới file gốc, dòng gốc, lớp, bài học, vị trí và kết quả audit.
- giữ đúng semantics phase 1 bằng cách chuẩn hóa cột cấp mẫu `evidence_fragment_ids` thành `raw_audit_blocking_evidence_fragment_ids`;
- tổng hợp `raw_audit_all_evidence_fragment_ids` từ toàn bộ `evidence_fragment_id` không rỗng trong checklist chi tiết;
- chưa định nghĩa evidence cấp benchmark candidate trong Plan 01; phần đó thuộc Plan 04.

Output dự kiến:

- `outputs/benchmark_conversion/conversion_input_pass_samples.csv`
- báo cáo số lượng mẫu đủ điều kiện theo lớp, chủ đề, bài học, mức nhận thức.

### Giai đoạn 2.2 — Chuyển hội thoại thô thành ứng viên mẫu benchmark

Mục tiêu:

- tách `student_prompt`, `conversation_history`, `gold_response`;
- tách riêng trường `gold_answer` từ `answer_sgv`;
- không sửa hội thoại gốc;
- Plan 01 dùng chiến lược pilot `final_tutor_response`: một raw dialogue tạo tối đa một candidate;
- Plan 02 sẽ migrate sang `each_tutor_turn`: mỗi lượt AI tạo đúng một candidate;
- `student_prompt` luôn là lượt HS đầu; history là các lượt từ sau prompt đến trước target AI;
- mọi lượt sau target không được dùng trong candidate đó; riêng lượt HS cuối của 297 hội thoại không được đưa vào bất kỳ candidate nào;
- không thêm `post_response_student_outcome`; provenance chi tiết được giữ trong bảng trace riêng;
- toàn bộ 665 raw sample phải có summary, còn candidate file giữ schema nội dung gọn;
- mọi candidate cùng `sample_id` tạo thành một family và phải nằm cùng split ở các bước sau để tránh leakage.

Output dự kiến:

- pilot Plan 01: `outputs/benchmark_conversion/pilot_v0/benchmark_candidate_splits.csv`
- full batch Plan 02: `outputs/benchmark_conversion/full_v0/benchmark_candidate_splits.csv`
- `conversion_trace.csv` trong thư mục run tương ứng;
- Plan 02 thêm `raw_sample_conversion_summary.csv` bao phủ đủ 665 raw sample.

### Giai đoạn 2.3 — Gán task/rubric và metadata còn thiếu

Mục tiêu:

- dùng task/rubric v0 từ experiment `20260705_215045`;
- migrate task/rubric v0 thành specification v1 cho phạm vi Tin học THCS lớp 6–9; không mang giới hạn diễn đạt “Tin học 9” của artifact v0 sang schema ứng viên mới;
- tạo serious-error catalog và provenance matrix trước khi audit candidate;
- gán task theo hành vi gia sư cần đánh giá, không gán chỉ theo mức nhận thức;
- mức nhận thức là metadata hỗ trợ, không thay thế task;
- nếu agent gợi ý task/rubric, phải có confidence và lý do.
- candidate không khớp task/rubric phải có disposition như `excluded_no_supported_task`; không xóa âm thầm khỏi luồng.
- vì một raw dialogue sinh nhiều candidate có history lồng nhau, coverage và metric downstream phải báo cả candidate-macro và raw-dialogue-family-macro hoặc weighting tương đương.

Output dự kiến:

- `outputs/benchmark_specification/spec_v1/`
- `outputs/benchmark_specification/candidate_assignment/benchmark_candidate_task_rubric_suggestions.csv`
- `outputs/benchmark_specification/candidate_assignment/task_rubric_review_queue.csv`

### Giai đoạn 2.4 — Đánh giá chất lượng ứng viên mẫu benchmark

Mục tiêu:

- dùng `benchmark-candidate-quality-checklist-v0.md`;
- kiểm cấu trúc benchmark, truy vết, task/rubric, học liệu, rò đáp án, trùng/gần trùng và khả năng dùng để chấm mô hình;
- tách rõ lỗi do chuyển đổi với lỗi vốn có trong dữ liệu thô.
- chuẩn hóa mọi quyết định chất lượng cấp ứng viên về đúng ba nhãn `pass`, `need_human_review`, `failed`; các nhãn cũ `needs_human_review` và `fail` chỉ được đọc để migration, không được ghi vào output mới.
- tạo `candidate_evidence_links.csv` và `candidate_content_evidence_fragment_ids` với semantics cấp candidate; không đổi nghĩa hai trường `raw_audit_*` của phase 1.

Output dự kiến:

- `outputs/benchmark_candidate_audit/full_v0/candidate_evidence_links.csv`
- `outputs/benchmark_candidate_audit/full_v0/candidate_checklist_results.csv`
- `outputs/benchmark_candidate_audit/full_v0/candidate_quality_suggestions.csv`
- `outputs/benchmark_candidate_audit/full_v0/candidate_review_queue.csv`
- `reports/benchmark-candidate-audit-summary.md`

### Giai đoạn 2.5 — Chuẩn bị pilot benchmark

Mục tiêu:

- chọn một tập ứng viên pass để HNMU/UET rà nhanh;
- thống kê độ phủ sau chuyển đổi trên toàn bộ lớp 6–9;
- tách reviewer, adjudicator và pilot participant; không cho author tự accept/reject mẫu của mình;
- chuẩn bị đầu vào cho giai đoạn thử nghiệm chấm mô hình.

Output dự kiến:

- `outputs/benchmark_pilot/benchmark_samples_pilot_v0.csv`
- `reports/benchmark-pilot-readiness-summary.md`

## 6. Nguyên tắc quan trọng

1. Không sửa file Excel gốc của HNMU.
2. Không dùng mẫu `need_human_review` như mẫu sạch nếu chưa có quyết định bổ sung.
3. Không trộn `gold_answer` vào `gold_response`.
4. `gold_response` là phản hồi gia sư lý tưởng trong bối cảnh `student_prompt` và `conversation_history`, không chỉ là đáp án cuối.
5. Mọi mẫu benchmark phải truy vết được về mẫu thô nguồn và học liệu SGK/SGV liên quan.
6. Nếu agent điền trường còn thiếu, phải lưu `confidence_score`, lý do và cờ cần người xác nhận.
7. Đánh giá chất lượng ứng viên benchmark là bước mới, không được đồng nhất với đánh giá chất lượng dữ liệu thô ở giai đoạn 1.
8. Tên file ứng viên sau tách hội thoại luôn là `benchmark_candidate_splits.csv`; pilot và full batch được tách bằng thư mục run `pilot_v0/` và `full_v0/`, không đổi tên file.
9. Nhóm ưu tiên của experiment là toàn bộ 665 mẫu `pass`; nhóm `need_human_review` và `failed` được giữ ngoài luồng chuyển đổi mặc định.

## 7. Việc chưa triển khai ngay

- Chưa chấm mô hình.
- Chưa xây dựng benchmark chính thức.
- Chưa thay đổi task/rubric v0 nếu chưa có yêu cầu riêng.
- Chưa đưa nhóm `need_human_review` vào chuyển đổi đại trà.
