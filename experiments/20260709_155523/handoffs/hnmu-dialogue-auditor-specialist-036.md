# Handoff — Plan 07: specialist kiểm toán dữ liệu thô HNMU

Ngày: 17/07/2026
Trạng thái: đã triển khai v0.

## Kết quả

Đã tạo specialist `hnmu-dialogue-auditor` để phục vụ phần kiểm ngữ nghĩa/sư phạm của Plan 04.

Artifact chính:

- `agents/hnmu-dialogue-auditor/SKILL.md`
- `agents/hnmu-dialogue-auditor/agents/openai.yaml`
- `agents/hnmu-dialogue-auditor/references/raw-dialogue-audit-output-schema.md`
- `agents/hnmu-dialogue-auditor/references/raw-dialogue-audit-workflow.md`
- `agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py`
- `.codex/agents/hnmu-dialogue-auditor.toml`
- `.claude/agents/hnmu-dialogue-auditor.md`
- `.agents/skills/hnmu-dialogue-auditor`
- `tests/agents/test_hnmu_dialogue_auditor.py`

## Phạm vi agent

Agent chỉ kiểm mẫu dữ liệu thô HNMU theo checklist dữ liệu thô. Agent không tạo mẫu benchmark, không gán task chính thức, không sửa file Excel gốc, và không thay HNMU/UET chốt đúng/sai chuyên môn.

## Cách dùng dự kiến trong Plan 04

Chạy pilot trên một shard nhỏ trước, ví dụ 20–30 mẫu lớp 6–7, ghi vào thư mục riêng:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/pilot_agent_audit/
```

Output quan trọng nhất là:

```text
raw_dialogue_checklist_results.csv
```

Sau khi kiểm thử chất lượng output, orchestrator mới quyết định có merge các gợi ý vào output chính hay không.

## Validation

Validator schema đã có ở:

```text
agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py
```

Lệnh kiểm:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python   agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py   path/to/raw_dialogue_checklist_results.csv
```

## Cần làm tiếp

- Chạy pilot agent trên shard nhỏ sau khi Quân duyệt cách gọi specialist.
- Soi xem agent có dùng đúng checklist và truy xuất học liệu đúng không.
- Nếu pilot ổn, mới chạy rộng hơn cho batch lớp 6–7.
