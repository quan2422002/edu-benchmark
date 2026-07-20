# Plan 03.4–03.5 — Tách fragment và dựng truy xuất từ Markdown OCR của Nguyên

Trạng thái: `APPROVED — ĐÃ MỞ RỘNG V0 ĐẾN LỚP 6–9`
Ngày lập: 16/07/2026
Thuộc plan cha: `03-learning-resource-normalization-and-retrieval-system.md`
Phạm vi trực tiếp: Pha 4 và Pha 5 của Plan 03

## 1. Mục tiêu

Biến dữ liệu OCR Markdown chất lượng cao do Nguyên gửi trong:

```text
shared/learning_resources/ocr_text/
```

thành một lớp học liệu có thể truy xuất ổn định cho specialist agent và các bước kiểm tra dữ liệu HNMU sau này.

Luồng chốt:

```text
Markdown OCR của Nguyên
→ manifest học liệu OCR
→ metadata tối thiểu
→ fragment học liệu
→ index truy xuất
→ hàm truy xuất cho specialist agent
```

## 2. Kết luận tiền đề

Dựa trên report:

```text
experiments/20260709_155523/reports/nguyen-ocr-text-readiness-for-phase5.md
```

dữ liệu của Nguyên **nên được dùng làm nguồn chính cho Pha 4**, thay vì các output OCR/MinerU thử nghiệm cũ do Codex tạo.

Tuy nhiên, dữ liệu này **chưa nên dùng thẳng cho Pha 5 bản hoàn chỉnh**, vì hiện mới ở cấp file bài/mục, chưa có:

- mã fragment ổn định;
- metadata đủ để lọc theo lớp, sách, bài, chủ đề, trang;
- bảng fragment;
- index truy xuất;
- hàm truy xuất rõ ràng cho specialist agent.

## 3. Phạm vi

### 3.1. Làm trong plan này

- Đăng ký các file OCR Markdown của Nguyên bằng manifest.
- Chuẩn hóa metadata tối thiểu cho SGK/SGV Tin học 6–9.
- Tách fragment từ Markdown theo bài/mục.
- Tạo bảng fragment có mã ổn định.
- Dựng index truy xuất v0 bằng SQLite hoặc DuckDB full-text search.
- Tạo API/hàm truy xuất tối thiểu để specialist agent tìm đúng đoạn học liệu.
- Viết test và report kết quả chạy thử.

### 3.2. Chưa làm trong plan này

- Không OCR lại ảnh SGK/SGV.
- Không chạy lại PaddleOCR, VietOCR, MinerU hoặc DeepSeek OCR.
- Không xóa output/probe cũ.
- Không chỉnh sửa nội dung Markdown OCR do Nguyên gửi, trừ khi tạo bản dẫn xuất ở thư mục output/fragment riêng.
- Không xác nhận nội dung chuyên môn thay HNMU.
- Không thiết kế task/rubric/metadata benchmark.
- Không OCR lại ảnh SGK/SGV; với lớp mới, chỉ xử lý khi Nguyên đã gửi Markdown/metadata cùng chuẩn trong `shared/learning_resources/ocr_text/`.

## 4. Nguyên tắc an toàn dữ liệu

### 4.1. Dữ liệu nguồn của Nguyên là read-only

Các file trong:

```text
shared/learning_resources/ocr_text/
```

được xem là nguồn đầu vào. Code Pha 4–5 chỉ đọc, không ghi đè, không format lại trực tiếp.

Nếu cần chuẩn hóa hoặc sửa lỗi kỹ thuật, tạo artifact dẫn xuất riêng trong:

```text
shared/learning_resources/fragments/
```

hoặc:

```text
experiments/20260709_155523/outputs/learning_resource_phase4_5/
```

### 4.2. Không đụng nhầm artifact OCR/MinerU cũ của Codex

Các file sau là marker/bản đồ cleanup, phải đọc trước khi dọn hoặc tái dùng artifact cũ:

```text
experiments/20260709_155523/reports/plan03-codex-artifact-cleanup-map.md
experiments/20260709_155523/outputs/PLAN03_CODEX_ARTIFACTS_CLEANUP_README.md
experiments/20260709_155523/handoffs/learning-resource-codex-artifact-cleanup-marking-032.md
```

Trong plan này:

- không xóa các thư mục trong `experiments/20260709_155523/outputs/`;
- không dùng `parsed_pages` cũ làm nguồn chính;
- không sửa các script OCR/MinerU cũ nếu không cần cho Pha 4–5;
- nếu cần dọn dẹp, tạo plan cleanup riêng sau khi Pha 5 chạy ổn.

