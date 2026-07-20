# Registry học liệu SGK/SGV Tin học THCS

Thư mục này chứa các bảng registry dùng chung cho học liệu SGK/SGV Tin học 6–9. Registry ở đây không phải là dữ liệu benchmark cuối cùng; chúng là lớp trung gian để truy vết học liệu, thống kê độ phủ, truy xuất đoạn học liệu và kiểm tra tính nhất quán của dữ liệu hội thoại HNMU.

Trạng thái hiện tại: `draft`. Các registry đã đủ dùng cho audit và truy xuất v0, nhưng chưa thay thế xác nhận chuyên môn cuối cùng của HNMU/UET.

## 1. Cách đọc tổng quát

Có thể hình dung các registry theo 5 tầng:

```text
Quyển SGK/SGV
→ sgk_sgv_source_registry.csv

File ảnh/trang gốc
→ learning_resource_file_manifest.csv

File Markdown OCR đã xử lý
→ ocr_text_manifest.csv

Chủ đề và bài học theo mục lục SGK/SGV
→ sgk_thcs_topic_lesson_map_v0.csv

Vị trí cụ thể trong bài/trang
→ sgk_thcs_lesson_position_registry_v0.csv
```

Các file này bổ trợ cho nhau, nhưng không thay thế nhau. Khi audit dữ liệu HNMU, cần đặc biệt phân biệt:

- **Chủ đề/bài học chuẩn**: lấy từ `sgk_thcs_topic_lesson_map_v0.csv`.
- **Nội dung truy xuất để đối chiếu**: lấy qua `ocr_text_manifest.csv`, `learning_resource_fragments.csv` và SQLite index trong `shared/learning_resources/indexes/`.
- **Vị trí cụ thể do dữ liệu HNMU nêu ra**: đối chiếu thêm bằng `sgk_thcs_lesson_position_registry_v0.csv`, nhưng không dùng file này làm nguồn chuẩn cho chủ đề.

## 2. Vai trò từng file

### 2.1. `sgk_sgv_source_registry.csv`

Vai trò: registry cấp **quyển sách**.

File này trả lời các câu hỏi:

- Có những quyển SGK/SGV nào đang được quản lý?
- Quyển đó thuộc lớp mấy?
- Là SGK hay SGV?
- URL gốc là gì?
- Mã nguồn trên trang tập huấn là gì?
- Dữ liệu local của quyển đó nằm ở thư mục nào?
- Trạng thái hiện tại là gì?

Các cột chính:

| Cột | Ý nghĩa |
| --- | --- |
| `learning_material_id` | Mã định danh cấp quyển, ví dụ `LM-SGK-TIN6-0001`. |
| `source_title` | Tên học liệu, ví dụ `Sách giáo khoa Tin học 6`. |
| `material_type` | Loại học liệu: thường là `SGK` hoặc `SGV`. |
| `grade` | Khối lớp. |
| `source_url` | URL nguồn trên trang tập huấn. |
| `source_key` | Mã nguồn rút từ URL hoặc hệ thống nguồn. |
| `local_file_path` | Thư mục local chứa ảnh trang gốc. |
| `version_label` | Nhãn phiên bản/lượt xử lý. |
| `status` | Trạng thái, hiện thường là `draft`. |
| `notes` | Ghi chú về nguồn, OCR, PDF dẫn xuất, quyền sử dụng hoặc điểm cần review. |

Khi dùng:

- Dùng để biết một `learning_material_id` thuộc quyển nào.
- Dùng để truy vết từ fragment hoặc OCR Markdown ngược về học liệu gốc.
- Dùng khi cần kiểm tra đã có đủ SGK/SGV cho một lớp hay chưa.

Không nên dùng để:

- Thống kê coverage theo bài học/chủ đề. Việc đó thuộc `sgk_thcs_topic_lesson_map_v0.csv`.
- Truy xuất nội dung chi tiết trong bài. Việc đó thuộc fragment/index.

### 2.2. `learning_resource_file_manifest.csv`

Vai trò: manifest cấp **file ảnh/trang gốc**.

File này ghi lại từng ảnh trang học liệu đang được quản lý trong `shared/learning_resources/raw_page_images/`.

