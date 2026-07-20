# Checklist snapshot cho lượt kiểm toán dữ liệu thô HNMU

Thư mục này chứa bản copy/snapshot của các file checklist đã được dùng để đánh giá dữ liệu hội thoại thô trong output audit tương ứng.

## 1. File trong thư mục này

- `raw-dialogue-quality-checklist-v0.md`: bản checklist diễn giải đầy đủ. File này có cả tiêu chí cấp batch, tiêu chí cấp từng mẫu, quy tắc tổng hợp và điều kiện chuyển sang Plan 06.
- `raw-dialogue-audit-criteria-v0.csv`: registry vận hành cho agent. File này chỉ chứa các tiêu chí bắt buộc ở cấp từng mẫu mà agent phải chấm, mỗi mẫu đúng một dòng cho mỗi `criterion_id`.

Nói ngắn gọn: file Markdown giải thích toàn bộ logic kiểm toán; file CSV là danh sách tiêu chí per-sample mà agent phải tạo output chi tiết.

## 2. Vì sao hai file không có cùng số tiêu chí?

`raw-dialogue-quality-checklist-v0.md` rộng hơn vì nó bao gồm nhiều lớp kiểm toán:

1. Tiêu chí cấp batch: kiểm phân bố, độ phủ, trùng lặp toàn batch, trạng thái quy trình.
2. Tiêu chí cấp từng mẫu do code kiểm được: thiếu trường, nhãn lượt nói, hội thoại quá ngắn, truy vết.
3. Tiêu chí cấp từng mẫu cần agent kiểm: nhất quán nội dung, dàn giáo, mức nhận thức, nguy cơ bịa học liệu, khuôn hội thoại lặp.
4. Quy tắc tổng hợp: cách đi từ kết quả chi tiết sang `quality_decision`, `confidence_score`, review queue.

`raw-dialogue-audit-criteria-v0.csv` hẹp hơn vì nó chỉ là registry 18 tiêu chí bắt buộc để agent chấm từng mẫu. Nó không chứa các tiêu chí chỉ có ý nghĩa ở cấp batch, ví dụ độ phủ theo lớp/chủ đề/bài học.

## 3. Tiêu chí được thể hiện ở file kết quả nào?

