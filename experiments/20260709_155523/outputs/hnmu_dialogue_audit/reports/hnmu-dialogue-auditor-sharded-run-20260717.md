# Báo cáo chạy `hnmu-dialogue-auditor` theo 3 shard bài học — Plan 04

Ngày chạy/merge: 2026-07-17T23:27:18+07:00

Ghi chú cập nhật 20/07/2026: số liệu trong báo cáo này là kết quả merge ban đầu trước khi repair đủ 18 tiêu chí/mẫu và trước khi strict-sync từ checklist chi tiết. Kết quả hiện hành của lớp 6–7 nằm ở:

```text
experiments/20260709_155523/reports/hnmu-dialogue-audit-batch-20260717.md
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/raw_dialogue_checklist_results.repaired.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/quality_check_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/hnmu_review_queue_suggestions.csv
```

Phân bố hiện hành sau strict-sync: 238 mẫu `pass`, 222 mẫu `needs_human_review`, 2 mẫu `fail`.

## 1. Phạm vi

Đã chạy 3 observable worker sub-agent theo logic `hnmu-dialogue-auditor`, mỗi agent xử lý một shard bài học riêng. Đây là phần của Plan 04, không phải Plan 07. Output không ghi đè các file chính của Plan 04.

## 2. Output merge riêng

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/
```

Các file merge:

- `raw_dialogue_checklist_results.csv`
- `quality_check_suggestions.csv`
- `hnmu_review_queue_suggestions.csv`
- `merge_validation_summary.json`

## 3. Tóm tắt số lượng

- Số mẫu input: 462

- Số mẫu có output: 462

- Số dòng checklist chi tiết: 7700

- Số dòng quality suggestions: 462

- Số dòng review queue suggestions: 105

- Quyết định cấp mẫu của bản merge ban đầu, đã bị thay thế bởi strict-sync ngày 20/07/2026: `{'pass': 357, 'needs_human_review': 103, 'fail': 2}`

- Kết quả cấp tiêu chí: `{'pass': 7370, 'uncertain': 320, 'fail': 7, 'not_applicable': 3}`

## 4. Kiểm tra merge

- Validator từng shard: pass.

- Validator file merge: pass.

- Trùng `sample_id` giữa shard: 0.

- Thiếu output so với input shard: 0.

- Output ngoài input shard: 0.

- Header consistency: `{'detail': True, 'quality': True, 'review': True}`.

## 5. Điểm cần chú ý

- Shard 02 tạo 18 tiêu chí/mẫu, trong khi shard 01 và shard 03 tạo 16 tiêu chí/mẫu. Đây là dấu hiệu output giữa sub-agent chưa thật sự đồng nhất, cần chuẩn hóa prompt hoặc dùng script template cho lần chạy rộng tiếp theo.

- `needs_sgv_verification`/`RAW-CON-02=uncertain` xuất hiện nhiều do evidence SGV/SGK vẫn ở trạng thái draft hoặc retrieval SGV chưa đủ chắc. Đây là vấn đề nguồn evidence, không tự động đồng nghĩa dữ liệu thô sai.

- Hai lỗi cơ học rõ vẫn được phát hiện: thiếu hội thoại và nhãn lượt nói lạ.

## 6. Khuyến nghị

1. Chưa merge vào `quality_check_results.csv` chính.

2. Trước khi dùng kết quả để chuyển Plan 06, cần chuẩn hóa bộ tiêu chí để mọi shard dùng cùng số tiêu chí.

3. Nên soi thủ công các mẫu `fail`, `needs_human_review`, và mẫu high priority trong review queue.

4. Cần cải thiện hoặc xác nhận chính sách đối với evidence SGV draft để tránh quá nhiều `uncertain` giả.
