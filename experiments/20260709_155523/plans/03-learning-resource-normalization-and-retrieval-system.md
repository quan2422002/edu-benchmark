# Plan 03 — Chuẩn hóa học liệu SGK/SGV và thiết kế hệ thống truy xuất học liệu

Experiment: `20260709_155523`
Trạng thái: `PHA 2 HOÀN THÀNH` — đã tạo danh mục học liệu v0 ngày 15/07/2026; các pha sau Pha 2 vẫn cần duyệt riêng.
Ngày lập: 11/07/2026
Ngày cập nhật: 15/07/2026

## 1. Mục tiêu

Lên kế hoạch chuẩn hóa học liệu SGK/SGV Tin học THCS từ ảnh đã crawl hoặc sẽ crawl, trước mắt để làm thước đo độ phủ và kiểm đáp án cho dữ liệu HNMU, về dài hạn để xây hệ thống học liệu có thể truy xuất khi đánh giá model gia sư.

Ảnh SGK đã crawl từ experiment trước nằm ở:

`experiments/20260705_215045/source_scope/raw_page_images`

Kiểm tra nhẹ ngày 14/07/2026 cho thấy có:

- `SGK_TIN6`: 78 ảnh
- `SGK_TIN7`: 86 ảnh
- `SGK_TIN8`: 98 ảnh
- `SGK_TIN9`: 94 ảnh

Dữ liệu HNMU mới có cột `Đáp án (SGV)`, vì vậy SGV cũng cần được đưa vào phạm vi học liệu. SGK dùng để kiểm câu hỏi/chủ đề/bài học/vị trí; SGV dùng để kiểm đáp án chuẩn và căn cứ giải thích.

## 2. Lý do cần plan riêng

Phần học liệu không chỉ phục vụ đếm độ phủ. Về sau, khi dùng benchmark để đánh giá model, học liệu được quản lý bởi database/retrieval system sẽ là nguồn để model truy vấn và phản hồi. Vì vậy không nên nhét phần này vào plan kiểm toán hội thoại HNMU.

Ngoài ra, ảnh SGK/SGV có thể là tài nguyên có bản quyền. Cần quản lý bằng manifest, checksum và chính sách version hóa rõ ràng; không mặc định push ảnh lên GitHub.

## 3. Pha triển khai đề xuất

### Pha 0 — Copy ảnh SGK đã crawl sang `shared/`

Mục tiêu: đưa ảnh SGK đã crawl từ experiment `20260705_215045` sang vùng học liệu dùng chung mà không phá vỡ khả năng truy vết experiment cũ.

Nguyên tắc:

- Copy, không move/xóa bản cũ trong bước đầu.
- Tạo manifest có checksum để biết file nào được copy từ đâu sang đâu.
- Không commit ảnh lên GitHub nếu chưa rõ quyền; chỉ commit manifest/README nếu phù hợp.

Output dự kiến:

- `shared/learning_resources/raw_page_images/sgk/tin_hoc_6/`
- `shared/learning_resources/raw_page_images/sgk/tin_hoc_7/`
- `shared/learning_resources/raw_page_images/sgk/tin_hoc_8/`
- `shared/learning_resources/raw_page_images/sgk/tin_hoc_9/`
- `shared/learning_resources/registries/learning_resource_file_manifest.csv`
- report trong experiment: `reports/sgk-image-shared-migration-plan.md` hoặc `reports/sgk-image-shared-migration-result.md` nếu được triển khai.

### Pha 1 — Crawl ảnh SGV tương ứng với SGK Tin học 6–9

Mục tiêu: bổ sung SGV vì dữ liệu HNMU có cột `Đáp án (SGV)`.

Lý do:

- Không có SGV thì chỉ kiểm được đáp án giáo viên đã nhập có vẻ khớp câu hỏi hay không.
- Có SGV thì có thể kiểm đáp án có truy vết tới nguồn hay không.
- Khi chưa có SGV, mọi kiểm tra đáp án phải gắn cờ `needs_sgv_verification`.

Output dự kiến:

- `shared/learning_resources/raw_page_images/sgv/tin_hoc_6/`
- `shared/learning_resources/raw_page_images/sgv/tin_hoc_7/`
- `shared/learning_resources/raw_page_images/sgv/tin_hoc_8/`
- `shared/learning_resources/raw_page_images/sgv/tin_hoc_9/`
- cập nhật `learning_resource_file_manifest.csv`
- `reports/sgv-crawl-source-and-risk-notes.md`

Câu hỏi cần chốt trước khi crawl:

- SGV có cùng nguồn `taphuan.nxbgd.vn` hoặc nguồn chính thức tương đương không?
- Có thể tải/crawl ảnh hợp lệ không?
- Dữ liệu ảnh SGV có được lưu local và có nên đưa vào Git không?

### Pha 2 — Danh mục học liệu v0

Mục tiêu: tạo bảng khối lớp, sách, chủ đề, bài học, trang/vị trí đủ dùng cho Plan 04.

Output dự kiến:

- `shared/learning_resources/registries/sgk_sgv_source_registry.csv`
- `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv`
- `shared/learning_resources/registries/sgk_thcs_lesson_position_registry_v0.csv`
- report trong experiment: `reports/learning-resource-registry-v0-for-hnmu-audit.md`

Bản v0 có thể dựa trên:

- ảnh SGK đã crawl;
- mục lục/chủ đề đã xử lý ở experiment `20260705_215045`;
- cột `Bài` và `Vị trí` trong dữ liệu HNMU;
- kiểm tra thủ công có giới hạn khi OCR chưa đủ tin cậy.

### Pha 3 — OCR và kiểm tra văn bản

Mục tiêu: OCR các ảnh cần thiết, ưu tiên mục lục và các trang học liệu thường được dùng trong dữ liệu HNMU.

Output dự kiến:

- OCR text theo trang;
- bảng chất lượng OCR;
- danh sách trang cần kiểm tra thủ công;
- trạng thái `needs_uet_review` hoặc `needs_hnmu_review` cho phần chưa chắc.

### Pha 4 — Fragment học liệu

Mục tiêu: chia học liệu thành đoạn có thể truy vết theo khối lớp, loại sách, chủ đề, bài học, trang và mục nhỏ.

Output dự kiến:

- `learning_resource_fragments.csv`
- quy tắc ID học liệu v0;
- trạng thái xác nhận của từng fragment.

### Pha 5 — Thiết kế database/retrieval system

Mục tiêu: thiết kế hệ thống quản lý học liệu để sau này model có thể truy vấn khi đánh giá.

Output dự kiến:

- schema database v0;
- API/retrieval contract v0;
- policy phân quyền chỉnh sửa học liệu;
- kế hoạch đồng bộ với benchmark samples.

## 4. Nguyên tắc

1. Không dùng OCR chưa kiểm tra làm nguồn chân lý.
2. Mọi trang, mục, fragment phải truy vết được tới ảnh/trang nguồn.
3. Tên chủ đề/bài học phải có trạng thái: `draft`, `needs_uet_review`, `needs_hnmu_review`, `confirmed`, hoặc `retired`.
4. Khi chưa có SGV crawl/OCR, các kiểm tra liên quan đến `Đáp án (SGV)` chỉ được coi là kiểm tra sơ bộ và phải gắn cờ `needs_sgv_verification`.
5. Không thiết kế database quá sớm trước khi có registry và fragment v0.
6. HNMU giữ quyền xác nhận nội dung chuyên môn và cách nhóm chủ đề.

## 5. Tiêu chí hoàn thành bản v0

Bản v0 hoàn thành khi có:

1. Ảnh SGK đã crawl được đăng ký trong manifest dùng chung hoặc có kế hoạch copy rõ ràng.
2. Kế hoạch crawl SGV tương ứng được ghi rõ, kể cả rủi ro nguồn/quyền.
3. Danh mục SGK Tin học THCS lớp 6–9 ở mức chủ đề/bài học.
4. Truy vết từ từng mục về ảnh/trang nguồn.
5. Báo cáo nêu rõ phần nào chắc chắn, phần nào cần HNMU xác nhận.
6. Đủ thông tin để Plan 04 dùng làm thước đo độ phủ batch HNMU.

## 6. Ngoài phạm vi bản v0

