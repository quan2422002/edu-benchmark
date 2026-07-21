# Kết quả Pha 5 — Index truy xuất học liệu v0

Ngày chạy bản đầu: 16/07/2026  
Ngày đồng bộ hiện tại: 18/07/2026  
Nguồn fragment: `shared/learning_resources/fragments/learning_resource_fragments.csv`  
Trạng thái: `draft`, phục vụ truy xuất/audit v0; chưa phải cơ sở chuyên môn đã xác nhận.

## 1. Kết luận hiện tại

Pha 5 hiện đã dựng lại index truy xuất v0 từ **2750** fragment SGK/SGV Tin học 6–9. Index dùng SQLite FTS để tìm kiếm toàn văn kết hợp bộ lọc metadata như lớp, loại sách, bài học, chủ đề và loại fragment.

Output chính:

```text
shared/learning_resources/indexes/learning_resources_v0.sqlite
shared/learning_resources/indexes/README.md
```

File `.sqlite` là artifact sinh lại được và đang được `.gitignore` bỏ qua theo rule `shared/**/*.sqlite`.

## 2. Code và script liên quan

Code dùng chung:

```text
src/edu_benchmark/learning_resources/ocr_text_manifest.py
src/edu_benchmark/learning_resources/fragment_markdown.py
src/edu_benchmark/learning_resources/retrieval_index.py
src/edu_benchmark/learning_resources/retrieval_api.py
```

Script chạy:

```text
scripts/learning_resources/build_ocr_text_manifest.py
scripts/learning_resources/build_learning_resource_fragments.py
scripts/learning_resources/build_learning_resource_index.py
scripts/learning_resources/query_learning_resource_index.py
```

## 3. Kết quả index

| Thành phần | Số lượng |
| --- | --- |
| Source OCR Markdown | 154 |
| Fragment được index | 2750 |

Phân bố fragment được index:

| Lớp | SGK | SGV |
| --- | --- | --- |
| 6 | 223 | 383 |
| 7 | 302 | 414 |
| 8 | 315 | 400 |
| 9 | 296 | 417 |

Các hàm truy xuất tối thiểu đã có:

```text
resolve_learning_resource(metadata)
search_learning_fragments(query, filters)
get_learning_fragment(fragment_id)
```

## 4. Query thử đại diện

### Lớp 6 — Scratch/chương trình máy tính

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "Scratch trung bình cộng ba số" \
  --grade 6 \
  --limit 5
```

Kỳ vọng: trả về các fragment liên quan Bài 17 SGK/SGV Tin học 6 về chương trình máy tính/Scratch.

### Lớp 7 — thuật toán tìm kiếm tuần tự

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "thuật toán tìm kiếm tuần tự" \
  --grade 7 \
  --limit 5
```

Kỳ vọng: trả về các fragment liên quan Bài 14 SGK/SGV Tin học 7.

### Lớp 8 — thuật toán tìm kiếm

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "thuật toán tìm kiếm" \
  --grade 8 \
  --limit 5
```

Kỳ vọng: trả về fragment SGK/SGV Tin học 8 liên quan chủ đề tổ chức lưu trữ, tìm kiếm và xử lý dữ liệu/thuật toán.

### Lớp 9 — hàm COUNTIF

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "hàm COUNTIF" \
  --grade 9 \
  --limit 5
```

Kỳ vọng: trả về fragment SGK/SGV Tin học 9 liên quan Bài 10A. Sử dụng hàm COUNTIF.

## 5. Cách chạy lại Pha 5

Dùng môi trường chính:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_index.py
```

Nếu OCR Markdown hoặc topic map thay đổi, chạy đủ ba bước theo thứ tự:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_ocr_text_manifest.py \
  --grade ""

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_fragments.py

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_index.py
```

## 6. Giới hạn hiện tại

- SQLite FTS v0 là truy xuất từ khóa; chưa dùng embedding/vector search.
- Một số query khái niệm có thể trả caption/bảng trước đoạn giải thích chính; ranking có thể tinh chỉnh sau.
- Kết quả truy xuất trả về evidence ứng viên, không phải phán quyết đúng/sai tự động.
- Agent kiểm dữ liệu HNMU phải đọc fragment, trạng thái và nguồn truy vết trước khi kết luận.
- Toàn bộ học liệu OCR/fragment/index vẫn là `draft` cho tới khi UET/HNMU review.
