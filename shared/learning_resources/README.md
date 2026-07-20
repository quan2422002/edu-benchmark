# Học liệu dùng chung

Thư mục này dành cho học liệu dùng chung của toàn dự án, gồm SGK, SGV, văn bản OCR, danh mục bài học, fragment và các bảng truy vết.

## Vai trò

Học liệu trong thư mục này phục vụ bốn việc chính:

1. Kiểm tra dữ liệu HNMU có phủ đủ chủ đề/bài học hay không.
2. Đối chiếu câu hỏi, đáp án và vị trí học liệu.
3. Tạo truy vết từ mẫu benchmark về nguồn học liệu.
4. Chuẩn bị nền cho hệ thống truy xuất học liệu về dài hạn.

## Cấu trúc

```text
shared/learning_resources/
  raw_page_images/
    sgk/
      tin_hoc_6/
      tin_hoc_7/
      tin_hoc_8/
      tin_hoc_9/
    sgv/
      tin_hoc_6/
      tin_hoc_7/
      tin_hoc_8/
      tin_hoc_9/
  ocr_text/
  registries/
  fragments/
  indexes/
  agent_context/
```

## Hướng dẫn vận hành

- [OCR_TEXT_PROCESSING_RUNBOOK.md](OCR_TEXT_PROCESSING_RUNBOOK.md): hướng dẫn đưa OCR Markdown SGK/SGV mới do Nguyên gửi vào manifest, fragment và index truy xuất. Dùng file này khi bổ sung lớp 8, lớp 9 hoặc các sách mới cùng chuẩn.
- [agent_context/README.md](agent_context/README.md): hub ngữ cảnh để specialist agent kiểm tra dữ liệu HNMU biết cần dùng checklist, fragment, index và công cụ truy xuất nào.

## Quy tắc an toàn

1. Ảnh SGK/SGV có thể là tài nguyên có bản quyền; không mặc định push ảnh lên GitHub nếu chưa rõ quyền.
2. Mọi file ảnh/học liệu đưa vào đây cần được ghi vào manifest.
3. OCR chưa được kiểm tra không được coi là nguồn chân lý.
4. Các phần cần HNMU xác nhận phải được gắn trạng thái rõ ràng.

Plan 03 đã đưa SGK/SGV Tin học 6–9 vào hệ học liệu dùng chung ở mức v0: ảnh gốc/ảnh crawl được quản lý bằng `learning_resource_file_manifest.csv`, OCR Markdown do Nguyên gửi được đăng ký trong `ocr_text_manifest.csv` với 154 đơn vị, tách thành 2.750 fragment và build thành SQLite FTS index truy xuất. Các fragment hiện vẫn ở trạng thái `draft`, chưa thay thế xác nhận chuyên môn của HNMU/UET.
