# Plan 02 — Multi-candidate conversion từ mọi lượt gia sư

Experiment: `20260722_000940`

Trạng thái: `COMPLETED` — được duyệt và hoàn thành ngày 23/07/2026; hardening sau hậu kiểm ngày 24/07/2026

Ngày cập nhật: 24/07/2026

Phụ thuộc: Plan 01 đã `COMPLETED`

## 1. Mục tiêu và vị trí của Plan 02

Plan 01 đã hoàn thành mục tiêu của một pilot kỹ thuật: tạo 665 conversion inputs đã `pass`, chốt semantics evidence phase 1, xây code path tách hội thoại, áp dụng hai correction overlay đã được người phụ trách dự án duyệt và xuất 40 candidate pilot theo contract ban đầu.

Plan 02 không lặp lại Plan 01 ở quy mô lớn một cách máy móc. Plan này sẽ:

1. migrate contract `final_tutor_response` của Plan 01 sang contract `each_tutor_turn`;
2. từ mỗi raw dialogue, tạo một candidate cho **mỗi lượt AI** trong hội thoại đã áp dụng correction;
3. chạy migration pilot có kiểm tra exhaustive bằng code/regex;
4. sau khi pilot đạt gate, chuyển toàn bộ 665 raw dialogue `pass` thành pool sơ bộ dự kiến 2.028 candidate;
5. giữ candidate content gọn, đồng thời tách provenance và thông tin correction sang bảng trace riêng.

Plan 02 chỉ tạo **pool ứng viên trước task/rubric**. Plan này không gán task/rubric, không đánh giá chất lượng sư phạm và không tuyên bố 2.028 candidate là benchmark chính thức.

## 2. Quyết định thiết kế D02-01 đã được duyệt

Policy đã được ghi tại `decisions/D02-01-multi-candidate-each-tutor-turn.md`:

- `split_strategy = each_tutor_turn`;
- một raw dialogue tạo đúng một candidate cho mỗi lượt AI;
- `student_prompt` của mọi candidate cùng raw dialogue luôn là lượt HS đầu tiên;
- `gold_response` là nội dung của lượt AI đang được chọn làm target;
- `conversation_history` gồm đúng các lượt từ sau `student_prompt` đến ngay trước target;
- phần hội thoại sau target không được dùng ở bất kỳ trường nội dung nào của candidate đó;
- nếu raw dialogue kết thúc bằng HS, lượt HS cuối chỉ là phần hậu tố sau target AI cuối và không xuất hiện ở bất kỳ candidate nào;
- không thêm trường `post_response_student_outcome`;
- có thể truy ngược toàn bộ hội thoại nguồn bằng `sample_id` và bảng trace;
- candidate không được gán task/rubric phù hợp ở Plan 03 sẽ bị loại khỏi benchmark cuối, nhưng phải có disposition rõ ràng thay vì biến mất âm thầm.

Đây là quyết định thiết kế của dự án dựa trên mục tiêu tạo tối đa candidate có ích từ dữ liệu đã thu thập. Các nghiên cứu kế thừa hỗ trợ việc đánh giá một phản hồi gia sư trong một lịch sử hội thoại cố định; riêng lựa chọn tạo candidate ở **mọi** lượt AI là suy luận thiết kế cần được xác nhận bằng migration pilot và audit ở các plan sau.

Căn cứ nghiên cứu và diễn giải được kế thừa tại:

- `experiments/20260709_155523/reports/three-paper-benchmark-use-synthesis.md`, đặc biệt phần phân biệt bằng chứng trực tiếp với suy luận “một hội thoại tạo nhiều mẫu”;
- `experiments/20260705_215045/literature_notes/paper_summaries/P03-P002-kmp-bench.md`, nơi KMP-Dialogue cắt hội thoại tại một lượt gia sư và đánh giá response trong context cố định.

