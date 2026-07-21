# Plan 04 — Tiếp nhận, kiểm tra độ phủ, nhất quán và trùng lặp hội thoại HNMU

Experiment: `20260709_155523`
Trạng thái: `HOÀN THÀNH V0` — đã kiểm toán batch lớp 6–7; đã có lượt follow-up riêng cho lớp 8–9, không ghi đè output cũ; đã chuẩn hóa rule tổng hợp agent audit từ checklist chi tiết sang kết quả cấp mẫu.
Ngày lập: 09/07/2026
Ngày cập nhật: 20/07/2026
Người phụ trách dự kiến: Quân, Nguyên, Codex hỗ trợ kỹ thuật.

## 1. Bối cảnh

HNMU đã bắt đầu chuyển giao dữ liệu hội thoại thô. Batch ban đầu hiện nằm ở:

```text
shared/raw_data/HNMU-teacher_dialog_samples/
  Lớp 6.xlsx
  Lớp 7.xlsx
  Lớp 8.xlsx  # đã xử lý trong lượt follow-up riêng ngày 19/07/2026
  Lớp 9.xlsx  # đã xử lý trong lượt follow-up riêng ngày 19/07/2026
```

Vòng audit code v0 ngày 17/07/2026 đã xử lý 462 dòng lớp 6–7: 460 mẫu qua được kiểm cơ học ban đầu, 2 mẫu có lỗi rõ cần review, 0 cặp trùng/gần trùng ứng viên. Sau đó specialist audit theo checklist 18 tiêu chí/mẫu được repair và strict-sync ngày 20/07/2026: 238 mẫu `pass`, 222 mẫu `need_human_review`, 2 mẫu `failed`. Lượt follow-up ngày 19/07/2026 đã xử lý thêm 588 dòng lớp 8–9 trong output riêng, gồm kiểm cơ học, 3-shard specialist audit và repair checklist specialist cho 154 mẫu từng bị ảnh hưởng bởi lỗi mapping bài nhánh A/B. Đây là kiểm toán cơ học/truy xuất/agent-assisted sơ bộ, chưa thay thế review chuyên môn HNMU/UET.

Dữ liệu có dùng AI hỗ trợ tạo và được thầy cô rà soát. Vì vậy cần kiểm toán trước khi chuyển đổi thành mẫu benchmark.

Plan này chỉ nên triển khai sau khi:

- Plan 01 có checklist kiểm định v0; khi chạy Plan 04, checklist vận hành là `experiments/20260709_155523/reports/raw-dialogue-quality-checklist-v0.md`;
- Plan 02 chốt cách quản lý raw data, manifest và code dùng chung;
- Plan 03 có ít nhất danh mục học liệu SGK/SGV v0 để kiểm độ phủ. Với các trục chủ đề/bài học, dữ liệu HNMU chỉ được dùng như input cần ánh xạ; nguồn chuẩn là registry SGK/SGV. Nếu chưa ánh xạ được, gắn cờ `unmapped`/`needs_learning_resource_review`, không lấy cột `Bài` hoặc `Vị trí` trong dữ liệu HNMU làm chuẩn.

## 2. Mục tiêu

Phạm vi output chính ban đầu: lớp 6 và lớp 7. Sau khi dữ liệu/học liệu lớp 8–9 được bổ sung, đã chạy một lượt follow-up riêng cho lớp 8 và lớp 9 tại `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/`. Không ghi đè output chính lớp 6–7.

Kiểm tra dữ liệu hội thoại HNMU theo năm nhóm:

1. Độ phủ: khối lớp, chủ đề, bài học, mức nhận thức, dạng câu hỏi/bài tập, hành vi gia sư.
2. Thiếu trường và lỗi định dạng: cột bắt buộc, format hội thoại, dòng trống, giá trị bất thường.
3. Tính nhất quán: hội thoại có khớp với metadata đi kèm không.
4. Trùng/gần trùng: phát hiện mẫu lặp hoặc quá giống nhau.
5. Chất lượng từng mẫu: checklist + điểm tự tin (`confidence_score`) + hàng đợi gửi HNMU kiểm lại.

