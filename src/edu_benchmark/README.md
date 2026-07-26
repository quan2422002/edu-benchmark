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

Các module sau phục vụ kiểm toán v0 dữ liệu hội thoại thô HNMU. Experiment hiện có output canonical riêng cho lớp 6–7 và lớp 8–9:

- `data_io.xlsx`: đọc raw `.xlsx` độc lập bằng thư viện chuẩn; dependency `openpyxl` của Plan 08 chỉ phục vụ xuất và kiểm tra workbook bàn giao.
- `dialogue_audit.hnmu_audit`: chuẩn hóa dòng raw, kiểm thiếu trường/định dạng, thống kê độ phủ, phát hiện trùng/gần trùng, truy xuất evidence học liệu v0 và sinh bảng chất lượng.
- `dialogue_audit.teacher_bundle`: đóng gói đúng 15 output canonical thành bốn workbook giáo viên, giữ `source_file` để truy vết nhưng không mở đường dẫn đó.
- `dialogue_audit.teacher_bundle_v2_complete`: builder canonical của bundle v2; dùng checklist repaired, tạo CSV root, duplicate toàn bộ lớp, độ phủ 75 bài học, sinh report Markdown một câu hỏi ở root và giữ summary 8 dòng theo lớp; build theo staging + atomic replacement và validator mở lại toàn bộ output.
- `dialogue_audit.fragment_analysis_hnmu`: giữ schema và writer phụ lục kỹ thuật đầy đủ.
- `dialogue_audit.fragment_analysis_hnmu_compact`: giữ renderer bốn cột cho các summary theo lớp.
- `dialogue_audit.fragment_analysis_root_deliverables`: sinh report Markdown HNMU và workbook kỹ thuật sáu sheet; sheet cuối bảo toàn nguyên vẹn bảng kỹ thuật 396 × 29 để truy vết.
- `dialogue_audit.teacher_bundle_v2_hnmu_docs`: sinh README, báo cáo và danh mục file đồng bộ với cây bundle.

CLI chạy bằng `benchmark_env`:

```bash
PYTHONPATH=src /home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/dialogue_audit/run_hnmu_dialogue_audit.py --grades 6 7
```

Plan 08 không chạy lại audit. Lệnh build bundle đã được duyệt dùng interpreter task-specific:

```bash
PYTHONPATH=src /home/dknguyen/miniconda3/envs/edu_ai/bin/python \
  scripts/dialogue_audit/build_hnmu_phase1_teacher_bundle.py
```

Bundle v2 dùng lệnh riêng và không sửa bundle v1:

```bash
PYTHONPATH=src /home/dknguyen/miniconda3/envs/edu_ai/bin/python \
  scripts/dialogue_audit/build_hnmu_phase1_teacher_bundle_v2.py
PYTHONPATH=src /home/dknguyen/miniconda3/envs/edu_ai/bin/python \
  scripts/dialogue_audit/build_hnmu_phase1_teacher_bundle_v2.py --validate-only
