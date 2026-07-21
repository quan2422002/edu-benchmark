# Specialist handoff

- Delegation ID: `hnmu-dialogue-audit-plan04-v0-035`
- Agent: orchestrator single-agent mode; no hidden specialist process spawned
- Status: completed v0
- Native thread ID/label: null

## Post-update note — strict checklist aggregation

Ngày 20/07/2026, kết quả agent-level lớp 6–7 đã được repair đủ 18 tiêu chí/mẫu và strict-sync từ checklist chi tiết. Vì vậy, các số liệu “460 mẫu `pass`” trong handoff này chỉ phản ánh kiểm toán cơ học/truy xuất v0 tại thời điểm 17/07/2026, không phải kết quả agent-level hiện hành.

Kết quả agent-level hiện hành:

- 238 mẫu `pass`;
- 222 mẫu `needs_human_review`;
- 2 mẫu `fail`;
- 224 mẫu trong `hnmu_review_queue_suggestions.csv`.

Nguồn hiện hành:

```text
experiments/20260709_155523/reports/hnmu-dialogue-audit-batch-20260717.md
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/quality_check_suggestions.csv
```

## Delegation prompt

Triển khai Plan 04 để kiểm toán v0 dữ liệu hội thoại thô HNMU, nhưng chỉ xử lý lớp 6–7 trong experiment `20260709_155523`. Lớp 8–9 nếu có trong thư mục raw phải được ghi nhận là ngoài scope, không xử lý trong output chính.

## Follow-up or steer messages

Người dùng chốt rõ: “không cần xử lý data raw của lớp 8 và 9 luôn đâu, cứ làm tốt cho 6-7 ở experiment này đã nhé”.

## Inputs read

- `experiments/20260709_155523/plans/04-hnmu-dialogue-intake-coverage-consistency-dedup.md`
- `experiments/20260709_155523/reports/benchmark-quality-checklist-v0.md`
- `shared/raw_data/HNMU-teacher_dialog_samples/Lớp 6.xlsx`
- `shared/raw_data/HNMU-teacher_dialog_samples/Lớp 7.xlsx`
- `shared/learning_resources/fragments/learning_resource_fragments.csv`
- `shared/learning_resources/indexes/learning_resources_v0.sqlite`

## Outputs created

- `src/edu_benchmark/data_io/xlsx.py`
- `src/edu_benchmark/dialogue_audit/hnmu_audit.py`
- `scripts/dialogue_audit/run_hnmu_dialogue_audit.py`
- `tests/dialogue_audit/test_hnmu_dialogue_audit.py`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/normalized_dialogue_rows.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/coverage_summary.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/missing_field_report.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/metadata_consistency_flags.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/duplicate_candidates.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/quality_check_results.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/hnmu_review_queue.csv`
- `experiments/20260709_155523/reports/hnmu-dialogue-audit-batch-20260717.md`

## Result summary

- File raw nhìn thấy: lớp 6, 7, 8, 9.
- File đã xử lý: lớp 6 và lớp 7.
- Tổng số dòng lớp 6–7 đọc được: 462.
- Quyết định chất lượng v0: 460 `pass`, 2 `fail`.
- Số cặp trùng/gần trùng ứng viên: 0.
- Số mẫu đưa vào `hnmu_review_queue.csv`: 2.
- Lớp 8–9 không được xử lý trong vòng này theo chỉ đạo của người dùng.

## Orchestrator decision tại thời điểm v0

Tại thời điểm kiểm toán cơ học/truy xuất v0, có thể cân nhắc dùng 460 mẫu `pass` làm đầu vào ứng viên cho Plan 06 sau khi người dùng chấp nhận mức kiểm toán v0. Sau strict-sync ngày 20/07/2026, quyết định hiện hành phải dựa trên `quality_check_suggestions.csv`: 238 mẫu `pass`, 222 mẫu `needs_human_review`, 2 mẫu `fail`.

## Uncertainty

- Audit hiện tại là cơ học + truy xuất học liệu v0; chưa phải kiểm định chuyên môn cuối cùng.
- Fragment học liệu lớp 6–7 đang đủ dùng cho truy xuất sơ bộ, nhưng vẫn là nguồn draft ở giai đoạn dự án này.
- Việc audit ngữ nghĩa sâu bằng specialist riêng vẫn là đề xuất cho vòng sau của Plan 04 hoặc một plan kế tiếp.

## Open questions and next human decisions

1. Người dùng/UET có chấp nhận dùng nhóm 238 mẫu `pass` sau strict-sync làm input thử ưu tiên cho Plan 06 không?
2. Hai mẫu fail sẽ sửa tại HNMU, UET hay loại khỏi batch hiện tại?
3. Khi nào mới mở scope lớp 8–9: trong experiment mới hay vòng audit sau khi học liệu 8–9 đã sẵn sàng?

## Validation

Python executable dùng để kiểm thử:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Lệnh kiểm thử:

```bash
PYTHONPATH=src /home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/dialogue_audit tests/learning_resources tests/agents -q
```

Kết quả: `45 passed in 0.27s`.

## Post-update note — checklist tách riêng

Ngày 17/07/2026, checklist tổng hợp `experiments/20260709_155523/reports/benchmark-quality-checklist-v0.md` đã được tách thành hai checklist vận hành:

- `experiments/20260709_155523/reports/raw-dialogue-quality-checklist-v0.md`: dùng cho Plan 04 và các bước kiểm dữ liệu thô HNMU.
- `experiments/20260709_155523/reports/benchmark-candidate-quality-checklist-v0.md`: dùng sau Plan 06, khi đã có ứng viên mẫu benchmark.

Các vòng audit Plan 04 sau ghi chú này phải dùng checklist dữ liệu thô, không dùng checklist ứng viên benchmark.
