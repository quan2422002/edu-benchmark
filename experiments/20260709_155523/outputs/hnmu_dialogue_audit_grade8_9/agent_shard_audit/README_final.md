# Specialist audit final — batch lớp 8–9

Thư mục này chứa kết quả chính sau specialist audit cho batch lớp 8–9. File này chỉ mô tả phần output không bị `.gitignore` loại.

## Thư mục chính

- `merged/`: nơi chứa toàn bộ kết quả final đã regex-repair và đồng bộ. Xem `merged/README_final.md`.

## File cần dùng khi review

- Cấp mẫu: `merged/quality_check_suggestions.csv`.
- Cấp tiêu chí: `merged/raw_dialogue_checklist_results.regex_repaired.csv`.
- Hàng đợi review: `merged/hnmu_review_queue_suggestions.csv`.
- Metadata đồng bộ: `merged/merge_validation_summary.json`.
- Ghi chú tổng hợp: `merged/agent_audit_notes.md`.

## Ghi chú

Các thư mục shard riêng, regex-repair intermediate và backup `.pre_*` không thuộc gói kết quả chính. Chúng có thể còn trên máy để truy vết lịch sử, nhưng không dùng khi review kết quả final.