## 3. Nguyên tắc lưu trữ

- Raw data HNMU đặt ở `shared/raw_data/HNMU-teacher_dialog_samples/`.
- Code kiểm toán đặt ở `src/edu_benchmark/dialogue_audit/`.
- Code đọc dữ liệu đặt ở `src/edu_benchmark/data_io/`.
- Kết quả chạy của experiment này đặt ở `experiments/20260709_155523/outputs/hnmu_dialogue_audit/` và báo cáo đặt ở `experiments/20260709_155523/reports/`.
- Không đặt raw data hoặc code dùng chung trong `experiments/20260709_155523/`.
- Không sửa nội dung hội thoại gốc.
- Tài nguyên phục vụ agent kiểm toán được gom theo kiểu “hub chỉ dẫn” tại `shared/learning_resources/agent_context/README.md`. Hub này không sao chép dữ liệu nguồn, mà trỏ tới fragment, SQLite index, checklist, mô tả phương pháp giàn giáo và công cụ truy xuất cần dùng.

## 4. Output dự kiến và lý do tạo

### 4.1. `shared/raw_data/HNMU-teacher_dialog_samples/manifest.csv`

Vai trò: đăng ký file gốc HNMU gửi theo từng batch.
Lý do tạo: cần biết mỗi batch có bao nhiêu mẫu, nguồn nào, ngày nhận nào, trạng thái ra sao.

### 4.2. `src/edu_benchmark/dialogue_audit/`

Vai trò: chứa code kiểm toán dữ liệu hội thoại.
Lý do tạo: code này sẽ được dùng lại ở nhiều experiment, không nên để trong thư mục experiment.

### 4.3. `experiments/20260709_155523/reports/hnmu-dialogue-audit-batch-YYYYMMDD.md`

Vai trò: báo cáo kết quả kiểm toán batch dữ liệu.
Lý do tạo: báo cáo là output của experiment, có thể gửi Quân/giáo sư/HNMU đọc.

### 4.4. Các bảng kết quả chạy

Các bảng dự kiến:

- `outputs/hnmu_dialogue_audit/coverage_summary.csv`
- `outputs/hnmu_dialogue_audit/missing_field_report.csv`
- `outputs/hnmu_dialogue_audit/metadata_consistency_flags.csv`
- `outputs/hnmu_dialogue_audit/duplicate_candidates.csv`
- `outputs/hnmu_dialogue_audit/raw_dialogue_checklist_results.csv`
- `outputs/hnmu_dialogue_audit/quality_check_results.csv`
- `outputs/hnmu_dialogue_audit/agent_shard_audit/merged/quality_check_suggestions.csv`
- `outputs/hnmu_dialogue_audit/hnmu_review_queue.csv`

Trong đó:

- `raw_dialogue_checklist_results.csv` là bảng chấm chi tiết theo từng tiêu chí cho từng mẫu, dùng để truy vết vì sao mẫu đạt/trượt/chưa chắc.
- `quality_check_results.csv` là kết quả nhanh từ code kiểm cơ học/truy xuất sơ bộ ở cấp từng mẫu. File này hữu ích để nhìn nhanh lỗi thiếu trường, lỗi định dạng hoặc truy xuất v0, nhưng không phải file review chính sau agent audit.
- `agent_shard_audit/merged/quality_check_suggestions.csv` là file chính ở cấp từng mẫu sau agent audit. File này phải được tổng hợp từ checklist chi tiết `raw_dialogue_checklist_results*.csv`, dùng schema canonical và cột `quality_decision` với ba nhãn `pass`, `need_human_review`, `failed`.
- `hnmu_review_queue.csv` là danh sách mẫu cần gửi lại HNMU kiểm tra, kèm lý do, mức nghiêm trọng và điểm tự tin.

## 5. Quy trình thực hiện

