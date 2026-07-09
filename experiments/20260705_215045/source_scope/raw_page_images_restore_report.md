# Báo cáo khôi phục ảnh raw SGK Tin học 6–8

Ngày tạo: 2026-07-07T07:38:59+07:00

## Mục đích

Khôi phục lại ảnh raw của SGK Tin học 6–8 đã từng được crawl trong quá trình xử lý học liệu. Việc này chỉ nhằm bảo toàn nguồn học liệu local; P02 bản thu gọn vẫn chỉ xử lý SGK Tin học 9.

## Kết quả

| Sách | Thư mục | Số ảnh | Dung lượng xấp xỉ | Trạng thái |
|---|---|---:|---:|---|
| SGK Tin học 6 | `source_scope/raw_page_images/SGK_TIN6/` | 78 | 51.05 MB | đã lưu đủ ảnh raw |
| SGK Tin học 7 | `source_scope/raw_page_images/SGK_TIN7/` | 86 | 54.12 MB | đã lưu đủ ảnh raw |
| SGK Tin học 8 | `source_scope/raw_page_images/SGK_TIN8/` | 98 | 65.31 MB | đã lưu đủ ảnh raw |

Tổng ảnh SGK Tin học 6–8: **262**.
Tổng dung lượng: **170.48 MB**.

## File liên quan

- `source_scope/raw_page_images_manifest.csv`: manifest tổng cho SGK Tin học 6–9.
- `source_scope/tin6_raw_page_images_manifest.csv`
- `source_scope/tin7_raw_page_images_manifest.csv`
- `source_scope/tin8_raw_page_images_manifest.csv`
- `source_scope/sgk_sgv_source_registry.csv`: đã thêm nguồn SGK Tin học 6–8 ở trạng thái raw archived.

## Phạm vi sử dụng

- SGK Tin học 6–8 chỉ được lưu raw để dùng cho P08 hoặc plan học liệu sau.
- Không dùng các ảnh này để thay đổi output chính của P02 bản thu gọn.
- Không OCR hoặc phân mảnh nội dung trong bước khôi phục này.

## Lỗi/tồn đọng

- Không ghi nhận lỗi tải ảnh sau khi retry trang bìa SGK Tin học 6.