## 5. Các artifact dự kiến và vai trò

### 5.1. Registry/manifest

#### `shared/learning_resources/registries/ocr_text_manifest.csv`

Lý do tạo:

- Ghi danh sách chính thức các file OCR Markdown của Nguyên.
- Là điểm vào ổn định cho Pha 4.
- Tránh việc script phải tự quét thư mục theo logic ngầm.

Vai trò:

- mỗi dòng ứng với một file Markdown bài/mục;
- nối file OCR với `learning_material_id` trong `sgk_sgv_source_registry.csv`;
- ghi số mốc trang, số ảnh, số bảng, tiêu đề đầu tiên, trạng thái xử lý.

Cột dự kiến:

```text
ocr_text_id
learning_material_id
material_type
grade
book_title
lesson_key
lesson_title
topic_title
source_markdown_path
source_metadata_path
image_dir
page_marker_count
page_stat_count
table_count
image_count
first_heading
status
notes
```

### 5.2. Fragment

#### `shared/learning_resources/fragments/learning_resource_fragments.csv`

Lý do tạo:

- Đây là bảng mapping chính để specialist agent và benchmark sample trích dẫn học liệu.
- Đảm bảo mỗi đoạn học liệu có mã ổn định và truy vết được.

Vai trò:

- mỗi dòng là một fragment học liệu;
- lưu metadata định vị: sách, lớp, bài, mục, trang, thứ tự;
- không bắt agent đọc cả file Markdown bài học.

Cột tối thiểu theo skill `learning-resource-curator`:

```text
fragment_id
learning_material_id
page_start
page_end
section_label
order_index
location_note
status
```

Cột mở rộng nên có cho dự án:

```text
ocr_text_id
material_type
grade
book_title
lesson_key
lesson_title
topic_title
page_marker_start
page_marker_end
section_path
fragment_type
source_markdown_path
markdown_text
text_preview
needs_hnmu_review
notes
```

#### `shared/learning_resources/fragments/README.md`

Lý do tạo:

- Giải thích fragment được tạo như thế nào.
- Giúp người sau không nhầm fragment với dữ liệu OCR gốc.

Vai trò:

- mô tả nguồn đầu vào;
- mô tả quy tắc tách fragment;
- mô tả trạng thái `draft`, `needs_uet_review`, `needs_hnmu_review`, `confirmed`, `retired`;
- nêu rõ không được sửa ID đã được sử dụng.

### 5.3. Index truy xuất

#### `shared/learning_resources/indexes/learning_resources_v0.sqlite`

Lý do tạo:

- Cần một index truy xuất nhanh, có thể lọc metadata và tìm toàn văn.
- SQLite đủ nhẹ cho v0, dễ kiểm tra, không cần server.

Vai trò:

- lưu bảng `learning_sources`;
- lưu bảng `learning_fragments`;
- tạo full-text search trên nội dung fragment;
- phục vụ các hàm `resolve_learning_resource`, `search_learning_fragments`, `get_learning_fragment`.

Lưu ý:

- file `.sqlite` đã được `.gitignore` bỏ qua theo rule `shared/**/*.sqlite`;
- nếu cần chia sẻ, export report/CSV thay vì push database nặng lên GitHub.

#### `shared/learning_resources/indexes/README.md`

Lý do tạo:

- Nhắc rõ database là artifact sinh lại được.
- Ghi lệnh build/rebuild index.

Vai trò:

- mô tả nguồn index;
- mô tả cách chạy script;
- mô tả cách test truy xuất.

### 5.4. Code dùng chung

#### `src/edu_benchmark/learning_resources/ocr_text_manifest.py`

Lý do tạo:

- Đóng gói logic đọc thư mục OCR của Nguyên và tạo manifest.
- Tránh viết logic quét thư mục trực tiếp trong notebook hoặc script rời.

Vai trò:

- đọc `shared/learning_resources/ocr_text`;
- trích xuất thống kê từ Markdown/metadata;
- nối với source registry;
- xuất `ocr_text_manifest.csv`.

#### `src/edu_benchmark/learning_resources/fragment_markdown.py`

Lý do tạo:

- Tách fragment là logic tái sử dụng, không nên để trong experiment output.

Vai trò:

- đọc manifest;
- tách Markdown theo mốc trang, heading, bảng, hoạt động/luyện tập/vận dụng;
- tạo fragment ID ổn định;
- xuất `learning_resource_fragments.csv`.

#### `src/edu_benchmark/learning_resources/retrieval_index.py`

Lý do tạo:

- Tách riêng logic build database/index.

Vai trò:

- đọc `learning_resource_fragments.csv`;
- tạo SQLite/DuckDB index;
- chuẩn hóa schema bảng;
- rebuild index khi fragment thay đổi.

#### `src/edu_benchmark/learning_resources/retrieval_api.py`

Lý do tạo:

- Specialist agent cần một lớp truy xuất ổn định, không nên tự đọc file thủ công.

Vai trò:

- cung cấp `resolve_learning_resource(metadata)`;
- cung cấp `search_learning_fragments(query, filters)`;
- cung cấp `get_learning_fragment(fragment_id)`;
- trả về text ngắn, metadata, đường dẫn nguồn và confidence sơ bộ.

### 5.5. Script dòng lệnh

#### `scripts/learning_resources/build_ocr_text_manifest.py`

Vai trò:

- wrapper mỏng để chạy `ocr_text_manifest.py`;
- dùng trong Pha 4 bước 1.

#### `scripts/learning_resources/build_learning_resource_fragments.py`

Vai trò:

- wrapper mỏng để chạy `fragment_markdown.py`;
- dùng trong Pha 4 bước 2–3.

#### `scripts/learning_resources/build_learning_resource_index.py`

Vai trò:

- wrapper mỏng để chạy `retrieval_index.py`;
- dùng trong Pha 5 bước 1.

#### `scripts/learning_resources/query_learning_resource_index.py`

Vai trò:

- kiểm thử thủ công truy xuất;
- giúp Quân/Nguyên chạy thử query không cần viết Python.

### 5.6. Test

#### `tests/learning_resources/test_ocr_text_manifest.py`

Vai trò:

- kiểm manifest không thiếu file Markdown/metadata;
- kiểm status hợp lệ;
- kiểm các đường dẫn tồn tại.

#### `tests/learning_resources/test_learning_resource_fragments.py`

Vai trò:

- kiểm mỗi fragment có `fragment_id` duy nhất;
- kiểm mỗi fragment trỏ về `learning_material_id` hợp lệ;
- kiểm fragment có locator hữu ích.

#### `tests/learning_resources/test_learning_resource_retrieval.py`

Vai trò:

- kiểm các hàm truy xuất trả kết quả đúng dạng;
- kiểm vài truy vấn mẫu tìm đúng bài/mục.

### 5.7. Report/handoff

#### `experiments/20260709_155523/reports/phase4-fragmentation-result.md`

Vai trò:

- báo cáo số lượng fragment tạo được;
- nêu lỗi/thiếu metadata;
- nêu fragment cần UET/HNMU review.

#### `experiments/20260709_155523/reports/phase5-retrieval-index-result.md`

Vai trò:

- báo cáo index build được hay chưa;
- thống kê số fragment index;
- nêu kết quả query thử;
- nêu điểm còn yếu trước khi dùng cho Plan 04.

#### `experiments/20260709_155523/handoffs/learning-resource-phase4-fragmentation.md`

Vai trò:

- bàn giao Pha 4 sang Pha 5;
- ghi input/output, validation, câu hỏi còn mở.

#### `experiments/20260709_155523/handoffs/learning-resource-phase5-retrieval-index.md`

Vai trò:

- bàn giao index truy xuất cho Plan 04 và các specialist agent.

## 6. Quy trình thực hiện Pha 4

### Bước 4.1 — Đóng băng phạm vi đầu vào

Đầu vào:

```text
shared/learning_resources/ocr_text/sgk_tin_hoc_6/
shared/learning_resources/ocr_text/sgv_tin_hoc_6/
shared/learning_resources/registries/sgk_sgv_source_registry.csv
```

Việc làm:

- kiểm số file Markdown/metadata;
- xác nhận phạm vi xử lý theo dữ liệu OCR Markdown hiện có; vòng hiện tại đã gồm SGK/SGV Tin học 6–9;
- không dùng output OCR/MinerU cũ làm nguồn chính.

Output:

- ghi nhận trong report Pha 4.

### Bước 4.2 — Tạo manifest OCR Markdown

Việc làm:

- quét các file `.md` và `.metadata.json`;
- trích xuất thống kê cơ học;
- nối với `learning_material_id`;
- gán trạng thái ban đầu `draft`.

Output:

```text
shared/learning_resources/registries/ocr_text_manifest.csv
```

Tiêu chí đạt:

- đủ các file SGK/SGV tương ứng với phạm vi OCR Markdown đang có; hiện tại là 17 SGK + 18 SGV lớp 6, 16 SGK + 17 SGV lớp 7, 20 SGK + 21 SGV lớp 8, 22 SGK + 23 SGV lớp 9;
- mọi file Markdown có metadata tương ứng;
- mọi dòng có `learning_material_id`.

