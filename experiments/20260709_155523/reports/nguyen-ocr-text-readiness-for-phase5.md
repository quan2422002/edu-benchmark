# Đánh giá nhanh dữ liệu OCR Markdown của Nguyên cho Pha 5 Plan 03

Ngày kiểm tra: 16/07/2026  
Thư mục kiểm tra: `shared/learning_resources/ocr_text`

## 1. Kết luận ngắn

Dữ liệu Markdown do Nguyên gửi **rất có giá trị và nên được dùng làm nguồn chính cho Pha 4** của Plan 03 đối với SGK/SGV Tin học 6.

Tuy nhiên, **chưa nên dùng trực tiếp ngay cho Pha 5 như một cơ sở truy xuất hoàn chỉnh**, vì Pha 5 cần dữ liệu đã được tách thành các đoạn học liệu có mã ổn định, metadata đủ giàu và index truy xuất. Các file hiện tại đang ở mức “Markdown theo bài/mục”, chưa phải “fragment truy xuất”.

Nếu cần làm bản thử nghiệm rất nhanh, có thể build một index tạm ở cấp bài học. Nhưng bản đúng hướng nên là:

```text
Markdown theo bài/mục của Nguyên
→ chuẩn hóa metadata
→ tách fragment
→ tạo bảng fragment
→ build SQLite/DuckDB full-text search
→ specialist agent truy xuất bằng fragment_id
```

## 2. Những gì đã có

Thống kê nhanh trong `shared/learning_resources/ocr_text`:

| Nhóm học liệu | Số thư mục bài/mục | Số file Markdown | Số file metadata | Số ảnh minh họa |
|---|---:|---:|---:|---:|
| SGK Tin học 6 | 17 | 17 | 17 | 237 |
| SGV Tin học 6 | 18 | 18 | 18 | 168 |

Nhận xét:

- SGK Tin học 6 có đủ 17 bài.
- SGV Tin học 6 có 17 bài và thêm mục hướng dẫn chung.
- Markdown giữ được heading, bảng, ảnh và mốc trang dạng `{0}`, `{1}`, ...
- Số mốc trang trong Markdown khớp với `page_stats` trong metadata.
- Một số bảng phức tạp được giữ bằng Markdown table, tốt hơn đáng kể so với output text thuần trước đây.

Ví dụ đã đọc:

- `shared/learning_resources/ocr_text/sgk_tin_hoc_6/tin_6_bai_1/tin_6_bai_1.md`
- `shared/learning_resources/ocr_text/sgk_tin_hoc_6/tin_6_bai_17/tin_6_bai_17.md`
- `shared/learning_resources/ocr_text/sgv_tin_hoc_6/sgv_tin_6_bai_1/sgv_tin_6_bai_1.md`
- `shared/learning_resources/ocr_text/sgv_tin_hoc_6/sgv_tin_6_00_hd_chung/sgv_tin_6_00_hd_chung.md`

## 3. Vì sao chưa dùng thẳng cho Pha 5?

Pha 5 không chỉ cần “có Markdown tốt”. Pha 5 cần một lớp truy xuất ổn định để agent/model có thể hỏi đúng vùng học liệu cần đọc.

Các file hiện tại còn thiếu một số thành phần cho truy xuất:

1. Metadata chưa đủ giàu  
   Các file `.metadata.json` hiện chủ yếu có `page_stats`, ví dụ số block theo `page_id`. Chưa có đủ các trường như:

   - khối lớp;
   - loại sách: SGK hay SGV;
   - tên bài;
   - chủ đề;
   - trang SGK/SGV thật;
   - đường dẫn ảnh nguồn;
   - trạng thái kiểm duyệt;
   - quan hệ SGK–SGV tương ứng.

2. Chưa có mã đoạn học liệu  
   Specialist agent cần truy xuất đến một đoạn cụ thể, ví dụ một mục, một bảng, một bài luyện tập, một hướng dẫn dạy học. Hiện tại mỗi file vẫn là một bài/mục khá dài.

3. Chưa có bảng fragment  
   Plan 03 Pha 4 yêu cầu tạo `shared/learning_resources/fragments/learning_resource_fragments.csv`. Bảng này mới là lớp trung gian quan trọng để Pha 5 build index.

4. Chưa có index truy xuất  
   Pha 5 cần SQLite/DuckDB full-text search, kèm metadata filter. Hiện tại dữ liệu mới ở dạng file.

## 4. Nên tận dụng dữ liệu này ở đâu?

### 4.1. Thay thế output OCR cũ làm nguồn chính cho Pha 4

Nên coi `shared/learning_resources/ocr_text` là **đầu vào chính thức cho Pha 4** với SGK/SGV Tin học 6.

Các output OCR cũ trong experiment, đặc biệt:

- `experiments/20260709_155523/outputs/learning_resource_phase3_grade6_7_all/parsed_pages`
- các output PaddleOCR + VietOCR dạng text/Markdown nháp

