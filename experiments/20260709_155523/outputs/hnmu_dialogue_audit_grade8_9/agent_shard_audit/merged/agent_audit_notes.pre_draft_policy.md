# Merged agent audit notes — HNMU lớp 8–9 sau regex repair

Ngày đồng bộ: 19/07/2026  
Trạng thái: `synced_from_regex_repaired_checklist`

## 1. Bản checklist hiện hành

Bản checklist specialist nên dùng hiện tại là:

```text
merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Bản này đã thay thế 616 dòng checklist của 154 mẫu từng bị ảnh hưởng bởi lỗi mapping bài nhánh A/B. Các tiêu chí đã repair là `RAW-CON-01`, `RAW-CON-02`, `RAW-CON-06`, `RAW-CON-07`.

File `merged/raw_dialogue_checklist_results.csv` được giữ để truy vết lịch sử trước repair, không nên dùng làm bản chính cho lớp 8–9.

## 2. Các file đã đồng bộ theo checklist mới

- `merged/quality_check_suggestions.csv`
- `merged/hnmu_review_queue_suggestions.csv`
- `merged/merge_validation_summary.json`

Bản trước repair của các file này được giữ bằng hậu tố `.pre_regex_repair` nếu file đã tồn tại trước khi đồng bộ.

## 3. Tóm tắt checklist sau repair

- Số mẫu: 588
- Số tiêu chí/mẫu: [18]
- Số dòng checklist: 10584
- Phân bố kết quả checklist: {'pass': 9408, 'uncertain': 1174, 'fail': 2}
- Phân bố gợi ý chất lượng: {'needs_human_review': 354, 'fail': 1, 'keep': 233}
- Số mẫu trong hàng đợi review gợi ý: 355
- Phân bố priority review: {'trung bình': 350, 'cao': 5}

## 4. Diễn giải nhanh

Sau repair, nhóm mẫu A/B không còn bị `uncertain` chỉ vì lỗi mapping bài học. Tuy nhiên, checklist specialist vẫn còn các mẫu `uncertain` ở những tiêu chí khác, nhất là các tiêu chí đối chiếu evidence học liệu/hội thoại hoặc tiêu chí sư phạm cần HNMU/UET xác nhận.

Do đó, file suggestion tổng hợp nên được xem là hàng đợi rà soát có giải thích, không phải quyết định chuyên môn cuối cùng.

## 5. Validation

Đã chạy validator trên checklist hiện hành:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Kết quả: `OK`.
