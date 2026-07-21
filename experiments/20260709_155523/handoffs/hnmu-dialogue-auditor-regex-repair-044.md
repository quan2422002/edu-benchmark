# Handoff — Repair checklist specialist sau mapping regex-only lớp 8–9

Ngày: 19/07/2026  
Mã handoff: `hnmu-dialogue-auditor-regex-repair-044`  
Specialist: `hnmu-dialogue-auditor`  
Model pin: `gpt-5.4-mini`, reasoning `medium`  
Native thread: `019f7a14-1f84-71b1-b891-a3b66b10bab1`

## 1. Mục tiêu

Repair các kết quả checklist specialist bị ảnh hưởng bởi lỗi mapping bài nhánh A/B ở dữ liệu lớp 8–9. Không chạy lại toàn bộ checklist, chỉ chạy subset 154 mẫu và 4 tiêu chí phụ thuộc evidence học liệu.

## 2. Input

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/regex_repair/affected_samples.csv
experiments/20260709_155523/reports/raw-dialogue-audit-criteria-v0.csv
experiments/20260709_155523/reports/raw-dialogue-quality-checklist-v0.md
shared/learning_resources/agent_context/README.md
```

## 3. Output

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/regex_repair/repair_raw_dialogue_checklist_results.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/regex_repair/regex_repair_notes.md
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
experiments/20260709_155523/reports/hnmu-dialogue-auditor-regex-repair-20260719.md
```

## 4. Kết quả

- Repair subset: 616 dòng = 154 mẫu × 4 tiêu chí.
- Các tiêu chí repair: `RAW-CON-01`, `RAW-CON-02`, `RAW-CON-06`, `RAW-CON-07`.
- Kết quả subset: 616 `pass`.
- Checklist đầy đủ sau merge: 10.584 dòng = 588 mẫu × 18 tiêu chí.
- Validator tổng: pass.

## 5. Lưu ý chuyển giao

Từ sau handoff này, nếu cần dùng kết quả checklist specialist lớp 8–9, dùng bản:

```text
raw_dialogue_checklist_results.regex_repaired.csv
```

Không dùng bản cũ `raw_dialogue_checklist_results.csv` làm bản chính cho các tiêu chí evidence học liệu, vì bản đó được tạo trước khi sửa mapping regex-only.
