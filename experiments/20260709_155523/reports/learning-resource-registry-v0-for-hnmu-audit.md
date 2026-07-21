# Danh mục học liệu v0 phục vụ kiểm toán HNMU

Ngày tạo bản đầu: 15/07/2026  
Ngày đồng bộ mới nhất: 18/07/2026  
Experiment: `20260709_155523`  
Trạng thái: `draft`, dùng được cho truy xuất/audit v0 nhưng chưa thay thế xác nhận chuyên môn của HNMU/UET.

## 1. Mục tiêu

Tạo danh mục học liệu v0 ở mức khối lớp, sách, chủ đề/bài học và vị trí/trang để Plan 04 có thể kiểm độ phủ và kiểm nhất quán dữ liệu HNMU.

Bản ngày 18/07/2026 đã đồng bộ lại sau khi có OCR Markdown SGK/SGV Tin học 8–9 do Nguyên gửi và dữ liệu hội thoại HNMU lớp 8–9.

## 2. Output hiện tại

- `shared/learning_resources/registries/sgk_sgv_source_registry.csv`
- `shared/learning_resources/registries/learning_resource_file_manifest.csv`
- `shared/learning_resources/registries/ocr_text_manifest.csv`
- `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv`
- `shared/learning_resources/registries/sgk_thcs_lesson_position_registry_v0.csv`
- `shared/learning_resources/fragments/learning_resource_fragments.csv`
- `shared/learning_resources/indexes/learning_resources_v0.sqlite` — artifact sinh lại được, bị ignore bởi Git.

## 3. Nguồn dùng

- OCR Markdown SGK/SGV Tin học 6–9 do Nguyên gửi: `shared/learning_resources/ocr_text/`.
- Ảnh/PDF học liệu dùng chung: `shared/learning_resources/raw_page_images/` và `shared/learning_resources/compiled_documents/`.
- Dữ liệu hội thoại HNMU lớp 6–9: `shared/raw_data/HNMU-teacher_dialog_samples/`.
- Source registry SGK/SGV: `shared/learning_resources/registries/sgk_sgv_source_registry.csv`.

Không còn dùng placeholder lớp 8 hoặc OCR mục lục từ experiment cũ làm nguồn chính cho topic map hiện tại.

## 4. Thống kê source/file registry

- `sgk_sgv_source_registry.csv`: 8 nguồn, gồm SGK và SGV Tin học 6–9.
- `learning_resource_file_manifest.csv`: 760 dòng ảnh/PDF.
  - SGK ảnh: 356 trang.
  - SGV ảnh: 396 trang.
  - PDF dẫn xuất: 8 file.

Các ảnh/PDF vẫn là nguồn truy vết. OCR Markdown là artifact xử lý riêng, đã đăng ký qua `ocr_text_manifest.csv`.

## 5. Thống kê topic/lesson map

| Lớp | Loại mục | Số lượng |
| --- | --- | --- |
| 6 | chu_de | 6 |
| 6 | bai_hoc | 17 |
| 6 | phu_luc | 1 |
| 7 | chu_de | 5 |
| 7 | bai_hoc | 16 |
| 7 | phu_luc | 1 |
| 8 | chu_de | 6 |
| 8 | chu_de_con | 2 |
| 8 | bai_hoc | 20 |
| 8 | phu_luc | 1 |
| 9 | chu_de | 6 |
| 9 | chu_de_con | 2 |
| 9 | bai_hoc | 22 |
| 9 | phu_luc | 1 |

Theo trạng thái:

| Trạng thái | Số lượng |
| --- | --- |
| needs_hnmu_review | 106 |

Ghi chú: topic/lesson map hiện dựa trên mục lục OCR Markdown do Nguyên gửi. Mặc dù OCR Markdown khá sạch, toàn bộ vẫn gắn `needs_hnmu_review` vì tên chủ đề/bài học là căn cứ sư phạm quan trọng.

## 6. Thống kê lesson-position registry

Theo lớp:

| Lớp | Số vị trí |
| --- | --- |
| 6 | 181 |
| 7 | 160 |
| 8 | 197 |
| 9 | 217 |

Theo loại học liệu:

| Loại học liệu | Số vị trí |
| --- | --- |
| SGK | 384 |
| SGK_or_unspecified | 289 |
| SGV | 82 |

Theo trạng thái:

| Trạng thái | Số lượng |
| --- | --- |
| needs_hnmu_review | 755 |

Các dòng position registry được tạo từ cột vị trí trong dữ liệu thô HNMU. Vì vậy, chúng là căn cứ để kiểm phủ và truy xuất, không phải bằng chứng rằng vị trí được khai báo đã đúng.

## 7. Thống kê OCR manifest và fragment

OCR manifest:

| Lớp | SGK | SGV |
| --- | --- | --- |
| 6 | 17 | 18 |
| 7 | 16 | 17 |
| 8 | 20 | 21 |
| 9 | 22 | 23 |

Fragment truy xuất:

| Lớp | SGK | SGV |
| --- | --- | --- |
| 6 | 223 | 383 |
| 7 | 302 | 414 |
| 8 | 315 | 400 |
| 9 | 296 | 417 |

Tổng cộng: 154 đơn vị OCR Markdown và 2750 fragment.

## 8. Quyết định bảo thủ

- Toàn bộ OCR Markdown/fragment/index giữ trạng thái `draft`.
- Topic/lesson map giữ `needs_hnmu_review` cho tới khi HNMU xác nhận.
- Lesson-position registry giữ `needs_hnmu_review` vì được lấy từ metadata HNMU khai báo, chưa qua audit đúng/sai.
- Với SGV, `topic_title` trong OCR manifest được nối theo bài SGK tương ứng để hỗ trợ truy xuất; đây là mapping kỹ thuật v0, không phải xác nhận chuyên môn cuối cùng.
- PDF dẫn xuất chỉ để đọc nhanh, không thay thế truy vết từng trang bằng ảnh gốc/Markdown/fragment.

## 9. Việc cần làm tiếp

- Khi chạy Plan 04 cho lớp 8–9, dùng registry hiện tại để truy xuất evidence nhưng không ghi đè output audit lớp 6–7 nếu chưa có plan rõ.
- Cần HNMU/UET kiểm một mẫu topic/lesson map và một mẫu fragment để quyết định có đủ tin cậy cho chuyển đổi benchmark hàng loạt hay không.
- Nếu Nguyên bổ sung hoặc sửa OCR Markdown, chạy lại runbook `shared/learning_resources/OCR_TEXT_PROCESSING_RUNBOOK.md` để rebuild manifest/fragment/index.
