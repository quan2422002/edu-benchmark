# Báo cáo cập nhật chính sách xử lý fragment `draft` — lớp 8–9

Ngày cập nhật: 19/07/2026  
Trạng thái: `completed_draft_fragment_as_keep_policy`

## 1. Quyết định

Nếu fragment học liệu có `status = draft` nhưng đã khớp đúng metadata và nội dung cần kiểm, trạng thái `draft` không tự động làm tiêu chí bị `uncertain`, không tự động bật cờ review, và không tự động làm mẫu rơi khỏi nhóm `keep`.

Chỉ giữ `uncertain`/review khi có một trong các tình huống thật sự cần xem lại:

- không tìm thấy fragment phù hợp;
- evidence thiếu, mơ hồ hoặc yếu;
- có dấu hiệu lệch/mâu thuẫn/sai nội dung;
- lỗi định dạng hội thoại;
- nguy cơ trùng lặp;
- vấn đề sư phạm cần HNMU/UET xác nhận.

## 2. File đã cập nhật

Checklist hiện hành:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Các file gợi ý đã đồng bộ lại:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/quality_check_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/hnmu_review_queue_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/merge_validation_summary.json
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/agent_audit_notes.md
```

Backup trước cập nhật chính sách:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.pre_draft_policy.csv
```

## 3. Kết quả

- Số dòng `uncertain` chuyển thành `pass`: 560.
- Phân bố chuyển đổi:
  - `RAW-CON-01`: 154
  - `RAW-CON-02`: 98
  - `RAW-CON-06`: 154
  - `RAW-CON-07`: 154
- Checklist sau cập nhật:
  - `pass`: 9.968
  - `uncertain`: 614
  - `fail`: 2
- `quality_check_suggestions.csv` sau cập nhật:
  - `keep`: 427
  - `needs_human_review`: 160
  - `fail`: 1
- `hnmu_review_queue_suggestions.csv` sau cập nhật: 161 mẫu.

## 4. Tài liệu/skill đã cập nhật

Đã cập nhật chính sách trong:

- `agents/hnmu-dialogue-auditor/SKILL.md`
- `agents/hnmu-dialogue-auditor/references/raw-dialogue-audit-workflow.md`
- `agents/hnmu-dialogue-auditor/references/raw-dialogue-audit-output-schema.md`
- `experiments/20260709_155523/reports/raw-dialogue-quality-checklist-v0.md`
- `experiments/20260709_155523/plans/04-hnmu-dialogue-intake-coverage-consistency-dedup.md`
- `shared/learning_resources/agent_context/README.md`

## 5. Validation

Python executable dùng để chạy validation:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Validator/test được chạy ở bước sau khi cập nhật.


## Kết quả validation sau cập nhật

Python executable đã dùng:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Đã kiểm tra:

- checklist đủ 10.584 dòng = 588 mẫu × 18 tiêu chí;
- validator checklist: `OK`;
- `pytest tests/agents tests/dialogue_audit -q`: 39 passed.


## Cập nhật full evidence-policy sync

Sau khi phát hiện `RAW-CON-04` cũng có cùng mẫu lý do `uncertain` do fragment `draft`, đã thực hiện full sync cho nhóm `RAW-CON-01`, `RAW-CON-02`, `RAW-CON-04`, `RAW-CON-06`, `RAW-CON-07`. Kết quả hiện hành: `keep=427`, `needs_human_review=160`, `fail=1`; review queue specialist còn 161 mẫu.
