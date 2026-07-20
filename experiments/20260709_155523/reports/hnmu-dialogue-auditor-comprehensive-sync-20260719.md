# Báo cáo đồng bộ toàn diện output specialist lớp 8–9

Ngày thực hiện: 19/07/2026  
Trạng thái: `completed_and_validated`

## 1. Lý do

Sau các lượt repair trước đó, `raw_dialogue_checklist_results.regex_repaired.csv` đã là checklist chính cho dữ liệu lớp 8–9. Tuy nhiên, một số cột tổng hợp trong `quality_check_suggestions.csv`, đặc biệt là `main_failure_reasons`, vẫn còn diễn đạt nhập nhằng kiểu “fragment draft hoặc chưa có fragment”.

Điều này dễ gây hiểu nhầm rằng mẫu bị đưa vào review chỉ vì fragment học liệu có trạng thái `draft`. Theo chính sách đã chốt, fragment `draft` nhưng khớp metadata và nội dung thì không tự động làm tiêu chí bị `uncertain`.

## 2. Nguyên tắc đồng bộ

- Lấy `raw_dialogue_checklist_results.regex_repaired.csv` làm nguồn chính.
- Tái sinh toàn diện `quality_check_suggestions.csv` và `hnmu_review_queue_suggestions.csv` từ các dòng checklist chưa `pass`.
- `main_failure_reasons` phải khớp trực tiếp với các `criterion_id` chưa `pass`.
- `source_checklist_rows` phải khớp chính xác với các `criterion_id` chưa `pass`.
- Nếu `evidence_fragment_id` trống, reason ghi rõ là chưa truy xuất được fragment phù hợp, không quy vấn đề về trạng thái `draft`.
- Không đổi quyết định `pass/uncertain/fail` trong checklist chỉ vì chỉnh wording.

## 3. File đã cập nhật

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/quality_check_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/hnmu_review_queue_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/merge_validation_summary.json
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/agent_audit_notes.md
```

Đồng thời đã cập nhật report tổng thể lớp 8–9 ở hai vị trí:

```text
experiments/20260709_155523/reports/hnmu-dialogue-audit-batch-grade8-9-20260719.md
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/reports/hnmu-dialogue-audit-batch-grade8-9-20260719.md
```

## 4. Kết quả hiện hành

- Checklist: 10.584 dòng.
- Phân bố checklist: 10.107 `pass`, 475 `uncertain`, 2 `fail`.
- `quality_check_suggestions.csv`: 588 mẫu.
  - 427 `keep`;
  - 160 `needs_human_review`;
  - 1 `fail`.
- `hnmu_review_queue_suggestions.csv`: 161 mẫu.
  - 118 priority `trung bình`;
  - 43 priority `cao`.
- Số lỗi đồng bộ giữa checklist và file tổng hợp: 0.
- Số dòng `main_failure_reasons` còn nhắc `draft/chưa xác nhận`: 0.
- Số dòng checklist chưa `pass` còn nhắc `draft/chưa xác nhận`: 0.

## 5. Kiểm tra mẫu

Mẫu `HNMU-G8-R0010-STT9` hiện đã đồng bộ đúng:

- không còn tiêu chí chưa `pass`;
- `suggested_quality_decision = keep`;
- `main_failure_reasons` trống;
- không nằm trong `hnmu_review_queue_suggestions.csv`.

Mẫu `HNMU-G8-R0100-STT1` hiện còn `needs_human_review`, nhưng lý do đã đúng bản chất:

- chưa truy xuất được fragment phù hợp cho các tiêu chí đối chiếu học liệu;
- không còn diễn đạt rằng vấn đề đến từ trạng thái `draft`.

## 6. Validation

Python executable đã dùng:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Đã chạy:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/agents tests/dialogue_audit -q
```

Kết quả:

- validator checklist: `OK`;
- kiểm tra đồng bộ tùy chỉnh: `sync_problem_count = 0`;
- pytest: 39 passed.
