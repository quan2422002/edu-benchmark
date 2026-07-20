# Plan 07 — Tạo specialist agent kiểm toán dữ liệu thô HNMU

Experiment: `20260709_155523`
Trạng thái: `APPROVED` — đã triển khai specialist v0 cho Plan 04.
Ngày lập: 17/07/2026
Người phụ trách dự kiến: Quân duyệt phạm vi; Codex triển khai kỹ thuật; HNMU/UET xác nhận chuyên môn ở các ca không chắc.

## 1. Bối cảnh

Plan 04 đã có phần kiểm toán cơ học bằng code cho dữ liệu hội thoại thô HNMU lớp 6–7: thống kê độ phủ, thiếu trường, định dạng, trùng/gần trùng và truy xuất học liệu sơ bộ.

Phần còn lại của Plan 04 là kiểm ngữ nghĩa và sư phạm ở cấp từng mẫu. Việc này không nên để orchestrator làm thủ công mỗi lần, vì:

- dữ liệu HNMU sẽ còn nhiều batch;
- checklist dữ liệu thô đã được tách riêng khỏi checklist ứng viên benchmark;
- output cần truy vết tới từng tiêu chí trong `raw_dialogue_checklist_results.csv`;
- agent phải dùng đúng học liệu SGK/SGV, phương pháp dàn giáo HNMU và các cờ review;
- nếu không chuyên biệt hóa, logic kiểm dễ bị trôi giữa các phiên làm việc.

Vì vậy, plan này đề xuất tạo specialist agent mới:

```text
hnmu-dialogue-auditor
```

Agent này là “kiểm toán viên dữ liệu thô HNMU”, không phải agent thiết kế benchmark.

## 2. Mục tiêu

Tạo một specialist agent hẹp, có thể dùng trong Plan 04 để kiểm chất lượng từng mẫu dữ liệu thô HNMU bằng:

- `experiments/20260709_155523/reports/raw-dialogue-quality-checklist-v0.md`;
- `shared/learning_resources/agent_context/README.md`;
- fragment/index học liệu SGK/SGV;
- tài liệu phương pháp dàn giáo HNMU;
- output cơ học từ code audit.

Agent phải tạo được kết quả có truy vết, tối thiểu gồm:

- kết quả từng tiêu chí trong `raw_dialogue_checklist_results.csv`;
- kết luận tổng hợp đề xuất cho `quality_check_results.csv`;
- danh sách mẫu cần HNMU/UET xem lại nếu cần.

## 3. Ngoài phạm vi

Agent này không làm các việc sau:

- không sửa file Excel gốc HNMU;
- không tạo mẫu benchmark hoàn chỉnh;
- không tách `student_prompt`, `conversation_history`, `gold_response`;
- không gán task chính thức;
- không kiểm độ phủ task/hành vi gia sư của benchmark;
- không chấm model;
- không thay HNMU/UET quyết định đúng/sai chuyên môn;
- không tự coi fragment hoặc OCR ở trạng thái `draft` là bằng chứng đã xác nhận.

Các việc trên thuộc Plan 06, Plan 05 hoặc review chuyên môn của HNMU/UET.

## 4. File/thư mục dự kiến tạo và vai trò

### 4.1. `agents/hnmu-dialogue-auditor/SKILL.md`

Vai trò: hướng dẫn canonical cho specialist agent.

Lý do tạo: đây là nguồn logic chính của agent; runtime adapters chỉ được mỏng, không được fork workflow. File này cần mô tả:

- khi nào dùng agent;
- input bắt buộc;
- các tài liệu phải đọc;
- quy trình kiểm từng mẫu;
- output schema;
- ranh giới quyền hạn;
- cách xử lý trường hợp không chắc.

Ngôn ngữ: English-first vì đây là file agent-facing/code-facing, nhưng giữ nguyên tên file, field ID và thuật ngữ tiếng Việt khi chúng là dữ liệu dự án.

### 4.2. `agents/hnmu-dialogue-auditor/agents/openai.yaml`

Vai trò: metadata hiển thị cho Codex UI/App.

Lý do tạo: giúp specialist xuất hiện rõ trong danh sách agent, có tên, mô tả ngắn và prompt mặc định đúng phạm vi.

### 4.3. `agents/hnmu-dialogue-auditor/references/raw-dialogue-audit-output-schema.md`

Vai trò: mô tả schema output mà agent phải trả về.

