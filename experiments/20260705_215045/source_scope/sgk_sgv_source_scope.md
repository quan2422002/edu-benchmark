# Phạm vi học liệu P02 bản thu gọn

## Kết luận phạm vi hiện tại

P02 bản thu gọn chỉ dùng **SGK Tin học 9** làm nguồn học liệu chính để chuẩn hóa danh sách chủ đề/bài học v0. Lý do là nguồn tập huấn hiện chủ yếu ở dạng ảnh; OCR toàn bộ SGK/SGV lớp 6–9 sẽ tốn thời gian và được tách sang P08 hoặc một plan xử lý học liệu riêng.

## Nguồn dùng trong P02

| Mã học liệu | Tên nguồn | Vai trò trong P02 | Trạng thái |
|---|---|---|---|
| `LM-SGK-TIN9-4700233123` | SGK Tin học 9 | Nguồn chính để lấy mục lục, tên chủ đề, tên bài học | Đã có ảnh local; mục lục đã OCR sơ bộ |

## Không nằm trong P02 bản thu gọn

- SGK/SGV Tin học lớp 6–8.
- SGV Tin học 9.
- OCR toàn văn SGK Tin học 9.
- Phân mảnh nội dung học liệu thành các đoạn nhỏ có mã học liệu chi tiết.

Các phần này vẫn quan trọng, nhưng cần xử lý trong P08 hoặc một plan học liệu dài hơi để tránh làm P02 bị phình phạm vi.

## Hệ quả thiết kế

- Tên chủ đề/bài học trong benchmark v0 nên bám vào mục lục SGK Tin học 9.
- Mã học liệu chi tiết cho từng đoạn/bài chưa được coi là chốt ở P02.
- Khi tạo phiếu tác giả ở giai đoạn tiếp theo, trường chủ đề có thể dùng danh sách v0 nhưng vẫn cần nhãn trạng thái `cần rà soát` cho đến khi HNMU xác nhận.

## Ghi chú khôi phục ảnh raw ngày 07/07/2026

Sau khi rà soát, ảnh raw của SGK Tin học 6–8 đã được crawl lại và lưu trong `source_scope/raw_page_images/` để không mất nguồn học liệu đã từng thu thập. Việc này **không mở rộng phạm vi xử lý của P02 bản thu gọn**: P02 vẫn chỉ dùng SGK Tin học 9 để tạo danh sách chủ đề/bài học v0. Ảnh SGK Tin học 6–8 chỉ là nguồn raw lưu trữ cho P08 hoặc một plan học liệu sau.

