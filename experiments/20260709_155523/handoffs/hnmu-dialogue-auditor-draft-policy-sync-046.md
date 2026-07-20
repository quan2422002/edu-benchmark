# Handoff — Cập nhật chính sách xử lý fragment draft

Ngày: 19/07/2026  
Mã handoff: `hnmu-dialogue-auditor-draft-policy-sync-046`

## 1. Nội dung

Theo quyết định của Quân, fragment học liệu `draft` nhưng khớp đúng metadata + nội dung được xử lý tương tự evidence dùng được ở mức sơ bộ. Không tự động đưa mẫu vào review và không cần cờ “evidence chưa xác nhận cuối”.

## 2. Output đã cập nhật

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/quality_check_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/hnmu_review_queue_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/merge_validation_summary.json
```

## 3. Kết quả

- 560 dòng checklist chuyển từ `uncertain` sang `pass`.
- `keep` tăng lên 288 mẫu.
- specialist review queue còn 300 mẫu.

## 4. Backup

Bản trước chính sách mới được giữ tại:

```text
raw_dialogue_checklist_results.regex_repaired.pre_draft_policy.csv
```


## Kết quả validation sau cập nhật

Python executable đã dùng:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Đã kiểm tra:

- checklist đủ 10.584 dòng = 588 mẫu × 18 tiêu chí;
- validator checklist: `OK`;
- `pytest tests/agents tests/dialogue_audit -q`: 39 passed.
