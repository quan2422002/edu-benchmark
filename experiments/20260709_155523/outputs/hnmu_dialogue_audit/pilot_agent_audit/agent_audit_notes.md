# Pilot agent audit — hnmu-dialogue-auditor

Ngày chạy: 2026-07-17T21:42:02+07:00
Chế độ: single-agent pilot, không spawn hidden process, không ghi đè output chính của Plan 04.

## Phạm vi

- Input: `normalized_dialogue_rows.csv`, `metadata_consistency_flags.csv`, `hnmu_review_queue.csv`, SQLite retrieval index học liệu.
- Số mẫu pilot: 24.
- Phân bố lớp: {'6': 12, '7': 12}.
- Có đưa vào 2 mẫu đang nằm trong review queue chính để kiểm khả năng bắt lỗi cấu trúc.

## Output

- `pilot_sample_selection.csv`: danh sách mẫu được chọn.
- `raw_dialogue_checklist_results.csv`: checklist chi tiết từng tiêu chí.
- `quality_check_suggestions.csv`: gợi ý kết luận tổng hợp theo mẫu.
- `hnmu_review_queue_suggestions.csv`: gợi ý hàng đợi review từ pilot.

## Kết quả tóm tắt

- Quyết định theo mẫu: {'fail': 2, 'pass': 20, 'needs_human_review': 2}.
- Kết quả theo tiêu chí: {'fail': 10, 'pass': 333, 'uncertain': 39, 'not_applicable': 2}.
- Tổng số dòng checklist: 384.

## Giới hạn

- Đây là pilot bằng single-agent mode, dùng heuristic và retrieval evidence để mô phỏng cách `hnmu-dialogue-auditor` nên trả output.
- Evidence học liệu hiện vẫn có nhiều fragment trạng thái `draft`, nên confidence được giữ thận trọng.
- Kết quả này chưa thay thế review chuyên môn HNMU/UET và chưa được merge vào `quality_check_results.csv` chính.
- Các tiêu chí SGV có thể bị `uncertain` nếu retrieval chưa tìm đúng fragment SGV, dù raw data có đáp án SGV.

## Khuyến nghị trước khi chạy rộng

1. Quân soi 5–10 mẫu trong `raw_dialogue_checklist_results.csv` để xem lý do và reviewer action đã hữu ích chưa.
2. Nếu ổn, chạy specialist thật/native thread hoặc single-agent theo shard nhỏ, mỗi shard ghi output riêng.
3. Chỉ merge vào output chính sau khi có quy tắc tổng hợp và review queue được duyệt.


## Data dictionary

Ý nghĩa từng cột trong các file CSV pilot được giải thích tại `csv_column_dictionary.md`. File này cũng ghi chú cột nào nên giữ, cột nào có thể gộp/bỏ sau khi format ổn định.


## Ranh giới Plan 04/Plan 07

Pilot nhỏ này dùng để kiểm thử specialist được tạo trong Plan 07. Việc chạy rộng trên toàn bộ batch lớp 6–7 bằng 3 sub-agent theo bài học thuộc Plan 04. Shard manifest nằm trong `lesson_based_shards/` chỉ là input chuẩn bị cho Plan 04, không phải output cuối của Plan 7.
