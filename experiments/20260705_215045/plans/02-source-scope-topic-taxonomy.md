# Plan 02 — Phạm vi nguồn học liệu và danh sách chủ đề SGK Tin học 9

Trạng thái: `COMPLETED_REDUCED` — đã hoàn tất P02 theo bản thu gọn ngày 06/07/2026.
Experiment: `20260705_215045`
Owner chính: `learning-resource-curator`
Có thể chạy độc lập: Có.

## 1. Mục tiêu

P02 bản thu gọn có mục tiêu rất hẹp: xác định nguồn học liệu chính đang dùng ngay, chốt cách dùng hai tài liệu HNMU hỗ trợ benchmark, và tạo danh sách chủ đề/bài học v0 từ **mục lục SGK Tin học 9**.

P02 không cố giải quyết toàn bộ bài toán học liệu. OCR toàn văn, phân mảnh học liệu, mã hóa từng đoạn học liệu, SGV và SGK lớp 6–8 được chuyển sang P08 hoặc một plan học liệu riêng.

## 2. Quyết định đã chốt

- Chỉ dùng 3 mức nhận thức: `Biết`, `Hiểu`, `Vận dụng`.
- Không dùng hệ 4 mức `Nhận biết`, `Thông hiểu`, `Vận dụng`, `Vận dụng cao` trong P02 hiện tại.
- Giữ phương pháp giàn giáo; chất lượng hỗ trợ theo phương pháp này được chấm chủ yếu bằng R3.
- Trong phiếu tác giả, cột `note` nên ghi mức hỗ trợ bằng nhãn tiếng Việt: `Gợi mở`, `Giải thích`, `Gợi ý`, `Hướng dẫn`, `Làm mẫu`.
- Phạm vi học liệu của P02: **SGK Tin học 9**.
- Tên chủ đề/bài học lấy theo mục lục SGK Tin học 9; danh sách hiện ở trạng thái `needs_hnmu_review`.
- Tài liệu “Các dạng bài tập” chưa dùng trong P02 bản thu gọn để tránh làm loạn taxonomy; format bài tập sẽ xử lý ở P04/P05 theo hướng đã trao đổi ở P03.

## 3. Input đã dùng

| Nguồn | Vai trò trong P02 |
|---|---|
| SGK Tin học 9 trên trang tập huấn NXBGD | Nguồn chính để lấy mục lục và tạo danh sách chủ đề/bài học v0 |
| `Biểu hiện mức độ nhận thức _Tin học.docx` | Căn cứ cho 3 mức nhận thức `Biết`, `Hiểu`, `Vận dụng` |
| `KhungDanGiao_HoiThoaiMinhHoa.docx` | Căn cứ để mô tả nhãn hỗ trợ giàn giáo và liên hệ với R3 |

## 4. Quy trình đã thực hiện

### Bước 1 — Thu hẹp phạm vi nguồn

Chốt rằng P02 chỉ giữ SGK Tin học 9 làm nguồn học liệu chính. Các nguồn lớp 6–8, SGV và OCR toàn văn không còn là output của P02.

Output:

- `source_scope/sgk_sgv_source_scope.md`
- `source_scope/sgk_sgv_source_registry.csv`

### Bước 2 — Chuẩn hóa hai tài liệu HNMU hỗ trợ benchmark

Ghi lại hai nguồn HNMU thực sự được dùng trong P02: tài liệu mức nhận thức và tài liệu giàn giáo.

Output:

- `source_scope/benchmark_support_source_registry.csv`
- `source_scope/cognitive_level_seed_map.md`
- `source_scope/scaffolding_function_notes.md`

### Bước 3 — Ghi nhận ảnh nguồn SGK Tin học 9

Giữ lại ảnh PNG của SGK Tin học 9 đã crawl để làm bằng chứng local. Không coi đây là OCR toàn văn.

Output:

- `source_scope/tin9_raw_page_images_manifest.csv`
- `source_scope/tin9_raw_page_images_report.md`
- `source_scope/raw_page_images/SGK_TIN9/` được git-ignore vì là dữ liệu ảnh raw.


### Bước bổ sung — Khôi phục kho ảnh raw SGK Tin học 6–8

Ngày 07/07/2026, ảnh raw của SGK Tin học 6–8 được crawl lại vì phần dữ liệu này đã từng được thu thập nhưng không còn trong workspace. Việc khôi phục này chỉ nhằm bảo toàn nguồn học liệu; không thay đổi phạm vi xử lý của P02 bản thu gọn.

Output bổ sung:

- `source_scope/raw_page_images/SGK_TIN6/`
- `source_scope/raw_page_images/SGK_TIN7/`
- `source_scope/raw_page_images/SGK_TIN8/`
- `source_scope/raw_page_images_manifest.csv`
- `source_scope/tin6_raw_page_images_manifest.csv`
- `source_scope/tin7_raw_page_images_manifest.csv`
- `source_scope/tin8_raw_page_images_manifest.csv`
- `source_scope/raw_page_images_restore_report.md`
- `handoffs/P02-raw-image-archive-restore-025.md`

### Bước 4 — OCR tối thiểu mục lục

Dùng EasyOCR trên một số trang đầu SGK Tin học 9 để tìm và đọc mục lục. Trang OCR hữu ích nhất hiện là:

- `topic_taxonomy/tin9_toc_ocr_probe/page_0005.txt`

Các file OCR probe trang 1–8 được giữ làm dấu vết kiểm tra, nhưng output chính của P02 là danh sách chủ đề/bài học đã chuẩn hóa bên dưới.

### Bước 5 — Tạo danh sách chủ đề/bài học v0

Tạo danh sách 31 dòng gồm chủ đề, chủ đề con, bài học và phụ lục theo mục lục SGK Tin học 9.

Output:

- `topic_taxonomy/tin9_sgk_topics_v0.csv`
- `topic_taxonomy/tin9_sgk_topics_v0.md`

### Bước 6 — Handoff sang P04

Tạo handoff để P04 dùng danh sách chủ đề/bài học v0, nhưng vẫn giữ trạng thái cần HNMU/UET xác nhận.

Output:

- `handoffs/P02-reduced-completion-018.md`
- `reports/P02-benchmark-support-open-questions.md`

## 5. Output chính và vai trò

| File/thư mục | Vai trò |
|---|---|
| `source_scope/benchmark_support_source_registry.csv` | Registry hai tài liệu HNMU dùng trong P02 |
| `source_scope/cognitive_level_seed_map.md` | Mô tả 3 mức nhận thức cho phiếu tác giả |
| `source_scope/scaffolding_function_notes.md` | Mô tả nhãn hỗ trợ giàn giáo và cách liên hệ với R3 |
| `source_scope/sgk_sgv_source_registry.csv` | Registry nguồn SGK Tin học 9 duy nhất trong P02 |
| `source_scope/sgk_sgv_source_scope.md` | Ghi rõ phạm vi học liệu và các phần đã loại khỏi P02 |
| `source_scope/tin9_raw_page_images_manifest.csv` | Manifest ảnh local SGK Tin học 9 |
| `source_scope/tin9_raw_page_images_report.md` | Báo cáo ngắn về ảnh nguồn SGK Tin học 9 |
| `topic_taxonomy/tin9_toc_ocr_probe/page_0005.txt` | Bằng chứng OCR mục lục SGK Tin học 9 |
| `topic_taxonomy/tin9_sgk_topics_v0.csv` | Bảng chủ đề/bài học v0 để P04/P05 dùng tiếp |
| `topic_taxonomy/tin9_sgk_topics_v0.md` | Bản đọc nhanh của danh sách chủ đề/bài học |
| `reports/P02-benchmark-support-open-questions.md` | Các điểm đã chốt và câu hỏi còn cần HNMU/UET xác nhận |
| `handoffs/P02-reduced-completion-018.md` | Handoff chính thức từ P02 bản thu gọn sang P04 |

## 6. Không làm trong P02 bản thu gọn

- Không thiết kế task/rubric.
- Không tạo ví dụ phiếu tác giả.
- Không triển khai database.
- Không chuẩn hóa toàn bộ Tin học 6–9.
- Không OCR toàn văn SGK Tin học 9.
- Không phân mảnh học liệu thành đoạn nhỏ/mã học liệu chi tiết.
- Không dùng tài liệu dạng bài để tạo taxonomy format.

## 7. Kiểm tra đã chạy

- Validate `source_scope/sgk_sgv_source_registry.csv` bằng `agents/learning-resource-curator/scripts/validate_learning_resource_registry.py`.
- Validate `source_scope/benchmark_support_source_registry.csv` bằng cùng validator.
- Kiểm tra `topic_taxonomy/tin9_sgk_topics_v0.csv`: không trùng `item_id`, `parent_id` hợp lệ, `learning_material_id` thống nhất.
- Kiểm tra `metadata.yaml` đọc được bằng PyYAML.
- Chạy `pytest tests/agents -q`.

Python dùng cho kiểm tra và cài package: `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.