1. Nhận batch dữ liệu HNMU và lưu nguyên bản vào `shared/raw_data/HNMU-teacher_dialog_samples/`.
2. Tạo manifest cho batch.
3. Đọc dữ liệu thành bảng trung gian, không sửa nội dung hội thoại.
4. Kiểm tra thiếu trường và lỗi định dạng bằng code.
5. Kiểm tra độ phủ bằng cách ánh xạ dữ liệu HNMU sang danh mục học liệu SGK/SGV v0. Trục chủ đề lấy từ SGK/SGV; trục bài học luôn kèm lớp. Các trường `Bài`, `Vị trí`, `Mức Bloom` trong dữ liệu HNMU là dữ liệu cần kiểm/đối chiếu, không phải nguồn chuẩn của học liệu.
6. Lọc trùng/gần trùng bằng code.
7. Agent kiểm nhất quán ngữ nghĩa theo `raw-dialogue-quality-checklist-v0.md` và evidence học liệu truy xuất từ Markdown index của Plan 03 nếu đã có. Markdown học liệu phải là bản đã qua tái dựng bố cục từ OCR có bbox, không dùng text thuần làm evidence chính cho bảng/mục lục.
8. Agent ghi bảng `raw_dialogue_checklist_results.csv` ở dạng một dòng cho mỗi cặp `sample_id` + `criterion_id`, để lưu kết quả từng tiêu chí trước khi tổng hợp.
9. Gán `quality_decision`, `confidence_score`, `failure_reasons`, `blocking_criterion_ids`, `suggested_reviewer_action` trong `agent_shard_audit/merged/quality_check_suggestions.csv` bằng rule strict từ checklist chi tiết. Checklist chi tiết là nguồn chân lý; output tổng hợp có thể tạo lại bằng `scripts/dialogue_audit/sync_quality_suggestions_from_checklist.py`.
10. Sinh báo cáo cho UET/HNMU.
11. Chốt batch nào đủ điều kiện chuyển sang Plan 06.

## 6. Phân vai giữa code, agent và con người

### 6.1. Code kiểm các phần cơ học

- Thiếu trường bắt buộc.
- Số dòng, số mẫu theo lớp/bài/mức Bloom.
- Hội thoại có chứa nhãn lượt nói như `HS:` và `AI:` hay không.
- Dòng trống hoặc nội dung quá ngắn.
- Trùng/gần trùng ở mức văn bản.
- Phân bố độ phủ theo các cột đã có.

### 6.2. Agent kiểm các phần ngữ nghĩa

- Câu hỏi có khớp với `Bài` và `Vị trí` không.
- `Đáp án (SGV)` có trả lời đúng câu hỏi không.
- Hội thoại có bám câu hỏi và đáp án không.
- `Mức Bloom` có hợp lý với yêu cầu của câu hỏi không.
- Hội thoại có thể hiện phương pháp giàn giáo không.
- Gia sư có lộ đáp án quá sớm không.
- Có lượt hội thoại thừa hoặc thiếu giá trị sư phạm không.
- Có tình huống agent không đủ chắc và cần HNMU xác nhận không.

Khi kiểm nhất quán với học liệu, agent không đọc toàn bộ thư mục Markdown. Agent phải dùng retrieval contract từ Plan 03, tối thiểu:

```text
resolve_learning_resource(metadata)
search_learning_fragments(query, filters)
get_learning_fragment(fragment_id)
```

Kết quả kiểm ngữ nghĩa nên lưu thêm:

```text
evidence_fragment_id
evidence_anchor
evidence_markdown_path
evidence_source_image
evidence_layout_status
evidence_status
evidence_match_reason
```

Ngoài kết luận tổng hợp theo mẫu, agent phải ghi bảng checklist chi tiết dạng dài vào `raw_dialogue_checklist_results.csv`. Mỗi dòng là một cặp `sample_id` + `criterion_id`, không phải một mẫu với hàng chục cột. Các cột tối thiểu:

```text
sample_id
criterion_id
criterion_group
criterion_name
result
confidence_score
evidence_fragment_id
evidence_source
evidence_match_reason
reason
suggested_reviewer_action
checked_by
checked_at
```

