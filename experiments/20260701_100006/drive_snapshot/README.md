# Snapshot đầu vào từ Google Drive

Ngày tạo snapshot: 04/07/2026  
Experiment Drive: `version 20260701_100006`  
Mục đích: đóng băng đầu vào đã dùng cho Bước 1 và chuẩn bị nguồn cho các bước tiếp theo.

## Cách đọc thư mục này

- `drive_file_manifest.csv`: bảng audit chính. Mỗi dòng là một folder hoặc file trên Drive, kèm mã Drive, loại file, thời điểm chỉnh sửa, đường dẫn local, trạng thái tải/export, kích thước và SHA-256.
- `files/teacher_packet/`: bản tải/export của các tài liệu dành cho giáo viên, trong đó `review_form.xlsx` là input chính cho Bước 1 — Kiểm tra phiếu tác giả.
- `files/literature_review/`: bản tải/export của tài liệu review nghiên cứu trong Drive experiment. Các file này chỉ được snapshot ở đây; chưa coi là literature review đầy đủ.
- `files/curriculum_sources/`: bản tải/export của tài liệu chương trình/học liệu trong Drive experiment. Các file này là input cho bước chuẩn hóa chủ đề và rà soát học liệu sau.
- `review_form.extracted.txt`: bản trích xuất text từ `files/teacher_packet/review_form.xlsx`, dùng để audit nhanh nội dung phiếu tác giả mà không cần mở Excel.

## Quy ước export

- Google Docs được export thành text/Markdown-like content để dễ đọc trong repo.
- Google Sheets được export thành `.xlsx`.
- File Office/PDF/CSV có sẵn trên Drive được tải dạng raw nếu có thể.
- Snapshot này không thay thế Google Drive gốc, không phải database học liệu production, và không tự động cập nhật khi Drive thay đổi.

## Lưu ý

Nếu cần dùng một file trong snapshot để đưa ra kết luận chuyên môn hoặc sư phạm, cần kiểm tra lại với bản Drive/HNMU khi có dấu hiệu file đã thay đổi sau ngày snapshot.
