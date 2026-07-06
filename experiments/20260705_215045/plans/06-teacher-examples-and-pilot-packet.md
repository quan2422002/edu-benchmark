# Plan 06 — Ví dụ phiếu tác giả và gói pilot cho HNMU

Trạng thái: `DRAFT` — chờ duyệt  
Experiment: `20260705_215045`  
Owner chính: `teacher-collaboration-designer`  
Phụ thuộc: P05.

## 1. Mục tiêu

Tạo các ví dụ cụ thể theo phiếu tác giả để giáo viên HNMU hiểu cách tạo mẫu. Đây là plan chuyển thiết kế kỹ thuật thành hướng dẫn làm việc thực tế cho giáo viên.

## 2. Input

- P05: `pilot_20_sample_allocation.csv`, `format_taxonomy_v0.md`.
- P04: compact rubric và task/Bloom registry.
- P02: topic taxonomy và mã học liệu/chủ đề.
- Phiếu tác giả: `review_form.xlsx` từ experiment `20260701_100006`.

## 3. Không làm trong plan này

- Không sửa phiếu tác giả gốc.
- Không chấm mẫu thật của HNMU.
- Không quyết định thay HNMU về nội dung chuyên môn.
- Không yêu cầu giáo viên sửa CSV/Git/schema.

## 4. Output sở hữu

Plan này chỉ ghi vào:

```text
experiments/20260705_215045/teacher_examples/
experiments/20260705_215045/teacher_packet/
experiments/20260705_215045/reports/P06-*.md
experiments/20260705_215045/handoffs/P06-*.md
```

Artifact dự kiến:

| File | Vai trò |
|---|---|
| `teacher_examples/author_form_example_01.md` | Ví dụ hoàn chỉnh mức Nhận biết. |
| `teacher_examples/author_form_example_02.md` | Ví dụ hoàn chỉnh mức Thông hiểu. |
| `teacher_examples/author_form_example_03.md` | Ví dụ hoàn chỉnh mức Vận dụng. |
| `teacher_examples/author_form_example_04.md` | Ví dụ hoàn chỉnh mức Vận dụng cao. |
| `teacher_examples/author_form_counterexample.md` | Ví dụ điền chưa tốt để giáo viên tránh. |
| `teacher_packet/hnmu-pilot-authoring-guide.md` | Hướng dẫn ngắn cho HNMU tạo 20 mẫu. |
| `teacher_packet/pilot-feedback-questions.md` | Câu hỏi để HNMU phản hồi sau khi tạo mẫu. |
| `reports/P06-teacher-packet-summary.md` | Bản tóm tắt gửi Quân/giáo sư. |

## 5. Acceptance criteria

- Mỗi ví dụ điền đủ trường cốt lõi trong phiếu tác giả.
- Có ít nhất một ví dụ cho mỗi mức Bloom.
- Có ít nhất một ví dụ thể hiện lịch sử trao đổi theo bước/lượt.
- Có mã học liệu/chủ đề hoặc ghi rõ nếu mã học liệu tạm thời.
- Hướng dẫn không yêu cầu giáo viên thao tác kỹ thuật.

## 6. Validation

- Chạy validator teacher packet nếu output theo schema task-card hiện có.
- Kiểm tra bằng mắt: giáo viên có thể làm theo mà không cần biết Git/CSV/schema.
- Kiểm tra mọi mã topic/task/học liệu tham chiếu tồn tại trong P02–P05.

## 7. Handoff

Handoff cần nêu:

- ví dụ nào gửi HNMU được ngay;
- ví dụ nào còn cần HNMU/giáo sư xác nhận;
- phản hồi nào cần thu từ giáo viên sau pilot.
