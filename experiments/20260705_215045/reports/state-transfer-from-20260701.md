# State transfer từ experiment `20260701_100006`

Ngày tạo: 05/07/2026  
Experiment mới: `20260705_215045`  
Nguồn đối chiếu: artifact trong `experiments/20260701_100006`.

## 1. Trạng thái hiện tại trước khi chuyển experiment

Experiment `20260701_100006` đã tạo được nền tảng v0:

- snapshot Drive của `review_form.xlsx`, `literature_review`, `curriculum_sources`;
- review phiếu tác giả;
- source map và fragment map học liệu v0;
- topic map Tin học 6–9 bản rất thận trọng;
- benchmark task/rubric/mã lỗi/provenance v0;
- danh sách câu hỏi mở gửi HNMU/UET.

Tuy nhiên, sau họp ngày 05/07/2026, hướng thiết kế cần chuyển trọng tâm sang Bloom/difficulty và ví dụ minh họa cho giáo viên.

## 2. Artifact nên dùng tiếp

| Artifact cũ | Vai trò trong experiment mới |
|---|---|
| `author_form/author_form_field_review.md` | Hiểu ý nghĩa trường phiếu tác giả và các điểm dễ nhầm. |
| `drive_snapshot/files/teacher_packet/review_form.xlsx` | Nguồn phiếu tác giả đã chốt tạm để tạo ví dụ. |
| `benchmark_spec/task_code_registry.csv` | Nguồn nhãn hành vi gia sư T01–T07; không nên mặc định là trục task chính nữa. |
| `benchmark_spec/rubric_dimensions.csv` | Nguồn để gom D1–D9 thành 3–4 rubric mới. |
| `benchmark_spec/rubric_error_mapping.csv` | Nguồn policy lỗi nghiêm trọng, tránh hiểu lỗi nghiêm trọng = 0 toàn bộ. |
| `learning_resources/learning_resource_source_map.csv` | Nguồn mã học liệu v0. |
| `learning_resources/learning_resource_fragments_v0.csv` | Nguồn fragment tạm để gắn căn cứ học liệu. |
| `reports/hnmu-open-questions.md` | Nguồn câu hỏi còn mở, cần lọc lại theo hướng Bloom/ví dụ. |

## 3. Artifact không nên bê nguyên

- Không bê nguyên task T01–T07 thành task chính nếu giáo sư muốn task theo Bloom.
- Không bê nguyên D1–D9 làm rubric chính vì mục tiêu mới là 3–4 rubric.
- Không coi topic map lớp 6–8 là đã đủ chắc; hiện chỉ là placeholder/suy luận.
- Không coi bản `benchmark_spec` ngày 04/07 là benchmark chính thức.

## 4. Quyết định thiết kế mới cần làm rõ

1. Task chính là mức Bloom, hay là tổ hợp `Bloom × format × topic`?
2. Các task hành vi gia sư T01–T07 sẽ trở thành nhãn phụ, case tương tác, hay rubric evidence?
3. Rubric 3–4 tiêu chí gồm những gì và có bằng chứng nào từ MathTutorBench/VietLegal/TutorBench?
4. Coverage đo theo bài/chủ đề SGK lớp 9 hay theo toàn bộ Tin học THCS?
5. Format diversity có những format chính xác nào và mỗi format có bắt buộc đủ 4 mức Bloom không?
6. 20 mẫu đầu tiên của HNMU nên được phân bổ ra sao để không lệch chủ đề/format/Bloom?

## 5. Gợi ý chuyển trạng thái

- `20260701_100006`: giữ như experiment tiền đề cho phiếu tác giả và bản đặc tả v0.
- `20260705_215045`: dùng để thiết kế lại theo Bloom, rút gọn rubric, và tạo ví dụ minh họa cho HNMU.
