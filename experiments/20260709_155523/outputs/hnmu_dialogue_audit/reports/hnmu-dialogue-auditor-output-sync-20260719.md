# Báo cáo đồng bộ output specialist từ checklist chi tiết

Ngày cập nhật lần đầu: 19/07/2026  
Ngày cập nhật rule thống nhất: 20/07/2026  
Trạng thái: `completed_canonical_quality_schema_sync`

## 1. Mục tiêu

Sau khi có bản checklist specialist đã repair, các file gợi ý/tổng hợp trong cùng thư mục cần được đồng bộ để không còn phản ánh bản checklist cũ. Báo cáo này ghi lại rule strict dùng cho lớp 8–9, áp dụng lại cho lớp 6–7 ngày 20/07/2026, và chuẩn hóa `quality_check_suggestions.csv` của cả hai batch về cùng một schema.

Checklist lớp 8–9:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Checklist lớp 6–7:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/raw_dialogue_checklist_results.repaired.csv
```

## 2. File đã đồng bộ

Các file chuẩn lớp 8–9 đã được tạo lại từ checklist `.regex_repaired.csv`:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/quality_check_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/hnmu_review_queue_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/merge_validation_summary.json
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/agent_audit_notes.md
```

Các bản trước repair, nếu tồn tại, được giữ bằng hậu tố `.pre_regex_repair` hoặc hậu tố backup tương ứng để truy vết.

Với cả hai batch lớp 6–7 và lớp 8–9, file chính ở cấp mẫu sau agent audit là:

```text
agent_shard_audit/merged/quality_check_suggestions.csv
```

File này dùng schema canonical `canonical_quality_check_suggestions_v1`, trong đó cột quyết định là `quality_decision`.

## 3. Quy tắc tổng hợp thống nhất

Quy tắc đồng bộ hiện tại:

- có bất kỳ tiêu chí `fail` → `quality_decision = failed`;
- không có `fail` nhưng có `uncertain` → `quality_decision = need_human_review`;
- tất cả tiêu chí đều `pass` hoặc `not_applicable` → `quality_decision = pass`.

Nhãn `keep` từng tồn tại ở output lớp 8–9 là nhãn legacy tương đương `pass`, nhưng không còn dùng trong file `quality_check_suggestions.csv` hiện hành.

Quy tắc `confidence_score` tổng thể:

- nếu quyết định là `failed`: lấy confidence thấp nhất trong các tiêu chí `fail`;
- nếu quyết định là `need_human_review`: lấy confidence thấp nhất trong các tiêu chí `uncertain`;
- nếu quyết định là `pass`: lấy confidence thấp nhất trong toàn bộ tiêu chí của mẫu.

Mọi mẫu `failed` hoặc `need_human_review` phải xuất hiện trong `hnmu_review_queue_suggestions.csv`.

Code dùng để đồng bộ:

```text
src/edu_benchmark/dialogue_audit/checklist_aggregation.py
scripts/dialogue_audit/sync_quality_suggestions_from_checklist.py
```

Đây là gợi ý vận hành để rà soát, không thay thế quyết định chuyên môn của HNMU/UET.

## 4. Kết quả sau đồng bộ hiện hành

- Lớp 6–7:
  - `quality_check_suggestions.csv`: 462 dòng.
  - `pass`: 238.
  - `need_human_review`: 222.
  - `failed`: 2.
  - `hnmu_review_queue_suggestions.csv`: 224 dòng.
- Lớp 8–9:
  - `quality_check_suggestions.csv`: 588 dòng.
  - `pass`: 427.
  - `need_human_review`: 160.
  - `failed`: 1.
  - `hnmu_review_queue_suggestions.csv`: 161 dòng.
- `merge_validation_summary.json`: ghi nguồn checklist, phân bố kết quả và danh sách output đã đồng bộ.

Hai file consistency audit đều báo 0 mâu thuẫn:

```text
experiments/20260709_155523/reports/quality-suggestion-consistency-audit-lop6-7-20260720.md
experiments/20260709_155523/reports/quality-suggestion-consistency-audit-lop8-9-20260720.md
```

## 5. Quan hệ với output cơ học

Các file cơ học ở root thư mục `hnmu_dialogue_audit_grade8_9/` đã được rerun trước đó bằng mapping regex-only, nên không cần tạo lại trong bước sync này:

```text
coverage_summary.csv
metadata_consistency_flags.csv
quality_check_results.csv
hnmu_review_queue.csv
```

Root `hnmu_review_queue.csv` vẫn là hàng đợi cơ học. File `agent_shard_audit/merged/hnmu_review_queue_suggestions.csv` là hàng đợi specialist rộng hơn, dùng để rà sâu các mẫu có tiêu chí `uncertain`/`fail`.

## 6. Validation

Python executable đã dùng:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Các kiểm tra đã chạy sau đồng bộ:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/agents tests/dialogue_audit -q
```

Kết quả được ghi ở lượt validation cuối của orchestrator.


## Cập nhật full evidence-policy sync

Sau khi phát hiện `RAW-CON-04` cũng có cùng mẫu lý do `uncertain` do fragment `draft`, đã thực hiện full sync cho nhóm `RAW-CON-01`, `RAW-CON-02`, `RAW-CON-04`, `RAW-CON-06`, `RAW-CON-07`. Kết quả hiện hành sau chuẩn hóa schema: `pass=427`, `need_human_review=160`, `failed=1`; review queue specialist còn 161 mẫu.

Ngày 20/07/2026, lớp 6–7 cũng đã được strict-sync từ `raw_dialogue_checklist_results.repaired.csv`. Kết quả hiện hành: `pass=238`, `need_human_review=222`, `failed=2`; review queue specialist có 224 mẫu.
