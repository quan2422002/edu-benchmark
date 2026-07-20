# Merged agent audit notes — HNMU lớp 8–9 sau full evidence-policy sync

Ngày đồng bộ: 19/07/2026  
Trạng thái: `full_sync_from_evidence_policy_checklist`

## 1. Chính sách hiện hành

Các tiêu chí nhất quán nội dung có dùng evidence học liệu được xử lý đồng nhất:

```text
RAW-CON-01, RAW-CON-02, RAW-CON-04, RAW-CON-06, RAW-CON-07
```

Nếu dòng checklist đang `uncertain`, có `evidence_fragment_id`, không có dấu hiệu mâu thuẫn/lệch/sai rõ, và lý do chủ yếu đến từ trạng thái `draft`, thì chuyển thành `pass`. Fragment `draft` nhưng khớp metadata + nội dung được coi là evidence sơ bộ đủ dùng cho audit v0.

Các dòng vẫn giữ `uncertain` khi không có fragment, evidence yếu/mơ hồ, hoặc có vấn đề sư phạm/định dạng/trùng lặp cần review.

## 2. Bản checklist hiện hành

```text
merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Backup trước lần đồng bộ toàn diện này:

```text
merged/raw_dialogue_checklist_results.regex_repaired.pre_evidence_policy_full_sync.csv
```

## 3. Các file đã sinh lại toàn diện từ checklist

- `merged/quality_check_suggestions.csv`
- `merged/hnmu_review_queue_suggestions.csv`
- `merged/merge_validation_summary.json`

Các file này được sinh lại toàn bộ dòng/cột từ checklist hiện hành, không cập nhật từng cột riêng lẻ.

## 4. Kết quả sau đồng bộ

- Số dòng `uncertain` chuyển thành `pass` trong lần sync này: 139
- Phân bố chuyển đổi theo tiêu chí: {'RAW-CON-04': 139}
- Checklist: {'pass': 10107, 'fail': 2, 'uncertain': 475}
- Quality suggestions: {'keep': 427, 'fail': 1, 'needs_human_review': 160}
- Review queue suggestions: 161 mẫu, priority {'cao': 5, 'trung bình': 156}

## 5. Kiểm tra đồng bộ

Sau khi sinh lại, cần kiểm tra:

- mỗi sample có đúng một dòng trong `quality_check_suggestions.csv`;
- `suggested_quality_decision`, `confidence_score`, `source_checklist_rows`, các cờ review và review queue đều được suy ra từ checklist hiện hành;
- không có sample tất cả tiêu chí `pass` nhưng vẫn nằm trong review queue.
