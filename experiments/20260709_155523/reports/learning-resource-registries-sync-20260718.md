# Đồng bộ registry học liệu và dữ liệu thô sau khi có lớp 8–9

Ngày thực hiện: 18/07/2026  
Experiment: `20260709_155523`  
Phạm vi: Plan 01, Plan 02, Plan 03 Pha 0–2 và các output học liệu đang được Plan 03 Pha 4–5 dùng lại.

## 1. Vì sao cần đồng bộ

Sau khi Nguyên bổ sung OCR Markdown SGK/SGV Tin học 8–9 và HNMU bổ sung file hội thoại lớp 8–9, một số tài liệu/registry vẫn còn mô tả theo trạng thái cũ của vòng lớp 6–7: lớp 8 là placeholder, lớp 9 lấy từ OCR cũ, hoặc ảnh SGK/SGV còn ghi “chưa OCR”. Lượt này rà lại để các file plan/report/output nói cùng một trạng thái.

## 2. Registry đã được kiểm tra

| Registry | Trạng thái sau đồng bộ | Ghi chú |
|---|---:|---|
| `shared/raw_data/HNMU-teacher_dialog_samples/manifest.csv` | 4 file lớp 6–9 | Lớp 8–9 mới đăng ký raw data, chưa chạy Plan 04 audit. |
| `shared/learning_resources/registries/learning_resource_file_manifest.csv` | 760 ảnh/PDF | Đã bỏ ghi chú lỗi thời “chưa OCR”; ảnh/PDF vẫn là nguồn truy vết, OCR Markdown là artifact riêng. |
| `shared/learning_resources/registries/sgk_sgv_source_registry.csv` | 8 sách SGK/SGV lớp 6–9 | Notes đã phản ánh OCR Markdown/fragment/index v0. |
| `shared/learning_resources/registries/ocr_text_manifest.csv` | 154 đơn vị OCR Markdown | Được build lại từ OCR Markdown và tự nối topic map khi có. |
| `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv` | 106 mục chủ đề/bài/phụ lục | Dựa trên mục lục OCR Markdown do Nguyên gửi; toàn bộ cần HNMU review. |
| `shared/learning_resources/registries/sgk_thcs_lesson_position_registry_v0.csv` | 755 vị trí từ dữ liệu HNMU | Dựa trên cột vị trí trong hội thoại thô lớp 6–9; chưa phải audit chất lượng. |
| `shared/learning_resources/fragments/learning_resource_fragments.csv` | 2750 fragment | Đã rebuild sau khi manifest OCR được đồng bộ. |
| `shared/learning_resources/indexes/learning_resources_v0.sqlite` | 154 nguồn / 2750 fragment | SQLite FTS sinh lại được, không push lên Git. |

## 3. Thống kê OCR Markdown

| Lớp | SGK | SGV |
| --- | --- | --- |
| 6 | 17 | 18 |
| 7 | 16 | 17 |
| 8 | 20 | 21 |
| 9 | 22 | 23 |

Tất cả 154 dòng trong `ocr_text_manifest.csv` đang ở trạng thái `draft`. Các bài SGK đều có `topic_title`; các bài SGV có `topic_title` được nối theo bài tương ứng trong topic map SGK. Các mục `hd_chung` của SGV không bắt buộc có topic bài học.

## 4. Thống kê fragment truy xuất

| Lớp | SGK | SGV |
| --- | --- | --- |
| 6 | 223 | 383 |
| 7 | 302 | 414 |
| 8 | 315 | 400 |
| 9 | 296 | 417 |

Tổng cộng: 2750 fragment. Đây là nguồn truy xuất v0 cho specialist agent khi kiểm nhất quán câu hỏi, đáp án, bài học, vị trí và hội thoại. Fragment vẫn ở trạng thái `draft`, chưa thay thế xác nhận chuyên môn.

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

Nguồn chính là mục lục OCR Markdown SGK do Nguyên gửi, không còn dùng placeholder lớp 8 hay danh mục Tin học 9 từ experiment cũ làm nguồn chính.

## 6. Thống kê lesson-position registry từ dữ liệu HNMU

Theo lớp:

| Lớp | Số vị trí |
| --- | --- |
| 6 | 181 |
| 7 | 160 |
| 8 | 197 |
| 9 | 217 |

Theo loại học liệu ghi trong dữ liệu thô:

| Loại học liệu | Số vị trí |
| --- | --- |
| SGK | 384 |
| SGK_or_unspecified | 289 |
| SGV | 82 |

Các dòng này được tạo từ thông tin vị trí trong file hội thoại thô. Chúng hỗ trợ kiểm phủ và truy xuất ban đầu, nhưng chưa khẳng định rằng metadata HNMU đã đúng.

## 7. Thống kê raw dialogue manifest

| Batch | File | Lớp | Dòng hội thoại ước tính | Trạng thái |
| --- | --- | --- | --- | --- |
| 20260714_initial | Lớp 6.xlsx | Lớp 6 | 237 | raw_registered_no_audit |
| 20260714_initial | Lớp 7.xlsx | Lớp 7 | 224 | raw_registered_no_audit |
| 20260718_grade8_9 | Lớp 8.xlsx | Lớp 8 | 280 | raw_registered_no_audit |
| 20260718_grade8_9 | Lớp 9.xlsx | Lớp 9 | 308 | raw_registered_no_audit |

Tổng số dòng hội thoại ước tính trong manifest: 1049. Plan 04 output hiện có vẫn chỉ là vòng audit lớp 6–7; lớp 8–9 cần chạy audit riêng khi được duyệt.

## 8. Code/runbook đã đồng bộ

- `src/edu_benchmark/learning_resources/ocr_text_manifest.py` đã tự nối `sgk_thcs_topic_lesson_map_v0.csv` khi build manifest OCR, bao gồm bài có hậu tố như 10A/10B.
- `scripts/learning_resources/build_ocr_text_manifest.py` mặc định đọc topic map hiện tại.
- `shared/learning_resources/OCR_TEXT_PROCESSING_RUNBOOK.md` đã được cập nhật số liệu 6–9 và cảnh báo không dùng output OCR/MinerU thử nghiệm cũ làm nguồn chính.

## 9. Giới hạn còn lại

- OCR Markdown/fragment/index vẫn là `draft` và cần UET/HNMU review khi dùng cho kết luận chuyên môn.
- Lesson-position registry phản ánh metadata HNMU khai báo, chưa phải kết quả kiểm đúng/sai.
- Chưa chạy Plan 04 audit cho lớp 8–9 trong lượt này.
- Chưa chuyển mẫu hội thoại lớp 8–9 thành mẫu benchmark.
