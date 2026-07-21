# Báo cáo repair checklist specialist sau khi sửa mapping regex-only — lớp 8–9

Ngày cập nhật: 19/07/2026  
Trạng thái: `completed_regex_repair` — đã repair các tiêu chí phụ thuộc evidence học liệu cho các mẫu từng bị gắn `Không rõ chủ đề` do mapping bài nhánh A/B chưa đúng.

## 1. Lý do repair

Trong lượt kiểm toán lớp 8–9 ban đầu, một số cách viết bài học của HNMU như `[8b] ...`, `Bài 8b: ...`, `10a. ...` chưa được map đúng vào registry SGK/SGV. Vì vậy, 154 mẫu bị gắn `Không rõ chủ đề` ở kiểm tra cơ học và một số tiêu chí specialist liên quan đến evidence học liệu bị đánh giá `uncertain`.

Sau khi chốt nguyên tắc **chỉ dùng regex, không dùng fuzzy matching**, mapper bài học đã được sửa để nhận diện chính xác `số bài + hậu tố A/B` và map theo khóa `grade + lesson_code`.

## 2. Phạm vi repair

Repair chỉ áp dụng cho 154 mẫu lớp 8–9 từng bị ảnh hưởng bởi lỗi mapping A/B, không chạy lại toàn bộ 588 mẫu.

Các tiêu chí được repair:

- `RAW-CON-01` — Câu hỏi khớp bài/vị trí.
- `RAW-CON-02` — Đáp án SGV khớp câu hỏi.
- `RAW-CON-06` — Bằng chứng học liệu truy xuất được.
- `RAW-CON-07` — Evidence đủ để kiểm nhất quán.

Số dòng repair: 154 mẫu × 4 tiêu chí = 616 dòng.

## 3. File output

Input repair:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/regex_repair/affected_samples.csv
```

Output subset do specialist tạo:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/regex_repair/repair_raw_dialogue_checklist_results.csv
```

Ghi chú của specialist:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/regex_repair/regex_repair_notes.md
```

Checklist đầy đủ sau merge repair:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
```

## 4. Kết quả trước/sau repair

| Hạng mục | Trước repair | Sau repair |
| --- | ---: | ---: |
| Tổng dòng checklist đầy đủ | 10.584 | 10.584 |
| Tổng mẫu | 588 | 588 |
| Tiêu chí/mẫu | 18 | 18 |
| Dòng được thay thế bởi repair | 0 | 616 |
| Tổng `pass` | 8.946 | 9.408 |
| Tổng `uncertain` | 1.636 | 1.174 |
| Tổng `fail` | 2 | 2 |

Riêng 154 mẫu bị ảnh hưởng:

| Kết quả ở 4 tiêu chí repair | Trước repair | Sau repair |
| --- | ---: | ---: |
| `pass` | 154 | 616 |
| `uncertain` | 462 | 0 |
| `fail` | 0 | 0 |

Diễn giải: phần lớn `uncertain` trước đó đến từ việc chưa truy xuất đúng evidence học liệu do lỗi mapping bài học, không phải do hội thoại chắc chắn sai.

## 5. Validation

Python executable đã dùng:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Đã chạy validator trên checklist đầy đủ sau merge:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Kết quả: `OK`.

## 6. Ghi chú sử dụng

Khi dùng kết quả specialist cho Plan 04/Plan 06, nên ưu tiên file:

```text
raw_dialogue_checklist_results.regex_repaired.csv
```

File cũ `raw_dialogue_checklist_results.csv` vẫn được giữ để truy vết, nhưng không còn là bản nên dùng cho các tiêu chí liên quan đến evidence học liệu lớp 8–9.
