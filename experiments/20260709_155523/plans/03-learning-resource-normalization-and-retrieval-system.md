# Plan 03 — Chuẩn hóa học liệu SGK/SGV và thiết kế hệ thống truy xuất học liệu

Experiment: `20260709_155523`
Trạng thái: `PHA 3 PROBE OCR NÂNG CAO HOÀN THÀNH; PHA A MINERU BOOK-LEVEL APPROVED FOR IMPLEMENTATION; PHA B-E MINERU POSTPROCESS APPROVED FOR IMPLEMENTATION` — đã kiểm tra EasyOCR GPU, PaddleOCR GPU, Paddle detect + VietOCR CPU, VietOCR `vgg_seq2seq` GPU và VietOCR `vgg_transformer` GPU trên vài ảnh ngày 15/07/2026; đã chốt cần thêm lớp tái dựng bố cục để sinh Markdown từ OCR; người dùng đã duyệt cài đặt Pha A book-level ngày 16/07/2026 và duyệt code trước các pha sau Pha A trong lúc MinerU đang chạy; chưa chạy hậu xử lý trên output đầy đủ.
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
- dữ liệu dòng/cụm chữ có tọa độ từ PaddleOCR để phục vụ tái dựng bố cục;
- bảng chất lượng OCR;
- danh sách trang cần kiểm tra thủ công;
- trạng thái `needs_uet_review` hoặc `needs_hnmu_review` cho phần chưa chắc.

Kết luận phương pháp hiện tại:

- Không dùng file text thuần làm đầu vào trực tiếp cho Pha 4.
- Hướng chính là `PaddleOCR detection/layout + VietOCR GPU recognition`.
- Output quan trọng của Pha 3 không chỉ là chữ, mà là **chữ + vị trí trên trang**. Tối thiểu mỗi dòng/cụm chữ cần giữ `text`, `bbox`, `page_number`, `line_order` và thông tin engine đã dùng.
- `vgg_transformer` GPU là nhánh ưu tiên khi cần chất lượng tiếng Việt; `vgg_seq2seq` GPU là nhánh tạo bản nháp nhanh nếu cần xử lý nhiều trang.

### Pha 3b — Tái dựng bố cục để sinh Markdown

Mục tiêu: biến output OCR dạng “chữ + tọa độ” thành Markdown có cấu trúc, trước khi tách fragment hoặc build index.

Lý do: nhiều trang SGK/SGV có bảng, mục lục, khung nội dung, bài tập hoặc nhiều cột. Nếu chỉ xuất text thuần, chữ có thể đúng nhưng quan hệ hàng/cột bị mất, làm sai ý nghĩa học liệu.

Flow v0:

```text
Ảnh trang SGK/SGV
→ PaddleOCR phát hiện vùng chữ và lấy bbox
→ VietOCR nhận dạng tiếng Việt trên từng vùng/crop
→ gom dòng/đoạn theo tọa độ
→ phát hiện bảng bằng tọa độ; dùng OpenCV khi bảng có đường kẻ rõ
→ xuất Markdown có front matter, heading, table và anchor
→ gắn trạng thái review cho trang/khối chưa chắc
```

Output dự kiến:

- Markdown trang đã xử lý ở `shared/learning_resources/parsed_pages/<book_type>/<book_id>/page_XXXX.md`;
- bảng chất lượng tái dựng bố cục, ví dụ `layout_reconstruction_quality.csv`;
- danh sách trang/bảng cần kiểm tra thủ công;
- artifact debug tùy chọn cho trang khó: bbox/crop/table-crop.

Quy tắc bảo thủ:

- Không để LLM tự viết lại nội dung học liệu. Nếu dùng LLM/specialist agent để sửa Markdown, agent chỉ được sắp xếp/định dạng lại dựa trên OCR evidence và ảnh gốc; nội dung không chắc phải gắn `needs_review`.
- Với bảng đơn giản, ưu tiên Markdown table.
- Với bảng phức tạp, có thể dùng HTML table trong Markdown hoặc giữ block ở trạng thái `needs_uet_review`.
- JSON/crop không bắt buộc cho mọi trang; chỉ sinh khi cần kiểm bbox, bảng phức tạp, cell-level retrieval hoặc debug OCR.

### Pha A — MinerU book-level Markdown draft

Trạng thái: `APPROVED FOR IMPLEMENTATION` ngày 16/07/2026.

Mục tiêu: chuẩn bị input để chạy MinerU theo từng cuốn SGK/SGV lớp 6–7, tạo Markdown nháp giữ bố cục tốt hơn trước khi đi vào cleanup và hậu kiểm.

