# Repair notes — shard 03

## Phạm vi

- Bổ sung đúng hai tiêu chí còn thiếu: `RAW-CON-06`, `RAW-CON-07`.
- Không sửa 16 tiêu chí đã có trong file shard gốc.
- Giữ lại các dòng repair một phần đã có nếu cùng `sample_id` + `criterion_id`; sinh bổ sung các cặp còn thiếu.

## Kết quả

- Số mẫu shard 03: 154.
- Số dòng repair: 308.
- Dòng repair giữ lại từ specialist trước đó: 28.
- Dòng repair sinh bổ sung: 280.
- Phân bố kết quả: {('RAW-CON-06', 'pass'): 152, ('RAW-CON-07', 'pass'): 153, ('RAW-CON-06', 'uncertain'): 2, ('RAW-CON-07', 'fail'): 1}.

## Quy tắc repair

- `RAW-CON-06` dựa trên các tiêu chí liên quan tới hội thoại bám câu hỏi, bám đáp án và không lạc hướng. Nếu các tiêu chí này fail/uncertain thì hạ xuống `uncertain` và đưa vào `ask_hnmu_review`.
- `RAW-CON-07` dựa trên các tiêu chí nhất quán metadata/hội thoại đã có: khớp bài/vị trí, bám câu hỏi, bám đáp án, mức nhận thức. Nếu tiêu chí liên quan fail thì `fail`; nếu uncertain thì `uncertain`.
- Đây là repair có kiểm soát dựa trên output audit gốc; không phải audit lại toàn bộ shard.
