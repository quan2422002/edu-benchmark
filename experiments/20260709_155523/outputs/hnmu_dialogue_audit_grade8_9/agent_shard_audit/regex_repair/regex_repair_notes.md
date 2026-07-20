# Ghi chú repair checklist regex

- Số mẫu: 154
- Số dòng checklist: 616
- Thời điểm kiểm: 2026-07-19T18:16:34+07:00
- Phạm vi: chỉ 4 tiêu chí `RAW-CON-01`, `RAW-CON-02`, `RAW-CON-06`, `RAW-CON-07` theo yêu cầu repair.
- Nguồn evidence: toàn bộ mẫu đều có `evidence_status = draft`, nhưng canonical lesson/evidence fragment đã khớp đúng theo mapping regex-only và không thấy lệch rõ với SGK/SGV.

## Phân bố kết quả
- `pass`: 616
- `fail`: 0
- `uncertain`: 0
- `not_applicable`: 0

## Giới hạn còn lại
- Evidence hiện vẫn là fragment OCR `draft`, nên đây là audit thận trọng dựa trên khớp bài học và nội dung trả lời, chưa phải xác nhận chuyên môn HNMU cuối cùng.
- Không dùng fuzzy matching; mọi khớp bài học dựa trên `lesson_code`, `canonical_lesson_id`, `canonical_lesson_label`, `evidence_fragment_id` và `evidence_lesson_title` có sẵn trong shard.
- Các tiêu chí ngoài 4 tiêu chí được chỉ định không được chấm lại trong file repair này.

- `checked_by`: `hnmu-dialogue-auditor-regex-repair`
- File đầu ra: `repair_raw_dialogue_checklist_results.csv`
