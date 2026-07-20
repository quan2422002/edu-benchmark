# Specialist handoff

- Delegation ID: `hnmu-dialogue-auditor-grade8-9-sharded-run-040`
- Agent: `hnmu-dialogue-auditor` qua 3 native specialist sub-agent
- Status: `completed`
- Native thread ID/label:
  - `shard_01`: `019f7679-79be-7a92-908e-116638991a23`
  - `shard_02`: `019f7679-ca9d-7b60-b6d1-d33bb2bad37d`
  - `shard_03`: `019f767a-1e25-73d2-877c-4514c35d4944`

## Delegation prompt

Chạy kiểm toán ngữ nghĩa/sư phạm dữ liệu hội thoại thô HNMU lớp 8–9 theo 3 shard bài học. Mỗi sub-agent dùng skill `hnmu-dialogue-auditor`, model `gpt-5.4-mini`, reasoning `medium`, checklist dữ liệu thô và registry 18 tiêu chí bắt buộc.

## Follow-up or steer messages

- User đã duyệt fan-out 3 specialist sub-agent.
- Orchestrator chia shard theo bài học, mỗi shard ghi vào thư mục riêng để tránh ghi đè.
- Sau khi sub-agent hoàn thành, orchestrator validate từng shard và merge output.

## Inputs read

- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/normalized_dialogue_rows.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/lesson_based_shards/`
- `experiments/20260709_155523/reports/raw-dialogue-audit-criteria-v0.csv`
- `experiments/20260709_155523/reports/raw-dialogue-quality-checklist-v0.md`
- `shared/learning_resources/agent_context/README.md`
- `shared/learning_resources/indexes/learning_resources_v0.sqlite`

## Outputs created

- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/shard_01/`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/shard_02/`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/shard_03/`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/quality_check_suggestions.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/hnmu_review_queue_suggestions.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/agent_audit_notes.md`
- `experiments/20260709_155523/reports/hnmu-dialogue-audit-batch-grade8-9-20260719.md`

- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/checklists/`

## Result summary

- Số mẫu lớp 8–9: 588.
- Số shard: 3.
- Mỗi shard: 196 mẫu, 18 tiêu chí/mẫu, 3.528 dòng checklist.
- File merged: 10.584 dòng checklist, 588 mẫu, đủ 18 tiêu chí/mẫu.
- Kết quả criterion-level trong file merged: 8.946 `pass`, 1.636 `uncertain`, 2 `fail`.
- Validator `hnmu-dialogue-auditor` pass cho file merged.
- Test liên quan pass: `/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/agents tests/dialogue_audit -q` → 38/38.

## Orchestrator decision

Giữ output agent lớp 8–9 tách riêng khỏi output lớp 6–7. Có thể dùng file checklist chi tiết merged làm cơ sở phân tích Plan 04 tiếp theo, nhưng chưa nên đưa thẳng toàn bộ 588 mẫu sang Plan 06 nếu chưa xử lý các điểm `unmapped`, nhãn tổng hợp chưa chuẩn hóa và mẫu cần review.

## Uncertainty

- Nhiều `uncertain` đến từ evidence học liệu đang ở trạng thái `draft` hoặc chưa map được fragment.
- 154 mẫu đang thuộc nhóm `Không rõ chủ đề`; nhiều khả năng do parser/registry chưa xử lý tốt bài nhánh A/B hoặc tên bài rút gọn.
- File gợi ý tổng hợp giữa các shard còn khác nhãn tiếng Việt/tiếng Anh và `True`/`true`.

## Open questions and next human decisions

1. Có sửa parser/registry để map bài nhánh A/B lớp 8–9 trước Plan 06 không?
2. Có normalize các file gợi ý tổng hợp để tạo bản gửi HNMU không?
3. Các mẫu trùng/lỗi định dạng/lộ đáp án sớm sẽ sửa, giữ hay loại khỏi batch hiện tại?
4. Có cần HNMU xác nhận một mẫu evidence SGK/SGV lớp 8–9 trước khi dùng checklist agent làm input chính thức không?


## Post-run note — regex-only lesson mapping

Sau lượt specialist sharded run, mapper bài học đã được sửa theo yêu cầu của user: cấm fuzzy matching, chỉ dùng regex để lấy `số bài + hậu tố A/B nếu có` và map sang registry SGK/SGV. Kiểm toán cơ học lớp 8–9 đã được rerun, làm nhóm `Không rõ chủ đề` giảm từ 154 xuống 0 và review queue cơ học giảm từ 101 xuống 3.

Output specialist checklist vẫn hợp lệ về cấu trúc, nhưng các tiêu chí phụ thuộc evidence học liệu có thể cần repair/rerun nếu dùng làm input chính thức cho Plan 06.