Hai nguồn này không tự động chứng minh rằng mọi candidate sinh ra đều có giá trị đánh giá; việc đó thuộc Plan 03–05 và thẩm quyền review của HNMU/UET.

## 3. Phạm vi đầu vào và baseline đã xác nhận

### 3.1. Chỉ dùng 665 raw dialogue `pass`

Đầu vào vận hành:

- `outputs/benchmark_conversion/conversion_input_pass_samples.csv`
- `outputs/benchmark_conversion/dialogue_corrections.csv`
- code và schema conversion v0 từ Plan 01;
- report và trace của Plan 01 để đối chiếu migration.

Không rà hoặc chuyển đổi toàn bộ 1.050 mẫu phase 1. Nhóm `need_human_review` và `failed` nằm ngoài Plan 02.

### 3.2. Điều kiện cấu trúc

Sau khi áp dụng đúng hai correction overlay đã duyệt:

- có đúng 665 `sample_id` duy nhất;
- 665/665 hội thoại bắt đầu bằng HS;
- 665/665 hội thoại xen kẽ HS/AI hợp lệ;
- không có hội thoại `pass` nào bắt đầu bằng AI;
- mỗi hội thoại có từ 2 đến 7 lượt AI, do đó đều tạo được candidate;
- không sửa `raw_dialogue`; splitter chỉ dùng `conversion_dialogue`.

### 3.3. Baseline candidate dự kiến

Preflight deterministic trên 665 `conversion_dialogue` cho kết quả:

| Lớp | Raw dialogue | Candidate dự kiến |
|---|---:|---:|
| 6 | 106 | 279 |
| 7 | 132 | 438 |
| 8 | 209 | 557 |
| 9 | 218 | 754 |
| **Tổng** | **665** | **2.028** |

Phân bố số candidate trên một raw dialogue:

| Candidate/raw dialogue | Số raw dialogue |
|---:|---:|
| 2 | 292 |
| 3 | 167 |
| 4 | 105 |
| 5 | 85 |
| 6 | 14 |
| 7 | 2 |

Phân bố độ dài `conversation_history`, tính theo số lượt:

| Số lượt history | Candidate dự kiến |
|---:|---:|
| 0 | 665 |
| 2 | 665 |
| 4 | 373 |
| 6 | 206 |
| 8 | 101 |
| 10 | 16 |
| 12 | 2 |

Các số trên là acceptance baseline cho full conversion, không phải chỉ tiêu lấy mẫu cần ép cho bằng.

## 4. Contract tách một hội thoại

Giả sử `conversion_dialogue` có các lượt xen kẽ:

`HS1, AI2, HS3, AI4, HS5, AI6, ...`

Splitter tạo:

| Candidate | `student_prompt` | `conversation_history` | `gold_response` |
|---|---|---|---|
| target AI2 | HS1 | `[]` | AI2 |
| target AI4 | HS1 | AI2, HS3 | AI4 |
| target AI6 | HS1 | AI2, HS3, AI4, HS5 | AI6 |

Quy tắc tổng quát với target ở effective turn `k`:

- `student_prompt = turn[1].content`;
- `conversation_history = turns[2:k]`, serialize thành JSON list có thứ tự và có role;
- `gold_response = turn[k].content`;
- `gold_answer = answer_sgv`;
- bỏ qua `turn[k+1:]` đối với candidate này.

Mọi content được copy nguyên văn từ `conversion_dialogue`; Plan 02 không viết lại câu trả lời gia sư. Effective turn index là chỉ số sau khi correction overlay được áp dụng. Turn nguồn và correction ID vẫn được truy qua trace.

### 4.1. Candidate ID

ID có dạng:

`BC-<sample_id>-AI<effective_turn_index_2_digits>`

Ví dụ:

- `BC-HNMU-G6-R0001-STT1-AI02`
- `BC-HNMU-G6-R0001-STT1-AI04`

ID phải duy nhất, deterministic và byte-stable khi chạy lại cùng input/correction version.

## 5. Schema output