Lý do tạo: agent cần ghi đúng các cột như `sample_id`, `criterion_id`, `result`, `confidence_score`, `evidence_fragment_id`, `reason`, `suggested_reviewer_action`. Nếu schema nằm riêng, `SKILL.md` sẽ gọn hơn và agent chỉ đọc khi cần ghi/kiểm output.

### 4.4. `agents/hnmu-dialogue-auditor/references/raw-dialogue-audit-workflow.md`

Vai trò: mô tả quy trình kiểm một mẫu hoặc một batch nhỏ.

Lý do tạo: quy trình kiểm có nhiều bước: đọc metadata, truy xuất học liệu, kiểm từng tiêu chí, phân biệt `pass`/`fail`/`uncertain`/`not_applicable`, rồi tổng hợp. Đưa vào reference riêng giúp dễ chỉnh workflow mà không làm `SKILL.md` quá dài.

### 4.5. `agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py`

Vai trò: validator cho output của agent.

Lý do tạo: cần kiểm các bảng agent tạo có đủ cột, giá trị `result` hợp lệ, `criterion_id` đúng dạng, không thiếu `sample_id`, và không ghi kết luận tổng hợp khi thiếu checklist chi tiết.

Script này chỉ kiểm hình thức/schema; không thay HNMU/UET kiểm chuyên môn.

### 4.6. `.codex/agents/hnmu-dialogue-auditor.toml`

Vai trò: adapter Codex cho specialist.

Lý do tạo: cho phép gọi specialist qua native observable subagent thread trong Codex CLI/App. Adapter phải mỏng, trỏ về canonical skill, không chứa workflow riêng.

Model đề xuất ban đầu:

```text
model: gpt-5.4-mini
reasoning: medium
```

Lý do: kiểm nhiều mẫu sẽ tốn token; `medium` đủ cho pilot. Nếu mẫu khó hoặc cần phân xử sâu, orchestrator có thể nâng reasoning trong từng lượt được duyệt riêng.

### 4.7. `.claude/agents/hnmu-dialogue-auditor.md`

Vai trò: adapter Claude Code để giữ tương thích cấu trúc multi-runtime.

Lý do tạo: dự án đang duy trì adapters Claude ở mức static validation. Không cần test runtime Claude ngay, nhưng adapter phải không fork workflow.

### 4.8. `.agents/skills/hnmu-dialogue-auditor`

Vai trò: skill discovery link.

Lý do tạo: để Codex phát hiện canonical skill theo cơ chế hiện tại của repo.

### 4.9. `tests/agents/test_hnmu_dialogue_auditor.py`

Vai trò: test tài liệu/adapters/validator cho specialist mới.

Lý do tạo: tránh tạo agent “có vẻ tồn tại” nhưng thiếu adapter, thiếu openai metadata, thiếu validator hoặc không được nhắc trong README/ARCHITECTURE.

### 4.10. Cập nhật `README.md`, `ARCHITECTURE.md`, `AGENTS.md`

Vai trò: công bố specialist mới trong tài liệu hệ thống.

Lý do tạo: specialist mới là thay đổi kiến trúc/ownership. README cần ghi onboarding/status; ARCHITECTURE cần ghi component/runtime; AGENTS cần ghi quy tắc sử dụng và model pin.

### 4.11. Cập nhật roadmap và metadata experiment

File dự kiến:

```text
experiments/20260709_155523/roadmap.md
experiments/20260709_155523/metadata.yaml
```

Vai trò: ghi nhận Plan 07 và các artifact mới.

Lý do tạo: để experiment không bị lệch trạng thái giữa roadmap, plan và file thực tế.

## 5. Input mà agent phải dùng

Agent phải được cung cấp hoặc tự đọc trong phạm vi được phép:

```text
shared/learning_resources/agent_context/README.md
experiments/20260709_155523/reports/raw-dialogue-quality-checklist-v0.md
shared/learning_resources/fragments/learning_resource_fragments.csv
shared/learning_resources/indexes/learning_resources_v0.sqlite
shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md
experiments/20260709_155523/outputs/hnmu_dialogue_audit/normalized_dialogue_rows.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit/coverage_summary.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit/missing_field_report.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit/duplicate_candidates.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit/metadata_consistency_flags.csv
```

Với từng batch chạy thật, orchestrator phải chỉ rõ:

- sample range hoặc danh sách `sample_id`;
- output path riêng cho agent;
- có được ghi trực tiếp vào output chính hay chỉ ghi shard/pilot;
- điều kiện dừng khi agent không chắc.

## 6. Output bắt buộc

