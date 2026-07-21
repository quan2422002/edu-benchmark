# Báo cáo pilot `hnmu-dialogue-auditor` — 17/07/2026

## 1. Phạm vi

Đã chạy pilot kiểm toán ngữ nghĩa/sư phạm cho dữ liệu hội thoại thô HNMU bằng logic của specialist `hnmu-dialogue-auditor` ở chế độ single-agent. Không spawn hidden process và không ghi đè output chính của Plan 04.

Output đặt tại:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/pilot_agent_audit/
```

Các file chính:

- `pilot_sample_selection.csv`: danh sách 24 mẫu được chọn;
- `raw_dialogue_checklist_results.csv`: checklist chi tiết từng tiêu chí;
- `quality_check_suggestions.csv`: gợi ý kết luận theo mẫu;
- `hnmu_review_queue_suggestions.csv`: gợi ý mẫu cần HNMU/UET xem lại;
- `agent_audit_notes.md`: ghi chú giới hạn pilot.

## 2. Cách chọn mẫu

Pilot chọn 24 mẫu, gồm:

- 2 mẫu đang nằm trong review queue chính của Plan 04 để kiểm khả năng bắt lỗi rõ;
- 22 mẫu còn lại rải theo lớp/bài học từ dữ liệu lớp 6–7.

Phân bố lớp: `{'6': 12, '7': 12}`.

## 3. Kết quả nhanh

Theo gợi ý tổng hợp cấp mẫu:

```text
{'fail': 2, 'pass': 20, 'needs_human_review': 2}
```

Theo dòng checklist chi tiết:

```text
{'fail': 10, 'pass': 333, 'uncertain': 39, 'not_applicable': 2}
```

Tổng số dòng checklist: 384.

Các tiêu chí `fail` nhiều nhất:

```text
{'RAW-STR-02': 1, 'RAW-STR-03': 2, 'RAW-STR-04': 1, 'RAW-CON-03': 1, 'RAW-CON-04': 1, 'RAW-PED-01': 1, 'RAW-PED-03': 1, 'RAW-PED-04': 1, 'RAW-PED-06': 1}
```

Các tiêu chí `uncertain` nhiều nhất:

```text
{'RAW-CON-02': 24, 'RAW-PED-02': 5, 'RAW-PED-03': 1, 'RAW-CON-04': 2, 'RAW-DUP-04': 5, 'RAW-CON-05': 2}
```

## 4. Nhận xét ban đầu

- Pilot bắt đúng 2 mẫu lỗi rõ đã có trong review queue: một mẫu thiếu hội thoại và một mẫu có nhãn lượt nói lạ `AII`.
- Nhiều mẫu `pass` vẫn có cờ `needs_sgv_verification=true` vì retrieval SGV chưa tìm được fragment đủ chắc. Đây không nhất thiết là lỗi dữ liệu; nó cho thấy hệ truy xuất SGV cần cải thiện hoặc cần mapping SGV tốt hơn trước khi chạy audit rộng.
- Các quyết định trong pilot là gợi ý, chưa thay thế review chuyên môn HNMU/UET.
- Vì fragment học liệu còn trạng thái `draft`, confidence được đặt thận trọng.

## 5. Khuyến nghị

1. Quân nên soi thủ công khoảng 5–10 dòng trong `raw_dialogue_checklist_results.csv`, ưu tiên các mẫu `needs_human_review` và `fail`.
2. Trước khi chạy rộng, nên quyết định rõ: mẫu `pass` nhưng `needs_sgv_verification=true` có được chuyển tiếp tạm thời không, hay phải chờ SGV retrieval chắc hơn.
3. Nếu output pilot ổn, bước tiếp theo là chạy theo shard nhỏ cho toàn bộ lớp 6–7, mỗi shard ghi riêng rồi mới tổng hợp.

## 6. Validation

Đã chạy validator schema:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py \
  experiments/20260709_155523/outputs/hnmu_dialogue_audit/pilot_agent_audit/raw_dialogue_checklist_results.csv

OK
```

Python executable: `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.
