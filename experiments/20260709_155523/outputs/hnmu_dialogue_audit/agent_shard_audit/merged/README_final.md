# Merged specialist audit final — batch lớp 6–7

Đây là tầng kết quả chính sau khi đã repair checklist và đồng bộ quyết định tổng thể cho 462 mẫu lớp 6–7.

## File final trong thư mục này

- `raw_dialogue_checklist_results.repaired.csv`: file chi tiết nhất. Mỗi dòng là một cặp mẫu + tiêu chí. Có 462 mẫu × 18 tiêu chí = 8.316 dòng.
- `quality_check_suggestions.csv`: file cấp mẫu chính để review. Có 462 dòng, dùng `quality_decision` với ba nhãn `pass`, `need_human_review`, `failed`.
- `hnmu_review_queue_suggestions.csv`: danh sách 224 mẫu cần HNMU/UET xem lại, được lấy từ các mẫu `need_human_review` hoặc `failed`.
- `merge_validation_summary.json`: metadata lượt đồng bộ, nguồn checklist, quy tắc tổng hợp, số dòng và môi trường Python.

## Quy tắc đọc nhanh

Nếu cần trả lời “mẫu này có nên dùng tiếp không?”, mở `quality_check_suggestions.csv`.

Nếu cần trả lời “vì sao mẫu này bị đánh dấu như vậy?”, mở `raw_dialogue_checklist_results.repaired.csv` và lọc theo `sample_id`.
