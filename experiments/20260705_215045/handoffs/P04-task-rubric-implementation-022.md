# Handoff P04 — Task và rubric rút gọn v0

## Trạng thái

P04 task/rubric-only đã được triển khai ở mức v0. Tất cả task và rubric hiện để trạng thái `needs_hnmu_review`, vì cần giáo sư/HNMU xác nhận trước khi dùng làm benchmark chính thức.

## Input đã dùng

- P02: `topic_taxonomy/tin9_sgk_topics_v0.csv`, `source_scope/cognitive_level_seed_map.md`, `source_scope/scaffolding_function_notes.md`, `source_scope/sgk_sgv_source_registry.csv`.
- P03: `reports/P03-literature-synthesis-for-design.md`, `literature_notes/evidence_to_design_matrix.csv`, `literature_notes/evidence_matrix.csv`.
- Plan P04 đã duyệt trong thread: task/rubric-only, không tạo mã lỗi nghiêm trọng.

## Output đã tạo

| Artifact | Vai trò |
|---|---|
| `benchmark_design/task_design_rationale_v0.md` | Luận giải task T1–T4 theo hành vi gia sư. |
| `benchmark_design/benchmark_tasks.csv` | Bảng task máy đọc được theo schema hiện có. |
| `benchmark_design/rubric_design_rationale_v0.md` | Luận giải rubric R1–R5, ranh giới giữa các rubric và thang Likert 1–5. |
| `benchmark_design/rubrics.csv` | Bảng 20 dòng task-rubric: T1_R1 ... T4_R5. |
| `reports/P04-task-rubric-open-questions.md` | Câu hỏi mở cho giáo sư/HNMU và input cho P05/P06. |

## Tóm tắt thiết kế

Task v0:

- `T1`: Giải thích thích ứng.
- `T2`: Phản hồi bài làm hoặc lập luận của học sinh.
- `T3`: Gợi ý từng bước để học sinh tự đi tiếp.
- `T4`: Chẩn đoán lỗi, hiểu lầm hoặc thiếu nền tảng.

Rubric v0:

- `R1`: Độ chính xác kiến thức và bám học liệu.
- `R2`: Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh.
- `R3`: Chất lượng hỗ trợ sư phạm/giàn giáo.
- `R4`: Tuân thủ mục tiêu task, yêu cầu học sinh và phạm vi Tin học 9.
- `R5`: Tuân thủ ranh giới an toàn, đạo đức và pháp lý.

## Validation đã chạy

- Kiểm tra `benchmark_tasks.csv` đủ cột, không trùng `task_id`.
- Kiểm tra `rubrics.csv` đủ cột, không trùng `rubric_id`, mọi `task_id` đều tồn tại.
- Kiểm tra các claim `P03-C...` được dùng đều có trong tập claim P03 đã biết.
- Kiểm tra các learning material ID được dùng đều có trong registry P02.
- Kiểm tra `tin9_sgk_topics_v0.csv` không có bài học thiếu `parent_id`.
- `pytest tests/agents -q` cần chạy sau khi handoff này được tạo.

## Quyết định cần người phụ trách/HNMU chốt

1. T4 là task độc lập hay nhãn phụ?
2. R1–R5 đã đủ gọn và đủ phân biệt chưa?
3. Mô tả thang Likert 1–5 đã đủ rõ cho giáo viên chấm thử chưa?
4. P05 phân bổ 20 mẫu pilot theo task × mức nhận thức × chủ đề như thế nào?
5. Có cần plan riêng cho catalog mã lỗi nghiêm trọng sau khi task/rubric được duyệt không?
