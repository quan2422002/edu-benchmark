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
```

## Quy tắc an toàn

1. Ảnh SGK/SGV có thể là tài nguyên có bản quyền; không mặc định push ảnh lên GitHub nếu chưa rõ quyền.
2. Mọi file ảnh/học liệu đưa vào đây cần được ghi vào manifest.
3. OCR chưa được kiểm tra không được coi là nguồn chân lý.
4. Các phần cần HNMU xác nhận phải được gắn trạng thái rõ ràng.

Plan 03 sẽ chịu trách nhiệm copy ảnh SGK đã crawl, bổ sung kế hoạch SGV và tạo registry học liệu v0.
