# `edu_benchmark`

Package này chứa code dùng chung cho dự án benchmark gia sư AI môn Tin học.

## Nguyên tắc

1. Code dùng chung đặt trong `src/edu_benchmark/`, không đặt rải trong từng experiment.
2. Code không sửa dữ liệu gốc; mọi kết quả xử lý phải là bản dẫn xuất có truy vết.
3. Các script/validator phải chạy bằng môi trường Conda `benchmark_env`, trừ bước VietOCR GPU recognition của Plan 03 được phép chạy bằng môi trường riêng `ocr_vietocr_gpu` và bước chạy MinerU được phép chạy bằng môi trường riêng `ocr_mineru`.
4. Các module ban đầu được tạo ở Plan 02; hiện đã có logic dùng chung cho đọc XLSX, audit dialogue v0, manifest/fragment/index học liệu và retrieval v0. Các phần chuyển đổi benchmark/evaluation vẫn thuộc plan sau.

## Cấu trúc

- `data_io`: đọc Excel/CSV và chuẩn hóa bảng trung gian.
- `dialogue_audit`: kiểm thiếu trường, độ phủ, nhất quán, trùng/gần trùng và chất lượng hội thoại.
- `benchmark_conversion`: chuyển dữ liệu thô đã qua kiểm toán thành mẫu benchmark.
- `learning_resources`: xử lý học liệu, chủ đề, bài học, OCR, fragment và registry.
- `benchmark_quality`: kiểm tra khả năng áp dụng/phân biệt của benchmark sau chuyển đổi.

## Ghi chú riêng cho OCR học liệu

Code chính cho Pha 3–5 của Plan 03 vẫn thuộc `src/edu_benchmark/learning_resources/`. Nếu cần chạy VietOCR GPU, chỉ bước nhận dạng crop bằng VietOCR dùng:

```text
/home/quannda/miniconda3/envs/ocr_vietocr_gpu/bin/python
```

Các bước còn lại như điều phối, tái dựng bố cục, xuất Markdown, tách fragment, build index và test vẫn dùng:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Riêng Pha A MinerU book-level: script chuẩn bị manifest/PDF và script gom Markdown vẫn chạy bằng `benchmark_env`; lệnh MinerU thật chạy ngoài sandbox bằng:

```text
/home/quannda/miniconda3/envs/ocr_mineru/bin/mineru
```

Sau khi MinerU chạy xong, script hậu xử lý vẫn chạy bằng `benchmark_env`:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python scripts/learning_resources/postprocess_mineru_book_phase.py
```

Script này tạo Markdown sạch theo trang và review queue ở output experiment; không tự động đưa học liệu vào vùng shared chính thức.

## Ghi chú Pha 4–5 từ dữ liệu OCR của Nguyên

Các module sau phục vụ luồng Markdown OCR của Nguyên → fragment → truy xuất:

- `ocr_text_manifest.py`: tạo manifest cho `shared/learning_resources/ocr_text` và tự nối topic map SGK khi có.
- `fragment_markdown.py`: tách Markdown theo bài/mục thành fragment có mã ổn định.
- `retrieval_index.py`: build SQLite full-text search index từ fragment.
- `retrieval_api.py`: cung cấp `resolve_learning_resource`, `search_learning_fragments`, `get_learning_fragment`.

Các bước này chỉ dùng môi trường `benchmark_env`; không dùng `ocr_vietocr_gpu` hay `ocr_mineru` vì không chạy OCR lại. Trạng thái hiện tại: 154 OCR units và 2.750 fragments cho SGK/SGV Tin học 6–9.

## Ghi chú Plan 04 audit hội thoại HNMU

Các module sau phục vụ kiểm toán v0 dữ liệu hội thoại thô HNMU. Vòng đã chạy chính thức trong experiment này là lớp 6–7; dữ liệu lớp 8–9 đã được đăng ký manifest nhưng cần một lượt audit riêng nếu muốn tạo output Plan 04:

- `data_io.xlsx`: đọc `.xlsx` bằng thư viện chuẩn Python để tránh phụ thuộc runtime vào `openpyxl`.
- `dialogue_audit.hnmu_audit`: chuẩn hóa dòng raw, kiểm thiếu trường/định dạng, thống kê độ phủ, phát hiện trùng/gần trùng, truy xuất evidence học liệu v0 và sinh bảng chất lượng.

CLI chạy bằng `benchmark_env`:

```bash
PYTHONPATH=src /home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/dialogue_audit/run_hnmu_dialogue_audit.py --grades 6 7
```

Lớp 8–9 hiện đã có học liệu truy xuất v0 từ OCR Markdown của Nguyên và raw Excel đã được đăng ký manifest. Nếu cần audit, chạy như một vòng riêng để không ghi đè output lớp 6–7 đã có.
