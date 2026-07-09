# Plan 06 — Ví dụ phiếu tác giả từ ma trận bao phủ P05

Trạng thái: `APPROVED_COMPLETED_STUDENT_WORK_WITH_PROBLEM_STATEMENT_V5`  
Experiment: `20260705_215045`  
Owner chính: `teacher-collaboration-designer`  
Phụ thuộc: P05.

## 1. Mục tiêu

Tạo một bộ ví dụ phiếu tác giả đủ rõ để giáo viên HNMU hình dung cách tạo mẫu benchmark. P06 không bắt đầu từ con số 20 mẫu cố định, mà chọn một lát cắt đại diện từ ma trận bao phủ P05.

Mục tiêu thực tế:

1. Chọn một số ô `core` và `recommended` từ P05 để minh họa.
2. Viết ví dụ theo đúng tinh thần task/rubric P04.
3. Giải thích bằng ngôn ngữ dễ hiểu để giáo viên không phải đọc CSV/schema kỹ thuật.
4. Ghi rõ vì sao mỗi ví dụ được chọn và nó phủ phần nào của benchmark.

## 2. Input

- P05: `coverage_design/general_coverage_matrix_v0.csv`.
- P05: `coverage_design/coverage_axis_values_v0.csv`.
- P05: `coverage_design/coverage_matrix_readme_v0.md`.
- P04: `benchmark_design/benchmark_tasks.csv` và `benchmark_design/rubrics.csv`.
- P02: `topic_taxonomy/tin9_sgk_topics_v0.csv`.
- P02: `source_scope/scaffolding_function_notes.md` để dùng nhãn hỗ trợ tiếng Việt cho R3.
- Phiếu tác giả từ experiment `20260701_100006`, đặc biệt sheet “Luận giải chi tiết trường dữ liệu”, để bắt buộc ví dụ bám đúng trường dữ liệu đã chốt.


## 3. Không làm trong plan này

- Không tạo dataset đầy đủ.
- Không cố tạo đủ 96 ô của ma trận P05.
- Không sửa task/rubric P04.
- Không sửa ma trận P05.
- Không chấm mẫu thật của HNMU.
- Không yêu cầu giáo viên thao tác kỹ thuật với CSV/Git/schema.

## 4. Quy trình dự kiến

### Bước 1 — Chọn lát cắt ví dụ từ P05

Chọn trước các ô `core`, sau đó thêm một số ô `recommended` để đảm bảo có đủ:

- T1, T2, T3, T4;
- Biết, Hiểu, Vận dụng;
- một số cụm chủ đề SGK Tin học 9 khác nhau;
- các nhóm định dạng không quá lệch về lý thuyết hoặc lập trình;
- nhiều kiểu đề bài/bài làm/câu hỏi/sản phẩm của học sinh, ví dụ tự luận, code, bảng tính, sản phẩm số hoặc tình huống đạo đức số.

### Bước 2 — Viết ví dụ phiếu tác giả

Mỗi ví dụ phải có đủ các trường trong phiếu tác giả: tên người tạo, mã task, chủ đề, mức độ nhận thức, yêu cầu học sinh, bài làm học sinh, lịch sử trao đổi, học liệu tham khảo, câu trả lời mẫu, cách trả lời hợp lệ khác, điểm Likert theo rubric, độ chính xác kiến thức, tuân thủ ranh giới, người kiểm tra chéo, thời gian và ghi chú. Trường mức độ nhận thức dùng 3 giá trị Biết, Hiểu, Vận dụng. Các nhãn phân loại thiết kế được giữ ở bảng theo dõi nội bộ, không đưa vào trường `student_work` của phiếu.

### Bước 3 — Viết ví dụ chưa tốt

Tạo ít nhất một phản ví dụ để giáo viên thấy các lỗi thường gặp như: quá mơ hồ, không ghi chủ đề, không ghi mức hỗ trợ, hoặc viết câu trả lời gia sư quá lệch task.

### Bước 4 — Viết gói hướng dẫn HNMU

