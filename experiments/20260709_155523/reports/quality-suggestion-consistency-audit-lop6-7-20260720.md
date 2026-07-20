# Kiểm tra nhất quán tổng hợp quality suggestions — lớp 6–7

Ngày cập nhật: 20/07/2026.

## Quy tắc kiểm tra

File checklist chi tiết là nguồn chân lý. Với mỗi mẫu:

- nếu có ít nhất một tiêu chí `fail` → kết quả tổng thể phải là `failed`;
- nếu không có `fail` nhưng có ít nhất một tiêu chí `uncertain` → kết quả tổng thể phải là `need_human_review`;
- nếu toàn bộ tiêu chí là `pass` hoặc `not_applicable` → kết quả tổng thể là `pass`.

`confidence_score` tổng thể được lấy từ các tiêu chí trực tiếp kích hoạt quyết định:

- `failed`: confidence thấp nhất trong các tiêu chí `fail`;
- `need_human_review`: confidence thấp nhất trong các tiêu chí `uncertain`;
- `pass`: confidence thấp nhất trong toàn bộ tiêu chí của mẫu.

## Kết quả

- Số mẫu kiểm tra: 462
- Số mẫu mâu thuẫn decision/confidence: 0
- Phân bố kết quả hiện tại: {'need_human_review': 222, 'pass': 238, 'failed': 2}
- Phân bố kết quả kỳ vọng theo rule: {'need_human_review': 222, 'pass': 238, 'failed': 2}

## File đối chiếu

- Checklist chi tiết: `experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/raw_dialogue_checklist_results.repaired.csv`
- Kết quả tổng thể chính: `experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/quality_check_suggestions.csv`
- Bảng audit từng mẫu: `experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/quality_suggestion_consistency_audit.csv`

Không còn mâu thuẫn giữa checklist chi tiết và file tổng hợp theo rule strict hiện tại.
