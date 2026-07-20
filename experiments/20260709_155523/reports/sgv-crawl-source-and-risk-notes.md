# Kết quả Pha 1 — crawl ảnh SGV Tin học 6–9

Ngày thực hiện: 15/07/2026
Experiment: `20260709_155523`
## Cập nhật trạng thái ngày 18/07/2026

Phần dưới đây là báo cáo lịch sử của Pha 1 ngày 15/07/2026. Trạng thái hiện tại đã được đồng bộ lại: OCR Markdown SGK/SGV Tin học 6–9 do Nguyên gửi đã được đăng ký trong `ocr_text_manifest.csv`, tách thành 2.750 fragment và build SQLite FTS index ở mức `draft`. Chi tiết xem `experiments/20260709_155523/reports/learning-resource-registries-sync-20260718.md`.


## 1. Mục tiêu

Crawl ảnh SGV Tin học 6–9 từ các link `taphuan.nxbgd.vn` do Quân cung cấp, lưu vào vùng học liệu dùng chung và cập nhật bảng truy vết.

Pha này **không OCR**, **không fragment**, **không xác nhận nội dung chuyên môn**, và **không quyết định việc commit ảnh lên GitHub**.

## 2. Kết quả crawl

| Sách | Mã học liệu | URL nguồn | Thư mục local | Số ảnh | Trạng thái |
| --- | --- | --- | --- | ---: | --- |
| Tin học 6 | `LM-SGV-TIN6-4918798731` | https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgv-tin-hoc-6.4918798731#page=0 | `shared/learning_resources/raw_page_images/sgv/tin_hoc_6` | 98 | `draft` |
| Tin học 7 | `LM-SGV-TIN7-4920462481` | https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgv-tin-hoc-7.4920462481#page=0 | `shared/learning_resources/raw_page_images/sgv/tin_hoc_7` | 94 | `draft` |
| Tin học 8 | `LM-SGV-TIN8-4923610683` | https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgv-tin-hoc-8.4923610683#page=0 | `shared/learning_resources/raw_page_images/sgv/tin_hoc_8` | 102 | `draft` |
| Tin học 9 | `LM-SGV-TIN9-4923777498` | https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgv-tin-hoc-9.4923777498#page=0 | `shared/learning_resources/raw_page_images/sgv/tin_hoc_9` | 102 | `draft` |

Tổng số ảnh SGV đã crawl và đăng ký: **396**.

Tổng số ảnh học liệu trong manifest hiện tại: **752** ảnh, gồm **356** ảnh SGK và **396** ảnh SGV.

## 3. File registry/manifest đã cập nhật

- `shared/learning_resources/registries/learning_resource_file_manifest.csv`: thêm từng file ảnh SGV, gồm URL ảnh nguồn, đường dẫn local, checksum, kích thước file và trạng thái xử lý.
- `shared/learning_resources/registries/sgk_sgv_source_registry.csv`: cập nhật `local_file_path`, `version_label` và `status` cho SGV Tin học 6–9.

## 4. Cách crawl

Trang `taphuan.nxbgd.vn` trả HTML có chứa URL ảnh trang sách từ CDN `cdn3.olm.vn`. Pha 1 trích các URL dạng trang ảnh SGV từ HTML, tải từng ảnh `.png`, và lưu theo tên chuẩn `page_0001.png`, `page_0002.png`, ... trong thư mục lớp tương ứng.

## 5. Rủi ro và lưu ý quyền sử dụng

- Ảnh SGK/SGV có thể là tài nguyên có bản quyền. Trước khi push lên GitHub, cần chốt rõ có được commit ảnh hay chỉ commit manifest/registry và giữ ảnh ở local/Drive.
- Trạng thái hiện tại của SGV là `draft`: đã crawl được ảnh, nhưng chưa OCR, chưa kiểm tra chất lượng trang, chưa được HNMU xác nhận.
- Nếu nguồn `taphuan.nxbgd.vn` hoặc CDN thay đổi URL, có thể cần crawl lại hoặc kiểm tra checksum lại.

## 6. Việc còn lại cho Pha 2 trở đi

- Tạo danh mục chủ đề/bài học/trang v0 cho SGK/SGV.
- Chạy OCR có kiểm tra chất lượng, không dùng OCR thô làm nguồn chân lý.
- Tạo fragment học liệu và trạng thái xác nhận.
- Thiết kế database/retrieval system khi registry và fragment v0 đủ ổn.