### 6.1. Output chính của agent

Trong pilot, nên ghi vào thư mục riêng trước:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/pilot_agent_audit/
```

Các file dự kiến:

```text
raw_dialogue_checklist_results.csv
quality_check_suggestions.csv
hnmu_review_queue_suggestions.csv
agent_audit_notes.md
```

Vai trò:

- `raw_dialogue_checklist_results.csv`: bảng chi tiết từng tiêu chí cho từng mẫu.
- `quality_check_suggestions.csv`: đề xuất kết luận tổng hợp; chưa ghi đè `quality_check_results.csv` nếu chưa duyệt.
- `hnmu_review_queue_suggestions.csv`: đề xuất mẫu cần gửi HNMU/UET xem lại.
- `agent_audit_notes.md`: ghi các giới hạn, pattern lỗi, tiêu chí hay `uncertain`, và đề xuất cải thiện checklist/code.

### 6.2. Schema tối thiểu của `raw_dialogue_checklist_results.csv`

```text
sample_id
criterion_id
criterion_group
criterion_name
result
confidence_score
evidence_fragment_id
evidence_source
evidence_match_reason
reason
suggested_reviewer_action
checked_by
checked_at
```

`result` chỉ được dùng một trong bốn giá trị:

```text
pass
fail
uncertain
not_applicable
```

## 7. Quy trình triển khai

### Bước 1 — Chốt phạm vi agent

Đọc lại:

- Plan 04;
- `raw-dialogue-quality-checklist-v0.md`;
- `agent_context/README.md`;
- output audit v0 lớp 6–7.

Sau đó chốt ranh giới:

- agent chỉ kiểm dữ liệu thô;
- agent không tạo benchmark;
- agent không gán task;
- agent phải tạo checklist chi tiết.

### Bước 2 — Tạo canonical skill

Tạo `agents/hnmu-dialogue-auditor/` với:

- `SKILL.md`;
- `agents/openai.yaml`;
- `references/`;
- `scripts/validate_raw_dialogue_audit_output.py`.

Nội dung phải ngắn gọn, có progressive disclosure: `SKILL.md` chứa workflow lõi; schema/workflow chi tiết nằm trong `references/`.

### Bước 3 — Tạo runtime adapters

Tạo:

- `.codex/agents/hnmu-dialogue-auditor.toml`;
- `.claude/agents/hnmu-dialogue-auditor.md`;
- `.agents/skills/hnmu-dialogue-auditor`.

Yêu cầu:

- adapters mỏng;
- không fork workflow;
- không dùng `codex exec`, `claude -p`, daemon hoặc hidden subprocess;
- Claude adapter chỉ static validation, chưa runtime test.

### Bước 4 — Cập nhật tài liệu hệ thống

Cập nhật:

- `README.md`;
- `ARCHITECTURE.md`;
- `AGENTS.md`;
- `experiments/20260709_155523/roadmap.md`;
- `experiments/20260709_155523/metadata.yaml`.

Mục tiêu là để mọi agent/human sau này biết specialist mới tồn tại, dùng khi nào, và không dùng khi nào.

### Bước 5 — Viết test và validator

Tạo hoặc cập nhật tests để kiểm:

- thư mục specialist có `SKILL.md`;
- `agents/openai.yaml` tồn tại;
- Codex/Claude adapters tồn tại;
- validator chạy được;
- output schema hợp lệ;
- README/ARCHITECTURE/AGENTS có nhắc specialist mới.

### Bước 6 — Pilot 20–30 mẫu

Chạy thử trên một tập nhỏ, không ghi đè output chính:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/pilot_agent_audit/
```

Pilot cần kiểm:

- agent có dùng đúng raw checklist không;
- agent có truy xuất học liệu đúng không;
- agent có tạo `raw_dialogue_checklist_results.csv` đầy đủ không;
- agent có quá tự tin không;
- các lý do `uncertain` có hữu ích không;
- review queue có giúp người đọc hành động được không.

### Bước 7 — Quyết định có chạy rộng hay chưa

Chỉ chạy rộng sau khi Quân duyệt pilot. Nếu chạy rộng, cần xác định:

- chạy một agent hay chia shard;
- nếu chia shard, mỗi shard ghi file riêng;
- orchestrator merge output;
- không spawn nhiều instance cùng specialist nếu chưa được duyệt count/rationale/write paths/merge plan.

## 8. Quy tắc delegation khi dùng specialist

Trước mỗi lần gọi agent, orchestrator phải thông báo:

- Specialist: `hnmu-dialogue-auditor`;
- Model: `gpt-5.4-mini`, reasoning `medium` nếu chưa có quyết định khác;
- Task: kiểm mẫu dữ liệu thô HNMU theo raw checklist;
- Inputs: danh sách file và sample range;
- Allowed writes: thư mục output pilot/shard;
- Expected outputs: checklist results, quality suggestions, review queue suggestions, notes;
- Không được sửa raw Excel;
- Không được tạo benchmark samples.

Nếu native specialist visibility không có, dùng single-agent mode trong parent thread hoặc dừng lại; không chạy hidden subprocess.

## 9. Validation

Sau khi triển khai, chạy bằng môi trường chính:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/hnmu-dialogue-auditor

env PYTHONPATH=src /home/quannda/miniconda3/envs/benchmark_env/bin/python \
  agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py \
  experiments/20260709_155523/outputs/hnmu_dialogue_audit/pilot_agent_audit/raw_dialogue_checklist_results.csv

env PYTHONPATH=src /home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests -q
```

Nếu chỉ mới tạo agent nhưng chưa chạy pilot, validator output có thể chạy trên fixture test thay vì file pilot thật.

## 10. Tiêu chí hoàn thành

Plan này hoàn thành khi:

1. Specialist `hnmu-dialogue-auditor` có canonical skill và metadata.
2. Codex/Claude adapters tồn tại và không fork workflow.
3. Skill discovery link được tạo.
4. Validator output schema chạy được.
5. Tests hiện có và tests mới pass bằng `benchmark_env`.
6. README, ARCHITECTURE, AGENTS, roadmap và metadata đã cập nhật.
7. Có handoff ghi rõ agent mới dùng cho Plan 04, không dùng cho Plan 06/05.
8. Nếu có pilot, pilot output nằm ở thư mục riêng và chưa ghi đè output chính.

## 11. Quyết định đã chốt cho v0

- Duyệt tên specialist: `hnmu-dialogue-auditor`.
- Duyệt model mặc định cho Codex adapter: `gpt-5.4-mini`, reasoning `medium`.
- Plan này chỉ tạo specialist scaffold, adapter, validator, test và tài liệu liên quan.
- Plan 07 chỉ tạo specialist scaffold, adapter, validator, test và pilot nhỏ để kiểm thử agent.
- Chạy audit rộng bằng nhiều specialist/sub-agent là công việc của Plan 04, không phải Plan 07.
- Output pilot nhỏ được giữ riêng tại `experiments/20260709_155523/outputs/hnmu_dialogue_audit/pilot_agent_audit/`.

## 12. Kết quả triển khai v0

Đã tạo specialist `hnmu-dialogue-auditor` với phạm vi hẹp cho Plan 04. Các thành phần đã có:

- canonical skill: `agents/hnmu-dialogue-auditor/SKILL.md`;
- OpenAI/Codex UI metadata: `agents/hnmu-dialogue-auditor/agents/openai.yaml`;
- reference schema/workflow: `agents/hnmu-dialogue-auditor/references/`;
- validator: `agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py`;
- Codex adapter: `.codex/agents/hnmu-dialogue-auditor.toml`;
- Claude adapter: `.claude/agents/hnmu-dialogue-auditor.md`;
- discovery symlink: `.agents/skills/hnmu-dialogue-auditor`;
- tests: `tests/agents/test_hnmu_dialogue_auditor.py` và cập nhật adapter/validator tests;
- handoff: `experiments/20260709_155523/handoffs/hnmu-dialogue-auditor-specialist-036.md`.

Validation đã chạy bằng `/home/quannda/miniconda3/envs/benchmark_env/bin/python`:

```text
Skill is valid!
31 passed in 0.03s
```

Bước tiếp theo thuộc Plan 04: dùng specialist đã tạo để chạy audit ngữ nghĩa/sư phạm rộng hơn theo các shard bài học. Plan 07 không ghi đè hay merge output Plan 04.


## 13. Ranh giới với Plan 04

Plan 07 dừng ở việc tạo và kiểm thử specialist `hnmu-dialogue-auditor`. Việc chạy audit trên batch dữ liệu thô HNMU lớp 6–7, kể cả chia 3 shard theo bài học và spawn nhiều sub-agent, thuộc Plan 04.

Shard manifest đã tạo tại:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/pilot_agent_audit/lesson_based_shards/
```

Các file này được xem là input chuẩn bị cho Plan 04, không phải output hoàn tất của Plan 7.