chỉ nên giữ làm dữ liệu debug hoặc so sánh, không nên dùng làm nguồn chính để tách fragment.

### 4.2. Tạo registry riêng cho OCR Markdown

Nên thêm một manifest/registry nhẹ, ví dụ:

```text
shared/learning_resources/registries/ocr_text_manifest.csv
```

Vai trò:

- đăng ký từng file Markdown;
- ghi rõ sách, lớp, bài, loại sách, số mốc trang, số ảnh;
- ghi trạng thái `draft` hoặc `needs_uet_review`;
- nối với `learning_material_id` hiện có trong `sgk_sgv_source_registry.csv`;
- tạo điểm vào ổn định cho Pha 4.

### 4.3. Tách fragment từ Markdown theo bài/mục

Pha 4 nên tách fragment theo thứ tự ưu tiên:

1. heading lớn trong bài;
2. mục kiến thức;
3. hoạt động/luyện tập/vận dụng;
4. bảng;
5. khối hướng dẫn dạy học trong SGV;
6. đoạn văn ngắn có thể dùng làm căn cứ kiểm tra câu hỏi, đáp án hoặc hội thoại.

Mỗi fragment nên giữ:

- `fragment_id`;
- `learning_material_id`;
- `book_type`;
- `grade`;
- `lesson_id`;
- `lesson_title`;
- `topic_title`;
- `page_marker`;
- `section_path`;
- `fragment_type`;
- `markdown_text`;
- `source_markdown_path`;
- `source_image_paths` nếu có;
- `status`;
- `notes`.

### 4.4. Build Pha 5 từ fragment, không build trực tiếp từ nguyên file bài

Sau khi có fragment, Pha 5 có thể build index bằng SQLite/DuckDB full-text search.

Các hàm truy xuất tối thiểu vẫn giữ như Plan 03:

```text
resolve_learning_resource(metadata)
search_learning_fragments(query, filters)
get_learning_fragment(fragment_id)
```

## 5. Có thể làm bản Pha 5 tạm ngay không?

Có, nhưng chỉ nên gọi là **prototype truy xuất cấp bài học**, không phải Pha 5 hoàn chỉnh.

Prototype này có thể index 35 file Markdown hiện có, mỗi bài/mục là một bản ghi. Cách này giúp test nhanh:

- agent có tìm đúng bài không;
- truy vấn theo từ khóa có ra đúng SGK/SGV không;
- dữ liệu Markdown có đủ tốt để hỗ trợ kiểm nhất quán mẫu hội thoại thô không.

Nhược điểm:

- kết quả trả về còn quá dài;
- agent vẫn phải đọc nhiều hơn mức cần thiết;
- khó chỉ đúng một bảng, một mục hoặc một đoạn căn cứ;
- chưa đạt yêu cầu “không phải đọc toàn bộ một file Markdown”.

Vì vậy, prototype cấp bài chỉ phù hợp để kiểm nhanh, không nên coi là bản Pha 5 chính.

## 6. Việc cần làm tiếp

Đề xuất thứ tự tiếp theo:

1. Tạo `ocr_text_manifest.csv` cho thư mục Nguyên gửi.
2. Chuẩn hóa metadata tối thiểu cho SGK/SGV Tin học 6.
3. Viết script tách fragment từ Markdown.
4. Xuất `learning_resource_fragments.csv`.
5. Build SQLite/DuckDB full-text search từ fragment.
6. Test truy xuất trên vài câu hỏi thật từ dữ liệu HNMU:
   - “Scratch trung bình cộng ba số”;
   - “thông tin và dữ liệu”;
   - “an toàn thông tin trên Internet”;
   - “chương trình máy tính”;
   - “hướng dẫn dạy học Bài 17”.

## 7. Lưu ý về Git và dữ liệu nặng

Thư mục `shared/learning_resources/ocr_text` có nhiều ảnh `.jpg`. Hiện `.gitignore` chưa có rule riêng để bỏ qua các ảnh này.

Nên cân nhắc:

- track Markdown và metadata nếu dung lượng hợp lý;
- ignore ảnh minh họa nặng nếu không cần push lên GitHub;
- hoặc chỉ track manifest, còn dữ liệu OCR đầy đủ lưu bằng Google Drive/DVC/cơ chế dữ liệu ngoài repo.

Chưa nên tự ý thay đổi `.gitignore` trước khi chốt chính sách lưu các ảnh trong `ocr_text`.

## 8. Kết luận

Dữ liệu Nguyên gửi **không nên đi thẳng vào Pha 5 bản hoàn chỉnh**, nhưng **nên trở thành nguồn đầu vào chính của Pha 4**, thay cho các output OCR nháp trước đó.

Nếu muốn đi nhanh, ta có thể làm một prototype Pha 5 cấp bài học trong thời gian ngắn. Nhưng để phục vụ specialist agent kiểm nhất quán dữ liệu HNMU một cách chặt chẽ, hướng đúng vẫn là: chuẩn hóa metadata → tách fragment → build index truy xuất từ fragment.
