# Báo cáo full sync chính sách evidence cho checklist specialist lớp 8–9

Ngày cập nhật: 19/07/2026  
Trạng thái: `completed_and_validated_full_sync_from_evidence_policy_checklist`

## 1. Lý do

Sau khi kiểm tra mẫu `HNMU-G8-R0010-STT9`, phát hiện chính sách `draft-as-keep` trước đó mới áp dụng cho `RAW-CON-01`, `RAW-CON-02`, `RAW-CON-06`, `RAW-CON-07`, nhưng chưa áp dụng cho `RAW-CON-04` dù tiêu chí này cũng có cùng kiểu lý do: hội thoại có xu hướng bám đáp án, nhưng fragment chỉ là `draft`.

Vì vậy đã thực hiện lại full sync theo nhóm tiêu chí evidence-related:

```text
RAW-CON-01
RAW-CON-02
RAW-CON-04
RAW-CON-06
RAW-CON-07
```

## 2. Nguyên tắc

Chỉ chuyển `uncertain` thành `pass` khi:

- tiêu chí thuộc nhóm trên;
- có `evidence_fragment_id`;
- không có dấu hiệu mâu thuẫn/lệch/sai/không khớp rõ trong reason/evidence;
- lý do `uncertain` chủ yếu đến từ trạng thái `draft` hoặc chưa xác nhận cuối.

Các dòng không có fragment hoặc evidence yếu/mơ hồ vẫn giữ `uncertain`.

## 3. Kết quả lần full sync này

- Chuyển thêm 139 dòng `RAW-CON-04` từ `uncertain` sang `pass`.
- Các dòng evidence-related còn `uncertain` đều do thiếu fragment phù hợp trong rule hiện tại.
- Checklist sau full sync:
  - `pass`: 10.107
  - `uncertain`: 475
  - `fail`: 2
- `quality_check_suggestions.csv` sau full sync:
  - `keep`: 427
  - `needs_human_review`: 160
  - `fail`: 1
- `hnmu_review_queue_suggestions.csv` sau full sync: 161 mẫu.

## 4. Đồng bộ toàn diện

Các file sau được sinh lại toàn bộ từ checklist hiện hành, không cập nhật từng cột riêng lẻ:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/quality_check_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/hnmu_review_queue_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/merge_validation_summary.json
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/agent_audit_notes.md
```

Backup trước full sync có hậu tố:

```text
.pre_evidence_policy_full_sync
```

## 5. Kiểm tra mẫu `HNMU-G8-R0010-STT9`

Sau full sync:

- checklist không còn tiêu chí non-pass;
- `quality_check_suggestions.csv`: `suggested_quality_decision = keep`, `confidence_score = 0.76`;
- mẫu không còn nằm trong `hnmu_review_queue_suggestions.csv`.

## 6. Validation

Python executable đã dùng:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Đã chạy:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/agents tests/dialogue_audit -q
```

Kết quả:

- sync problems: 0;
- validator checklist: `OK`;
- pytest: 39 passed.
