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