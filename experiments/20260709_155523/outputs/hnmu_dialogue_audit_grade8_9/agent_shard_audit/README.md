# Agent shard audit — batch lớp 8–9

Thư mục này chứa kết quả kiểm toán ngữ nghĩa/sư phạm bằng `hnmu-dialogue-auditor` cho batch HNMU lớp 8–9.

## 0. Report snapshot

Report tổng kết liên quan đến output audit này được copy vào thư mục:

```text
../reports/
```

Dùng thư mục đó khi cần thu gom toàn bộ output audit mà không phải quay lại `experiments/20260709_155523/reports/`.

## 1. File hiện hành nên dùng

File checklist chi tiết mới nhất:

```text
merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Kết quả xác thực:

- 588 mẫu.
- 18 tiêu chí/mẫu.
- 10.584 dòng checklist.
- Validator: pass.

File cũ dưới đây được giữ để truy vết trước repair/chính sách draft-as-keep, không nên dùng làm bản chính:

```text
merged/raw_dialogue_checklist_results.csv
```

Lý do có bản repair: sau lượt sharded audit ban đầu, mapper bài học lớp 8–9 đã được sửa bằng regex-only để nhận diện bài nhánh A/B, ví dụ `[8b]`, `Bài 8b`, `10a`. Vì vậy, 154 mẫu từng bị ảnh hưởng đã được repair ở 4 tiêu chí evidence: `RAW-CON-01`, `RAW-CON-02`, `RAW-CON-06`, `RAW-CON-07`.

## 2. Shard input

Thư mục:

```text
lesson_based_shards/
```

lưu kế hoạch chia 588 mẫu thành 3 shard theo bài học:

- `shard_01`: 196 mẫu, lớp 8.
- `shard_02`: 196 mẫu, lớp 8 + lớp 9.
- `shard_03`: 196 mẫu, lớp 9.

## 3. Các file gợi ý tổng hợp đã đồng bộ

Các file dưới đây đã được tạo lại từ `merged/raw_dialogue_checklist_results.regex_repaired.csv`:

- `merged/quality_check_suggestions.csv`
- `merged/hnmu_review_queue_suggestions.csv`
- `merged/merge_validation_summary.json`
- `merged/agent_audit_notes.md`

Các bản trước repair/chính sách mới, nếu tồn tại, được giữ bằng hậu tố `.pre_regex_repair` hoặc `.pre_draft_policy` để truy vết.

`merged/quality_check_suggestions.csv` là file chính ở cấp mẫu sau agent audit. File này đã được chuẩn hóa ngày 20/07/2026 để dùng cùng schema canonical với batch lớp 6–7:

```text
sample_id, source_file, source_row_number, grade, lesson, quality_decision,
confidence_score, failure_reasons, blocking_criterion_ids,
suggested_reviewer_action, needs_hnmu_review,
needs_learning_resource_review, needs_sgv_verification,
evidence_fragment_ids, checked_by, checked_at, source_shard
```

Quy tắc tổng hợp hiện tại:

- có bất kỳ tiêu chí `fail` → `quality_decision = failed`;
- không có `fail` nhưng có `uncertain` → `quality_decision = need_human_review`;
- tất cả tiêu chí đều `pass` hoặc `not_applicable` → `quality_decision = pass`.

Đây là gợi ý vận hành để rà soát, không thay thế phán quyết chuyên môn của HNMU/UET.

## 4. Chính sách `draft` hiện hành

Toàn bộ fragment học liệu hiện vẫn có `status = draft`. Từ cập nhật ngày 19/07/2026, `draft` không tự động làm mẫu bị review nếu fragment đã khớp đúng metadata và nội dung. Các file suggestion hiện hành đã được đồng bộ lại theo chính sách này.