`result` dùng một trong bốn giá trị: `pass`, `fail`, `uncertain`, `not_applicable`. Nếu cần hiển thị cho người đọc, có thể quy ước `pass = o`, `fail = x`, nhưng trong CSV nên dùng giá trị chữ để tránh nhập nhằng.

Nếu học liệu truy xuất có fragment `draft` nhưng khớp đúng metadata và nội dung, mẫu được xử lý như evidence dùng được ở mức sơ bộ và không tự động bị đưa vào review. Chỉ gắn `needs_learning_resource_review` khi không tìm được evidence phù hợp, evidence mơ hồ, hoặc có dấu hiệu lệch/mâu thuẫn.

Với các mẫu phụ thuộc vào bảng, mục lục hoặc đáp án SGV dạng bảng, agent phải ưu tiên evidence từ Markdown đã giữ được cấu trúc bảng. Nếu chỉ có text thuần hoặc bảng bị mất cấu trúc, kết quả kiểm chỉ là sơ bộ.

Khi chưa có SGV crawl/OCR/Markdown index, các kiểm tra liên quan đến `Đáp án (SGV)` cần thận trọng. Nếu đã có fragment SGV/SGK khớp metadata + nội dung thì không tự động gắn `needs_sgv_verification`; chỉ gắn cờ khi thiếu, mơ hồ hoặc mâu thuẫn evidence.

### 6.3. Ngữ cảnh tập trung cho agent kiểm toán

Trước khi chạy agent kiểm ngữ nghĩa, orchestrator phải cung cấp cho agent hub ngữ cảnh:

```text
shared/learning_resources/agent_context/README.md
```

Hub này giúp agent biết rõ:

- dữ liệu gốc HNMU nằm ở đâu và không được sửa trực tiếp;
- checklist kiểm dữ liệu thô `raw-dialogue-quality-checklist-v0.md` nằm ở đâu;
- fragment học liệu và SQLite index nào được dùng để tìm evidence;
- hàm/công cụ truy xuất nào nên gọi trước;
- khi nào phải gắn cờ `needs_learning_resource_review`, `needs_sgv_verification` hoặc đưa vào hàng đợi HNMU kiểm lại.

Cách làm này cố ý không “gom” tất cả file nguồn vào một thư mục mới, vì như vậy dễ tạo bản sao lệch nhau. Thay vào đó, `agent_context/` đóng vai trò bản đồ điều hướng tới nguồn chính thống.

### 6.4. Khả năng tạo specialist riêng cho kiểm toán hội thoại

Plan 04 nên cân nhắc tạo một specialist/skill riêng, ví dụ `hnmu-dialogue-auditor`, nếu việc kiểm toán dữ liệu HNMU trở thành quy trình lặp lại theo nhiều batch.

Nhiệm vụ đề xuất của specialist này:

- kiểm độ chính xác và tính nhất quán giữa câu hỏi, đáp án, bài học, vị trí, hội thoại và evidence học liệu;
- dùng `raw-dialogue-quality-checklist-v0.md` và retrieval học liệu từ Plan 03;
- kiểm dấu hiệu dàn giáo dựa trên bản Markdown chuẩn hóa `shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md`; khi cần đối chiếu tuyệt đối thì quay lại tài liệu gốc HNMU `KhungDanGiao_HoiThoaiMinhHoa.docx`; bản `scaffolding_function_notes.md` chỉ là ghi chú lịch sử/rút gọn;
- xuất `quality_decision`, `confidence_score`, `failure_reasons`, `evidence_fragment_id`, `suggested_reviewer_action`;
- tạo hàng đợi mẫu cần HNMU/UET xác nhận.

Ranh giới bắt buộc:

- không sửa dữ liệu thô;
- không thay HNMU quyết định chuyên môn;
- không tự coi fragment `draft` là xác nhận chuyên môn cuối cùng, nhưng cũng không tự động coi `draft` là lý do review nếu metadata + nội dung đã khớp;
- không chạy nhiều specialist cùng loại trên cùng một batch nếu chưa có phân mảnh input và kế hoạch merge rõ ràng.

