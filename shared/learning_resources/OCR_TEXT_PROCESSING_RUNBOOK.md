# Runbook — xử lý OCR Markdown SGK/SGV mới do Nguyên gửi

Mục đích: hướng dẫn người hoặc agent mới đưa dữ liệu OCR Markdown mới vào hệ thống học liệu truy xuất của dự án.

Áp dụng cho trường hợp Nguyên gửi thêm hoặc sửa SGK/SGV mới dưới dạng thư mục Markdown + metadata. Tính đến 18/07/2026, runbook này đã được dùng để xử lý SGK/SGV Tin học 6–9.

## 1. Kết luận chạy nhanh

Nếu dữ liệu mới đã được đặt đúng cấu trúc trong:

```text
shared/learning_resources/ocr_text/
```

thì chạy lần lượt:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_ocr_text_manifest.py \
  --grade ""

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_fragments.py

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_index.py

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "thuật toán tìm kiếm tuần tự" \
  --grade 7 \
  --limit 5

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  -m pytest tests/learning_resources tests/agents -q
```

Điểm quan trọng: dùng `--grade ""` để rebuild manifest cho **tất cả khối lớp đang có** trong `ocr_text`, không chỉ lớp 6.

Script manifest hiện mặc định đọc thêm `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv` để nối `topic_title`/tên bài từ mục lục SGK, bao gồm các bài có hậu tố như 10A/10B. Nếu topic map vừa được cập nhật, hãy chạy lại manifest → fragment → index theo đúng thứ tự này.

## 2. Không chạy OCR ở bước này

Runbook này **không dùng để OCR ảnh**. Nó chỉ xử lý khi đã có Markdown OCR tương đối sạch do Nguyên gửi.

Không dùng các môi trường OCR:

```text
/home/quannda/miniconda3/envs/ocr_vietocr_gpu
/home/quannda/miniconda3/envs/ocr_mineru
```

Chỉ dùng môi trường chính:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

## 3. Cấu trúc thư mục đầu vào cần có

Mỗi sách đặt trong:

```text
shared/learning_resources/ocr_text/
```

Quy ước hiện tại:

```text
shared/learning_resources/ocr_text/
  sgk_tin_hoc_6/
    tin_6_bai_1/
      tin_6_bai_1.md
      tin_6_bai_1.metadata.json
      *_img.jpg
    ...
  sgv_tin_hoc_6/
    sgv_tin_6_00_hd_chung/
      sgv_tin_6_00_hd_chung.md
      sgv_tin_6_00_hd_chung.metadata.json
    sgv_tin_6_bai_1/
      sgv_tin_6_bai_1.md
      sgv_tin_6_bai_1.metadata.json
    ...
```

Khi thêm lớp mới, nên giữ cùng mẫu:

```text
shared/learning_resources/ocr_text/
  sgk_tin_hoc_8/
    tin_8_bai_1/
      tin_8_bai_1.md
      tin_8_bai_1.metadata.json
    ...
  sgv_tin_hoc_8/
    sgv_tin_8_00_hd_chung/
      sgv_tin_8_00_hd_chung.md
      sgv_tin_8_00_hd_chung.metadata.json
    sgv_tin_8_bai_1/
      sgv_tin_8_bai_1.md
      sgv_tin_8_bai_1.metadata.json
    ...
```

Với lớp 9 cũng tương tự:

```text
sgk_tin_hoc_9/tin_9_bai_<số_bài>/
sgv_tin_hoc_9/sgv_tin_9_bai_<số_bài>/
```

## 4. Kiểm tra trước khi chạy

### 4.1. Kiểm tra source registry

Mở file:

```text
shared/learning_resources/registries/sgk_sgv_source_registry.csv
```

Đảm bảo đã có dòng tương ứng cho sách mới, ví dụ:

```text
LM-SGK-TIN8-0001
LM-SGV-TIN8-4923610683
LM-SGK-TIN9-0001
LM-SGV-TIN9-4923777498
```

Nếu thiếu dòng source registry, script vẫn có thể chạy nhưng manifest sẽ thiếu `learning_material_id`, không nên dùng để build fragment chính thức.

### 4.2. Kiểm tra nhanh file Markdown/metadata

Ví dụ kiểm lớp 8:

```bash
find shared/learning_resources/ocr_text/sgk_tin_hoc_8 \
  -maxdepth 2 -type f \( -name "*.md" -o -name "*.metadata.json" \) | sort

