# Checklist final — batch lớp 8–9

File này chỉ mô tả cách các checklist được nối với gói kết quả chính hiện tại, không tính file/thư mục bị `.gitignore`.

## File checklist trong thư mục này

- `raw-dialogue-quality-checklist-v0.md`: checklist diễn giải đầy đủ, gồm cả tiêu chí cấp batch và tiêu chí cấp từng mẫu.
- `raw-dialogue-audit-criteria-v0.csv`: registry 18 tiêu chí bắt buộc ở cấp từng mẫu mà specialist agent phải chấm.

## Tiêu chí và file kết quả chính

| Mã tiêu chí | Nội dung kiểm | Mức kiểm | File kết quả chính |
| --- | --- | --- | --- |
| `RAW-COV-01` | Phủ khối lớp | Batch | `../coverage_summary.csv` với `dimension = grade` |
| `RAW-COV-02` | Phủ chủ đề SGK/SGV | Batch | `../coverage_summary.csv` với `dimension = topic` |
| `RAW-COV-03` | Phủ bài học theo lớp | Batch | `../coverage_summary.csv` với `dimension = lesson_by_grade` |
| `RAW-COV-04` | Phủ mức nhận thức | Batch | `../coverage_summary.csv` với `dimension = bloom_band` |
| `RAW-COV-05` | Phủ dạng câu hỏi/bài tập | Batch | Chưa có file final riêng trong gói kết quả hiện tại. `coverage_summary.csv` chưa có trục `question_type`, nên không dùng nó để thay thế tiêu chí này. |
| `RAW-COV-06` | Phân bố có chủ đích, không bắt buộc đều tuyệt đối | Batch + nhận xét | `../coverage_summary.csv`; diễn giải trong `../reports/bao-cao-gui-hnmu-ket-qua-ra-soat-du-lieu-hoi-thoai-lop-6-9-20260719.md` và `../reports/hnmu-dialogue-audit-batch-grade8-9-20260719.md` |
| `RAW-STR-01` | Có đủ cột bắt buộc ở cấp file/batch | Batch/file | `../missing_field_report.csv` |
| `RAW-STR-02` | Không thiếu trường lõi | Từng mẫu | `../missing_field_report.csv`; `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-STR-03` | Có nhãn lượt nói | Từng mẫu | `../missing_field_report.csv`; `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-STR-04` | Hội thoại đủ dài để kiểm | Từng mẫu | `../missing_field_report.csv`; `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-STR-05` | Có truy vết dòng gốc | Từng mẫu/batch | `../normalized_dialogue_rows.csv` |
| `RAW-STR-06` | Không sửa dữ liệu thô | Quy trình | `../normalized_dialogue_rows.csv`; `shared/raw_data/HNMU-teacher_dialog_samples/README.md`; `shared/raw_data/HNMU-teacher_dialog_samples/manifest.csv`; `../reports/hnmu-dialogue-audit-batch-grade8-9-20260719.md` |
| `RAW-CON-01` | Câu hỏi khớp bài/vị trí | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-CON-02` | Đáp án SGV khớp câu hỏi | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-CON-03` | Hội thoại bám câu hỏi | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-CON-04` | Hội thoại bám đáp án | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-CON-05` | Mức nhận thức hợp lý | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-CON-06` | Không bịa học liệu | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-CON-07` | Nhất quán metadata | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-PED-01` | Có dấu hiệu dàn giáo | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-PED-02` | Không lộ đáp án quá sớm | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-PED-03` | Trình tự hội thoại hợp lý | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-PED-04` | Lượt nói có giá trị | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-PED-05` | Phù hợp lứa tuổi | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-PED-06` | Không thay thế bằng câu trả lời lạc hướng | Từng mẫu | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv` |
| `RAW-DUP-01` | Trùng chính xác | Batch/cụm mẫu | `../duplicate_candidates.csv` |
| `RAW-DUP-02` | Gần trùng | Batch/cụm mẫu | `../duplicate_candidates.csv` |
| `RAW-DUP-03` | Biến thể tầm thường | Từng mẫu + ngữ cảnh batch | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv`; tham chiếu `../duplicate_candidates.csv` nếu có |
| `RAW-DUP-04` | Khuôn AI lặp lại | Từng mẫu + ngữ cảnh batch | `../agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv`; tham chiếu `../duplicate_candidates.csv` nếu có |
| Không phải mã tiêu chí riêng | Kết luận tổng thể từng mẫu | Từng mẫu | `../agent_shard_audit/merged/quality_check_suggestions.csv` |
| Không phải mã tiêu chí riêng | Hàng đợi HNMU/UET xem lại | Từng mẫu | `../agent_shard_audit/merged/hnmu_review_queue_suggestions.csv` |
| Không phải mã tiêu chí riêng | Metadata lượt đồng bộ | Batch/run | `../agent_shard_audit/merged/merge_validation_summary.json` |

## Quy tắc tổng hợp final

`quality_check_suggestions.csv` được tổng hợp từ `raw_dialogue_checklist_results.regex_repaired.csv`:

- có ít nhất một tiêu chí `fail` → `failed`;
- không có `fail` nhưng có ít nhất một tiêu chí `uncertain` → `need_human_review`;
- toàn bộ tiêu chí là `pass` hoặc `not_applicable` → `pass`.

`confidence_score` cấp mẫu là độ tin cậy của quyết định tổng thể, không phải điểm chất lượng của mẫu.