- Không xây database production ngay.
- Không bắt model truy vấn học liệu ngay.
- Không tự xác nhận nội dung chuyên môn thay HNMU.
- Không xóa hoặc di chuyển bản ảnh SGK cũ trong experiment `20260705_215045` nếu chưa có quyết định rõ.

## 7. Kết quả Pha 0 ngày 15/07/2026

Pha 0 đã hoàn thành theo phạm vi được Quân duyệt:

- Copy ảnh SGK Tin học 6–9 từ `experiments/20260705_215045/source_scope/raw_page_images` sang `shared/learning_resources/raw_page_images/sgk/`.
- Tổng số ảnh đã đăng ký trong manifest: **356**.
- Tạo/cập nhật `shared/learning_resources/registries/learning_resource_file_manifest.csv`.
- Tạo `shared/learning_resources/registries/sgk_sgv_source_registry.csv` theo schema v0 của `learning-resource-curator`.
- Ghi nhận các URL SGV Tin học 6–9 do Quân cung cấp để chuẩn bị cho Pha 1, nhưng chưa crawl SGV.
- Tạo báo cáo `experiments/20260709_155523/reports/sgk-image-shared-migration-result.md`.

Các ảnh SGK cũ ở experiment `20260705_215045` được giữ nguyên.


## 8. Kết quả Pha 1 ngày 15/07/2026

Pha 1 đã hoàn thành theo phạm vi được Quân duyệt:

- Crawl ảnh SGV Tin học 6–9 từ các URL `taphuan.nxbgd.vn` đã cung cấp.
- Lưu ảnh vào `shared/learning_resources/raw_page_images/sgv/`.
- Tổng số ảnh SGV đã đăng ký trong manifest: **396**.
- Cập nhật `shared/learning_resources/registries/learning_resource_file_manifest.csv`.
- Cập nhật `shared/learning_resources/registries/sgk_sgv_source_registry.csv`.
- Tạo báo cáo `experiments/20260709_155523/reports/sgv-crawl-source-and-risk-notes.md`.

Số ảnh theo lớp:

| Sách | Số ảnh SGV |
| --- | ---: |
| Tin học 6 | 98 |
| Tin học 7 | 94 |
| Tin học 8 | 102 |
| Tin học 9 | 102 |

Pha này chưa OCR, chưa fragment và chưa xác nhận nội dung chuyên môn.


## 9. Kết quả tạo PDF dẫn xuất ngày 15/07/2026

Đã tạo 8 PDF dẫn xuất từ ảnh SGK/SGV Tin học 6–9 để người dùng dễ mở xem.

- Thư mục PDF: `shared/learning_resources/compiled_documents/`
- Manifest đã cập nhật: `shared/learning_resources/registries/learning_resource_file_manifest.csv`
- Báo cáo: `experiments/20260709_155523/reports/compiled-learning-resource-pdfs-result.md`

PDF là bản dẫn xuất để xem nhanh, không thay thế ảnh từng trang và không thay thế truy vết trong manifest.


## 10. Kết quả Pha 2 ngày 15/07/2026

Pha 2 đã tạo danh mục học liệu v0 phục vụ Plan 04:

- `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv`
- `shared/learning_resources/registries/sgk_thcs_lesson_position_registry_v0.csv`
- `experiments/20260709_155523/reports/learning-resource-registry-v0-for-hnmu-audit.md`

Nguyên tắc bảo thủ:

- Lớp 6–7 lấy bài/vị trí từ dữ liệu HNMU, nhóm chủ đề là suy luận và cần HNMU xác nhận.
- Lớp 9 dùng lại OCR mục lục từ experiment `20260705_215045`, chưa chốt chính thức.
- Lớp 8 chưa tạo danh mục bài học vì chưa có OCR mục lục hoặc nguồn HNMU xác nhận.
- Registry vị trí v0 giữ cả vị trí cấp bài và một số vị trí cấp chủ đề/phụ lục của Tin học 9. Vì vậy, cột `lesson_item_id` trong bản v0 nên được hiểu là tham chiếu tới `item_id` học liệu trong topic/lesson map; tên cột này có thể cần đổi thành tên tổng quát hơn trong pha thiết kế schema sau.