find shared/learning_resources/ocr_text/sgv_tin_hoc_8 \
  -maxdepth 2 -type f \( -name "*.md" -o -name "*.metadata.json" \) | sort
```

Mỗi thư mục bài/mục nên có:

- 1 file `.md`;
- 1 file `.metadata.json`;
- ảnh minh họa nếu có.

## 5. Các bước xử lý chính

### Bước 1 — Build manifest OCR Markdown

Script:

```text
scripts/learning_resources/build_ocr_text_manifest.py
```

Code chính:

```text
src/edu_benchmark/learning_resources/ocr_text_manifest.py
```

Lệnh khuyến nghị:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_ocr_text_manifest.py \
  --grade ""
```

Output:

```text
shared/learning_resources/registries/ocr_text_manifest.csv
```

Vai trò:

- đăng ký toàn bộ file Markdown OCR hiện có;
- nối từng file với `learning_material_id`;
- ghi `grade`, `material_type`, `lesson_key`, `lesson_title`, `topic_title`;
- thống kê số mốc trang, số bảng, số ảnh;
- gắn trạng thái `draft` hoặc `needs_uet_review`.

Lưu ý:

- Nếu chỉ muốn build riêng một lớp để kiểm thử, có thể dùng `--grade 8`.
- Khi build chính thức cho index chung, dùng `--grade ""`.

### Bước 2 — Tách fragment

Script:

```text
scripts/learning_resources/build_learning_resource_fragments.py
```

Code chính:

```text
src/edu_benchmark/learning_resources/fragment_markdown.py
```

Lệnh:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_fragments.py
```

Output:

```text
shared/learning_resources/fragments/learning_resource_fragments.csv
shared/learning_resources/fragments/README.md
```

Vai trò:

- tách Markdown theo mốc trang, heading, bảng, hoạt động, luyện tập, vận dụng;
- tạo `fragment_id`;
- giữ `source_markdown_path`;
- gắn trạng thái ban đầu `draft`;
- đánh dấu `needs_hnmu_review=true` cho một số đoạn hướng dẫn dạy học/đáp án trong SGV.

### Bước 3 — Build index truy xuất

Script:

```text
scripts/learning_resources/build_learning_resource_index.py
```

Code chính:

```text
src/edu_benchmark/learning_resources/retrieval_index.py
src/edu_benchmark/learning_resources/retrieval_api.py
```

Lệnh:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_index.py
```

Output:

```text
shared/learning_resources/indexes/learning_resources_v0.sqlite
shared/learning_resources/indexes/README.md
```

Ghi chú:

- File `.sqlite` là artifact sinh lại được.
- File này đang được `.gitignore` bỏ qua theo rule `shared/**/*.sqlite`.
- Không cần push file SQLite lên GitHub nếu có thể rebuild từ manifest + fragment.

### Bước 4 — Query thử

Script:

```text
scripts/learning_resources/query_learning_resource_index.py
```

Ví dụ lớp 7:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "thuật toán tìm kiếm tuần tự" \
  --grade 7 \
  --limit 5
```

Ví dụ lớp 8:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "sắp xếp dữ liệu" \
  --grade 8 \
  --limit 5
```

Ví dụ lớp 9:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "Python danh sách" \
  --grade 9 \
  --limit 5
```

Ví dụ chỉ tìm trong SGV:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "hướng dẫn dạy học" \
  --grade 8 \
  --material-type SGV \
  --limit 5
```

## 6. Kiểm thử sau khi chạy

Chạy:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  -m pytest tests/learning_resources tests/agents -q
```

Kỳ vọng: tất cả test liên quan phải pass. Số lượng test có thể tăng theo thời gian, nên không dùng một con số cố định làm điều kiện duy nhất.

## 7. Kiểm tra thống kê sau khi chạy

Dùng lệnh sau để xem số lượng manifest/fragment:

```bash
PYTHONPATH=src /home/quannda/miniconda3/envs/benchmark_env/bin/python - <<'PY'
import csv
from collections import Counter

manifest = list(csv.DictReader(open(
    "shared/learning_resources/registries/ocr_text_manifest.csv",
    encoding="utf-8",
)))
fragments = list(csv.DictReader(open(
    "shared/learning_resources/fragments/learning_resource_fragments.csv",
    encoding="utf-8",
)))