### 6.5. HNMU/UET quyết định

- Mẫu nào giữ.
- Mẫu nào cần HNMU sửa hoặc xác nhận.
- Mẫu nào loại khỏi batch hiện tại.
- Mẫu nào đủ điều kiện chuyển sang Plan 06.

## 7. Quy tắc điểm tự tin

Mỗi mẫu nên có các trường dẫn xuất:

```text
quality_decision: pass / need_human_review / failed
confidence_score: 0.00–1.00
failure_reasons: danh sách lý do
suggested_reviewer_action: keep / ask_hnmu_review / exclude_from_current_batch
needs_sgv_verification: true / false
needs_learning_resource_review: true / false
```

Nguyên tắc:

- `pass`: chỉ dùng khi toàn bộ tiêu chí trong `raw_dialogue_checklist_results.csv` của mẫu là `pass` hoặc `not_applicable`.
- `failed`: dùng khi có ít nhất một tiêu chí `fail`, ví dụ thiếu hội thoại, câu hỏi không khớp đáp án, hội thoại lệch hoàn toàn.
- `need_human_review`: dùng khi không có tiêu chí `fail` nhưng có ít nhất một tiêu chí `uncertain`, ví dụ rủi ro ngữ nghĩa, evidence chưa chắc, hoặc cần HNMU xác nhận.

`confidence_score` tổng hợp là độ tin cậy của quyết định tổng thể, không phải điểm chất lượng của mẫu:

- nếu quyết định là `failed`: lấy confidence thấp nhất trong các tiêu chí `fail`;
- nếu quyết định là `need_human_review`: lấy confidence thấp nhất trong các tiêu chí `uncertain`;
- nếu quyết định là `pass`: lấy confidence thấp nhất trong toàn bộ tiêu chí của mẫu.

Mọi mẫu `failed` hoặc `need_human_review` phải xuất hiện trong hàng đợi HNMU/UET xem lại.

## 8. Tiêu chí hoàn thành

Plan hoàn thành khi có:

1. Ít nhất một batch thật được đăng ký bằng manifest.
2. Code audit chạy được bằng `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.
3. Báo cáo độ phủ/thiếu trường/nhất quán/trùng lặp cho batch đầu tiên.
4. Bảng `raw_dialogue_checklist_results.csv` có kết quả từng tiêu chí cho từng mẫu, gồm `sample_id`, `criterion_id`, `result`, `confidence_score`, evidence và lý do.
5. Bảng `agent_shard_audit/merged/quality_check_suggestions.csv` có schema canonical, gồm `quality_decision`, `confidence_score`, `failure_reasons`, `blocking_criterion_ids` và các cờ review tổng hợp theo mẫu.
6. Bảng kết quả có evidence học liệu nếu Markdown index của Plan 03 đã sẵn sàng.
7. Danh sách `hnmu_review_queue.csv` để gửi lại HNMU.
8. Handoff nêu rõ dữ liệu nào đủ điều kiện chuyển đổi thử sang Plan 06.

## 9. Ngoài phạm vi

- Không tạo benchmark samples hoàn chỉnh; việc đó thuộc Plan 06.
- Không chấm model.
- Không sửa nội dung hội thoại gốc.
- Không xây database học liệu production.


## Agent audit theo 3 shard bài học

Sau khi Plan 07 đã tạo specialist `hnmu-dialogue-auditor` và pilot nhỏ cho thấy output schema chạy được, phần kiểm ngữ nghĩa/sư phạm rộng hơn của Plan 04 sẽ chạy theo 3 shard bài học.

### Lý do chia theo bài học

- Mỗi sub-agent làm việc trong một cụm học liệu tương đối liền mạch.
- Không chia một bài học cho nhiều agent, tránh kết luận lệch nhau do ngữ cảnh khác nhau.
- Dễ truy vết lỗi về bài/chủ đề khi báo cáo lại cho HNMU/UET.

### Shard input

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/pilot_agent_audit/lesson_based_shards/
```