Các cột chính:

| Cột | Ý nghĩa |
| --- | --- |
| `resource_batch_id` | Lượt copy/crawl/đăng ký file. |
| `source_type` | Loại nguồn, ví dụ `SGK` hoặc `SGV`. |
| `grade` | Khối lớp. |
| `source_path` | Đường dẫn ban đầu trước khi đưa vào `shared/`. |
| `shared_path` | Đường dẫn ảnh trong vùng shared. |
| `sha256` | Checksum để phát hiện file thay đổi hoặc trùng file. |
| `file_size_bytes` | Kích thước file. |
| `registered_date` | Ngày đăng ký. |
| `processing_status` | Trạng thái xử lý file, ví dụ `copied`, `crawled`. |
| `notes` | Ghi chú về nguồn và trạng thái OCR. |

Khi dùng:

- Dùng để truy vết file ảnh vật lý.
- Dùng khi cần kiểm tra file nặng nào có nguy cơ push nhầm.
- Dùng khi cần xác minh một ảnh trang có đúng là ảnh đã copy/crawl từ nguồn trước đó không.

Không nên dùng để:

- Làm nguồn chuẩn cho nội dung văn bản sau OCR.
- Thống kê coverage theo bài học/chủ đề.

### 2.3. `ocr_text_manifest.csv`

Vai trò: manifest cấp **đơn vị OCR Markdown**.

Đây là registry quan trọng để nối từ học liệu gốc sang bản Markdown đã OCR. Mỗi dòng thường tương ứng với một bài hoặc một đơn vị xử lý OCR.

Các cột chính:

| Cột | Ý nghĩa |
| --- | --- |
| `ocr_text_id` | Mã đơn vị OCR Markdown, ví dụ `OCR-SGK-TIN6-BAI01`. |
| `learning_material_id` | Mã quyển sách tương ứng trong `sgk_sgv_source_registry.csv`. |
| `material_type` | `SGK` hoặc `SGV`. |
| `grade` | Khối lớp. |
| `book_title` | Tên quyển sách. |
| `lesson_key` | Khóa bài học dạng ổn định, ví dụ `bai_01`. |
| `lesson_number` | Số bài, nếu có. |
| `lesson_title` | Tên bài học. |
| `topic_title` | Tên chủ đề chứa bài học. |
| `source_markdown_path` | Đường dẫn file Markdown OCR. |
| `source_metadata_path` | Đường dẫn metadata đi kèm, nếu có. |
| `image_dir` | Thư mục ảnh/phụ kiện đi kèm OCR Markdown. |
| `page_marker_count` | Số marker trang nhận diện được trong Markdown. |
| `page_stat_count` | Số trang theo thống kê metadata. |
| `table_count` | Số bảng phát hiện trong Markdown. |
| `image_count` | Số ảnh/hình minh họa trong đơn vị OCR. |
| `first_heading` | Heading đầu tiên trong Markdown. |
| `status` | Trạng thái của OCR Markdown, hiện thường là `draft`. |
| `notes` | Ghi chú thêm. |

Khi dùng:

- Dùng để biết file Markdown OCR của một bài nằm ở đâu.
- Dùng làm đầu vào để tách fragment và build retrieval index.
- Dùng để truy vết một fragment về bài học/quyển sách gốc.

Không nên dùng để:

- Chốt chính thức chủ đề/bài học nếu chưa đối chiếu mục lục. Việc này nên dựa vào `sgk_thcs_topic_lesson_map_v0.csv`.
- Coi OCR là chân lý tuyệt đối; trạng thái hiện vẫn là `draft`.

### 2.4. `sgk_thcs_topic_lesson_map_v0.csv`

Vai trò: bản đồ **chủ đề → bài học** theo mục lục SGK/SGV Tin học THCS.

Đây là file quan trọng nhất cho thống kê coverage theo chủ đề và bài học. Các bài học phụ thuộc vào từng lớp, còn chủ đề là trục xuyên suốt để nhìn toàn bộ THCS.

Các cột chính:

| Cột | Ý nghĩa |
| --- | --- |
| `item_id` | Mã chủ đề hoặc bài học, ví dụ `TIN6-CD01`, `TIN6-B01`. |
| `parent_id` | Mã cha. Với bài học, đây là mã chủ đề chứa bài đó. |
| `item_type` | Loại item: `chu_de` hoặc `bai_hoc`. |
| `grade` | Khối lớp. |
| `source_label` | Nhãn gốc theo mục lục, ví dụ `Chủ đề 1. Máy tính và cộng đồng`. |
| `normalized_label` | Nhãn đã chuẩn hóa để so khớp/thống kê. |
| `print_page_start` | Trang in bắt đầu theo mục lục. |
| `source_image_page_start` | Trang ảnh bắt đầu, nếu đã map chắc. |
| `learning_material_id` | Quyển SGK/SGV chứa item này. |
| `evidence_type` | Loại bằng chứng dùng để tạo dòng registry. |
| `evidence_source` | Nguồn bằng chứng, thường là file OCR Markdown chứa mục lục. |
| `status` | Trạng thái xác nhận. |
| `notes` | Ghi chú về nguồn và việc cần HNMU/UET review. |

Khi dùng:

- Dùng để map trường `Bài` trong dữ liệu HNMU sang bài học chuẩn.
- Dùng để thống kê coverage theo `topic` và `lesson_by_grade`.
- Dùng để xác định bài học thuộc chủ đề nào.
- Dùng làm nguồn chuẩn hơn so với cách ghi tự do trong dữ liệu thô HNMU.

Không nên dùng để:

- Truy xuất nội dung chi tiết trong bài. Muốn đọc nội dung thì dùng OCR Markdown/fragment/index.
- Thay thế xác nhận chuyên môn của HNMU/UET, vì nhiều dòng vẫn là `needs_hnmu_review`.

Lưu ý quan trọng:

- Khi thống kê bài học, luôn kèm `grade`, vì “Bài 1” ở lớp 6 khác “Bài 1” ở lớp 7/8/9.
- Khi thống kê chủ đề, nên dùng `normalized_label` và cân nhắc chuẩn hóa viết hoa/thường, ví dụ `Hướng nghiệp với Tin học` và `Hướng nghiệp với tin học`.

### 2.5. `sgk_thcs_lesson_position_registry_v0.csv`

Vai trò: registry cấp **vị trí cụ thể trong bài/trang**.

File này ghi các vị trí như “Hoạt động 1, Trang 6 SGK”, “Câu 1.b, Luyện tập, Trang 7 SGK”, hoặc các vị trí trong SGV được dữ liệu HNMU nhắc đến.

Các cột chính:

| Cột | Ý nghĩa |
| --- | --- |
| `position_id` | Mã vị trí cụ thể. |
| `grade` | Khối lớp. |
| `learning_material_id` | Quyển sách liên quan. |
| `material_type` | `SGK` hoặc `SGV`. |
| `lesson_item_id` | Mã bài học trong `sgk_thcs_topic_lesson_map_v0.csv`, nếu map được. |
| `lesson_label` | Tên bài học. |
| `position_label` | Vị trí cụ thể trong bài/trang. |
| `print_page` | Trang in được nhắc tới. |
| `page_kind` | Cách hiểu trang, ví dụ lấy từ cột `Vị trí` của HNMU. |
| `source_image_path` | Ảnh trang nếu đã map chắc. Hiện có thể để trống. |
| `pdf_path` | PDF dẫn xuất để người dùng mở xem nhanh. |
| `source_batch` | Batch dữ liệu HNMU tạo ra vị trí này. |
| `evidence_type` | Loại bằng chứng của vị trí. |
| `status` | Trạng thái xác nhận. |
| `hnmu_dialogue_count` | Số mẫu HNMU nhắc tới vị trí này. |
| `notes` | Ghi chú về độ chắc chắn. |

Khi dùng:

- Dùng để truy vết vị trí mà giáo viên HNMU nêu trong dữ liệu thô.
- Dùng để biết vị trí nào được nhiều mẫu hội thoại nhắc tới.
- Dùng làm gợi ý để người/agent mở đúng trang PDF hoặc tìm fragment liên quan.

Không nên dùng để:

- Làm nguồn chuẩn cho chủ đề. Chủ đề phải lấy từ `sgk_thcs_topic_lesson_map_v0.csv`.
- Kết luận chắc chắn về trang ảnh nếu `source_image_path` còn trống hoặc `status` chưa confirmed.

## 3. Quan hệ với fragment và retrieval index

Registry trong thư mục này không trực tiếp chứa toàn bộ nội dung học liệu. Nội dung chi tiết nằm ở các lớp sau:

```text
shared/learning_resources/ocr_text/
shared/learning_resources/fragments/learning_resource_fragments.csv
shared/learning_resources/indexes/learning_resources_v0.sqlite
```

Luồng truy xuất thường là:

```text
Dữ liệu HNMU có grade + Bài + Vị trí + Câu hỏi/Đáp án
→ map bài/chủ đề bằng sgk_thcs_topic_lesson_map_v0.csv
→ tìm OCR unit bằng ocr_text_manifest.csv
→ tìm đoạn học liệu bằng fragment/index
→ ghi evidence_fragment_id trong audit output
```

Vì vậy, registry là “bản đồ”, còn fragment/index là “nội dung có thể đọc và tìm kiếm”.

## 4. Quy tắc sử dụng trong Plan 04 audit

Khi kiểm dữ liệu hội thoại HNMU:

1. Không lấy cột `Bài` trong dữ liệu HNMU làm chuẩn tuyệt đối. Cột đó là input cần map sang registry.
2. Chủ đề và bài học chuẩn lấy từ `sgk_thcs_topic_lesson_map_v0.csv`.
3. Bài học phải luôn gắn với lớp.
4. Vị trí cụ thể trong SGK/SGV có thể đối chiếu bằng `sgk_thcs_lesson_position_registry_v0.csv`, nhưng nếu chưa map chắc trang ảnh thì phải giữ cờ review.
5. Nội dung SGK/SGV để kiểm câu hỏi/đáp án/hội thoại phải truy xuất qua fragment/index, không đọc thủ công cả thư mục Markdown.
6. Nếu evidence có `status = draft`, kết luận phải ghi là sơ bộ và không thay thế HNMU/UET review.

## 5. Khi nào cần cập nhật file nào?

| Tình huống | File cần cập nhật |
| --- | --- |
| Thêm một quyển SGK/SGV mới | `sgk_sgv_source_registry.csv` |
| Copy/crawl thêm ảnh trang | `learning_resource_file_manifest.csv` |
| Nguyên gửi thêm OCR Markdown hoặc OCR được thay thế | `ocr_text_manifest.csv` |
| Chốt/sửa mục lục, chủ đề, bài học | `sgk_thcs_topic_lesson_map_v0.csv` |
| Có vị trí học liệu mới từ dữ liệu HNMU hoặc đã map được trang cụ thể | `sgk_thcs_lesson_position_registry_v0.csv` |
| Muốn agent tìm kiếm nội dung tốt hơn | rebuild `learning_resource_fragments.csv` và SQLite index, không chỉ sửa registry |

## 6. Trạng thái và giới hạn hiện tại

- Phần lớn registry vẫn ở mức `draft` hoặc `needs_hnmu_review`.
- Các file được tạo để phục vụ audit và truy xuất v0, chưa phải hệ database học liệu chính thức.
- Một số nhãn chủ đề/bài học, đặc biệt bài nhánh A/B lớp 8–9, có thể cần chuẩn hóa thêm để giảm nhóm `Không rõ chủ đề` trong audit.
- Không nên push ảnh/nguồn học liệu nặng hoặc có khả năng vướng bản quyền lên GitHub nếu chưa có quyết định rõ.

## 7. Đường dẫn liên quan

- Học liệu OCR Markdown: `shared/learning_resources/ocr_text/`
- Fragment học liệu: `shared/learning_resources/fragments/learning_resource_fragments.csv`
- SQLite retrieval index: `shared/learning_resources/indexes/learning_resources_v0.sqlite`
- Hub cho audit agent: `shared/learning_resources/agent_context/README.md`
- Raw data HNMU: `shared/raw_data/HNMU-teacher_dialog_samples/`
- Code xử lý học liệu: `src/edu_benchmark/learning_resources/`