Phạm vi cài đặt:

- tạo manifest theo từng cuốn, không xóa ảnh gốc;
- loại các trang đầu sách và cuối sách không phục vụ học liệu khỏi lượt chạy MinerU bằng manifest;
- giữ lại mục lục;
- ghép ảnh còn lại của từng cuốn thành PDF;
- sinh lệnh MinerU để người dùng chạy ngoài sandbox;
- sau khi người dùng chạy MinerU, gom Markdown từng cuốn về `book_markdown/`.

Code dùng chung:

```text
src/edu_benchmark/learning_resources/mineru_book_phase_a.py
src/edu_benchmark/learning_resources/mineru_postprocess.py
scripts/learning_resources/prepare_mineru_book_phase_a.py
scripts/learning_resources/collect_mineru_book_markdown.py
scripts/learning_resources/postprocess_mineru_book_phase.py
```

Output experiment:

```text
experiments/20260709_155523/outputs/mineru_book_phase_a/
```

Quy tắc lọc mặc định của Pha A: loại trang gốc `1-4` và 2 trang cuối của mỗi cuốn khỏi lượt chạy MinerU. Các trang này vẫn nằm trong manifest để giữ truy vết, nhưng không đi vào PDF `_filtered.pdf`.

Cấu hình MinerU mặc định cho các lần chạy Pha A mới:

```text
backend: hybrid-engine
effort: medium
image-analysis: false
formula: true
table: true
concurrency: 1
```

### Pha B–E — Hậu xử lý Markdown MinerU

Trạng thái: `APPROVED FOR IMPLEMENTATION` ngày 16/07/2026.

Mục tiêu: sau khi MinerU chạy xong, xử lý output `hybrid-engine` để tạo Markdown theo trang, làm sạch ảnh/icon, đối chiếu với OCR truyền thống nếu có và tạo hàng đợi review.

Phạm vi cài đặt:

- đọc `*_content_list_v2.json` của MinerU để tách nội dung theo trang;
- ánh xạ `pdf_page_1based` về `original_page` thông qua manifest Pha A;
- xoá dòng ảnh Markdown, `image_url_placeholder`, đường dẫn ảnh rời và tag ảnh HTML;
- giữ heading, đoạn văn, danh sách và bảng HTML/Markdown do MinerU sinh;
- sinh Markdown theo trang trong output experiment, kèm front matter và anchor;
- nếu có OCR truyền thống `PaddleOCR + VietOCR`, tính chỉ số hậu kiểm sơ bộ: `ocr_to_md_coverage`, `md_extra_ratio`, `number_mismatch_count`;
- tạo `mineru_postprocess_review_queue.csv` cho trang cần người kiểm tra.

Output experiment:

```text
experiments/20260709_155523/outputs/mineru_book_phase_a/postprocessed/
```

Lưu ý: output Pha B–E vẫn là `draft`. Chưa tự động đưa vào `shared/learning_resources/parsed_pages/` cho tới khi có quyết định review/chuẩn hóa tiếp theo.

### Pha 4 — Fragment học liệu

Mục tiêu: chia học liệu thành đoạn có thể truy vết theo khối lớp, loại sách, chủ đề, bài học, trang và mục nhỏ. Sau quyết định ngày 15/07/2026, Pha 4 đi theo hướng **Markdown-first**: mỗi trang đã xử lý có Markdown với front matter, heading, bảng nếu có và anchor; các fragment được tách/index từ Markdown.

Điểm quan trọng: Markdown của Pha 4 phải được sinh từ Pha 3b, tức từ OCR có tọa độ và bước tái dựng bố cục. Không dùng text thuần làm artifact chính vì sẽ làm mất cấu trúc bảng/mục lục.

Output dự kiến:

- `shared/learning_resources/parsed_pages/<book_type>/<book_id>/page_XXXX.md`
- `shared/learning_resources/fragments/learning_resource_fragments.csv`
- quy tắc `fragment_id` v0;
- trạng thái xác nhận của từng fragment;
- JSON/crop debug chỉ sinh cho trang/bảng phức tạp hoặc khi cần kiểm lại OCR.

### Pha 5 — Thiết kế database/retrieval system

Mục tiêu: thiết kế hệ thống quản lý học liệu để specialist agent và sau này model có thể truy vấn khi đánh giá. Bản v0 chưa cần vector database; ưu tiên SQLite/DuckDB full-text search trên Markdown fragments kèm metadata filter.

Output dự kiến:

- schema SQLite/DuckDB index v0;
- API/retrieval contract v0, tối thiểu gồm `resolve_learning_resource`, `search_learning_fragments`, `get_learning_fragment`;
- policy phân quyền chỉnh sửa học liệu;
- kế hoạch đồng bộ với benchmark samples.

### Quy ước code và môi trường chạy cho Pha 3–5

Từ Pha 3 trở đi sẽ phải có code dùng lại, vì vậy không đặt script xử lý rải trong thư mục experiment. Quy ước như sau.

Code dùng chung đặt trong:

```text
src/edu_benchmark/learning_resources/
```

Dự kiến tách module theo vai trò:

```text
src/edu_benchmark/learning_resources/
  ocr_detection.py              # PaddleOCR detection/layout: ảnh → bbox/crop metadata
  vietocr_recognition.py        # VietOCR recognition: crop → text tiếng Việt
  layout_reconstruction.py      # text + bbox → heading/đoạn/bảng
  markdown_export.py            # layout blocks → Markdown có front matter/anchor
  fragment_indexing.py          # Markdown → fragment table + SQLite/DuckDB index
  quality_checks.py             # kiểm chất lượng OCR/layout/Markdown
```

Nếu cần script CLI mỏng để gọi các module này, đặt trong:

```text
scripts/learning_resources/
```

Script CLI chỉ điều phối tham số và gọi code trong `src/edu_benchmark/learning_resources/`; không chứa logic chính.

Output của một lần chạy probe hoặc batch đặt trong:

```text
experiments/20260709_155523/outputs/
```

Artifact học liệu đã xử lý và được dùng lại giữa các experiment đặt trong:

```text
shared/learning_resources/
  parsed_pages/
  fragments/
  indexes/
  parsed_pages_debug/
```

#### Môi trường chạy

Môi trường chính của dự án vẫn là:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Dùng `benchmark_env` cho:

- đọc manifest/registry;
- chạy code điều phối pipeline;
- tái dựng bố cục;
- xuất Markdown;
- tách fragment;
- build SQLite/DuckDB index;
- validation và test;
- các bước không phụ thuộc VietOCR GPU.

Riêng bước nhận dạng bằng VietOCR GPU phải chạy bằng môi trường:

```text
/home/quannda/miniconda3/envs/ocr_vietocr_gpu/bin/python
```

Dùng `ocr_vietocr_gpu` cho:

- `vietocr_recognition.py`;
- nhận dạng crop bằng VietOCR `vgg_transformer` hoặc `vgg_seq2seq`;
- các probe cần PyTorch GPU/VietOCR GPU.

Lý do tách môi trường: PaddleOCR GPU/PaddlePaddle và VietOCR GPU/PyTorch có thể xung đột dependency CUDA nếu trộn lâu dài trong cùng một environment. Vì vậy pipeline Pha 3 nên được thiết kế theo kiểu nhiều bước có file trung gian:

```text
benchmark_env:
  ảnh → PaddleOCR bbox/crop metadata

ocr_vietocr_gpu:
  crop metadata + ảnh nguồn → text tiếng Việt theo bbox

benchmark_env:
  text + bbox → tái dựng bố cục → Markdown → fragment/index
```

Ví dụ lệnh chạy dự kiến, tên script có thể điều chỉnh khi triển khai:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/run_paddle_detection.py \
  --input shared/learning_resources/raw_page_images/sgk/tin_hoc_6 \
  --output experiments/20260709_155523/outputs/learning_resource_pipeline/detection/sgk_tin_hoc_6

/home/quannda/miniconda3/envs/ocr_vietocr_gpu/bin/python \
  scripts/learning_resources/run_vietocr_recognition.py \
  --detection experiments/20260709_155523/outputs/learning_resource_pipeline/detection/sgk_tin_hoc_6 \
  --model vgg_transformer \
  --output experiments/20260709_155523/outputs/learning_resource_pipeline/recognition/sgk_tin_hoc_6

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_markdown_pages.py \
  --recognition experiments/20260709_155523/outputs/learning_resource_pipeline/recognition/sgk_tin_hoc_6 \
  --output shared/learning_resources/parsed_pages/sgk/tin_hoc_6

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_index.py \
  --parsed-pages shared/learning_resources/parsed_pages \
  --output shared/learning_resources/indexes/learning_resources.sqlite