### 5.1. File candidate gọn

`benchmark_candidate_splits.csv` chỉ chứa các cột phục vụ nội dung benchmark và khóa truy vết:

1. `benchmark_candidate_id`
2. `sample_id`
3. `grade`
4. `lesson`
5. `position`
6. `bloom_level`
7. `student_prompt`
8. `conversation_history`
9. `gold_response`
10. `gold_answer`

Không đưa các trường sau vào file candidate:

- `raw_dialogue`
- `conversion_dialogue`
- `dialogue_correction_ids`
- raw-audit evidence
- `post_response_student_outcome`
- task/rubric suggestion
- candidate quality decision.

### 5.2. File trace riêng

`conversion_trace.csv` có một dòng cho mỗi candidate:

1. `benchmark_candidate_id`
2. `sample_id`
3. `source_batch`
4. `source_file`
5. `source_row_number`
6. `target_tutor_turn_index`
7. `split_strategy`
8. `dialogue_correction_ids`

Trace giữ provenance kỹ thuật mà không làm phình schema candidate. `raw_dialogue`, `conversion_dialogue` và hai trường `raw_audit_*` vẫn nằm ở conversion input cấp mẫu và được join lại bằng `sample_id` khi cần điều tra.

### 5.3. Bảng disposition cấp raw sample

`conversion_dispositions.csv` có đúng 665 dòng:

1. `sample_id`
2. `grade`
3. `candidate_count`
4. `first_target_tutor_turn_index`
5. `last_target_tutor_turn_index`
6. `conversion_disposition`: `converted`, `need_human_review`, hoặc `failed`
7. `reason_code`
8. `reason`

Trong một run hợp lệ dự kiến 665 dòng đều là `converted`. Hai nhãn còn lại chỉ dùng khi validator phát hiện lỗi kỹ thuật hoặc input lệch khỏi precondition; pipeline phải fail closed và không công bố full output đạt gate.

## 6. Thay đổi code cụ thể khi Plan 02 được duyệt

### 6.1. `src/edu_benchmark/benchmark_conversion/schema.py`

- đổi `SPLIT_STRATEGIES` để hỗ trợ `each_tutor_turn`;
- tách `CANDIDATE_SPLIT_COLUMNS` thành schema gọn ở mục 5.1;
- mở rộng `TRACE_COLUMNS` theo mục 5.2;
- thêm `CONVERSION_DISPOSITION_COLUMNS`;
- validator history theo role/content và đúng thứ tự;
- validator 1:1 giữa candidate và trace;
- validator group coverage giữa raw sample, số lượt AI và candidate count.

Schema Plan 01 vẫn phải đọc được để so sánh migration; không ghi đè output pilot cũ.

### 6.2. `src/edu_benchmark/benchmark_conversion/dialogue_split.py`

Refactor parser hiện tại vì `parse_dialogue_turns(...)` của Plan 01 đang gắn điều kiện “lượt cuối phải là tutor” ngay ở tầng parse:

- tầng parse chung chỉ kiểm cú pháp label, lượt đầu là HS và role xen kẽ; chấp nhận cả hội thoại kết thúc bằng HS hoặc AI;
- `split_final_tutor_response_candidate(...)` tự giữ precondition lượt cuối là AI để regression behavior Plan 01 không đổi;
- splitter mới không đặt precondition lên role cuối.

Thêm:

- `split_each_tutor_turn_candidates(...)`;
- parse `conversion_dialogue` đúng một lần;
- xác nhận lượt đầu là HS và toàn chuỗi xen kẽ;
- lặp qua mọi lượt AI theo effective turn index tăng dần;
- dựng đúng fixed `student_prompt`, prefix history và target response;
- không copy bất kỳ suffix nào sau target.

Giữ splitter Plan 01 để regression test, nhưng full run Plan 02 không dùng `final_tutor_response`.

### 6.3. `src/edu_benchmark/benchmark_conversion/pipeline.py`

Thêm:

- `run_multi_candidate_migration_pilot(...)`;
- `run_full_multi_candidate_conversion(...)`;
- kiểm input schema/hash và correction overlay trước khi tách;
- ghi candidate, trace, conversion disposition, error queue và summary JSON;
- sort deterministic theo `sample_id`, rồi `target_tutor_turn_index`;
- dừng full run nếu output không đạt các baseline ở mục 3.3.
- ghi toàn bộ output vào staging directory và chỉ publish nguyên bundle sau khi mọi gate đạt;
- nếu input, baseline hoặc serialized mapping lỗi, publish failure bundle chỉ có error/summary/status; không để candidate cũ ở đường dẫn output;
- ghi `run_status.json` để downstream kiểm `status = complete`;
- chạy post-write validator: parse toàn bộ source bằng regex `HS:/AI:` rồi so sánh chính xác mọi prompt, history, target, answer, trace và disposition.

### 6.4. CLI

Tạo:

- `scripts/benchmark_conversion/run_multi_candidate_migration_pilot.py`
- `scripts/benchmark_conversion/run_full_conversion.py`

Argument tối thiểu:

- `--experiment-root`
- `--input-path`
- `--corrections-path`
- `--output-dir`

Không hard-code đường dẫn máy cá nhân hoặc thay đổi snapshot kế thừa.

### 6.5. Tests

Mở rộng `tests/benchmark_conversion/`:

- `test_dialogue_split.py` cho parser và multi-candidate splitter;
- `test_full_conversion_pipeline.py`
- cập nhật schema/CLI tests liên quan.

Test tối thiểu:

1. 665/665 input bắt đầu bằng HS sau correction overlay;
2. 665/665 input xen kẽ role hợp lệ;
3. target của mọi candidate là lượt AI;
4. `student_prompt` luôn đúng lượt 1;
5. candidate target AI2 có history `[]`;
6. history của mỗi candidate bằng chính xác prefix từ lượt 2 đến trước target;
7. không source-turn index nào thuộc suffix sau target được ánh xạ vào `student_prompt`, history hoặc `gold_response`;
8. source turn HS cuối của 297 hội thoại không được ánh xạ vào bất kỳ candidate nào; không kiểm bằng string matching vì nội dung trùng có thể xuất hiện ở lượt khác;
9. mỗi lượt AI tạo đúng một candidate và mỗi candidate trỏ tới đúng một lượt AI;
10. candidate count của mỗi `sample_id` bằng số lượt AI;
11. có đúng 2.028 candidate và 2.028 ID duy nhất;
12. số candidate theo lớp và history length khớp mục 3.3;
13. candidate và trace có quan hệ 1:1;
14. candidate file không chứa raw dialogue, correction hoặc raw-audit evidence;
15. hai correction đã duyệt giữ đúng source hash/ID và không phát sinh correction ngầm;
16. chạy lại cùng input cho output byte-stable;
17. mọi candidate cùng `sample_id` được nhận diện là một candidate family để downstream split theo nhóm.

## 7. Quy trình thực hiện

### Bước 1 — Ghi decision record

Tạo:

`experiments/20260722_000940/decisions/D02-01-multi-candidate-each-tutor-turn.md`

Record ghi:

- policy ở mục 2;
- phạm vi đúng 665 mẫu `pass`;
- effective-turn semantics và candidate ID;
- quyết định không giữ lượt HS cuối trong benchmark candidate;
- quyết định không thêm outcome column;
- cách kế thừa hai correction;
- versioning và rollback.

### Bước 2 — Migration pilot

Chọn deterministic 20 raw dialogue:

- 5 mẫu mỗi lớp;
- phủ các candidate count/history length khác nhau;
- bắt buộc chứa hai sample có correction;
- lưu `pilot_sample_ids.csv` kèm lý do chọn.

Kiểm exhaustive bằng code cho từng target:

- parser regex nhận diện và kiểm chuỗi role `HS:/AI:`;
- prompt phải đúng lượt HS đầu;
- history phải đúng prefix theo turn index/role/content;
- target phải đúng lượt AI;
- suffix phải bị bỏ đúng;
- nội dung không được sửa hoặc ghép ngoài correction đã duyệt;
- candidate, trace và disposition phải khớp 1:1/cấp family.

Kết quả ghi vào `candidate_mapping_validation.json`. Nếu một bất biến sai, không chạy full conversion. Không yêu cầu người đọc thủ công 69 candidate deterministic.

### Bước 3 — Full conversion

Sau khi migration pilot đạt gate:

- đọc đúng 665 conversion inputs;
- tạo một candidate cho mỗi lượt AI;
- ghi candidate file gọn và trace riêng;
- tạo raw-sample summary đủ 665 dòng;
- không gán task/rubric và không loại candidate theo giá trị đánh giá trong bước này.

### Bước 4 — Validation và report

Report tách rõ:

- raw sample count;
- candidate count và candidate/raw distribution;
- count theo lớp và history length;
- correction coverage;
- lỗi kỹ thuật;
- reproducibility hashes;
- cảnh báo về candidate-family leakage và weighting.

## 8. Output dự kiến

### 8.1. Migration pilot

`outputs/benchmark_conversion/multi_candidate_migration_pilot/`

- `pilot_sample_ids.csv`
- `benchmark_candidate_splits.csv`
- `conversion_trace.csv`
- `conversion_dispositions.csv`
- `dialogue_split_errors.csv`
- `candidate_mapping_validation.json`
- `conversion_summary.json`
- `run_status.json`

Report:

- `reports/plan02-multi-candidate-migration-pilot.md`

### 8.2. Full run

`outputs/benchmark_conversion/full_v0/`

- `benchmark_candidate_splits.csv`
- `conversion_trace.csv`
- `conversion_dispositions.csv`
- `dialogue_split_errors.csv`
- `candidate_mapping_validation.json`
- `conversion_summary.json`
- `run_status.json`

Handoff:

- `reports/plan02-full-multi-candidate-conversion-summary.md`
- `handoffs/plan02-full-multi-candidate-conversion.md`
- coordination events append-only.

## 9. Quan hệ với Plan 03 và các plan sau

Plan 02 tạo pool sơ bộ 2.028 candidate. Plan 03 phải:

- gán task/rubric trong bảng riêng keyed bằng `benchmark_candidate_id`;
- dùng disposition rõ ràng như `assigned`, `need_human_review`, `excluded_no_supported_task`;
- không xóa âm thầm candidate không khớp task/rubric;
- chỉ chuyển candidate phù hợp sang các bước audit và lựa chọn benchmark cuối.

Mọi candidate cùng `sample_id` là một **candidate family** có ngữ cảnh lồng nhau. Khi chia train/dev/test hoặc các tập đánh giá sau này, toàn bộ family phải nằm cùng một split để tránh leakage.

Vì hội thoại dài sinh nhiều candidate hơn, báo cáo/metric sau này không được chỉ tính candidate-macro rồi coi mỗi candidate độc lập tuyệt đối. Plan 03–05 phải đề xuất ít nhất:

- thống kê candidate-macro; và
- thống kê raw-dialogue-family-macro hoặc weighting tương đương.

Task/rubric suitability, chất lượng sư phạm của từng target và quyết định giữ/loại cuối cùng vẫn cần agent-assisted audit và HNMU/UET review; Plan 02 không thay thế thẩm quyền đó.

## 10. Rủi ro và biện pháp

