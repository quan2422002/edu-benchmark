# Merged agent audit notes — HNMU lớp 8–9 sau comprehensive reason sync

Ngày đồng bộ: 19/07/2026  
Trạng thái: `comprehensive_reason_sync_from_regex_repaired_checklist`

## 1. Nguồn chính

File checklist chi tiết hiện hành:

```text
merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Lần đồng bộ này lấy checklist trên làm nguồn chính để tái sinh toàn diện:

- `merged/quality_check_suggestions.csv`
- `merged/hnmu_review_queue_suggestions.csv`
- `merged/merge_validation_summary.json`

## 2. Chính sách được áp dụng

- Nếu có fragment khớp metadata và nội dung, trạng thái `draft` của fragment không tự động làm tiêu chí bị `uncertain`.
- Nếu không có `evidence_fragment_id`, reason phải nói đúng là chưa truy xuất/tìm thấy fragment phù hợp, không viết nhập nhằng là do fragment `draft`.
- `main_failure_reasons` trong `quality_check_suggestions.csv` được sinh lại trực tiếp từ các dòng checklist chưa `pass`.
- `source_checklist_rows` phải khớp chính xác với các `criterion_id` chưa `pass` của từng mẫu.

## 3. Kết quả đồng bộ

- Số dòng checklist được làm sạch wording: 266
- Phân bố dòng làm sạch theo tiêu chí: {'RAW-CON-01': 98, 'RAW-CON-02': 56, 'RAW-CON-04': 56, 'RAW-CON-06': 56}
- Checklist: {'pass': 10107, 'fail': 2, 'uncertain': 475}
- Quality suggestions: {'keep': 427, 'fail': 1, 'needs_human_review': 160}
- Review queue suggestions: 161 mẫu, priority {'cao': 43, 'trung bình': 118}

## 4. Kiểm tra đồng bộ

- `sync_problem_count`: 0
- `draft_or_unconfirmed_mentions_in_quality_reasons`: 0
- `draft_or_unconfirmed_mentions_in_nonpass_checklist_without_fragment`: 0

Backup trước lần đồng bộ này có hậu tố:

```text
.pre_comprehensive_reason_sync
```