print("manifest_count", len(manifest))
print("manifest_by_type_grade", Counter((r["material_type"], r["grade"]) for r in manifest))
print("manifest_status", Counter(r["status"] for r in manifest))
print("fragment_count", len(fragments))
print("fragment_by_type_grade", Counter((r["material_type"], r["grade"]) for r in fragments))
print("fragment_type", Counter(r["fragment_type"] for r in fragments).most_common())
print("needs_hnmu_review", Counter(r["needs_hnmu_review"] for r in fragments))
PY
```

Hiện tại, sau khi đã xử lý SGK/SGV Tin học 6–9 ngày 18/07/2026, kết quả kỳ vọng là:

```text
manifest_count 154
manifest_status Counter({'draft': 154})
fragment_count 2750
```

Phân bố hiện tại:

```text
OCR manifest: SGK/SGV lớp 6 = 17/18; lớp 7 = 16/17; lớp 8 = 20/21; lớp 9 = 22/23.
Fragment: SGK/SGV lớp 6 = 223/383; lớp 7 = 302/414; lớp 8 = 315/400; lớp 9 = 296/417.
```

Nếu số lượng thay đổi sau khi Nguyên gửi bản OCR mới, cần ghi lại trong report/handoff của lượt xử lý đó.

## 8. Các file không nên sửa thủ công

Không sửa thủ công các file sinh tự động sau, trừ khi đang debug có chủ đích:

```text
shared/learning_resources/registries/ocr_text_manifest.csv
shared/learning_resources/fragments/learning_resource_fragments.csv
shared/learning_resources/indexes/learning_resources_v0.sqlite
```

Nếu cần thay đổi logic, sửa code trong:

```text
src/edu_benchmark/learning_resources/
```

rồi chạy lại pipeline.

## 9. Các output/probe cũ không dùng làm nguồn chính

Không dùng các output OCR/MinerU cũ của Codex làm nguồn chính cho fragment/index, trừ khi có plan riêng để so sánh hoặc debug.

Đọc trước:

```text
experiments/20260709_155523/reports/plan03-codex-artifact-cleanup-map.md
experiments/20260709_155523/outputs/PLAN03_CODEX_ARTIFACTS_CLEANUP_README.md
experiments/20260709_155523/handoffs/learning-resource-codex-artifact-cleanup-marking-032.md
```

Nguồn chính hiện tại là:

```text
shared/learning_resources/ocr_text/
```

## 10. Checklist bàn giao cho agent mới

Nếu giao cho một agent mới, prompt nên nói rõ:

```text
Bạn chỉ xử lý dữ liệu OCR Markdown đã có trong shared/learning_resources/ocr_text.
Không chạy OCR lại.
Không sửa file Markdown nguồn.
Không đụng output/probe OCR-MinerU cũ.
Dùng benchmark_env.
Chạy build_ocr_text_manifest.py --grade "" để rebuild toàn bộ manifest và tự nối topic map.
Chạy build_learning_resource_fragments.py.
Chạy build_learning_resource_index.py.
Query thử theo lớp mới.
Chạy pytest tests/learning_resources tests/agents -q.
Báo số manifest, số fragment, query thử và test result.
```

## 11. Khi nào cần sửa code?

Chỉ sửa code nếu gặp một trong các trường hợp sau:

1. Cấu trúc thư mục Nguyên gửi khác quy ước hiện tại.
2. Tên file không theo mẫu `tin_<lớp>_bai_<số>` hoặc `sgv_tin_<lớp>_bai_<số>`.
3. Metadata JSON thiếu hoặc đổi cấu trúc.
4. Fragment quá vụn hoặc quá rộng.
5. Query thường xuyên trả caption hình/bảng trước đoạn giải thích chính.
6. Cần thêm filter mới, ví dụ `topic_title`, `lesson_title`, `fragment_type`.

Nếu sửa code, phải chạy lại test.

## 12. Vấn đề Git cần nhớ

Thư mục `ocr_text` có thể chứa nhiều ảnh `.jpg`. Trước khi push lên GitHub, cần kiểm tra chính sách dữ liệu nặng/bản quyền.

Hiện có thể cân nhắc:

- track Markdown + metadata;
- ignore ảnh `.jpg` nếu quá nặng hoặc không nên push;
- lưu ảnh đầy đủ ở Google Drive/DVC/cơ chế ngoài Git nếu cần.

Không tự ý xóa ảnh OCR của Nguyên khi chưa có quyết định rõ.
