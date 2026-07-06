# Plan 01 — Thiết kế lại task/rubric theo Bloom và tạo ví dụ phiếu tác giả

Trạng thái: `SUPERSEDED_DRAFT` — không triển khai trực tiếp; đã được tách thành roadmap và các plan độc lập `02`–`07` trong cùng experiment  
Ngày tạo: 05/07/2026  
Experiment: `20260705_215045`  
Nguồn chính: note họp ngày 05/07/2026 trong `user_diary.md`.

## 0. Ghi chú supersede

Plan này là bản nháp monolithic đầu tiên sau họp 05/07/2026. Theo yêu cầu mới của người phụ trách dự án, plan đã được tách thành các plan nhỏ hơn, có ownership không chồng chéo và có thể commit độc lập. Không triển khai trực tiếp file này; dùng `roadmap.md` và các plan `02`–`07` thay thế.

## 1. Lý do

Sau họp ngày 05/07/2026, hướng ưu tiên của giáo sư là:

- coi phiếu tác giả là đã chốt tạm để chạy;
- tạo ví dụ minh họa để HNMU biết cách dùng phiếu;
- ưu tiên chia task theo độ khó/Bloom;
- giảm rubric còn khoảng 3–4 tiêu chí;
- mọi task/rubric cần có bằng chứng khoa học rõ ràng;
- dùng 20 mẫu đầu tiên của HNMU để kiểm tra lại khung thiết kế.

Plan này tách khỏi experiment `20260701_100006` để tránh trộn bản task/rubric v0 ngày 04/07 với hướng thiết kế mới.

## 2. Mục tiêu

Tạo một gói thiết kế tối thiểu để giáo viên có thể bắt đầu làm mẫu, gồm:

1. Bản đọc paper có mục tiêu cho MathTutorBench và VietLegal.
2. Bản task taxonomy mới theo Bloom/difficulty.
3. Bản rubric rút gọn 3–4 tiêu chí, có truy vết bằng chứng.
4. Bảng bao phủ tình huống để định hướng 20 mẫu đầu tiên.
5. Một số ví dụ phiếu tác giả đã điền mẫu.

## 3. Đầu vào

### 3.1. Từ repo

- `user_diary.md`, mục `Update plan (05-07-2026)`.
- `document/paper/source_paper/2502.18940v2.pdf`.
- `document/paper/source_paper/2512.14554v5.pdf`.
- `document/paper/source_paper/2510.02663v1.pdf`, nếu cần bổ sung căn cứ task/rubric gia sư.
- `experiments/20260701_100006/drive_snapshot/files/teacher_packet/review_form.xlsx`.
- `experiments/20260701_100006/benchmark_spec/task_code_registry.csv`.
- `experiments/20260701_100006/benchmark_spec/rubric_dimensions.csv`.
- `experiments/20260701_100006/learning_resources/learning_resource_fragments_v0.csv`.

### 3.2. Từ HNMU/UET sau này

- Comment của HNMU trong sheet `Luận giải chi tiết trường dữ liệu`.
- Khoảng 20 mẫu pilot do HNMU tạo.
- Quyết định của giáo sư về task chính: Bloom-only hay tổ hợp Bloom với format/topic.

## 4. Phạm vi file dự kiến

Chỉ tạo/sửa trong:

```text
experiments/20260705_215045/
```

| Đường dẫn | Vai trò | Lý do tạo |
|---|---|---|
| `literature_notes/` | Ghi chú đọc paper có mục tiêu. | Cần bằng chứng khoa học cho task/rubric, không chỉ intuition. |
| `benchmark_design/` | Task taxonomy theo Bloom, rubric rút gọn, bảng bao phủ tình huống. | Đây là lõi thiết kế mới sau họp 05/07. |
| `teacher_examples/` | Ví dụ phiếu tác giả đã điền mẫu. | HNMU cần nhìn mẫu cụ thể để tạo 20 mẫu đầu tiên. |
| `reports/` | Ghi chú họp, state transfer, summary gửi người phụ trách/giáo sư. | Lớp đọc nhanh, không bắt người đọc mở CSV. |
| `handoffs/` | Bàn giao nếu dùng specialist/single-agent fallback. | Tuân thủ quy trình observability. |
| `coordination/` | Log delegation/fallback. | Truy vết ai làm gì, input/output nào. |

## 5. Artifact dự kiến