```

Quy tắc validation:

- Các test/validator của repo chạy bằng `benchmark_env`.
- Các probe VietOCR GPU phải báo rõ Python executable là `/home/quannda/miniconda3/envs/ocr_vietocr_gpu/bin/python`.
- Mỗi báo cáo/handoff của Pha 3–5 phải ghi rõ bước nào chạy bằng env nào.
- Không coi output từ `ocr_vietocr_gpu` là validation chung của repo; nó chỉ là output OCR trung gian.

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


| Sách      | Số ảnh SGV |
| ---------- | -----------: |
| Tin học 6 |           98 |
| Tin học 7 |           94 |
| Tin học 8 |          102 |
| Tin học 9 |          102 |

Tại thời điểm hoàn thành Pha 1, pha này chưa OCR, chưa fragment và chưa xác nhận nội dung chuyên môn. Cập nhật 18/07/2026: OCR Markdown do Nguyên gửi đã được xử lý ở Pha 4–5; ảnh SGK/SGV trong manifest vẫn giữ vai trò nguồn truy vết gốc.

## 9. Kết quả tạo PDF dẫn xuất ngày 15/07/2026

Đã tạo 8 PDF dẫn xuất từ ảnh SGK/SGV Tin học 6–9 để người dùng dễ mở xem.

- Thư mục PDF: `shared/learning_resources/compiled_documents/`
- Manifest đã cập nhật: `shared/learning_resources/registries/learning_resource_file_manifest.csv`
- Báo cáo: `experiments/20260709_155523/reports/compiled-learning-resource-pdfs-result.md`

PDF là bản dẫn xuất để xem nhanh, không thay thế ảnh từng trang và không thay thế truy vết trong manifest.

## 10. Kết quả Pha 2, đồng bộ lại ngày 18/07/2026

Pha 2 đã tạo và sau đó đồng bộ lại danh mục học liệu v0 phục vụ Plan 04:

- `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv`
- `shared/learning_resources/registries/sgk_thcs_lesson_position_registry_v0.csv`
- `experiments/20260709_155523/reports/learning-resource-registry-v0-for-hnmu-audit.md`
- `experiments/20260709_155523/reports/learning-resource-registries-sync-20260718.md`

Trạng thái sau đồng bộ ngày 18/07/2026:

- Topic/lesson map hiện bao phủ SGK Tin học 6–9, dựa trên mục lục OCR Markdown do Nguyên gửi. Không còn dùng placeholder lớp 8 hoặc OCR mục lục từ experiment cũ làm nguồn chính.
- Lesson-position registry hiện lấy vị trí từ dữ liệu hội thoại HNMU lớp 6–9. Đây là metadata thô để kiểm phủ/truy xuất, chưa phải xác nhận rằng vị trí HNMU khai báo là đúng.
- `learning_resource_file_manifest.csv` đã được cập nhật để không còn ghi chú lỗi thời “chưa OCR”; ảnh/PDF vẫn là nguồn truy vết, OCR Markdown là artifact xử lý riêng.
- Toàn bộ topic/lesson map và lesson-position registry vẫn giữ trạng thái cần HNMU review khi dùng cho quyết định chuyên môn.

Số liệu chính:

- Topic/lesson map: 106 mục, gồm chủ đề, chủ đề con, bài học và phụ lục của lớp 6–9.
- Lesson-position registry: 755 vị trí lấy từ dữ liệu HNMU lớp 6–9.
- OCR manifest: 154 đơn vị OCR Markdown SGK/SGV lớp 6–9.
- Fragment truy xuất: 2.750 fragment, đã rebuild sau khi manifest OCR tự nối topic map.

Registry vị trí v0 vẫn giữ cả vị trí cấp bài và một số vị trí cấp chủ đề/phụ lục nếu dữ liệu nguồn ghi như vậy. Vì vậy, cột `lesson_item_id` trong bản v0 nên được hiểu là tham chiếu tới `item_id` học liệu trong topic/lesson map; tên cột này có thể cần đổi thành tên tổng quát hơn trong pha thiết kế schema sau.

## 11. Kết quả Pha 3 probe GPU ngày 15/07/2026

Pha 3 mới chạy ở mức **probe**, chưa OCR hàng loạt.

Đã cài và kiểm tra stack OCR GPU trong môi trường `benchmark_env`:

- Python: `/home/quannda/miniconda3/envs/benchmark_env/bin/python`
- `torch==2.11.0+cu128`
- `torchvision==0.26.0+cu128`
- `easyocr==1.7.2`
- GPU: NVIDIA GeForce RTX 4060 Ti, khoảng 16GB VRAM

Output:

- `requirements-ocr-gpu.txt`
- `experiments/20260709_155523/outputs/ocr_probe/ocr_probe_environment.json`
- `experiments/20260709_155523/outputs/ocr_probe/ocr_probe_summary.csv`
- `experiments/20260709_155523/outputs/ocr_probe/cpu_compare.json`
- `experiments/20260709_155523/reports/ocr-gpu-probe-result.md`
- `experiments/20260709_155523/handoffs/learning-resource-phase3-ocr-gpu-probe-010.md`

Kết quả chính:

- PyTorch nhận GPU và phép thử CUDA chạy thành công.
- EasyOCR GPU chạy được với ngôn ngữ `vi`, `en`.
- OCR thử 4 ảnh SGK/SGV mất khoảng 0.4–0.8 giây/trang sau khi reader đã sẵn sàng.
- So sánh một trang mục lục Tin học 9: GPU khoảng 0.824 giây, CPU khoảng 3.547 giây.
- Chất lượng đủ để tạo bản nháp mục lục/trang trọng điểm, nhưng chưa đủ để dùng làm nguồn chân lý nếu chưa có kiểm tra thủ công.

Quyết định bảo thủ:

- Không OCR hàng loạt trong probe này.
- Không dùng text OCR chưa rà soát để xác nhận chuyên môn hoặc đáp án SGV.
- Bước OCR tiếp theo nên ưu tiên mục lục SGK/SGV Tin học 6–9 và tạo bảng chất lượng OCR trước khi fragment học liệu.

## 12. Kết quả probe PaddleOCR ngày 15/07/2026

Đã thử PaddleOCR GPU trên cùng 4 ảnh của probe EasyOCR.

Output:

- `requirements-ocr-gpu.txt`
- `requirements-ocr-easyocr-gpu.txt`
- `requirements-ocr-paddle-gpu.txt`
- `experiments/20260709_155523/outputs/paddleocr_probe/paddleocr_probe_environment.json`
- `experiments/20260709_155523/outputs/paddleocr_probe/paddleocr_probe_summary.csv`
- `experiments/20260709_155523/reports/paddleocr-gpu-probe-result.md`
- `experiments/20260709_155523/handoffs/learning-resource-phase3-paddleocr-probe-011.md`

Kết quả chính:

- PaddlePaddle GPU nhận `gpu:0` và PaddleOCR chạy được.
- PaddleOCR nhanh hơn EasyOCR trong probe nhỏ: 4 ảnh mất khoảng 1.67 giây.
- Confidence của PaddleOCR rất cao, khoảng 0.98–0.99.
- Tuy nhiên, chất lượng tiếng Việt không đạt kỳ vọng: nhiều dấu/nguyên âm bị mất, ví dụ `MỤC LỤC` thành `MUC LUC`, `Chủ đề` thành `Ch đ`.

Quyết định bảo thủ:

- Không dùng PaddleOCR cấu hình hiện tại làm engine nhận dạng chữ chính cho SGK/SGV tiếng Việt.
- Không OCR hàng loạt bằng PaddleOCR trong cấu hình này.
- Nếu muốn tận dụng PaddleOCR, nên xem nó như ứng viên tốt cho detection/layout, sau đó thử recognizer tiếng Việt khác như VietOCR trên các crop quan trọng.
- EasyOCR GPU và PaddleOCR GPU không nên cài lẫn trong cùng một môi trường lâu dài vì dependency CUDA runtime xung đột. Nên cân nhắc tạo môi trường OCR riêng nếu tiếp tục thử nghiệm nhiều engine.

## 13. Kết quả so sánh hướng OCR ngày 15/07/2026

Đã thử thêm hướng lai: PaddleOCR dùng để phát hiện vùng chữ/thứ tự dòng, VietOCR dùng để nhận dạng tiếng Việt trên từng crop.

Output:

- `requirements-ocr-paddle-vietocr-cpu.txt`
- `experiments/20260709_155523/outputs/ocr_method_compare/paddle_detect_vietocr_summary.csv`
- `experiments/20260709_155523/outputs/ocr_method_compare/manual_phrase_accuracy_probe.csv`
- `experiments/20260709_155523/outputs/ocr_method_compare/texts/`
- `experiments/20260709_155523/reports/ocr-method-comparison-result.md`
- `experiments/20260709_155523/handoffs/learning-resource-phase3-ocr-method-comparison-012.md`

Kết quả chính:

- Paddle detect + VietOCR CPU giữ tiếng Việt tốt nhất trong probe nhỏ: khớp 30/33 cụm chuẩn có dấu.
- EasyOCR GPU khớp 15/33 cụm chuẩn có dấu; tốc độ tốt nhưng hay tách dòng vụn.
- PaddleOCR GPU khớp 2/33 cụm chuẩn có dấu; tốc độ rất nhanh nhưng recognition tiếng Việt không đạt yêu cầu trong cấu hình đã thử.
- Hướng lai hiện chậm hơn vì VietOCR chạy CPU: khoảng 5.2 giây/trang nếu cộng detection và recognition, ước lượng khoảng 65 phút cho 752 trang SGK/SGV.

Quyết định bảo thủ:

- Không OCR hàng loạt ngay bằng một engine duy nhất.
- Nếu chỉ OCR mục lục/trang trọng điểm, ưu tiên thử Paddle detect + VietOCR rồi rà soát thủ công.
- Nếu cần OCR toàn bộ sách, nên tạo môi trường OCR riêng cho VietOCR GPU hoặc recognizer tiếng Việt GPU khác, tránh tiếp tục trộn PaddlePaddle GPU và PyTorch GPU trong `benchmark_env`.

## 14. Kết quả probe VietOCR `vgg_seq2seq` GPU ngày 15/07/2026

Đã kiểm tra môi trường Conda riêng:

`/home/quannda/miniconda3/envs/ocr_vietocr_gpu`

Output:

- `requirements-ocr-vietocr-gpu.txt`
- `experiments/20260709_155523/outputs/ocr_vietocr_gpu_probe/environment.json`
- `experiments/20260709_155523/outputs/ocr_vietocr_gpu_probe/vietocr_vgg_seq2seq_gpu_summary.csv`
- `experiments/20260709_155523/outputs/ocr_vietocr_gpu_probe/manual_phrase_accuracy_probe.csv`
- `experiments/20260709_155523/outputs/ocr_vietocr_gpu_probe/texts/`
- `experiments/20260709_155523/reports/vietocr-vgg-seq2seq-gpu-probe-result.md`
- `experiments/20260709_155523/handoffs/learning-resource-phase3-vietocr-gpu-probe-013.md`

Kết quả chính:

- PyTorch GPU trong env mới nhận RTX 4060 Ti và chạy CUDA được.
- VietOCR `vgg_seq2seq` GPU nhận dạng 4 trang crop trong khoảng 2.176 giây sau khi model đã sẵn sàng.
- Nếu cộng detection PaddleOCR đã đo trước đó, pipeline xấp xỉ 3.85 giây/4 trang, tức khoảng 0.96 giây/trang trong probe nhỏ.
- Độ khớp cụm chuẩn có dấu là 28/33, thấp hơn nhẹ so với VietOCR `vgg_transformer` CPU 30/33, nhưng nhanh hơn rất nhiều.

Quyết định bảo thủ:

- Hướng `PaddleOCR detection + VietOCR vgg_seq2seq GPU` là ứng viên tốt nhất hiện tại để thử tiếp trên 20–30 trang.
- Chưa OCR toàn bộ 752 trang trước khi có probe đa dạng hơn.
- Nên giữ mô hình hai môi trường: môi trường Paddle cho detection/layout và môi trường `ocr_vietocr_gpu` cho recognition.

## 15. Kết quả probe VietOCR `vgg_transformer` GPU ngày 15/07/2026

Đã thử thêm VietOCR `vgg_transformer` GPU trong cùng môi trường:

`/home/quannda/miniconda3/envs/ocr_vietocr_gpu`

Output:

- `experiments/20260709_155523/outputs/ocr_vietocr_gpu_probe/environment_vgg_transformer_gpu.json`
- `experiments/20260709_155523/outputs/ocr_vietocr_gpu_probe/vietocr_vgg_transformer_gpu_summary.csv`
- `experiments/20260709_155523/outputs/ocr_vietocr_gpu_probe/manual_phrase_accuracy_vgg_transformer_gpu.csv`
- `experiments/20260709_155523/outputs/ocr_vietocr_gpu_probe/texts/`
- `experiments/20260709_155523/reports/vietocr-vgg-transformer-gpu-probe-result.md`
- `experiments/20260709_155523/handoffs/learning-resource-phase3-vietocr-transformer-gpu-probe-014.md`

Kết quả chính:

- VietOCR `vgg_transformer` GPU đạt 30/33 cụm chuẩn có dấu, cao hơn `vgg_seq2seq` GPU 28/33.
- Thời gian nhận dạng 4 trang crop là 6.913 giây, chậm hơn `vgg_seq2seq` GPU 2.176 giây.
- Peak memory inference PyTorch khoảng 179.0 MB, vẫn nhẹ so với GPU 16GB.

Quyết định bảo thủ:

- `vgg_transformer` GPU nên là lựa chọn chất lượng cao cho mục lục/trang trọng điểm.
- `vgg_seq2seq` GPU phù hợp hơn nếu cần bản nháp nhanh trên nhiều trang.
- Có thể cân nhắc pipeline hai pass: `vgg_seq2seq` tạo nháp trước, `vgg_transformer` kiểm lại trang/đoạn nghi ngờ.

## 16. Quyết định Markdown-first cho Pha 4–5 ngày 15/07/2026

Đã chốt hướng tối giản cho học liệu đã OCR/chuẩn hóa:

- Markdown có front matter, heading và anchor là artifact chính tạm thời.
- SQLite/DuckDB index build từ Markdown là lớp truy xuất cho specialist agent.
- JSON/crop chi tiết chỉ sinh thêm khi cần bbox, bảng phức tạp, cell-level retrieval hoặc debug OCR.

Output ghi nhận quyết định:

- `experiments/20260709_155523/reports/learning-resource-markdown-retrieval-decision.md`
- `experiments/20260709_155523/handoffs/learning-resource-markdown-retrieval-decision-015.md`

Quy ước artifact v0:

```text
shared/learning_resources/
  parsed_pages/
    sgk/tin_hoc_6/page_0005.md
  fragments/
    learning_resource_fragments.csv
  indexes/
    learning_resources.sqlite
  parsed_pages_debug/
    sgk/tin_hoc_6/page_0005.blocks.json   # optional