| Rủi ro | Biện pháp trong/ngoài Plan 02 |
|---|---|
| Candidate cùng raw dialogue rò sang nhiều split | khóa group bằng `sample_id`; validator và downstream contract bắt buộc group split |
| Hội thoại dài bị overweight vì sinh nhiều candidate | luôn báo candidate/raw distribution; dùng family-macro/weighting ở plan sau |
| Các history lồng nhau tạo candidate gần trùng | giữ family ID qua `sample_id`; kiểm near-duplicate và sampling ở Plan 04 |
| Lượt AI sớm quá chung chung hoặc không khớp task | không sửa trong conversion; Plan 03 ghi assignment disposition và loại có truy vết |
| `gold_answer` không trực tiếp khớp một lượt scaffold sớm | giữ `answer_sgv` làm provenance answer; kiểm appropriateness ở Plan 04 |
| Correction làm thay đổi effective turn index | trace correction ID, source hash và target effective index; ID versioned theo policy |
| Nhầm pool sơ bộ với benchmark sạch | report và schema luôn gọi đây là candidate pool trước assignment/audit |

## 11. Allowed writes khi được duyệt

Plan 02 chỉ được ghi vào:

- `src/edu_benchmark/benchmark_conversion/`
- `scripts/benchmark_conversion/`
- `tests/benchmark_conversion/`
- `experiments/20260722_000940/decisions/D02-01-*`
- `experiments/20260722_000940/outputs/benchmark_conversion/multi_candidate_migration_pilot/`
- `experiments/20260722_000940/outputs/benchmark_conversion/full_v0/`
- `experiments/20260722_000940/reports/plan02-*`
- `experiments/20260722_000940/handoffs/plan02-*`
- coordination log theo chế độ append-only;
- `README.md`, `ARCHITECTURE.md` và roadmap khi component/status thay đổi.

Không sửa:

- output Plan 01;
- inherited snapshots;
- raw Excel;
- shared learning resources;
- task/rubric artifacts trong Plan 02.

## 12. Cổng hoàn thành

Plan 02 chỉ hoàn thành khi:

1. plan được người phụ trách đổi rõ sang `APPROVED`;
2. D02-01 được ghi thành decision record;
3. migration pilot đạt toàn bộ kiểm tra prefix/target/suffix;
4. full run đọc đúng 665 `pass` sample;
5. xuất đúng 2.028 candidate duy nhất theo baseline;
6. 665 raw sample có summary và candidate count đúng số lượt AI;
7. candidate/trace quan hệ 1:1 và truy vết được correction;
8. lượt HS cuối không xuất hiện trong candidate;
9. output deterministic khi chạy lại;
10. tests liên quan pass bằng `benchmark_env`;
11. report nêu rõ đây là pool trước task/rubric filtering, không phải benchmark chính thức.

## 13. Ngoài phạm vi

- Không đưa 382 `need_human_review` hoặc 3 `failed` từ phase 1 vào conversion.
- Không gán hoặc chốt task/rubric.
- Không xác nhận candidate evidence.
- Không audit chất lượng candidate.
- Không sửa `gold_response` về mặt sư phạm.
- Không chia train/dev/test trong Plan 02.
- Không chấm model.
- Không commit; người phụ trách dự án commit thủ công.

## 14. Kết quả thực thi

- Decision record: `decisions/D02-01-multi-candidate-each-tutor-turn.md`.
- Migration pilot: 20 raw dialogue, 69 candidate, 0 lỗi blocking.
- Full conversion: 665 raw dialogue, 2.028 candidate, 0 lỗi blocking.
- Candidate/trace: 2.028/2.028 ID khớp 1:1.
- Conversion disposition: 665/665 dòng có `conversion_disposition = converted`.
- Hai correction đã duyệt được tái tạo từ raw dialogue và kiểm đúng source hash.
- Chạy lại full conversion giữ nguyên SHA-256 của bốn CSV output.
- Post-write regex/structural validation: 2.028/2.028 candidate pass.
- Output được publish nguyên bundle qua staging; failure bundle không giữ candidate stale.
- Validation cuối: 89 test repository pass bằng `benchmark_env`.

Report:

- `reports/plan02-multi-candidate-migration-pilot.md`
- `reports/plan02-full-multi-candidate-conversion-summary.md`
