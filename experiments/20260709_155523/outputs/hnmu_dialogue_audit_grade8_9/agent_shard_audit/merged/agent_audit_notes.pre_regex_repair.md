# Merged agent audit notes — HNMU lớp 8–9

## shard_01

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

## shard_02

# Ghi chú audit shard 02

- Phạm vi: 196 mẫu từ `shard_02_samples.csv` (14 lesson group, grade 8 và 9).
- Checklist bắt buộc: 18 tiêu chí / mẫu.
- Tổng dòng checklist: 3528.
- Phân bố kết quả: pass=3469, uncertain=59, fail=0, not_applicable=0.
- Số mẫu đề xuất giữ: 194.
- Số mẫu đề xuất review: 2.
- Cặp trùng chính xác trong shard: ['HNMU-G9-R0018-STT3', 'HNMU-G9-R0032-STT3'].
- Evidence học liệu cho shard đều có fragment ID truy xuất; trạng thái fragment là `draft` nhưng `evidence_match_reason` đều chỉ ra khớp top-1 theo metadata/keyword.
- Không có mẫu trong shard bị gắn `needs_learning_resource_review=true` ở báo cáo flags đã lọc theo shard.
- Mẫu review duy nhất do rủi ro trùng/tầm thường là cặp question duplicate chính xác sau chuẩn hóa.
- Tiêu chí có phát sinh non-pass: {'RAW-PED-01': 52, 'RAW-PED-02': 3, 'RAW-DUP-03': 2, 'RAW-DUP-04': 2}.

## shard_03

# Ghi chú audit shard 03

- Phạm vi: 196 mẫu, toàn bộ lớp 9, 14 nhóm bài học, 18 tiêu chí bắt buộc/mẫu.
- Tổng dòng checklist: 3528.
- Phân bố kết quả: pass=2930, uncertain=598, fail=0, not_applicable=0.
- Điểm chính:
  - `RAW-CON-01`, `RAW-CON-06`, `RAW-CON-07` được chấm `uncertain` cho toàn shard vì fragment học liệu chủ yếu ở trạng thái `draft` hoặc không có fragment xác nhận.
  - `HNMU-G9-R0191-STT8` có lỗi mất nhãn đầu hội thoại; đây là mẫu cần ưu tiên HNMU/UET xem lại.
  - `HNMU-G9-R0240-STT1`, `HNMU-G9-R0243-STT4`, `HNMU-G9-R0245-STT6`, `HNMU-G9-R0249-STT10`, `HNMU-G9-R0277-STT10` được gắn `uncertain` ở `RAW-PED-02` vì lượt AI đầu khá trực tiếp, cần xem lại mức độ lộ đáp án sớm.
- Không phát hiện cặp trùng trong shard 03 theo `duplicate_candidates.csv`.
- Đã giữ nguyên `checked_by=hnmu-dialogue-auditor(shard-03-grade8-9)` và timestamp dùng cho toàn bộ các dòng: 2026-07-18T23:34:26+07:00.
- Cần chạy validator sau khi xuất file checklist.

## Thống kê thêm theo tiêu chí
- RAW-STR-02: pass=196, uncertain=0, fail=0
- RAW-STR-03: pass=195, uncertain=1, fail=0
- RAW-STR-04: pass=194, uncertain=2, fail=0
- RAW-CON-01: pass=0, uncertain=196, fail=0
- RAW-CON-02: pass=196, uncertain=0, fail=0
- RAW-CON-03: pass=196, uncertain=0, fail=0
- RAW-CON-04: pass=196, uncertain=0, fail=0
- RAW-CON-05: pass=196, uncertain=0, fail=0
- RAW-CON-06: pass=0, uncertain=196, fail=0
- RAW-CON-07: pass=0, uncertain=196, fail=0
- RAW-PED-01: pass=196, uncertain=0, fail=0
- RAW-PED-02: pass=191, uncertain=5, fail=0
- RAW-PED-03: pass=195, uncertain=1, fail=0
- RAW-PED-04: pass=195, uncertain=1, fail=0
- RAW-PED-05: pass=196, uncertain=0, fail=0
- RAW-PED-06: pass=196, uncertain=0, fail=0
- RAW-DUP-03: pass=196, uncertain=0, fail=0
- RAW-DUP-04: pass=196, uncertain=0, fail=0
