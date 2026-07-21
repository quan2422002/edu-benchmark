# Handoff — Full sync chính sách evidence lớp 8–9

Ngày: 19/07/2026  
Mã handoff: `hnmu-dialogue-auditor-full-evidence-policy-sync-047`

## 1. Nội dung

Đã rà lại toàn bộ nhóm tiêu chí evidence-related, gồm:

```text
RAW-CON-01
RAW-CON-02
RAW-CON-04
RAW-CON-06
RAW-CON-07
```

Lần sync này bổ sung `RAW-CON-04`, vốn bị bỏ sót ở lượt chính sách `draft-as-keep` trước đó.

## 2. Output đã cập nhật

```text
raw_dialogue_checklist_results.regex_repaired.csv
quality_check_suggestions.csv
hnmu_review_queue_suggestions.csv
merge_validation_summary.json
agent_audit_notes.md
```

Tất cả nằm trong:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/
```

## 3. Kết quả

- Chuyển thêm 139 dòng `RAW-CON-04` từ `uncertain` sang `pass`.
- Checklist sau sync: `pass=10107`, `uncertain=475`, `fail=2`.
- Quality suggestions sau sync: `keep=427`, `needs_human_review=160`, `fail=1`.
- Review queue specialist sau sync: 161 mẫu.
- Mẫu `HNMU-G8-R0010-STT9` hiện là `keep` và không còn nằm trong review queue.

## 4. Validation

- Sync problems: 0.
- Validator checklist: OK.
- `pytest tests/agents tests/dialogue_audit -q`: 39 passed.
