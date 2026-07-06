# Plan 04 — Task taxonomy theo Bloom và rubric rút gọn

Trạng thái: `DRAFT` — chờ duyệt  
Experiment: `20260705_215045`  
Owner chính: `benchmark-specification-designer`  
Phụ thuộc: P02 và P03.

## 1. Mục tiêu

Thiết kế bản task/rubric mới theo hướng giáo sư chốt ngày 05/07/2026:

- task ưu tiên theo độ khó/Bloom;
- rubric rút gọn còn khoảng 3–4 tiêu chí;
- task/rubric có truy vết tới evidence paper và học liệu/chủ đề;
- task T01–T07 cũ chỉ dùng như nhãn hành vi gia sư/case tương tác nếu hữu ích.

## 2. Input

- P02: `topic_taxonomy/thcs_topic_taxonomy_v0.csv`, `coverage_unit_registry.csv`.
- P03: `literature_notes/evidence_to_design_matrix.csv`, synthesis report.
- Tham khảo: `experiments/20260701_100006/benchmark_spec/task_code_registry.csv`.
- Tham khảo: `experiments/20260701_100006/benchmark_spec/rubric_dimensions.csv`.
- Tham khảo: `experiments/20260701_100006/benchmark_spec/rubric_error_mapping.csv`.

## 3. Không làm trong plan này

- Không sửa taxonomy chủ đề của P02.
- Không sửa evidence matrix của P03.
- Không tạo ví dụ phiếu tác giả cho giáo viên.
- Không phân tích 20 mẫu pilot.

## 4. Output sở hữu

Plan này chỉ ghi vào:

```text
experiments/20260705_215045/benchmark_design/
experiments/20260705_215045/reports/P04-*.md
experiments/20260705_215045/handoffs/P04-*.md
```

Artifact dự kiến:

| File | Vai trò |
|---|---|
| `benchmark_design/bloom_task_taxonomy_v0.md` | Luận giải 4 mức Bloom trong bối cảnh Tin học 9 và gia sư LLM. |
| `benchmark_design/bloom_task_registry.csv` | Mã task/mức Bloom, định nghĩa, input/output, trạng thái. |
| `benchmark_design/tutor_behavior_case_labels.csv` | Nhãn phụ lấy từ T01–T07 cũ, dùng để mô tả kiểu hỗ trợ gia sư. |
| `benchmark_design/compact_rubric_v0.md` | Rubric 3–4 tiêu chí bằng văn xuôi. |
| `benchmark_design/compact_rubric.csv` | Rubric máy đọc được. |
| `benchmark_design/serious_error_policy_v0.md` | Policy lỗi nghiêm trọng tách khỏi rubric chính nếu cần. |
| `benchmark_design/design_provenance_matrix.csv` | Task/rubric/policy → evidence paper → topic/học liệu → quyết định cần xác nhận. |
| `reports/P04-design-open-questions.md` | Câu hỏi cần giáo sư/HNMU chốt. |

## 5. Acceptance criteria

- Bốn mức Bloom có định nghĩa phân biệt rõ, có ví dụ ngắn trong Tin học 9.
- Rubric còn 3–4 tiêu chí nhưng vẫn bao phủ: đúng chuyên môn, phù hợp mức/chủ đề, chất lượng gia sư, an toàn/ranh giới hoặc policy lỗi.
- Mỗi rubric có observable evidence: reviewer nhìn vào phản hồi/hội thoại để chấm được.
- Mỗi claim chính có evidence hoặc nhãn `teacher_decision_needed`.
- Không tuyên bố benchmark chính thức nếu HNMU/giáo sư chưa xác nhận.

## 6. Validation

- Chạy validator benchmark spec nếu xuất các CSV theo schema.
- Kiểm tra mọi `topic_id` dùng trong task tồn tại trong P02.
- Kiểm tra mọi `research_id` dùng trong provenance tồn tại trong P03.

## 7. Handoff

Handoff phải chỉ rõ:

- rubric nào được gom từ D1–D9;
- task T01–T07 cũ được dùng như thế nào;
- điểm nào cần giáo sư/HNMU chốt trước khi tạo ví dụ đại trà.
