# Handoff P02 bản thu gọn - source scope và topic taxonomy

## Trạng thái

`P02 bản thu gọn` đã được thực hiện theo phạm vi hiện tại, không còn coi các phần mở rộng trước đó là output chính.

## Quyết định đã phản ánh trong artifact

- Chỉ dùng 3 mức nhận thức: `Biết`, `Hiểu`, `Vận dụng`.
- Giữ phương pháp giàn giáo; dùng để giải thích rubric R3 và cột `note` trong phiếu tác giả bằng nhãn tiếng Việt.
- Chỉ dùng SGK Tin học 9 làm học liệu chính ở P02.
- Tên chủ đề/bài học lấy từ mục lục SGK Tin học 9.
- OCR toàn văn và phân mảnh học liệu được chuyển sang P08/later.

## Output chính

| File/thư mục | Vai trò |
|---|---|
| `source_scope/benchmark_support_source_registry.csv` | Đăng ký hai tài liệu HNMU đang thực sự dùng trong P02: mức nhận thức và giàn giáo |
| `source_scope/cognitive_level_seed_map.md` | Mô tả 3 mức nhận thức dùng cho phiếu tác giả |
| `source_scope/scaffolding_function_notes.md` | Mô tả nhãn hỗ trợ giàn giáo bằng tiếng Việt và cách liên hệ với R3 |
| `source_scope/sgk_sgv_source_registry.csv` | Đăng ký nguồn SGK Tin học 9 duy nhất trong P02 bản thu gọn |
| `source_scope/sgk_sgv_source_scope.md` | Ghi rõ phạm vi học liệu hiện tại và các phần không thuộc P02 |
| `source_scope/tin9_raw_page_images_manifest.csv` | Manifest ảnh local của SGK Tin học 9 |
| `source_scope/tin9_raw_page_images_report.md` | Báo cáo ngắn về ảnh nguồn đã có |
| `topic_taxonomy/tin9_toc_ocr_probe/page_0005.txt` | Bằng chứng OCR mục lục SGK Tin học 9 |
| `topic_taxonomy/tin9_sgk_topics_v0.csv` | Danh sách chủ đề/bài học v0 dạng bảng để dùng tiếp |
| `topic_taxonomy/tin9_sgk_topics_v0.md` | Bản đọc nhanh của danh sách chủ đề/bài học |
| `reports/P02-benchmark-support-open-questions.md` | Các điểm đã chốt và câu hỏi còn cần xác nhận |

## Ghi chú chuyển tiếp

P04 có thể dùng `tin9_sgk_topics_v0.csv` làm danh sách chủ đề tạm thời trong phiếu tác giả, nhưng cần giữ trạng thái `needs_hnmu_review` cho đến khi HNMU/UET xác nhận. Các yêu cầu mã hóa đoạn học liệu chi tiết không nên nhét lại vào P02; nên xử lý ở P08 hoặc plan học liệu riêng.