Chuyển các ví dụ thành hướng dẫn ngắn, dễ đọc, ưu tiên tiếng Việt, không dùng thuật ngữ kỹ thuật nếu không cần.

## 5. Output sở hữu

Plan này chỉ ghi vào:

```text
experiments/20260705_215045/teacher_examples/
experiments/20260705_215045/teacher_packet/
experiments/20260705_215045/reports/P06-*.md
experiments/20260705_215045/handoffs/P06-*.md
```

Artifact dự kiến:

| File | Vì sao tạo | Vai trò |
|---|---|---|
| `teacher_examples/author_form_field_reference_v0.csv` | Cần có bảng đối chiếu trực tiếp với sheet “Luận giải chi tiết trường dữ liệu”. | Là từ điển trường dữ liệu để kiểm tra ví dụ có bám phiếu tác giả hay không. |
| `teacher_examples/selected_coverage_cells_v0.csv` | Cần ghi rõ P06 chọn ô nào từ P05 và vì sao. | Cầu nối giữa ma trận bao phủ và ví dụ cụ thể. |
| `teacher_examples/author_form_example_*.md` | Giáo viên cần thấy mẫu điền hoàn chỉnh, không chỉ đọc mô tả trừu tượng. | Ví dụ phiếu tác giả theo từng tình huống. |
| `teacher_examples/author_form_counterexample.md` | Giáo viên cũng cần biết mẫu chưa tốt trông như thế nào. | Phản ví dụ để tránh lỗi phổ biến. |
| `teacher_packet/hnmu-pilot-authoring-guide.md` | Cần tài liệu gửi HNMU có thể đọc độc lập. | Hướng dẫn tạo mẫu pilot. |
| `teacher_packet/pilot-feedback-questions.md` | Cần thu phản hồi có cấu trúc sau khi giáo viên dùng thử. | Câu hỏi phản hồi cho HNMU. |
| `reports/P06-teacher-packet-summary.md` | Cần bản tóm tắt cho Quân/giáo sư. | Báo cáo ngắn về gói ví dụ. |

## 6. Acceptance criteria

- Ví dụ dùng đúng task T1–T4 và rubric R1–R5 từ P04.
- Mỗi ví dụ phải có đủ các trường trong sheet “Luận giải chi tiết trường dữ liệu” của `review_form.xlsx`, bao gồm trường `Mức độ nhận thức` (`cognitive_level`).
- Trường `student_work` gồm đề bài và bài làm của học sinh, ghi ngắn theo dạng `Đề bài: ...` và `Bài làm: ...`; nếu chưa có bài làm thì ghi `Bài làm: Chưa có bài làm.`
- Ví dụ chỉ dùng 3 mức nhận thức: Biết, Hiểu, Vận dụng.
- Mỗi ví dụ tham chiếu được `coverage_id` từ P05.
- Mỗi ví dụ có `student_work` rõ ràng để giáo viên thấy đề bài và bài làm/chỗ kẹt của học sinh nếu có.
- Có ít nhất một ví dụ thể hiện R3/giàn giáo với nhãn hỗ trợ tiếng Việt trong cột note.
- Hướng dẫn không yêu cầu giáo viên biết Git, CSV hoặc schema kỹ thuật.
- Có ghi rõ phần nào là ví dụ minh họa, phần nào là quy tắc bắt buộc.

## 7. Validation

- Kiểm tra mọi `coverage_id` được chọn tồn tại trong P05.
- Kiểm tra mọi `task_id` tồn tại trong P04.
- Kiểm tra mọi `topic_id` tồn tại trong P02.
- Đọc bằng mắt để bảo đảm giáo viên có thể làm theo mà không cần kiến thức kỹ thuật.

## 8. Handoff

Handoff cần nêu:

- ví dụ nào có thể gửi HNMU ngay;
- ví dụ nào còn cần HNMU/giáo sư xác nhận;
- phản hồi nào cần thu từ giáo viên sau pilot;
- nếu số ví dụ chưa đủ, cần chọn thêm ô nào từ P05.
