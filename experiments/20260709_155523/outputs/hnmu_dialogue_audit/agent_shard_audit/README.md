# Agent shard audit — batch lớp 6–7

Thư mục này chứa kết quả kiểm toán ngữ nghĩa/sư phạm bằng `hnmu-dialogue-auditor` cho batch HNMU lớp 6–7.

## 0. Report snapshot

Report tổng kết liên quan đến output audit này đã được copy vào thư mục:

```text
../reports/
```

Dùng thư mục đó khi cần thu gom toàn bộ output audit mà không phải quay lại `experiments/20260709_155523/reports/`.

## 1. File hiện hành nên dùng

File checklist chi tiết mới nhất:

```text
merged/raw_dialogue_checklist_results.repaired.csv
```

Đây là bản đã sửa để mỗi mẫu có đủ 18 tiêu chí trong `checklists/raw-dialogue-audit-criteria-v0.csv`.

Kết quả xác thực:

- 462 mẫu.
- 18 tiêu chí/mẫu.
- 8.316 dòng checklist.
- Validator: pass.

## 2. File cũ không nên dùng làm kết quả cuối

Các file sau là artifact lịch sử hoặc bản trước khi repair:

- `merged/raw_dialogue_checklist_results.csv`: bản merge cũ, chỉ có 7.700 dòng; một số mẫu ở shard 01 và shard 03 thiếu tiêu chí `RAW-CON-06` và `RAW-CON-07`.
- `shard_01/raw_dialogue_checklist_results.csv`: bản shard 01 trước repair.
- `shard_03/raw_dialogue_checklist_results.csv`: bản shard 03 trước repair.

Các bản repair tương ứng:

- `shard_01/raw_dialogue_checklist_results.repaired.csv`
- `shard_03/raw_dialogue_checklist_results.repaired.csv`
- `merged/raw_dialogue_checklist_results.repaired.csv`

## 3. Các file gợi ý tổng hợp

Các file sau đã được strict-sync ngày 20/07/2026 từ `merged/raw_dialogue_checklist_results.repaired.csv`:

- `merged/quality_check_suggestions.csv`
- `merged/hnmu_review_queue_suggestions.csv`
- `merged/merge_validation_summary.json`

`merged/quality_check_suggestions.csv` là file chính ở cấp mẫu sau agent audit. File này dùng schema canonical chung với batch lớp 8–9:

```text
sample_id, source_file, source_row_number, grade, lesson, quality_decision,
confidence_score, failure_reasons, blocking_criterion_ids,
suggested_reviewer_action, needs_hnmu_review,
needs_learning_resource_review, needs_sgv_verification,
evidence_fragment_ids, checked_by, checked_at, source_shard
```

Quy tắc hiện hành:

- có tiêu chí `fail` → mẫu tổng thể là `failed`;
- không có `fail` nhưng có tiêu chí `uncertain` → mẫu tổng thể là `need_human_review`;
- toàn bộ tiêu chí là `pass` hoặc `not_applicable` → mẫu tổng thể là `pass`.

Phân bố hiện hành: 238 mẫu `pass`, 222 mẫu `need_human_review`, 2 mẫu `failed`. Nếu cần kiểm lại logic, đọc thêm `../reports/hnmu-dialogue-auditor-output-sync-20260719.md` và `merged/merge_validation_summary.json`.

## 4. Shard input

Thư mục:

```text
lesson_based_shards/
```

là snapshot kế hoạch chia shard theo bài học. Ban đầu kế hoạch này được tạo trong `../pilot_agent_audit/lesson_based_shards/`; hiện đã được copy vào đây để cấu trúc batch 6–7 nhất quán với batch 8–9.

## 5. Có thể xóa file cũ không?

Về mặt sử dụng hiện tại, các file cũ trước repair không nên dùng nữa. Tuy nhiên, nếu muốn xóa để gọn repo, nên xóa trong một bước cleanup riêng để tránh mất dấu lịch sử vì sao từng phải repair shard 01 và shard 03.