Các file input:

- `shard_01_input_samples.csv`;
- `shard_02_input_samples.csv`;
- `shard_03_input_samples.csv`;
- `lesson_based_shard_plan.csv`.

### Output riêng từng sub-agent

Mỗi sub-agent chỉ được ghi trong thư mục riêng:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/shard_01/
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/shard_02/
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/shard_03/
```

Mỗi shard phải tạo đủ:

- `raw_dialogue_checklist_results.csv`;
- `quality_check_suggestions.csv`;
- `hnmu_review_queue_suggestions.csv`;
- `agent_audit_notes.md`.

### Quy tắc merge

Orchestrator chỉ merge sau khi:

1. validator schema pass cho từng `raw_dialogue_checklist_results.csv`;
2. kiểm tra không có `sample_id` bị trùng giữa shard;
3. các cột giữ nguyên theo `csv_column_dictionary.md`;
4. đồng bộ lại `quality_check_suggestions.csv` và `hnmu_review_queue_suggestions.csv` từ checklist chi tiết bằng rule strict;
5. báo cáo rõ giới hạn của agent audit và các nhóm lỗi phổ biến.

Output merge phải nằm trong `agent_shard_audit/merged/`. Sau khi Quân duyệt dùng `quality_check_suggestions.csv` làm file review chính ở cấp mẫu, chuẩn hóa schema bằng:

```bash
PYTHONPATH=src /home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/dialogue_audit/sync_quality_suggestions_from_checklist.py \
  --checklist path/to/raw_dialogue_checklist_results.csv \
  --quality-template path/to/quality_check_suggestions.csv \
  --review-template path/to/hnmu_review_queue_suggestions.csv \
  --output-quality path/to/quality_check_suggestions.csv \
  --output-review-queue path/to/hnmu_review_queue_suggestions.csv \
  --decision-column quality_decision \
  --pass-label pass \
  --normalized-rows path/to/normalized_dialogue_rows.csv \
  --canonical-quality-schema
```


## 9. Follow-up lớp 8–9 ngày 19/07/2026

Lượt follow-up này xử lý `Lớp 8.xlsx` và `Lớp 9.xlsx` sau khi raw manifest và học liệu SGK/SGV lớp 8–9 đã được bổ sung.

Output riêng:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/
```

Báo cáo tổng thể:

```text
experiments/20260709_155523/reports/hnmu-dialogue-audit-batch-grade8-9-20260719.md
```

Tóm tắt:

- 588 dòng hội thoại lớp 8–9.
- 20 issue thiếu trường/định dạng.
- 1 cặp trùng chính xác về câu hỏi.
- Sau regex-only lesson mapping: 0 mẫu `Không rõ chủ đề`.
- Sau regex-only lesson mapping: 3 mẫu trong review queue cơ học.
- Agent audit chia 3 shard theo bài học, mỗi shard 196 mẫu.
- File checklist merged có 10.584 dòng, tương ứng 588 mẫu × 18 tiêu chí/mẫu, validator pass.

Điểm cần xử lý tiếp:

- Không dùng fuzzy matching trong ánh xạ bài học; chỉ dùng regex lấy `số bài + hậu tố A/B nếu có`.
- Lớp 8–9 đã có output tổng hợp strict-sync từ checklist chi tiết và đã được chuẩn hóa schema ngày 20/07/2026: 427 mẫu `pass`, 160 mẫu `need_human_review`, 1 mẫu `failed`; không còn mâu thuẫn giữa checklist chi tiết và file tổng hợp.
- Khi dùng cho Plan 06, ưu tiên file `agent_shard_audit/merged/quality_check_suggestions.csv` đã chuẩn hóa; không dùng nhãn legacy `keep`.
- Soi thủ công mẫu lỗi định dạng, mẫu trùng và các mẫu có dấu hiệu dàn giáo chưa chắc.
