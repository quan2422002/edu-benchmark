# Handoff — Đồng bộ output specialist lớp 8–9 sau regex repair

Ngày: 19/07/2026  
Mã handoff: `hnmu-dialogue-auditor-output-sync-045`

## 1. Mục tiêu

Đồng bộ các file gợi ý/tổng hợp trong thư mục output lớp 8–9 với bản checklist specialist đã repair:

```text
raw_dialogue_checklist_results.regex_repaired.csv
```

## 2. File đã cập nhật

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/quality_check_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/hnmu_review_queue_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/merge_validation_summary.json
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/agent_audit_notes.md
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/README.md
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/reports/hnmu-dialogue-audit-batch-grade8-9-20260719.md
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/reports/bao-cao-gui-hnmu-ket-qua-ra-soat-du-lieu-hoi-thoai-lop-6-9-20260719.md
```

## 3. Backup/truy vết

Các file suggestion/note cũ trong `merged/`, nếu đã tồn tại trước đồng bộ, được giữ bằng hậu tố `.pre_regex_repair`.

## 4. Kết quả

- `quality_check_suggestions.csv`: 588 dòng; 233 `keep`, 354 `needs_human_review`, 1 `fail`.
- `hnmu_review_queue_suggestions.csv`: 355 dòng; 350 priority `trung bình`, 5 priority `cao`.
- File snapshot report trong output đã được đồng bộ để không còn trình bày 154 mẫu là lỗi hiện tại.

## 5. Lưu ý

Root `hnmu_review_queue.csv` và specialist `hnmu_review_queue_suggestions.csv` có vai trò khác nhau:

- root `hnmu_review_queue.csv`: hàng đợi cơ học sau rerun regex-only, còn 3 mẫu;
- specialist `hnmu_review_queue_suggestions.csv`: hàng đợi rà sâu theo checklist specialist, còn 355 mẫu do tính cả `uncertain`.