| File | Vai trò |
|---|---|
| `literature_notes/mathtutorbench-task-rubric-notes.md` | Đọc MathTutorBench để rút ra cách chia task theo phẩm chất gia sư và rubric. |
| `literature_notes/vietlegal-bloom-difficulty-notes.md` | Đọc VietLegal để rút ra cách chia độ khó theo Bloom. |
| `literature_notes/evidence-to-design-matrix.csv` | Nối claim thiết kế với paper/source cụ thể. |
| `benchmark_design/bloom_task_taxonomy_v0.md` | Định nghĩa task/mức Bloom bản v0. |
| `benchmark_design/bloom_task_registry.csv` | Bảng máy đọc được cho task/mức Bloom. |
| `benchmark_design/compact_rubric_v0.md` | Rubric rút gọn 3–4 tiêu chí. |
| `benchmark_design/compact_rubric.csv` | Bảng máy đọc được cho rubric rút gọn. |
| `benchmark_design/case_coverage_matrix.csv` | Bảng bao phủ tình huống: topic × Bloom × format × case gia sư. |
| `teacher_examples/author_form_example_*.md` | Ví dụ phiếu tác giả đã điền bằng văn bản dễ đọc. |
| `reports/professor-review-brief.md` | Bản tóm tắt gửi giáo sư để review nhanh. |

## 6. Quy trình đề xuất

### Bước 1 — Đọc paper có mục tiêu

Đọc `2502.18940v2.pdf` và `2512.14554v5.pdf`, tập trung vào:

- cách định nghĩa task;
- cách phân tầng độ khó;
- cách thiết kế rubric;
- cách chứng minh coverage/diversity;
- vai trò con người trong tạo/chấm dữ liệu.

Đầu ra:

```text
literature_notes/mathtutorbench-task-rubric-notes.md
literature_notes/vietlegal-bloom-difficulty-notes.md
literature_notes/evidence-to-design-matrix.csv
```

### Bước 2 — Thiết kế task theo Bloom

Tạo bản taxonomy v0 với bốn mức:

- Nhận biết.
- Thông hiểu.
- Vận dụng.
- Vận dụng cao.

Cần quyết định liệu task chính chỉ là Bloom level hay là tổ hợp `Bloom × format × topic`.

Đầu ra:

```text
benchmark_design/bloom_task_taxonomy_v0.md
benchmark_design/bloom_task_registry.csv
```

### Bước 3 — Rút gọn rubric

Gom D1–D9 của experiment cũ thành khoảng 3–4 rubric có thể chấm được:

1. Đúng chuyên môn và bám học liệu/chương trình.
2. Phù hợp mức nhận thức, chủ đề và tiền kiến thức.
3. Chất lượng sư phạm/giàn giáo của phản hồi gia sư.
4. An toàn, công bằng và không bịa nguồn/quy định — có thể là rubric hoặc policy lỗi nghiêm trọng.

Đầu ra:

```text
benchmark_design/compact_rubric_v0.md
benchmark_design/compact_rubric.csv
```

### Bước 4 — Lập bảng bao phủ tình huống

Tạo matrix để định hướng 20 mẫu đầu tiên:

```text
chủ đề lớp 9 × mức Bloom × định dạng câu hỏi × kiểu hỗ trợ gia sư
```

Đầu ra:

```text
benchmark_design/case_coverage_matrix.csv
```

### Bước 5 — Tạo ví dụ phiếu tác giả

Viết một số ví dụ đã điền theo phiếu tác giả, ưu tiên bao phủ:

- ít nhất 4 mức Bloom;
- ít nhất 3–4 format;
- một số chủ đề lớp 9 quan trọng;
- có mã học liệu hoặc fragment học liệu v0;
- có lịch sử trao đổi theo đúng quy ước bước/lượt.

Đầu ra:

```text
teacher_examples/author_form_example_*.md
reports/professor-review-brief.md
```

## 7. Acceptance criteria

- Mỗi task/mức Bloom có định nghĩa dễ hiểu và ví dụ phân biệt.
- Rubric rút gọn còn 3–4 tiêu chí, nhưng không làm mất khả năng phát hiện lỗi nghiêm trọng.
- Mỗi quyết định thiết kế quan trọng có evidence hoặc nhãn `cần HNMU/giáo sư xác nhận`.
- Bảng bao phủ tình huống đủ để hướng dẫn 20 mẫu pilot đầu tiên.
- Ví dụ phiếu tác giả đủ cụ thể để giáo viên nhìn vào là biết cách làm.

## 8. Ranh giới

- Chưa sửa `review_form.xlsx`.
- Chưa chốt benchmark chính thức.
- Chưa thay thế toàn bộ task/rubric v0 của `20260701_100006`; chỉ thiết kế hướng mới.
- Chưa mở rộng coverage lớp 6–8 nếu chưa có học liệu bóc tách đủ chắc.
- Không spawn nhiều specialist cùng lúc nếu chưa có duyệt riêng.
