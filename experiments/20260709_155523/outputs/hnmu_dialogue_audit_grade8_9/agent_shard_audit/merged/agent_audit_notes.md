# Merged agent audit notes — HNMU lớp 8–9 sau comprehensive sync

Ngày đồng bộ: 19/07/2026  
Trạng thái: `comprehensive_missing_fragment_reason_sync_from_regex_repaired_checklist`

## 1. Nguồn chính

```text
merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Các file được tái sinh toàn diện từ checklist hiện hành:

- `merged/quality_check_suggestions.csv`
- `merged/hnmu_review_queue_suggestions.csv`
- `merged/merge_validation_summary.json`

## 2. Nguyên tắc đồng bộ

- `main_failure_reasons` được ghép trực tiếp từ tất cả dòng checklist chưa `pass` của từng mẫu.
- `source_checklist_rows` khớp chính xác với các `criterion_id` chưa `pass`.
- Mẫu `keep` không nằm trong review queue; mẫu `fail` hoặc `needs_human_review` nằm trong review queue.
- Nếu `evidence_fragment_id` trống, reason ghi rõ là chưa truy xuất được fragment phù hợp, không diễn đạt thành vấn đề do trạng thái `draft`.
- Nếu fragment `draft` nhưng khớp metadata và nội dung, trạng thái `draft` không tự động làm tiêu chí bị `uncertain`.

## 3. Kết quả

- Số dòng checklist được làm sạch reason thiếu fragment ở lượt cuối: 140
- Phân bố theo tiêu chí: {'RAW-CON-07': 98, 'RAW-CON-06': 42}
- Checklist: {'pass': 10107, 'fail': 2, 'uncertain': 475}
- Quality suggestions: {'keep': 427, 'fail': 1, 'needs_human_review': 160}
- Review queue suggestions: 161 mẫu, priority {'cao': 43, 'trung bình': 118}
- `sync_problem_count`: 0
- `draft_or_unconfirmed_mentions_in_quality_reasons`: 0
- `draft_or_unconfirmed_mentions_in_nonpass_checklist`: 0

Backup trước các lượt sync có hậu tố:

```text
.pre_comprehensive_reason_sync
.pre_missing_fragment_reason_sync
```
