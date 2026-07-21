# Kết quả Pha 0 — copy ảnh SGK sang vùng học liệu dùng chung

Ngày thực hiện: 15/07/2026
Experiment: `20260709_155523`
## Cập nhật trạng thái ngày 18/07/2026

Phần dưới đây là báo cáo lịch sử của Pha 0 ngày 15/07/2026. Tính đến 18/07/2026, SGK/SGV Tin học 6–9 đã có OCR Markdown do Nguyên gửi, manifest OCR, fragment và SQLite FTS index ở mức `draft`. Ảnh/PDF vẫn là nguồn truy vết gốc, không bị thay thế bởi OCR. Chi tiết xem `experiments/20260709_155523/reports/learning-resource-registries-sync-20260718.md`.


## 1. Mục tiêu

Đưa ảnh SGK Tin học 6–9 đã crawl ở experiment `20260705_215045` sang vùng dùng chung `shared/learning_resources/`, theo nguyên tắc copy, không move/xóa bản cũ.

## 2. Kết quả copy

| Sách | Nguồn cũ | Đích shared | Số ảnh | Copy mới | Đã có sẵn cùng hash | Mã học liệu |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Tin học 6 | `experiments/20260705_215045/source_scope/raw_page_images/SGK_TIN6` | `shared/learning_resources/raw_page_images/sgk/tin_hoc_6` | 78 | 78 | 0 | `LM-SGK-TIN6-0001` |
| Tin học 7 | `experiments/20260705_215045/source_scope/raw_page_images/SGK_TIN7` | `shared/learning_resources/raw_page_images/sgk/tin_hoc_7` | 86 | 86 | 0 | `LM-SGK-TIN7-0001` |
| Tin học 8 | `experiments/20260705_215045/source_scope/raw_page_images/SGK_TIN8` | `shared/learning_resources/raw_page_images/sgk/tin_hoc_8` | 98 | 98 | 0 | `LM-SGK-TIN8-0001` |
| Tin học 9 | `experiments/20260705_215045/source_scope/raw_page_images/SGK_TIN9` | `shared/learning_resources/raw_page_images/sgk/tin_hoc_9` | 94 | 94 | 0 | `LM-SGK-TIN9-0001` |

Tổng số ảnh SGK đã đăng ký: **356**.

## 3. Registry đã tạo/cập nhật

- `shared/learning_resources/registries/learning_resource_file_manifest.csv`: manifest từng file ảnh, gồm đường dẫn nguồn, đường dẫn shared, checksum và trạng thái xử lý.
- `shared/learning_resources/registries/sgk_sgv_source_registry.csv`: source map v0 cho SGK/SGV.

## 4. Nguồn SGV đã được ghi nhận cho Pha 1

Các link SGV do Quân cung cấp đã được ghi vào source registry để phục vụ Pha 1. Chưa crawl SGV trong Pha 0.

| Sách | Mã học liệu | Tên nguồn | URL | Trạng thái |
| --- | --- | --- | --- | --- |
| Tin học 6 | `LM-SGV-TIN6-4918798731` | Sách giáo viên Tin học 6 | https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgv-tin-hoc-6.4918798731#page=0 | `needs_uet_review` |
| Tin học 7 | `LM-SGV-TIN7-4920462481` | Sách giáo viên Tin học 7 | https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgv-tin-hoc-7.4920462481#page=0 | `needs_uet_review` |
| Tin học 8 | `LM-SGV-TIN8-4923610683` | Sách giáo viên Tin học 8 | https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgv-tin-hoc-8.4923610683#page=0 | `needs_uet_review` |
| Tin học 9 | `LM-SGV-TIN9-4923777498` | Sách giáo viên Tin học 9 | https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgv-tin-hoc-9.4923777498#page=0 | `needs_uet_review` |

## 5. Quyết định an toàn

- Không xóa hoặc di chuyển ảnh cũ trong `experiments/20260705_215045/source_scope/raw_page_images`.
- Không OCR trong Pha 0.
- Không coi ảnh/registry là đã được HNMU xác nhận.
- Chưa quyết định có commit ảnh SGK lên GitHub hay chỉ giữ local/Drive; cần Quân chốt trước khi push.

## 6. Việc còn lại cho các pha sau

- Pha 1: crawl ảnh SGV từ các link đã đăng ký, nếu được duyệt.
- Pha 2: tạo danh mục chủ đề/bài học/trang v0.
- Pha 3: OCR có kiểm tra chất lượng.
- Pha 4: fragment học liệu.
- Pha 5: thiết kế database/retrieval system.
