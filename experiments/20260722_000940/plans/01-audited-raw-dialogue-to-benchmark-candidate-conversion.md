# Plan 01 — Contract và pilot chuyển raw dialogue thành benchmark candidate

Experiment: `20260722_000940`
Trạng thái: `COMPLETED` — được duyệt và triển khai ngày 23/07/2026; đã áp dụng hai correction sau review, Plan 02 còn blocker cho 297 trailing-`HS`
Ngày lập: 22/07/2026
Ngày sửa theo review: 23/07/2026

## 1. Lý do và vị trí của Plan 01

Mục tiêu của toàn experiment là xây dựng benchmark candidate từ 665 raw dialogue đã `pass`, sau đó đánh giá chất lượng các candidate. Không nên thực hiện toàn bộ quy trình đó trong một plan duy nhất.

Plan 01 chỉ làm ba việc:

1. Chốt contract/schema dùng chung cho conversion.
2. Viết và kiểm thử code deterministic để chọn input, tổng hợp raw-audit evidence và tách hội thoại.
3. Chạy pilot trên 40 raw mẫu `pass`, dự kiến 10 mẫu mỗi lớp 6, 7, 8, 9.

Plan 01 không chạy conversion full-scale, không gán task/rubric bằng agent và không audit chất lượng toàn bộ candidate. Plan 02–05 trong roadmap sẽ tiếp tục các phần đó sau khi pilot đạt gate.

Phạm vi môn học là Tin học THCS lớp 6–9.

## 2. Đầu vào chỉ đọc

Plan dùng snapshot trong experiment hiện tại làm input vận hành:

### Lớp 6–7

- `inherited_resources/from_20260709_155523/raw_audit_grade6_7/normalized_dialogue_rows.csv`
- `inherited_resources/from_20260709_155523/raw_audit_grade6_7/quality_check_suggestions.csv`
- `inherited_resources/from_20260709_155523/raw_audit_grade6_7/raw_dialogue_checklist_results.repaired.csv`

### Lớp 8–9

- `inherited_resources/from_20260709_155523/raw_audit_grade8_9/normalized_dialogue_rows.csv`
- `inherited_resources/from_20260709_155523/raw_audit_grade8_9/quality_check_suggestions.csv`
- `inherited_resources/from_20260709_155523/raw_audit_grade8_9/raw_dialogue_checklist_results.regex_repaired.csv`

### Schema và học liệu tham chiếu

- `inherited_resources/from_20260709_155523/checklists/benchmark-candidate-quality-checklist-v0.md`
- `shared/learning_resources/fragments/learning_resource_fragments.csv`
- `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv`
- `shared/learning_resources/agent_context/README.md`

Không sửa bất kỳ file snapshot, raw Excel hoặc tài nguyên shared nào trong plan này.

## 3. Quy ước schema cần chốt

### 3.1. Nhãn quyết định chất lượng

Mọi output đánh giá chất lượng sau này chỉ dùng:

- `pass`
- `need_human_review`
- `failed`

Plan 01 chưa tạo `candidate_quality_decision`, vì candidate chưa qua Plan 04. Không ghi giá trị rỗng vào một cột quyết định chưa được chấm; cột này chỉ được thêm trong output audit candidate.

### 3.2. `gold_answer` và `gold_response`

- `gold_answer`: đáp án chuyên môn lấy từ `answer_sgv`.
- `gold_response`: lượt phản hồi gia sư mục tiêu cần chấm.
- Hai trường không được trộn vào nhau.

Trong pilot, dùng `split_strategy = final_tutor_response`: lượt AI cuối là `gold_response`; các lượt nằm trước nó được phân bổ vào `student_prompt` và `conversation_history`.

### 3.3. Evidence theo đúng semantics của phase 1

Căn cứ đối chiếu:

