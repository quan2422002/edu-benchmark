# Handoff — Plan 04 sharded `hnmu-dialogue-auditor` run

Ngày: 2026-07-17T23:27:18+07:00
Trạng thái: đã chạy 3 shard, đã merge riêng, chưa ghi đè output chính.

## Output

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/
```

Thư mục merge riêng:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/
```

## Kết quả

- Input samples: 462
- Output samples: 462
- Detail rows: 7700
- Quality rows: 462
- Review queue rows: 105
- Validator merged detail: pass
- Duplicate output sample IDs: 0
- Missing output IDs: 0
- Extra output IDs: 0

## Cảnh báo

Shard 02 dùng 18 tiêu chí/mẫu, trong khi shard 01 và 03 dùng 16 tiêu chí/mẫu. Trước khi dùng kết quả này làm production audit, cần chuẩn hóa prompt/template để tất cả shard dùng cùng bộ tiêu chí.

## Không làm

- Không ghi đè `quality_check_results.csv` chính.
- Không ghi đè `hnmu_review_queue.csv` chính.
- Không tạo benchmark samples.
