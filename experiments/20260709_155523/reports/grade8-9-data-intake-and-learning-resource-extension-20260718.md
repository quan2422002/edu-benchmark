# Mở rộng dữ liệu lớp 8–9 — đăng ký hội thoại và xử lý học liệu OCR

Ngày thực hiện: 18/07/2026  
Experiment: `20260709_155523`

Ghi chú cập nhật 20/07/2026: tại thời điểm report này được viết, lớp 8–9 mới được đăng ký raw-data và chưa audit Plan 04. Sau đó lớp 8–9 đã được xử lý trong lượt audit riêng ngày 19/07/2026 tại:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/
```

## 1. Phạm vi đã làm

Theo chỉ đạo mới, lượt này xử lý hai nhóm dữ liệu nhưng giữ ranh giới rõ:

1. Dữ liệu hội thoại HNMU lớp 8–9: tại thời điểm 18/07/2026 chỉ đăng ký vào vùng raw-data dùng chung theo Plan 02, giữ nguyên file gốc và chưa chạy audit Plan 04.
2. Dữ liệu OCR Markdown do Nguyên gửi cho SGK/SGV lớp 8–9: đưa vào Pha 4–5 của Plan 03, tức manifest → fragment → SQLite FTS index truy xuất.

## 2. Dữ liệu hội thoại HNMU

Đã đăng ký thêm trong:

```text
shared/raw_data/HNMU-teacher_dialog_samples/manifest.csv
```

Hai file mới:

| File | Số dòng đọc được | Số dòng có hội thoại ước tính | SHA-256 |
|---|---:|---:|---|
| `Lớp 8.xlsx` | 281 | 280 | `9109c5aa21444c7cd1172eef0831e73ea790ee07b366e41c314217439658912c` |
| `Lớp 9.xlsx` | 309 | 308 | `cb28795ebb4b1b5064cbf93c8c81e8887feab07c7377402b45b3d0a7734b9f1a` |

Lưu ý: chưa sửa file Excel gốc, chưa chạy kiểm toán Plan 04 và chưa tạo output chuyển đổi benchmark.

## 3. Học liệu OCR Markdown do Nguyên gửi

Đã rebuild toàn bộ pipeline Pha 4–5 cho SGK/SGV Tin học 6–9:

```text
shared/learning_resources/registries/ocr_text_manifest.csv
shared/learning_resources/fragments/learning_resource_fragments.csv
shared/learning_resources/indexes/learning_resources_v0.sqlite
```

Thống kê manifest:

| Lớp | SGK | SGV |
|---:|---:|---:|
| 6 | 17 | 18 |
| 7 | 16 | 17 |
| 8 | 20 | 21 |
| 9 | 22 | 23 |

Thống kê fragment:

| Lớp | SGK | SGV |
|---:|---:|---:|
| 6 | 223 | 383 |
| 7 | 302 | 414 |
| 8 | 315 | 400 |
| 9 | 296 | 417 |

Tổng cộng: 154 nguồn OCR Markdown và 2.750 fragment.

## 4. Sửa lỗi phát hiện trong lúc mở rộng

Khi build index cho lớp 8–9, pipeline phát hiện trùng `ocr_text_id` ở các bài có hậu tố như `10A/10B`, `11A/11B`. Nguyên nhân là logic cũ chỉ giữ số bài, ví dụ cả `tin_8_bai_10a` và `tin_8_bai_10b` đều thành `bai_10`.

Đã sửa `src/edu_benchmark/learning_resources/ocr_text_manifest.py` để giữ hậu tố bài trong `lesson_key`, ví dụ:

- `tin_8_bai_10a` → `bai_10a`;
- `tin_8_bai_10b` → `bai_10b`;
- `OCR-SGK-TIN8-BAI10A` và `OCR-SGK-TIN8-BAI10B` không còn trùng.

Đã bổ sung test hồi quy cho trường hợp này.

## 5. Kiểm thử truy xuất nhanh

Truy vấn lớp 8:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "thuật toán tìm kiếm" --grade 8 --limit 3
```

Truy vấn lớp 9:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "mô phỏng thuật toán" --grade 9 --limit 3
```

Cả hai truy vấn đều trả về fragment hợp lệ kèm lớp, loại sách, bài, section, trang và đường dẫn Markdown nguồn.

## 6. Việc chưa làm

- Chưa chạy audit Plan 04 cho hội thoại lớp 8–9.
- Chưa dùng specialist `hnmu-dialogue-auditor` cho batch lớp 8–9.
- Chưa chuyển dữ liệu lớp 8–9 sang mẫu benchmark.
- Fragment học liệu vẫn ở trạng thái `draft`; chưa coi là xác nhận chuyên môn của HNMU/UET.

## 7. Lệnh đã dùng

Python executable:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Các lệnh chính:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_ocr_text_manifest.py --grade ""

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_fragments.py

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_index.py
```


## 8.1. Cập nhật sau rà soát registry cùng ngày

Sau khi rà lại các registry dùng chung, đã đồng bộ thêm các điểm sau:

- `learning_resource_file_manifest.csv` đã được cập nhật notes để không còn ghi “chưa OCR” cho ảnh/PDF SGK/SGV, vì OCR Markdown v0 đã tồn tại riêng trong `ocr_text_manifest.csv`.
- `sgk_thcs_topic_lesson_map_v0.csv` hiện bao phủ SGK Tin học 6–9 theo mục lục OCR Markdown do Nguyên gửi: 106 mục, gồm chủ đề, chủ đề con, bài học và phụ lục.
- `sgk_thcs_lesson_position_registry_v0.csv` hiện có 755 vị trí lấy từ dữ liệu HNMU lớp 6–9; đây là metadata thô để hỗ trợ kiểm phủ/truy xuất, chưa phải xác nhận đúng/sai.
- `build_ocr_text_manifest.py` đã được cập nhật để tự nối topic map khi rebuild manifest OCR. Vì vậy các lần rebuild sau sẽ không làm mất `topic_title` cho bài SGK/SGV.
- Đã rebuild lại `ocr_text_manifest.csv`, `learning_resource_fragments.csv` và `learning_resources_v0.sqlite` sau khi sync.

Báo cáo chi tiết: `experiments/20260709_155523/reports/learning-resource-registries-sync-20260718.md`.

## 8. Validation

Đã chạy bằng:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Kết quả:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/learning_resources tests/agents -q
47 passed in 0.10s

/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/dialogue_audit -q
6 passed in 0.27s
```