### Bước 4.3 — Chuẩn hóa metadata tối thiểu

Việc làm:

- suy ra `material_type`, `grade`, `lesson_key` từ đường dẫn;
- lấy `lesson_title` từ heading hoặc tên file;
- lấy `topic_title` từ mục lục/heading nếu có;
- ghi `needs_uet_review` nếu title/topic không chắc.

Output:

- cập nhật `ocr_text_manifest.csv`;
- danh sách dòng cần UET kiểm lại trong report.

Tiêu chí đạt:

- không để trống `grade`, `material_type`, `lesson_key`;
- title không chắc phải được đánh dấu, không tự coi là confirmed.

### Bước 4.4 — Tách fragment

Việc làm:

- tách theo heading và mốc trang;
- giữ bảng như một fragment riêng nếu bảng có ý nghĩa độc lập;
- giữ hoạt động/luyện tập/vận dụng như fragment riêng khi có thể;
- với SGV, ưu tiên các mục: mục đích yêu cầu, chuẩn bị, gợi ý dạy học, đáp án/gợi ý, lưu ý sư phạm.

Output:

```text
shared/learning_resources/fragments/learning_resource_fragments.csv
shared/learning_resources/fragments/README.md
```

Trạng thái fragment:

- `draft`: fragment sinh tự động, chưa kiểm;
- `needs_uet_review`: thiếu thông tin kỹ thuật hoặc ranh giới chưa chắc;
- `needs_hnmu_review`: cần xác nhận chuyên môn/sư phạm;
- không dùng `confirmed` trong vòng đầu nếu chưa có người duyệt.

### Bước 4.5 — Kiểm chất lượng fragment

Việc làm:

- kiểm ID trùng;
- kiểm fragment rỗng/quá ngắn/quá dài;
- kiểm fragment không có locator;
- kiểm fragment không trỏ về file nguồn;
- kiểm số fragment theo bài/sách.

Output:

```text
experiments/20260709_155523/reports/phase4-fragmentation-result.md
```

Tiêu chí đạt:

- không có `fragment_id` trùng;
- mọi fragment có `learning_material_id`;
- mọi fragment có ít nhất một locator: trang, section, hoặc location note;
- có danh sách review queue nếu cần.

## 7. Quy trình thực hiện Pha 5

### Bước 5.1 — Thiết kế schema index v0

Database v0 nên có ít nhất:

```text
learning_sources
learning_fragments
learning_fragments_fts
```

Trong đó:

- `learning_sources` lấy từ source registry và manifest;
- `learning_fragments` lấy từ `learning_resource_fragments.csv`;
- `learning_fragments_fts` là full-text search trên text fragment.

### Bước 5.2 — Build index

Việc làm:

- đọc `learning_resource_fragments.csv`;
- tạo database;
- insert sources/fragments;
- build full-text search.

Output:

```text
shared/learning_resources/indexes/learning_resources_v0.sqlite
shared/learning_resources/indexes/README.md
```

### Bước 5.3 — Viết hàm truy xuất

Hàm tối thiểu:

```text
resolve_learning_resource(metadata)
search_learning_fragments(query, filters)
get_learning_fragment(fragment_id)
```

Ví dụ truy xuất:

```text
search_learning_fragments(
  query="Scratch trung bình cộng ba số",
  filters={"grade": 6, "material_type": ["SGK", "SGV"]}
)
```

Kết quả nên trả:

```text
fragment_id
score
material_type
grade
lesson_title
section_path
page_start/page_end hoặc page_marker
text_preview
source_markdown_path
status
```

### Bước 5.4 — Test truy xuất bằng query thật

Query test tối thiểu:

- “Scratch trung bình cộng ba số”
- “chương trình máy tính”
- “thông tin và dữ liệu”
- “an toàn thông tin trên Internet”
- “hướng dẫn dạy học Bài 17”
- “vật mang tin”

Tiêu chí đạt:

- query về Scratch/chương trình máy tính trả về Bài 17 SGK/SGV Tin học 6 ở nhóm đầu;
- query về thông tin/dữ liệu trả về Bài 1;
- query về an toàn thông tin trả về Bài 9;
- kết quả trả về fragment đủ ngắn để agent không phải đọc toàn file bài.

### Bước 5.5 — Bàn giao cho Plan 04

Output:

```text
experiments/20260709_155523/reports/phase5-retrieval-index-result.md
experiments/20260709_155523/handoffs/learning-resource-phase5-retrieval-index.md
```

Nội dung bàn giao:

- database/index nằm ở đâu;
- cách chạy lại index;
- cách query;
- giới hạn hiện tại;
- trường hợp cần HNMU/UET xác nhận.

## 8. Lệnh chạy dự kiến

Tất cả script Pha 4–5 dùng môi trường chính:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Dự kiến:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_ocr_text_manifest.py

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_fragments.py

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_index.py

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "Scratch trung bình cộng ba số" \
  --grade 6
```

Không dùng môi trường `ocr_vietocr_gpu` trong Pha 4–5, vì không chạy nhận dạng OCR nữa.

## 9. Kiểm thử và validation

Sau khi implement, chạy:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/learning_resources -q
```

Nếu có validator registry riêng, chạy thêm:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/validate_learning_resource_registry.py
```

Nếu validator chưa hỗ trợ schema mới, cần cập nhật validator hoặc ghi rõ phần chưa được validate trong report.

## 10. Rủi ro và cách kiểm soát

### 10.1. Fragment quá nhỏ hoặc quá lớn

Kiểm soát:

- đặt ngưỡng độ dài tối thiểu/tối đa;
- flag `needs_uet_review` cho fragment bất thường;
- không cố tối ưu ngay từ vòng đầu.

### 10.2. Metadata bài/chủ đề suy ra sai

Kiểm soát:

- không gán `confirmed`;
- ghi `notes`;
- tạo review queue nếu không chắc.

### 10.3. SGK và SGV không căn bài hoàn toàn theo cùng cấu trúc

Kiểm soát:

- dùng `lesson_key` và `lesson_title` làm nối mềm;
- không ép quan hệ SGK–SGV nếu chưa chắc;
- để quan hệ cần xác nhận trong report.

### 10.4. Ảnh trong `ocr_text` có thể nặng

Kiểm soát:

- không tự ý xóa;
- không tự ý sửa `.gitignore` trong plan này nếu chưa được duyệt;
- trước khi push, kiểm tra dung lượng và chính sách track ảnh.

### 10.5. Agent dùng kết quả truy xuất như “sự thật tuyệt đối”

Kiểm soát:

- mọi fragment ban đầu để `draft` hoặc `needs_uet_review`;
- kết quả truy xuất trả kèm trạng thái;
- các kiểm định chuyên môn vẫn cần HNMU/UET duyệt.

## 11. Điều kiện hoàn thành

Pha 4 hoàn thành khi:

- có manifest OCR Markdown;
- có bảng fragment;
- có report số lượng/chất lượng fragment;
- mọi fragment có ID, nguồn, locator và trạng thái.

Pha 5 hoàn thành khi:

- có index truy xuất v0;
- có hàm truy xuất tối thiểu;
- có test tự động;
- có query thử chứng minh truy xuất đúng các bài trọng yếu;
- có handoff cho Plan 04.

## 12. Quyết định cần Quân duyệt trước khi implement

1. Có duyệt dùng `shared/learning_resources/ocr_text` làm nguồn chính thức cho Pha 4 không?
2. Với các lớp mới, có đồng ý rebuild manifest/fragment/index chung thay vì tạo index tách riêng từng lớp không?
3. Có đồng ý tạo các file/directory mới nêu ở Mục 5 không?
4. Có muốn track ảnh `.jpg` trong `ocr_text` trên GitHub hay ignore ảnh nặng và chỉ track Markdown/metadata/manifest?
5. Có cần giữ prototype index cấp bài học như một bước trung gian rất nhanh không, hay đi thẳng vào fragment-level index?


## 13. Kết quả mở rộng ngày 18/07/2026

Sau khi Nguyên bổ sung OCR Markdown cho SGK/SGV Tin học 8–9, Pha 4–5 đã được rebuild cho toàn bộ lớp 6–9.

Kết quả hiện tại:

- `shared/learning_resources/registries/ocr_text_manifest.csv`: 154 nguồn OCR Markdown;
- `shared/learning_resources/fragments/learning_resource_fragments.csv`: 2.750 fragment;
- `shared/learning_resources/indexes/learning_resources_v0.sqlite`: SQLite FTS index sinh lại được;
- đã sửa logic `lesson_key` để phân biệt bài tách nhánh như `Bài 10A` và `Bài 10B`, tránh trùng `ocr_text_id`.

Phạm vi này chỉ xử lý học liệu do Nguyên gửi. Tại thời điểm 18/07/2026, dữ liệu hội thoại HNMU lớp 8–9 mới được đăng ký manifest raw-data và chưa chạy audit Plan 04. Cập nhật sau: lớp 8–9 đã được audit trong lượt riêng ngày 19/07/2026 tại `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/`.
