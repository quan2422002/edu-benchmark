# Plan 05 — Ma trận bao phủ tổng quát cho task/rubric và pilot

Trạng thái: `APPROVED_COMPLETED_GENERAL_COVERAGE_V0_PLUS_STUDENT_WORK_TYPE`
Experiment: `20260705_215045`
Owner chính: `benchmark-specification-designer`
Phụ thuộc: P02, P03, P04.

## 1. Mục tiêu

Tạo ma trận bao phủ tổng quát để nhìn được không gian thiết kế benchmark trước khi viết mẫu pilot.

Điểm điều chỉnh quan trọng so với bản nháp cũ: **không khóa P05 vào đúng 20 mẫu pilot**. Con số 20 chỉ còn là một lát cắt tượng trưng để chạy thử sau này. P05 cần trả lời câu hỏi lớn hơn: nếu benchmark gia sư AI môn Tin học 9 muốn bao phủ tốt, nó cần nhìn theo những trục nào và vùng nào nên ưu tiên trước?

Ba mục tiêu kiểm soát chính:

1. Độ phủ task/hành vi gia sư.
2. Độ phủ mức nhận thức: Biết, Hiểu, Vận dụng.
3. Độ phủ chủ đề SGK Tin học 9 và định dạng mẫu.
4. Độ phủ dạng bài làm/câu hỏi/sản phẩm của học sinh.

## 2. Giả định đã chốt tạm

Theo chỉ đạo mới, các câu hỏi mở từ P04 được coi là tạm chốt để dự án tiếp tục chạy. Nếu HNMU hoặc giáo sư phản hồi khác sau này, ta sẽ cập nhật quy tắc/ưu tiên của ma trận thay vì dừng toàn bộ tiến độ.

Các giả định P05 dùng:

- Task lấy từ P04: T1, T2, T3, T4.
- Rubric lấy từ P04: R1–R5, thang Likert 1–5.
- Mức nhận thức lấy từ P02 rút gọn: Biết, Hiểu, Vận dụng.
- Chủ đề lấy từ mục lục SGK Tin học 9 trong P02.
- Định dạng mẫu chỉ là nhóm thiết kế ban đầu, chưa phải schema cuối cùng của phiếu tác giả.
- Dạng bài làm của học sinh được tách thành trục `student_work_type`, dựa trên P03 và phạm vi SGK Tin học 9.

## 3. Input

- `experiments/20260705_215045/benchmark_design/benchmark_tasks.csv`: danh sách task P04.
- `experiments/20260705_215045/benchmark_design/rubrics.csv`: rubric P04.
- `experiments/20260705_215045/topic_taxonomy/tin9_sgk_topics_v0.csv`: chủ đề SGK Tin học 9 từ P02.
- `experiments/20260705_215045/source_scope/cognitive_level_seed_map.md`: quyết định dùng 3 mức nhận thức.
- `experiments/20260705_215045/source_scope/scaffolding_function_notes.md`: nhãn hỗ trợ dùng cho R3.
- `experiments/20260705_215045/reports/P03-literature-synthesis-for-design.md`: căn cứ từ review 3 paper hạt giống.

## 4. Không làm trong plan này

- Không tạo ví dụ chi tiết cho từng mẫu; việc đó thuộc P06.
- Không tạo hoặc sửa phiếu tác giả.
- Không sửa task/rubric P04.
- Không sửa taxonomy chủ đề P02.
- Không chấm mẫu thật của HNMU.
- Không tạo mã lỗi nghiêm trọng.
- Không ép phải có đúng 20 mẫu.

## 5. Quy trình thực hiện

### Bước 1 — Chốt trục bao phủ

Xác định các trục bắt buộc của ma trận:

- task;
- mức nhận thức;
- cụm chủ đề SGK Tin học 9;
- nhóm định dạng mẫu;
- dạng bài làm/câu hỏi/sản phẩm của học sinh;
- mức ưu tiên bao phủ.

### Bước 2 — Tạo bảng giá trị hợp lệ cho từng trục

Viết `coverage_axis_values_v0.csv` để mọi người biết mỗi mã trong ma trận nghĩa là gì và đến từ đâu.

### Bước 3 — Sinh ma trận bao phủ tổng quát

Kết hợp 4 task × 3 mức nhận thức × 8 cụm chủ đề SGK Tin học 9. Mỗi ô có:

- task;
- mức nhận thức;
- chủ đề;
- định dạng nên ưu tiên;
- dạng bài làm/câu hỏi/sản phẩm nên ưu tiên;
- mức ưu tiên;
- gợi ý ngắn cho người viết mẫu;
- ghi chú rủi ro/cần rà soát.

### Bước 4 — Viết cách đọc và chỉ số kiểm soát độ phủ

Viết tài liệu giải thích để P06 có thể dùng ma trận này chọn lát cắt mẫu. Mục tiêu là tránh tình trạng “đủ số lượng nhưng lệch thiết kế”.

### Bước 5 — Handoff sang P06

Bàn giao rõ P06 nên chọn ô `core` và `recommended` trước, không cần cố phủ toàn bộ ma trận trong pilot đầu.

## 6. Output sở hữu

Plan này chỉ ghi vào:

```text
experiments/20260705_215045/coverage_design/
experiments/20260705_215045/reports/P05-*.md
experiments/20260705_215045/handoffs/P05-*.md
```

Artifact:


| File                                             | Vì sao tạo                                                                                                                                          | Vai trò                                                                            |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `coverage_design/coverage_axis_values_v0.csv`    | Cần bảng giải nghĩa mã để tránh mỗi người hiểu task/chủ đề/format/dạng bài làm theo một cách.                                     | Từ điển giá trị hợp lệ cho các trục bao phủ, bao gồm`student_work_type`. |
| `coverage_design/general_coverage_matrix_v0.csv` | Cần nhìn toàn bộ không gian task × mức nhận thức × chủ đề trước khi chọn mẫu, đồng thời thấy rõ dạng bài làm của học sinh. | Ma trận bao phủ tổng quát, hiện có 96 ô và cột`student_work_type`.         |
| `coverage_design/coverage_summary_v0.csv`        | Cần kiểm tra nhanh phân bố theo một số trục mà không phải đọc toàn bộ ma trận.                                                         | Bảng đếm hỗ trợ rà soát.                                                     |
| `coverage_design/coverage_matrix_readme_v0.md`   | Cần giải thích cách đọc ma trận cho P06 và người không trực tiếp tạo file CSV.                                                          | Hướng dẫn sử dụng ma trận.                                                    |
| `coverage_design/coverage_metrics_v0.md`         | Cần tiêu chí chọn lát cắt pilot bất kỳ, không phụ thuộc số 20.                                                                            | Quy tắc kiểm soát độ phủ của tập mẫu.                                      |
| `reports/P05-general-coverage-brief.md`          | Cần bản đọc nhanh cho Quân/giáo sư/HNMU.                                                                                                       | Tóm tắt kết quả và quyết định thiết kế.                                   |
| `handoffs/P05-general-coverage-matrix-023.md`    | Cần bàn giao rõ cho P06.                                                                                                                           | Handoff sang bước viết ví dụ/packet.                                           |

## 7. Acceptance criteria

- Ma trận dùng đúng task T1–T4 từ P04.
- Ma trận dùng đúng 3 mức nhận thức: Biết, Hiểu, Vận dụng.
- Mọi `topic_id` trong ma trận tồn tại trong taxonomy P02.
- Mọi nhóm định dạng được định nghĩa trong `coverage_axis_values_v0.csv`.
- Có mức ưu tiên để chọn mẫu, thay vì coi mọi ô ngang nhau.
- Có `primary_student_work_type` và `secondary_student_work_type` để thể hiện rõ dạng bài làm/câu hỏi/sản phẩm của học sinh.
- Có tài liệu giải thích cách dùng ma trận cho P06.

## 8. Validation

- Kiểm tra `general_coverage_matrix_v0.csv` có 96 dòng dữ liệu.
- Kiểm tra mọi task ID tồn tại trong `benchmark_tasks.csv`.
- Kiểm tra mọi topic ID tồn tại trong `tin9_sgk_topics_v0.csv`.
- Kiểm tra mọi mức nhận thức thuộc tập `{Biết, Hiểu, Vận dụng}`.
- Kiểm tra mọi `student_work_type` tồn tại trong `coverage_axis_values_v0.csv`.
- Chạy `pytest tests/agents -q` để bảo đảm không ảnh hưởng phần agent hiện có.

## 9. Handoff

Handoff cần nêu:

- file nào là input chính cho P06;
- cách chọn ô ưu tiên cho ví dụ phiếu tác giả;
- rủi ro còn lại về OCR mục lục SGK và xác nhận HNMU;
- nhắc lại rằng 20 mẫu chỉ là lát cắt pilot, không phải cấu trúc benchmark.
