# Handoff — Pilot `hnmu-dialogue-auditor`

Ngày: 17/07/2026
Trạng thái: đã chạy pilot, chưa merge vào output chính.

## Output

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/pilot_agent_audit/
```

File quan trọng nhất:

```text
raw_dialogue_checklist_results.csv
```

## Tóm tắt

- Số mẫu: 24.
- Số dòng checklist: 384.
- Quyết định cấp mẫu: `{'fail': 2, 'pass': 20, 'needs_human_review': 2}`.
- Kết quả cấp tiêu chí: `{'fail': 10, 'pass': 333, 'uncertain': 39, 'not_applicable': 2}`.
- Validator schema: pass.

## Lưu ý

Đây là pilot single-agent, dùng logic `hnmu-dialogue-auditor` nhưng chưa phải native specialist thread. Không sửa dữ liệu thô và không ghi đè output chính Plan 04.

Điểm cần Quân xem: nhiều mẫu `pass` vẫn có cờ cần xác minh SGV vì retrieval SGV chưa đủ chắc.
