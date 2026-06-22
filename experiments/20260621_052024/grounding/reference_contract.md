# Reference contract

## Mục đích

Mọi câu hỏi, câu trả lời minh họa và rubric criterion trong C01 phải truy ngược được tới căn cứ cụ thể. Chỉ ghi URL chung của tài liệu là không đủ.

## Loại reference

- `curriculum`: nội dung học sinh lớp 9 cần biết hoặc làm được.
- `research`: hành vi tutoring, cách thiết kế task/rubric hoặc phương pháp đánh giá được literature hỗ trợ.
- `internal_draft`: workbook hoặc artifact nội bộ dùng để tham khảo cấu trúc/mẫu, không phải bằng chứng chuẩn tắc.

## Trường bắt buộc

```text
reference_id
source_id
reference_type
title
url_or_path
publisher
year
grade
strand
topic
page
section_or_table
location_note
short_excerpt_or_paraphrase
accessed_at
```

## Quy tắc vị trí

- `page`: số trang hiển thị trong PDF. Nếu số trang in trên tài liệu khác PDF index, ghi rõ cả hai trong `location_note`.
- `section_or_table`: tên phần, mục, bảng hoặc tiêu đề gần nhất.
- `location_note`: mô tả đủ để người khác tìm lại, ví dụ “bảng yêu cầu cần đạt lớp 9, hàng Chủ đề E”.
- Nếu nguồn HTML không có trang, để `page` trống và ghi heading/anchor/path trong `location_note`.
- Không ghi số trang, mục, khoản hoặc trích đoạn nếu chưa kiểm tra trực tiếp.

## Trích dẫn

- Ưu tiên diễn giải trung thành.
- Chỉ dùng trích đoạn ngắn khi wording của nguồn quan trọng.
- Không sao chép đoạn dài vào artifact.
- Mỗi diễn giải phải giữ nguyên phạm vi, đối tượng và mức độ bắt buộc của nguồn.
- Nguồn giải thích không được trình bày như văn bản chuẩn tắc.

## Reference ID

```text
CURR-G9-<strand>-NNN  yêu cầu chương trình lớp 9
GUIDE-G9-NNN          diễn giải từ tài liệu bồi dưỡng
LIT-NNN               literature claim từ P02
WB-NNN                workbook/internal draft reference
```

ID ổn định trong experiment. Không dùng số dòng Excel làm ID.

## Evidence status

- `supported`: có căn cứ trực tiếp và đã kiểm tra vị trí.
- `provisional`: đề xuất tạm thời, đang chờ literature hoặc teacher review.
- `teacher_judgment`: quyết định chuyên môn/sư phạm thuộc giáo viên, nguồn không quy định trực tiếp.
- `open_question`: chưa đủ căn cứ để quyết định.

## Nối criterion với reference

Mỗi rubric criterion có:

```text
criterion_id
criterion_text
reference_ids
evidence_status
teacher_review_status
teacher_rationale
```

- Criterion nội dung phải có ít nhất một `CURR-*`.
- Criterion tutoring chỉ có `LIT-*` khi P02 đã cung cấp claim có provenance.
- Nếu chưa có `LIT-*`, gắn `provisional`; không dùng workbook để thay literature.
- Nếu criterion là lựa chọn sư phạm không được nguồn quy định trực tiếp, gắn `teacher_judgment`.

## Quyền quyết định

Agent có thể trích xuất, diễn giải và đề xuất mapping. Expert teacher xác nhận correctness, grade fit và pedagogical suitability. Bất đồng phải được ghi lại, không sửa âm thầm.