- `experiments/20260709_155523/plans/04-hnmu-dialogue-intake-coverage-consistency-dedup.md`: xác định checklist chi tiết và bảng gợi ý cấp mẫu là hai output khác nhau của raw-dialogue audit.
- `experiments/20260709_155523/plans/07-hnmu-dialogue-auditor-specialist.md` mục 6.1–6.2: định nghĩa `raw_dialogue_checklist_results.csv` ở cấp tiêu chí với cột số ít `evidence_fragment_id`.
- `experiments/20260709_155523/reports/raw-dialogue-quality-checklist-v0.md` mục 3.1, 3.2 và 11: định nghĩa bảng chi tiết là nguồn sự thật, bảng cấp mẫu dùng `blocking_criterion_ids` và `evidence_fragment_ids` cho tiêu chí chặn.
- `experiments/20260709_155523/reports/hnmu-dialogue-auditor-output-sync-20260719.md` mục 3: chốt rule strict `fail` → `failed`, `uncertain` → `need_human_review`, còn lại → `pass`.
- Hai báo cáo batch lớp 6–7 và lớp 8–9: xác nhận các file repaired/regex-repaired và `quality_check_suggestions.csv` là bộ output hiện hành.

Phase 1 có hai cột khác nhau:

#### `evidence_fragment_id` trong checklist chi tiết

Hai file checklist chi tiết có cột số ít `evidence_fragment_id`. Mỗi dòng là một cặp `sample_id + criterion_id`, nên cột này ghi fragment mà agent dùng cho riêng tiêu chí đó.

- Cột có thể khác rỗng ở dòng `pass`, `uncertain` hoặc `fail`.
- Một raw sample `pass` vẫn có thể có nhiều dòng checklist chứa fragment.
- Cột này không phải quyết định cấp mẫu và không tuân theo quy tắc “mẫu pass thì rỗng”.

#### `evidence_fragment_ids` trong `quality_check_suggestions.csv`

File cấp mẫu có cột số nhiều `evidence_fragment_ids`. Cột này chỉ tổng hợp fragment thuộc các tiêu chí trực tiếp kích hoạt quyết định:

- nếu có tiêu chí `fail`, lấy fragment từ các dòng `fail`;
- nếu không có `fail` nhưng có `uncertain`, lấy fragment từ các dòng `uncertain`;
- nếu toàn bộ tiêu chí `pass`/`not_applicable`, không có dòng chặn nên để rỗng.

Quy tắc rỗng:


