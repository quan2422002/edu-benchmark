# Ghi chú audit shard 02 — hnmu-dialogue-auditor

Thời điểm kiểm: `2026-07-17T23:23:33+07:00`  
Người/cơ chế kiểm: `hnmu-dialogue-auditor(worker-shard-02)`  
Phạm vi: `experiments/20260709_155523/outputs/hnmu_dialogue_audit/pilot_agent_audit/lesson_based_shards/shard_02_input_samples.csv`

## Tóm tắt phạm vi

- Số sample: 154
- Số dòng checklist chi tiết: 2772 = 154 sample × 18 tiêu chí
- Phân bố lớp: {'6': 84, '7': 70}
- Số bài học: 11
- Gợi ý quyết định cấp mẫu: {'pass': 125, 'needs_human_review': 29}
- Gợi ý review queue: 29 mẫu, phân bố priority {'medium': 28, 'high': 1}

## Output đã ghi

- `raw_dialogue_checklist_results.csv`
- `quality_check_suggestions.csv`
- `hnmu_review_queue_suggestions.csv`
- `agent_audit_notes.md`

## Cách kiểm và giới hạn

Audit dùng 18 tiêu chí: `RAW-STR-02`, `RAW-STR-03`, `RAW-STR-04`, `RAW-CON-01`–`RAW-CON-07`, `RAW-PED-01`–`RAW-PED-06`, `RAW-DUP-03`, `RAW-DUP-04`.

Evidence chính:

- `normalized_dialogue_rows.csv` cho cấu trúc, câu hỏi, đáp án, hội thoại và nhãn Bloom;
- `metadata_consistency_flags.csv` cho evidence SGK/SGV top-1 đã sinh ở Plan 04;
- retrieval SGV theo lớp + tên bài từ `shared/learning_resources/indexes/learning_resources_v0.sqlite`;
- `shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md` cho tiêu chí dàn giáo;
- `duplicate_candidates.csv` cho rủi ro trùng/gần trùng.

Giới hạn quan trọng: hầu hết SGK/SGV fragment đang ở trạng thái `draft` từ OCR/Markdown. Vì vậy các mẫu có thể `pass` ở mức kiểm sơ bộ nhưng vẫn giữ `needs_sgv_verification=true` trong `quality_check_suggestions.csv`; đây là cờ xác minh trước chuyển đổi chính thức, không tự động đồng nghĩa với loại mẫu.

## Mẫu/nhóm cần chú ý

- `HNMU-G6-R0081-STT10` được đưa vào review ưu tiên cao: câu hỏi nói về “vùng dữ liệu trên trang tính” trong khi metadata ghi `Bài 6: Mạng thông tin toàn cầu`. Có thể đây là câu ôn tập trong SGV, nhưng cần HNMU/UET xác nhận để tránh lệch bài.
- Một số mẫu hội thoại ngắn, nhãn Bloom cần xem lại hoặc AI lượt đầu gợi rất gần đáp án được đánh dấu `uncertain` ở `RAW-STR-04`, `RAW-PED-02` hoặc `RAW-DUP-04`. Đây chủ yếu là cờ review nhẹ, không phải kết luận fail.
- Nhãn Bloom được kiểm bằng rule sơ bộ theo động từ/dạng câu hỏi. Các trường hợp `RAW-CON-05=uncertain` nên do HNMU/UET quyết định nếu mẫu được chọn chuyển đổi.

## Thống kê criterion-level

- Result theo toàn bộ checklist: {'pass': 2693, 'uncertain': 79}
- `uncertain` theo criterion: {'RAW-DUP-04': 32, 'RAW-CON-05': 22, 'RAW-PED-02': 9, 'RAW-CON-04': 7, 'RAW-STR-04': 1, 'RAW-PED-04': 1, 'RAW-CON-01': 1, 'RAW-CON-02': 1, 'RAW-CON-03': 2, 'RAW-CON-06': 1, 'RAW-CON-07': 1, 'RAW-PED-06': 1}
- `fail` theo criterion: {}

## Validation

Chạy validator bắt buộc sau khi ghi file:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/shard_02/raw_dialogue_checklist_results.csv
```
