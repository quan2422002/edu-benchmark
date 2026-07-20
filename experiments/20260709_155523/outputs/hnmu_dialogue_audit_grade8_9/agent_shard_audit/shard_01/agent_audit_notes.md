# Ghi chú audit shard 01 — hnmu-dialogue-auditor

- Chế độ: `hnmu-dialogue-auditor(shard-01-grade8-9)`
- Shard: `shard_01`
- Số mẫu: 196
- Số tiêu chí bắt buộc mỗi mẫu: 18
- Số dòng checklist kỳ vọng: 3528
- Python kiểm chứng: `/home/quannda/miniconda3/envs/benchmark_env/bin/python`

## Tóm tắt kết quả

- `raw_dialogue_checklist_results.csv`: 3528 dòng, 196 mẫu, 18 tiêu chí.
- `quality_check_suggestions.csv`: 196 dòng.
- `hnmu_review_queue_suggestions.csv`: 196 dòng.

## Bất định chính

- 98 mẫu nửa sau shard không có fragment học liệu khớp trong `metadata_consistency_flags.csv`.
- 98 mẫu nửa đầu có fragment nhưng ở trạng thái `draft`, nên các tiêu chí đối chiếu SGK/SGV được giữ ở mức `uncertain` theo chỉ dẫn của shard.
- 1 mẫu có lỗi nhãn lượt nói và lệch công thức trong hội thoại: `HNMU-G8-R0068-STT11`.

## Quyết định cần HNMU/UET

- Xác nhận lại các fragment học liệu `draft` hoặc còn thiếu fragment cho nhóm bài từ `[8b]` đến `[10b]`.
- Xác nhận/sửa mẫu `HNMU-G8-R0068-STT11` trước khi chuyển tiếp.
- Duyệt hay loại các mẫu đang ở hàng đợi review do tiêu chí SGK/SGV còn `uncertain`.