| `quality_decision`  | Khi`evidence_fragment_ids` khác rỗng                     | Khi`evidence_fragment_ids` rỗng                                                                                                                                                              |
| ------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pass`              | Không xảy ra theo rule phase 1                           | Luôn rỗng vì không có tiêu chí chặn                                                                                                                                                   |
| `need_human_review` | Ít nhất một dòng`uncertain` có `evidence_fragment_id` | Các dòng`uncertain` không viện dẫn fragment; nguyên nhân có thể là không tìm thấy fragment hoặc tiêu chí chặn thuộc cấu trúc, trùng lặp, mức nhận thức hay sư phạm |
| `failed`            | Ít nhất một dòng`fail` có `evidence_fragment_id`      | Các dòng`fail` không viện dẫn fragment                                                                                                                                                   |

Kết quả thực tế:


| Batch     | `pass` khác rỗng | `need_human_review` khác rỗng | `failed` khác rỗng |
| --------- | -----------------: | ------------------------------: | -------------------: |
| Lớp 6–7 |              0/238 |                         175/222 |                  1/2 |
| Lớp 8–9 |              0/427 |                           2/160 |                  1/1 |

#### Hai trường dẫn xuất của Plan 01

Để không đổi nghĩa cột phase 1, `conversion_input_pass_samples.csv` dùng hai tên có prefix:

- `raw_audit_blocking_evidence_fragment_ids`: bản chuẩn hóa dạng JSON-list từ `quality_check_suggestions.evidence_fragment_ids`. Vì Plan 01 chỉ lấy raw sample `pass`, cả 665 dòng hiện tại phải là `[]`.
- `raw_audit_all_evidence_fragment_ids`: union của mọi `evidence_fragment_id` không rỗng trong 18 dòng checklist chi tiết; loại trùng, sắp xếp ổn định và ghi dạng JSON-list. Cả 665 raw sample `pass` hiện tại phải khác rỗng.

Nếu một raw sample `pass` không có `raw_audit_all_evidence_fragment_ids`, input validation ghi lỗi và không chọn mẫu đó vào pilot.

Plan 01 không định nghĩa hoặc ghi evidence cấp benchmark candidate. Tên và rule của candidate-level evidence sẽ được chốt trong Plan 04; không tái sử dụng cột `evidence_fragment_ids` của phase 1 với một ý nghĩa mới.

### 3.4. Tên file candidate

Tên file luôn là `benchmark_candidate_splits.csv`.

- Plan 01 ghi pilot tại `outputs/benchmark_conversion/pilot_v0/benchmark_candidate_splits.csv`.
- Plan 02 sẽ ghi full batch tại `outputs/benchmark_conversion/full_v0/benchmark_candidate_splits.csv`.

### 3.5. Correction sau review của người phụ trách dự án

Không sửa snapshot kế thừa hoặc raw Excel. Hai quyết định sửa vai trò được lưu tại:

`outputs/benchmark_conversion/dialogue_corrections.csv`

Mỗi correction có `sample_id`, thao tác theo turn index, SHA-256 của dialogue gốc, nguồn quyết định và lý do. Schema conversion giữ:

- `raw_dialogue`: nguyên văn từ snapshot;
- `conversion_dialogue`: bản hiệu lực sau correction để parser sử dụng;
- `dialogue_correction_ids`: JSON-list ID correction, bằng `[]` nếu không sửa.

Pipeline fail closed nếu hash nguồn không khớp hoặc correction không tạo được chuỗi vai trò hợp lệ.

## 4. Cách chọn 40 mẫu pilot

Code chọn pilot deterministic, không chọn tay và không dùng agent:

1. Lọc đúng `quality_decision = pass`.
2. Chọn 10 mẫu mỗi lớp.
3. Trong từng lớp, ưu tiên phủ ba mức nhận thức `Biết`, `Hiểu`, `Vận dụng`.
4. Phủ ba nhóm độ dài hội thoại theo số lượt đã parse: `4–6`, `7–9`, `>=10`.
5. Có cả mẫu một fragment và nhiều fragment raw-audit evidence nếu dữ liệu lớp đó cho phép.
6. Phân tán theo bài học; không lấy quá hai mẫu cùng một bài nếu vẫn còn bài khác đủ điều kiện.
7. Khi nhiều mẫu cùng điều kiện, sắp xếp theo `sample_id` và lấy theo thứ tự để kết quả tái lập.

Nếu không đủ một strata, code phải ghi fallback vào `pilot_selection_summary.json`, không tự thay đổi kích thước pilot hoặc chọn ngẫu nhiên.

## 5. Thay đổi code cụ thể

### 5.1. Package dùng chung

Tạo các file dưới `src/edu_benchmark/benchmark_conversion/`:

#### `schema.py`

Chứa:

- hằng số tên cột cho conversion input và candidate split;
- contract cho `raw_audit_blocking_evidence_fragment_ids` và `raw_audit_all_evidence_fragment_ids`;
- contract `gold_answer`/`gold_response`;
- hàm `validate_conversion_input_row(...)`;
- hàm `validate_candidate_split_row(...)`;
- kiểm tra JSON-list fields và các bất biến của raw-audit evidence.

#### `input_selection.py`

Chứa:

- `load_audit_snapshot(...)`: đọc normalized rows, quality rows và checklist chi tiết;
- `aggregate_all_raw_audit_evidence(...)`: tạo union fragment ID từ checklist chi tiết theo `sample_id`;
- `normalize_blocking_evidence(...)`: chuẩn hóa cột cấp mẫu của phase 1 thành JSON-list;
- `build_pass_conversion_input(...)`: join ba nguồn, lọc `pass`, kiểm uniqueness và truy vết;
- `select_conversion_pilot(...)`: chọn 40 mẫu theo quy tắc tại mục 4.

Module phải phát hiện:

- sample ID thiếu hoặc trùng;
- raw sample có mặt ở một bảng nhưng thiếu ở bảng khác;
- decision ngoài `pass`, `need_human_review`, `failed`;
- raw mẫu `pass` thiếu trường lõi hoặc thiếu raw-audit fragment;
- checklist không đủ 18 tiêu chí cho một mẫu.

#### `dialogue_split.py`

Chứa:

- `parse_dialogue_turns(...)`: parse nhãn `HS:` và `AI:` thành danh sách lượt có thứ tự;
- `split_final_tutor_response_candidate(...)`: tạo một candidate từ lượt AI cuối;
- kiểm tra lượt đầu là HS, lượt cuối là AI và vai trò xen kẽ hợp lệ;
- tạo `student_prompt`, `conversation_history`, `gold_response`;
- giữ nguyên `raw_dialogue` để audit và không sửa nội dung lượt nói.

#### `pipeline.py`

Chứa:

- `run_conversion_input_build(...)`;
- `run_conversion_pilot(...)`;
- điều phối đọc input, validation, pilot selection, dialogue split và ghi output;
- không chứa logic task/rubric hoặc candidate-quality audit.

### 5.2. CLI

Tạo dưới `scripts/benchmark_conversion/`:

#### `build_conversion_input.py`

Nhiệm vụ:

- đọc hai batch snapshot;
- tạo bảng 665 raw mẫu pass đã join;
- tạo `input_validation_errors.csv`;
- không tách hội thoại.

#### `run_conversion_pilot.py`

Nhiệm vụ:

- đọc conversion input hợp lệ;
- chọn 40 mẫu;
- chạy `final_tutor_response`;
- ghi candidate splits, trace, split errors và selection summary.

CLI phải cho phép override đường dẫn bằng argument nhưng default phải trỏ đúng experiment `20260722_000940`.

### 5.3. Tests

Tạo dưới `tests/benchmark_conversion/`:

- `test_schema.py`
- `test_input_selection.py`
- `test_dialogue_split.py`
- `test_conversion_pipeline.py`

Test tối thiểu:

1. `raw_audit_all_evidence_fragment_ids` loại trùng và có thứ tự ổn định.
2. `raw_audit_blocking_evidence_fragment_ids` giữ đúng semantics của cột cấp mẫu phase 1.
3. Join thiếu/duplicate sample bị fail.
4. Nhãn ngoài canonical bị reject.
5. `gold_answer` lấy đúng từ `answer_sgv`.
6. Parser giữ nguyên nội dung và thứ tự lượt.
7. Final AI response được tách đúng.
8. Hội thoại sai nhãn/thứ tự đi vào split errors, không bị sửa ngầm.
9. Raw sample `pass` có blocking evidence khác rỗng bị validator gắn cờ không nhất quán với rule phase 1.
10. Raw sample `pass` thiếu all-evidence bị đưa vào `input_validation_errors.csv`.
11. Pilot có đúng 40 mẫu và 10 mẫu mỗi lớp.
12. Hai lần chạy cùng input tạo cùng sample IDs và output candidate.

## 6. Output của Plan 01

### Toàn bộ input pass

`outputs/benchmark_conversion/`

- `conversion_input_pass_samples.csv` — 665 raw mẫu pass sau join và evidence aggregation.
- `input_validation_errors.csv` — lỗi input; rỗng nếu gate đạt.
- `dialogue_corrections.csv` — correction overlay do người phụ trách dự án duyệt, không phải bản sao/sửa trực tiếp dữ liệu gốc.
- `last_student_turn_analysis.csv` và `last_student_turn_analysis_summary.json` — phân tích heuristic 297 lượt `HS` cuối để chuẩn bị decision Plan 02.

### Pilot

`outputs/benchmark_conversion/pilot_v0/`

- `pilot_sample_ids.csv`
- `benchmark_candidate_splits.csv`
- `conversion_trace.csv`
- `dialogue_split_errors.csv`
- `pilot_selection_summary.json`

### Báo cáo và handoff

- `reports/plan01-benchmark-conversion-pilot-summary.md`
- `handoffs/plan01-benchmark-conversion-pilot.md`
- coordination event append-only theo template của repository.

## 7. Allowed writes

Plan 01 chỉ được ghi vào:

- `src/edu_benchmark/benchmark_conversion/`
- `scripts/benchmark_conversion/`
- `tests/benchmark_conversion/`
- `experiments/20260722_000940/outputs/benchmark_conversion/`
- `experiments/20260722_000940/reports/plan01-*`
- `experiments/20260722_000940/handoffs/plan01-*`
- coordination logs append-only của experiment hiện tại;
- `README.md` và `ARCHITECTURE.md` chỉ khi implementation làm thay đổi onboarding hoặc component status.

Không sửa `inherited_resources/`, experiment cha, raw data hoặc shared learning resources.

## 8. Trình tự triển khai

1. Tạo schema và unit tests cho field semantics.
2. Cài đặt join/filter/evidence aggregation và test.
3. Chạy build input trên hai batch; yêu cầu đúng 665 mẫu pass và zero validation error trước khi tiếp tục.
4. Cài đặt parser/splitter và test bằng fixtures nhỏ.
5. Cài đặt deterministic pilot selection.
6. Chạy pilot 40 mẫu.
7. Kiểm output schema, trace và lỗi split.
8. Viết báo cáo pilot; không tự chạy full batch.

## 9. Cổng hoàn thành Plan 01

Plan chỉ hoàn thành khi:

1. `conversion_input_pass_samples.csv` có đúng 665 `sample_id` duy nhất.
2. Cả 665 dòng có `raw_audit_blocking_evidence_fragment_ids = []`.
3. Cả 665 dòng có `raw_audit_all_evidence_fragment_ids` khác rỗng.
4. `input_validation_errors.csv` không có lỗi blocking.
5. Pilot có đúng 40 raw samples, 10 mẫu mỗi lớp.
6. Mỗi candidate truy vết được về raw sample, file và dòng nguồn.
7. Candidate hợp lệ có `gold_answer`, `student_prompt`, `conversation_history`, `gold_response`.
8. Plan 01 không ghi cột evidence cấp candidate với tên hoặc semantics mới.
9. Lỗi split không bị sửa ngầm; mọi lỗi nằm trong `dialogue_split_errors.csv`.
10. Toàn bộ test liên quan pass bằng `benchmark_env`.
11. Báo cáo chỉ rõ blocker và đề xuất có cho Plan 02 chạy full-scale hay không.

## 10. Lệnh validation dự kiến

Chỉ dùng project interpreter:

```bash
PYTHONPATH=src /home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/benchmark_conversion/build_conversion_input.py

PYTHONPATH=src /home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/benchmark_conversion/run_conversion_pilot.py \
  --pilot-size-per-grade 10 \
  --split-strategy final_tutor_response

/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest \
  tests/benchmark_conversion -q
```

## 11. Ngoài phạm vi

- Không chạy conversion toàn bộ 665 mẫu thành candidate.
- Không gán task/rubric.
- Không mở rộng coverage matrix.
- Không chạy benchmark-candidate quality audit đầy đủ.
- Không chọn benchmark pilot cuối cùng cho HNMU/UET.
- Không chấm model.
- Không commit; người phụ trách dự án sẽ commit thủ công sau khi roadmap và plan được chốt.