```

Mỗi Markdown page cần có metadata tối thiểu:

```text
page_id
book_type
book_name
grade
page_number
source_image
ocr_detector
ocr_recognizer
status
needs_review
```

Mỗi block/fragment quan trọng cần có anchor ổn định để retrieval trả về đúng vùng cần đọc, thay vì bắt agent đọc toàn bộ file Markdown.

Retrieval contract v0:

```text
resolve_learning_resource(metadata)
search_learning_fragments(query, filters)
get_learning_fragment(fragment_id)
```

Quyết định bảo thủ:

- Không dùng text thuần làm artifact chính vì text thuần làm mất cấu trúc bảng.
- Không bắt buộc JSON đầy đủ cho mọi trang ở giai đoạn này.
- Nếu trang có bảng phức tạp hoặc có mẫu HNMU cần kiểm sâu, mới sinh JSON/crop bổ sung cho trang đó.

## 17. Cập nhật flow OCR → Markdown ngày 15/07/2026

Sau khi xem kết quả OCR trang mục lục SGK Tin học 6, đã chốt rõ hơn rằng pipeline hiện tại không dừng ở file text thuần.

Flow được dùng cho các bước tiếp theo của Plan 03:

```text
Ảnh trang SGK/SGV
→ PaddleOCR phát hiện vùng chữ và lấy bbox
→ VietOCR GPU nhận dạng tiếng Việt trên từng vùng
→ lưu output trung gian gồm text + bbox + thứ tự dòng
→ tái dựng bố cục: đoạn, heading, bảng, nhiều cột nếu có
→ xuất Markdown có front matter, heading, table và anchor
→ build index truy xuất từ Markdown
```

Vai trò từng phần:

- PaddleOCR không được dùng làm recognizer chính cho tiếng Việt trong cấu hình hiện tại, nhưng vẫn hữu ích cho phát hiện vùng chữ và bố cục.
- VietOCR GPU là recognizer chính cho chữ tiếng Việt.
- Bước tái dựng bố cục là lớp bổ trợ bắt buộc để biến OCR thành Markdown tốt.
- Markdown là artifact chính cho người đọc và làm đầu vào cho retrieval index.
- JSON/crop là artifact phụ, chỉ sinh khi cần kiểm vùng ảnh, bảng phức tạp hoặc từng ô bảng.

Tiêu chí của probe kế tiếp trước khi OCR hàng loạt:

1. Chọn 20–30 trang đa dạng: mục lục, bài học thường, bảng, bài tập, trang có code/Scratch/Python, trang SGV có đáp án/hướng dẫn.
2. Sinh Markdown bằng pipeline có tái dựng bố cục.
3. So sánh với ảnh gốc ở ba mức: chữ có đúng không, bảng/bố cục có giữ nghĩa không, specialist agent có truy xuất đúng đoạn không.
4. Gắn trạng thái `draft`, `needs_uet_review` hoặc `needs_hnmu_review` cho từng trang/block.
5. Chỉ sau probe này mới cân nhắc OCR rộng hơn.

## 18. Cập nhật quy ước code/env cho Pha 3–5 ngày 15/07/2026

Đã bổ sung quy ước rõ ràng cho phần cài đặt sau này:

- Code chính đặt trong `src/edu_benchmark/learning_resources/`.
- Script CLI mỏng, nếu cần, đặt trong `scripts/learning_resources/`.
- Output chạy thử/batch đặt trong `experiments/20260709_155523/outputs/`.
- Artifact học liệu dùng chung đặt trong `shared/learning_resources/`.
- `benchmark_env` chạy điều phối, layout reconstruction, Markdown export, fragment, index, validation và test.
- `ocr_vietocr_gpu` chỉ chạy VietOCR GPU recognition.

Điều này giúp Pha 3–5 có thể code mà không lẫn experiment output với code dùng chung, đồng thời tránh nhầm môi trường khi chạy VietOCR.

## 19. Kết quả cài đặt code Pha 3 ngày 15/07/2026

Đã cài đặt code reusable cho Pha 3 theo contract đã chốt.

Code chính:

- `src/edu_benchmark/learning_resources/ocr_detection.py`
- `src/edu_benchmark/learning_resources/vietocr_recognition.py`
- `src/edu_benchmark/learning_resources/layout_reconstruction.py`
- `src/edu_benchmark/learning_resources/markdown_export.py`
- `src/edu_benchmark/learning_resources/quality_checks.py`
- `src/edu_benchmark/learning_resources/utils.py`

Script CLI mỏng:

- `scripts/learning_resources/run_paddle_detection.py`
- `scripts/learning_resources/run_vietocr_recognition.py`
- `scripts/learning_resources/build_markdown_pages.py`
- `scripts/learning_resources/summarize_ocr_quality.py`

Test:

- `tests/learning_resources/test_ocr_pipeline_units.py`

Probe đã chạy trên `shared/learning_resources/raw_page_images/sgk/tin_hoc_6/page_0005.png`:

- PaddleOCR detection chạy bằng `benchmark_env` ngoài sandbox để dùng GPU thật.
- VietOCR `vgg_transformer` recognition chạy bằng `ocr_vietocr_gpu` ngoài sandbox với `cuda:0`.
- Markdown nháp và quality summary được build bằng `benchmark_env`.

Output probe:

- `experiments/20260709_155523/outputs/learning_resource_phase3_pipeline_probe/detection/`
- `experiments/20260709_155523/outputs/learning_resource_phase3_pipeline_probe/recognition/`
- `experiments/20260709_155523/outputs/learning_resource_phase3_pipeline_probe/parsed_pages/`
- `experiments/20260709_155523/outputs/learning_resource_phase3_pipeline_probe/ocr_quality_summary.csv`
- `experiments/20260709_155523/outputs/learning_resource_phase3_pipeline_probe/markdown_manifest.csv`

Kết quả quan sát:

- Pipeline chạy được theo đúng mô hình nhiều môi trường.
- Markdown nháp giữ được cấu trúc mục lục dạng bảng tốt hơn text thuần.
- OCR/layout vẫn có nhiễu, ví dụ một số chữ trang trí bị nhập vào dòng bài học. Vì vậy output vẫn ở trạng thái `draft` và `needs_review: true`.


## 20. Cập nhật đồng bộ registry và code ngày 18/07/2026

Sau khi có OCR Markdown SGK/SGV Tin học 8–9 và dữ liệu hội thoại HNMU lớp 8–9, đã rà lại các output của Plan 02 và Plan 03 để đồng bộ với phạm vi lớp 6–9:

- `build_ocr_text_manifest.py` giờ mặc định đọc thêm `sgk_thcs_topic_lesson_map_v0.csv` để nối tên chủ đề/bài học từ mục lục SGK, bao gồm các bài có hậu tố 10A/10B.
- Đã rebuild `ocr_text_manifest.csv`, `learning_resource_fragments.csv` và `learning_resources_v0.sqlite` từ dữ liệu OCR Markdown lớp 6–9.
- Đã cập nhật `learning_resource_file_manifest.csv` để bỏ ghi chú lỗi thời “chưa OCR”.
- Đã cập nhật report registry v0 và tạo report đồng bộ: `reports/learning-resource-registries-sync-20260718.md`.

Lưu ý phạm vi: đây là đồng bộ học liệu/registry, không phải audit chất lượng hội thoại lớp 8–9. Plan 04 output đã có vẫn là vòng audit lớp 6–7; lớp 8–9 cần một lượt chạy riêng nếu muốn kiểm toán.
