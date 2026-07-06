# Plan 05 — Bảng bao phủ tình huống và phân bổ 20 mẫu pilot

Trạng thái: `DRAFT` — chờ duyệt  
Experiment: `20260705_215045`  
Owner chính: `benchmark-specification-designer`  
Phụ thuộc: P02 và P04.

## 1. Mục tiêu

Tạo bảng bao phủ tình huống để kiểm soát ba tiêu chí benchmark tốt mà giáo sư nêu:

1. Độ phủ kiến thức.
2. Độ phân hóa theo Bloom.
3. Độ đa dạng định dạng.

Bảng này dùng để định hướng 20 mẫu pilot đầu tiên của HNMU, tránh tình trạng mẫu tạo ra bị lệch quá nhiều về một chủ đề, một mức Bloom hoặc một format dễ làm.

## 2. Input

- P02: taxonomy chủ đề và coverage unit.
- P04: Bloom task registry, compact rubric, tutor behavior labels.
- Phiếu tác giả từ `20260701_100006/drive_snapshot/files/teacher_packet/review_form.xlsx` để biết các trường giáo viên sẽ điền.

## 3. Không làm trong plan này

- Không tạo ví dụ chi tiết cho từng mẫu; việc đó thuộc P06.
- Không sửa task/rubric của P04.
- Không sửa topic taxonomy của P02.
- Không nhận/phân tích mẫu thật; việc đó thuộc P07.

## 4. Output sở hữu

Plan này chỉ ghi vào:

```text
experiments/20260705_215045/coverage_design/
experiments/20260705_215045/reports/P05-*.md
experiments/20260705_215045/handoffs/P05-*.md
```

Artifact dự kiến:

| File | Vai trò |
|---|---|
| `coverage_design/case_coverage_matrix.csv` | Matrix `topic × Bloom × format × tutor_behavior_case`. |
| `coverage_design/pilot_20_sample_allocation.csv` | Đề xuất phân bổ 20 mẫu đầu tiên. |
| `coverage_design/format_taxonomy_v0.md` | Định nghĩa format: trắc nghiệm, tự luận lý thuyết, sửa lỗi code Scratch/Python, viết chương trình. |
| `coverage_design/coverage_metrics_v0.md` | Cách tính coverage/difficulty/format diversity ở mức pilot. |
| `reports/P05-pilot-allocation-brief.md` | Bản đọc nhanh cho Quân/giáo sư/HNMU. |

## 5. Acceptance criteria

- Mỗi dòng trong allocation có topic, Bloom level, format, case gia sư, và rationale.
- 20 mẫu pilot không tập trung vào một topic/format duy nhất.
- Có ghi rõ phần nào là bắt buộc, phần nào là khuyến nghị nếu HNMU thiếu thời gian.
- Có thể dùng output P05 làm input trực tiếp để viết ví dụ P06.

## 6. Validation

- Kiểm tra mọi topic ID tồn tại trong P02.
- Kiểm tra mọi Bloom/task ID tồn tại trong P04.
- Kiểm tra mọi format nằm trong `format_taxonomy_v0.md`.
- Kiểm tra tổng allocation = 20 hoặc có lý do nếu khác.

## 7. Handoff

Handoff cần nêu rõ:

- phân bổ 20 mẫu đề xuất;
- rủi ro coverage còn lại;
- phần nào cần HNMU xác nhận trước khi giao giáo viên làm mẫu.