| Nhóm tiêu chí trong checklist Markdown | Mức kiểm | File kết quả chính | Ghi chú |
| --- | --- | --- | --- |
| `RAW-COV-01` đến `RAW-COV-06` — độ phủ lớp, chủ đề, bài học, mức nhận thức, dạng bài, phân bố có chủ đích | Batch | `../coverage_summary.csv` và phần nhận xét trong report batch | Đây là thống kê toàn batch, không phải output từng mẫu của agent. |
| `RAW-STR-01` — đủ cột bắt buộc ở cấp file/batch | Batch/file | `../missing_field_report.csv` | Nếu thiếu cột lõi ở cả file thì đây là lỗi cấp batch. |
| `RAW-STR-02` đến `RAW-STR-04` — thiếu trường lõi, nhãn lượt nói, hội thoại đủ dài | Từng mẫu | `../missing_field_report.csv`; nếu có agent audit thì xem thêm file checklist chi tiết trong `../agent_shard_audit/` | Code phát hiện lỗi cơ học; agent có thể diễn giải thêm khi cần. |
| `RAW-STR-05` — truy vết dòng gốc | Từng mẫu/batch | `../normalized_dialogue_rows.csv` | Dùng để đối chiếu `sample_id`, file gốc, lớp, bài, dòng nguồn. |
| `RAW-STR-06` — không sửa raw data | Quy trình | `shared/raw_data/HNMU-teacher_dialog_samples/README.md`; `shared/raw_data/HNMU-teacher_dialog_samples/manifest.csv`; `../normalized_dialogue_rows.csv`; report/handoff cụ thể ở phần 8 của README này | Đây là ràng buộc quy trình, không phải tiêu chí agent chấm từng mẫu. |
| `RAW-CON-01` đến `RAW-CON-07` — nhất quán câu hỏi, bài học, đáp án SGV, hội thoại, metadata, học liệu | Từng mẫu | `../metadata_consistency_flags.csv`; nếu có agent audit thì xem `raw_dialogue_checklist_results*.csv` trong `../agent_shard_audit/merged/` | `metadata_consistency_flags.csv` là kiểm truy xuất sơ bộ; agent checklist là diễn giải theo từng tiêu chí. |
| `RAW-PED-01` đến `RAW-PED-06` — dàn giáo và chất lượng sư phạm hội thoại thô | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results*.csv` | Đây là phần cần agent/người kiểm; code không tự kết luận chắc chắn được. |
| `RAW-DUP-01`, `RAW-DUP-02` — trùng/gần trùng bằng so khớp văn bản | Batch/cụm mẫu | `../duplicate_candidates.csv` | Code phát hiện ứng viên trùng/gần trùng. |
| `RAW-DUP-03`, `RAW-DUP-04` — biến thể tầm thường, khuôn AI lặp lại | Từng mẫu + batch context | `../agent_shard_audit/merged/raw_dialogue_checklist_results*.csv`; tham chiếu `../duplicate_candidates.csv` nếu có | Agent dùng kết quả code và ngữ cảnh batch để nhận xét. |
| Quyết định tổng hợp chính `quality_decision`, `confidence_score`, `failure_reasons`, `blocking_criterion_ids`, `suggested_reviewer_action` | Từng mẫu | `../agent_shard_audit/merged/quality_check_suggestions.csv` | Đây là file review chính ở cấp mẫu sau agent audit, được tổng hợp từ checklist chi tiết. `../quality_check_results.csv` chỉ là kết quả nhanh từ code kiểm cơ học/truy xuất sơ bộ. |
| Hàng đợi HNMU/UET xem lại | Từng mẫu | `../hnmu_review_queue.csv`; nếu có agent audit thì xem thêm `../agent_shard_audit/merged/hnmu_review_queue_suggestions.csv` | Dùng để gom các mẫu cần hỏi lại HNMU/UET. |

## 4. File nào là quan trọng nhất khi đối chiếu từng mẫu?

Nếu muốn xem từng mẫu được agent đánh giá thế nào, ưu tiên mở file checklist chi tiết trong `../agent_shard_audit/merged/`:

- Mỗi dòng là một cặp `sample_id` + `criterion_id`.
- Mỗi mẫu phải có đủ 18 `criterion_id` trong `raw-dialogue-audit-criteria-v0.csv`.
- `result` chỉ dùng một trong bốn giá trị: `pass`, `fail`, `uncertain`, `not_applicable`.
- `evidence_fragment_id`, `evidence_source`, `evidence_match_reason` cho biết agent dựa vào học liệu nào, nếu có.

Nếu muốn xem toàn batch có phủ đều/đủ không, mở `../coverage_summary.csv` trước.

Nếu muốn xem mẫu nào cần gửi HNMU/UET sau agent audit, mở `../agent_shard_audit/merged/hnmu_review_queue_suggestions.csv`. File `../hnmu_review_queue.csv` chỉ phản ánh hàng đợi nhanh từ code kiểm cơ học/truy xuất sơ bộ.

## 5. Quy tắc tổng hợp hiện hành từ checklist chi tiết

Với output agent audit, `raw_dialogue_checklist_results*.csv` là nguồn chân lý. File `quality_check_suggestions.csv` phải được đồng bộ từ checklist chi tiết theo rule strict:

- có ít nhất một tiêu chí `fail` → mẫu tổng thể là `failed`;
- không có `fail` nhưng có ít nhất một tiêu chí `uncertain` → mẫu tổng thể là `need_human_review`;
- toàn bộ tiêu chí là `pass` hoặc `not_applicable` → mẫu tổng thể là `pass`.

`confidence_score` tổng thể là độ tin cậy của quyết định tổng thể:

- `failed`: lấy confidence thấp nhất trong các tiêu chí `fail`;
- `need_human_review`: lấy confidence thấp nhất trong các tiêu chí `uncertain`;
- `pass`: lấy confidence thấp nhất trong toàn bộ tiêu chí của mẫu.

Mọi mẫu `failed` hoặc `need_human_review` phải có mặt trong `hnmu_review_queue_suggestions.csv`.

## 6. Quy ước snapshot

- Đây là snapshot để thu gom, đối chiếu và truy vết cùng output audit.
- Bản canonical vẫn nằm trong `experiments/20260709_155523/reports/`.
- Nếu checklist canonical thay đổi trong tương lai, cần tạo snapshot mới trong output của lượt audit mới, không sửa ngầm snapshot cũ.

## 7. Ghi chú riêng cho output lớp 8–9

Trong lượt lớp 8–9, cả 3 shard đã dùng đủ 18 tiêu chí trong `raw-dialogue-audit-criteria-v0.csv`. Sau các bước debug/sync, file merged chính hiện hành là:

```text
../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Validator đã xác nhận file này có đủ 588 mẫu × 18 tiêu chí = 10.584 dòng. File `raw_dialogue_checklist_results.csv` cũ chỉ nên xem như bản trung gian để truy vết, không dùng làm kết quả tổng thể mới nhất.

Sau strict-sync, các file tổng hợp hiện hành là:

```text
../agent_shard_audit/merged/quality_check_suggestions.csv
../agent_shard_audit/merged/hnmu_review_queue_suggestions.csv
../agent_shard_audit/merged/merge_validation_summary.json
```

Phân bố kết quả tổng hợp hiện tại trong `quality_check_suggestions.csv`: 427 mẫu `pass`, 160 mẫu `need_human_review`, 1 mẫu `failed`. File này dùng schema canonical gồm cột `quality_decision`; nhãn legacy `keep` đã được chuẩn hóa thành `pass`. File `quality_suggestion_consistency_audit.csv` xác nhận không còn mâu thuẫn giữa checklist chi tiết và bảng tổng hợp.

## 8. File cụ thể cho `RAW-STR-06` ở batch lớp 8–9

Để truy vết tiêu chí “không sửa raw data”, đối chiếu các file cụ thể sau:

- `shared/raw_data/HNMU-teacher_dialog_samples/README.md`: quy ước không sửa Excel gốc.
- `shared/raw_data/HNMU-teacher_dialog_samples/manifest.csv`: đăng ký file raw gốc và trạng thái batch.
- `../normalized_dialogue_rows.csv`: bản dẫn xuất do code đọc từ Excel, không phải file raw đã bị sửa.
- `experiments/20260709_155523/reports/hnmu-dialogue-audit-batch-grade8-9-20260719.md`: report batch lớp 8–9.
- `experiments/20260709_155523/handoffs/hnmu-dialogue-auditor-grade8-9-sharded-run-040.md`: handoff lượt 3-shard agent audit lớp 8–9.

Nếu cần kiểm tuyệt đối, so sánh lại file Excel gốc trong `shared/raw_data/HNMU-teacher_dialog_samples/` với `../normalized_dialogue_rows.csv` bằng code đọc Excel, không chỉnh trực tiếp Excel.
