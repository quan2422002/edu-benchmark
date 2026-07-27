# Tài nguyên kế thừa của experiment `20260727_170150`

Snapshot được tạo lúc 17:01:50 ngày 27/07/2026 từ experiment
`20260722_000940`. Mục tiêu là khởi động phương pháp chấm mức độ cần thiết
của sáu nguyên tắc mà không phải đọc hoặc sao chép lại toàn bộ lịch sử thử
nghiệm.

## 1. Nguyên tắc kế thừa

1. File trong thư mục này là snapshot bất biến. Mọi output mới phải ghi
   dưới `experiments/20260727_170150/outputs/`.
2. Nguồn canonical của code vẫn nằm dưới `src/` và `scripts/`; không copy
   code dùng chung vào experiment.
3. Tài nguyên nặng dùng chung như fragment SGK/SGV và SQLite index vẫn đọc
   từ `shared/learning_resources/`.
4. `snapshot_manifest.csv` khóa SHA-256 của đủ 41 file được copy.
5. Artifact trong `diagnostic_legacy/` chỉ dùng để giải thích vì sao phương
   pháp chọn trực tiếp tập nhãn bị thay thế. Runner, prompt và validator mới
   không được đọc thư mục này.

## 2. Active input đã hoàn thành

### `benchmark_conversion/full_v0/`

Nguồn:
`experiments/20260722_000940/outputs/benchmark_conversion/full_v0/`.

Đây là bundle Plan 02 đã hoàn thành: 2.028 candidate từ 665 hội thoại
`pass`, trace 1:1, disposition đủ 665 family, mapping validation và
`run_status.json`. `benchmark_candidate_splits.csv` có `gold_response`,
nhưng Plan 01 mới phải tạo view chấm nguyên tắc không chứa trường này.

### `benchmark_specification/candidate_grounding/`

Nguồn:
`experiments/20260722_000940/outputs/benchmark_specification/task_discovery/method_revision_v3/`.

`candidate_principle_grounding_pool.csv` có đúng 2.028 dòng và đủ các
trường cho một lượt grounding duy nhất: prompt, history, câu hỏi nguồn và
`gold_answer`; không có `gold_response`. Plan 01 gửi các trường này đồng
thời trong một request, không chia context pass và grounding pass. Đây là
active input chính của Plan 01.

### `benchmark_specification/capability_model/`

Nguồn:
`experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/`.

Gồm mô hình sáu năng lực, 15 cặp ranh giới, bằng chứng quan sát và truy vết
nghiên cứu. Đại diện UET đã phê duyệt tạm thời làm nền xây tiêu chí; trạng
thái này không thay thế xác nhận HNMU.

### `benchmark_specification/principle_foundation/`

Nguồn:
`experiments/20260722_000940/outputs/benchmark_specification/task_discovery/pedagogical_principles.csv`.

Đây là registry sáu nguyên tắc KMP đã được làm rõ bằng Allison–Tharby và
KMP-Bench. Các định nghĩa vẫn là tạm thời, cần HNMU xác nhận trong gói tích
hợp tiêu chí và ví dụ.

### `literature/`

- `measurement_foundations/`: giao thức, danh mục 13 nguồn, ma trận bằng
  chứng và tổng hợp nền tảng đo lường của Workstream A.
- `pre_plan03_task_rubric_review/`: bốn tóm tắt paper có mục tiêu, ma trận
  bằng chứng và ma trận phát biểu vận hành về nhiệm vụ/tiêu chí.

### `reports/` và `decisions/`

Giữ báo cáo conversion, tổng hợp bốn paper, báo cáo A–B và quyết định mỗi
lượt gia sư tạo một candidate.

## 3. Bằng chứng chẩn đoán, không phải active input

`diagnostic_legacy/` gồm:

- summary C0b theo schema chính–phụ;
- metric tái lập cũ;
- summary và validation của forward test v3 đạt cấu trúc nhưng chỉ khớp
  3/5 tập kỳ vọng.

Các file này chứng minh vấn đề của phương pháp cũ. Không được dùng nhãn
trong đó để huấn luyện, few-shot, hiệu chỉnh ngưỡng hoặc làm ground truth
cho Plan 01 mới.

## 4. Tài nguyên dùng chung không copy

- `shared/learning_resources/fragments/learning_resource_fragments.csv`;
- `shared/learning_resources/indexes/learning_resources_v0.sqlite`;
- `shared/learning_resources/registries/ocr_text_manifest.csv`;
- `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv`;
- `shared/learning_resources/agent_context/`.
