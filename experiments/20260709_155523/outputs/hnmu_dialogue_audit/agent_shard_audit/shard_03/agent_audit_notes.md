# Agent audit notes — SHARD 03

- checked_by: `hnmu-dialogue-auditor(shard-03)`
- checked_at: `2026-07-17T23:19:58+07:00`
- Scope: `experiments/20260709_155523/outputs/hnmu_dialogue_audit/pilot_agent_audit/lesson_based_shards/shard_03_input_samples.csv`
- Sample count: 154; unique sample_id: 154; checklist rows: 2464
- Allowed write path used: `experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/shard_03/`
- Không sửa raw Excel, normalized data, checklist, skill hoặc output shard khác.

## Lesson coverage trong shard

- Lớp 6 — Bài 11: Định dạng văn bản: 14 mẫu
- Lớp 6 — Bài 14: Hoàn thiện sổ lưu niệm: 14 mẫu
- Lớp 6 — Bài 17: Chương trình máy tính: 14 mẫu
- Lớp 6 — Bài 4. Mạng máy tính: 14 mẫu
- Lớp 6 — Bài 7: Tìm kiếm thông tin trên Internet: 14 mẫu
- Lớp 7 — Bài 1. Thiết bị vào - ra: 14 mẫu
- Lớp 7 — Bài 12: Định dạng đối tượng trên trang chiếu: 14 mẫu
- Lớp 7 — Bài 15. Thuật toán tìm kiếm nhị phân: 14 mẫu
- Lớp 7 — Bài 3. Quản lí dữ liệu trong máy tính: 14 mẫu
- Lớp 7 — Bài 6: Làm quen với phần mềm bảng tính: 14 mẫu
- Lớp 7 — Bài 9: Trình bày bảng tính: 14 mẫu

## Kết quả tổng hợp

- `raw_dialogue_checklist_results.csv`: 2464 dòng = 154 mẫu × 16 tiêu chí.
- Phân bố result: fail=7, not_applicable=3, pass=2436, uncertain=18
- `quality_check_suggestions.csv`: fail=2, needs_human_review=13, pass=139
- `hnmu_review_queue_suggestions.csv`: 15 dòng; priority: high=2, medium=13

## Mẫu cần chú ý

- Thiếu hội thoại: HNMU-G6-R0045-STT2.
- Nhãn lượt nói lạ: HNMU-G7-R0010-STT9.
- Evidence SGV yếu/cần xác minh: HNMU-G6-R0148-STT7, HNMU-G6-R0150-STT9, HNMU-G6-R0155-STT14, HNMU-G6-R0189-STT6, HNMU-G6-R0190-STT7, HNMU-G6-R0191-STT8, HNMU-G6-R0194-STT11, HNMU-G6-R0196-STT13, HNMU-G6-R0234-STT9, HNMU-G7-R0078-STT7, HNMU-G7-R0116-STT3, HNMU-G7-R0120-STT7, HNMU-G7-R0123-STT10.

## Major uncertainty/failure patterns

- Phần lớn SGK/SGV evidence truy xuất được nhưng fragment có `status=draft`; dùng được để định hướng audit, chưa phải xác nhận chuyên môn cuối cùng của HNMU/UET.
- Hai lỗi cơ học quan trọng từ output Plan 04 chính vẫn xuất hiện trong shard: một mẫu thiếu `dialogue`, một mẫu có nhãn `AII`.
- Một nhóm nhỏ mẫu có `RAW-CON-02=uncertain` vì matcher SGV yếu dù câu hỏi/hội thoại nhìn chung bám bài; cần HNMU/UET hoặc cải thiện retrieval SGV xác minh.
- Tiêu chí lộ đáp án sớm/khuôn hội thoại lặp lại chỉ được kiểm sơ bộ ở mức shard; khi merge toàn batch nên kiểm lại pattern liên shard trước khi chọn mẫu Plan 06.

## Validation command

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/shard_03/raw_dialogue_checklist_results.csv
```
