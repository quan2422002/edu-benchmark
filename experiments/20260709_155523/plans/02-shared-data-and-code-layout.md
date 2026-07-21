# Plan 02 — Quy ước layout dữ liệu dùng chung và code dùng chung

Experiment: `20260709_155523`
Trạng thái: `HOÀN THÀNH` — được Quân duyệt và triển khai ngày 15/07/2026.
Ngày lập: 11/07/2026
Ngày cập nhật: 18/07/2026

## 1. Mục tiêu

Chốt quy ước đặt file để tránh lẫn lộn giữa:

- dữ liệu dùng chung qua nhiều experiment;
- học liệu SGK/SGV dùng chung;
- code dùng chung;
- plan/report/kết quả chạy riêng của từng experiment.

Sau cập nhật ngày 14/07/2026, dữ liệu HNMU thật đã xuất hiện trong `shared/raw_data/HNMU-teacher_dialog_samples/`. Vì vậy, Plan 02 không còn là plan chuẩn bị trừu tượng, mà cần đăng ký batch đã nhận và quy định cách quản lý dữ liệu thô.

## 2. Nguyên tắc

1. Experiment chỉ lưu plan, report, handoff, slide và kết quả chạy gắn với experiment đó.
2. Raw data dùng chung không đặt trong experiment.
3. Code dùng chung không đặt trong experiment.
4. Mọi dữ liệu thô phải giữ nguyên bản gốc; bản chuẩn hóa là dẫn xuất riêng.
5. Không sửa trực tiếp file Excel HNMU gửi.
6. Ảnh SGK/SGV có thể là tài nguyên có bản quyền; không mặc định push ảnh lên GitHub nếu chưa rõ quyền. Manifest/README có thể được version hóa.
7. Chỉ di chuyển/tạo thư mục sau khi plan được duyệt.

## 3. Layout đề xuất

### 3.1. `shared/raw_data/HNMU-teacher_dialog_samples/`

Vai trò: lưu dữ liệu hội thoại thô do HNMU gửi.
Lý do tạo: dữ liệu HNMU sẽ được dùng lại ở nhiều experiment, không nên bị chôn trong một experiment cụ thể.

Tình trạng hiện tại sau đồng bộ ngày 18/07/2026:

```text
shared/raw_data/HNMU-teacher_dialog_samples/
  Lớp 6.xlsx
  Lớp 7.xlsx
  Lớp 8.xlsx
  Lớp 9.xlsx
  README.md
  manifest.csv
```

Cấu trúc quản lý đề xuất sau khi Plan 02 được duyệt:

```text
shared/raw_data/HNMU-teacher_dialog_samples/
  README.md
  manifest.csv
  original/
    20260714_initial/
      Lớp 6.xlsx
      Lớp 7.xlsx
    20260718_grade8_9/
      Lớp 8.xlsx
      Lớp 9.xlsx
```

Nếu không muốn di chuyển file gốc ngay, có thể giữ file tại vị trí hiện tại và tạo manifest trỏ tới đường dẫn hiện có. Điều quan trọng là mọi batch phải được đăng ký, không xử lý file “trôi nổi”.

`manifest.csv` nên có các cột:

- `batch_id`
- `received_date`
- `source_file`
- `grade`
- `estimated_rows`
- `estimated_dialogue_rows`
- `sha256`
- `source_owner`
- `processing_status`
- `notes`

### 3.2. `shared/learning_resources/`

Vai trò: lưu học liệu dùng chung, gồm ảnh SGK/SGV đã crawl, OCR, danh mục chủ đề/bài học, fragment và metadata.
Lý do tạo: học liệu là nền chung cho độ phủ, truy vết, kiểm đáp án và sau này cho retrieval/database.

Cấu trúc đề xuất:

```text
shared/learning_resources/
  README.md
  raw_page_images/
    sgk/
      tin_hoc_6/
      tin_hoc_7/
      tin_hoc_8/
      tin_hoc_9/
    sgv/
      tin_hoc_6/
      tin_hoc_7/
      tin_hoc_8/
      tin_hoc_9/
  ocr_text/
  registries/
    learning_resource_file_manifest.csv
    sgk_sgv_source_registry.csv
  fragments/
```

Ảnh SGK đã crawl hiện nằm ở `experiments/20260705_215045/source_scope/raw_page_images/` và có đủ `SGK_TIN6` đến `SGK_TIN9`. Plan 03 sẽ quyết định việc copy sang `shared/` bằng manifest/checksum.

### 3.3. `src/`

Vai trò: chứa code dùng chung cho xử lý dữ liệu, kiểm toán benchmark, chuyển đổi mẫu, chuẩn hóa học liệu và đánh giá.
Lý do tạo: code phải tách khỏi experiment để tái sử dụng và test được.

Cấu trúc đề xuất:

```text
src/
  edu_benchmark/
    data_io/
    dialogue_audit/
    benchmark_conversion/
    learning_resources/
    benchmark_quality/
```

Vai trò từng phần:

- `data_io`: đọc Excel/CSV, chuẩn hóa bảng dẫn xuất, không sửa dữ liệu gốc.
- `dialogue_audit`: kiểm thiếu trường, độ phủ, nhất quán, trùng/gần trùng, chất lượng hội thoại.
- `benchmark_conversion`: chuyển dữ liệu thô sang mẫu benchmark hoàn chỉnh.
- `learning_resources`: xử lý học liệu, chủ đề, bài học, trang, OCR/fragment.
- `benchmark_quality`: logic đánh giá khả năng áp dụng/phân biệt của benchmark sau chuyển đổi.

Lưu ý: môi trường hiện chưa có `openpyxl`. Khi triển khai code, cần quyết định hoặc thêm dependency này vào `requirements.txt`, hoặc đọc `.xlsx` bằng thư viện chuẩn zip/XML trong bước đầu.

### 3.4. `experiments/20260709_155523/`

Vai trò: lưu plan, report, handoff, slide và output chạy của experiment này.
Lý do tạo: giữ experiment nhẹ, có thể đọc như nhật ký nghiên cứu.

Output chạy code nên đặt ở một thư mục con rõ ràng, ví dụ:

```text
experiments/20260709_155523/outputs/
  hnmu_dialogue_audit/
  benchmark_conversion/
  learning_resource_registry/
```

## 4. Output dự kiến

- `shared/raw_data/HNMU-teacher_dialog_samples/README.md`.
- `shared/raw_data/HNMU-teacher_dialog_samples/manifest.csv`.
- `shared/learning_resources/README.md` nếu bắt đầu đưa học liệu vào `shared/`.
- `shared/learning_resources/registries/learning_resource_file_manifest.csv` nếu copy ảnh SGK/SGV.
- `src/edu_benchmark/README.md` hoặc cấu trúc package tối thiểu nếu sau này triển khai code.
- Cập nhật README/ARCHITECTURE nếu layout được duyệt và thật sự được tạo.

## 5. Tiêu chí hoàn thành

Plan hoàn thành khi:

1. Có quy ước rõ raw data, học liệu, code và output experiment đặt ở đâu.
2. Có manifest cho batch HNMU đã nhận hoặc quyết định rõ chưa tạo manifest trong bước này.
3. Có README giải thích vai trò từng thư mục nếu thư mục được tạo.
4. Không di chuyển dữ liệu cũ nếu chưa có quyết định rõ.
5. README/ARCHITECTURE được cập nhật nếu có thay đổi cấu trúc repo thật.

## 5.1. Kết quả triển khai ngày 15/07/2026

Plan 02 đã được triển khai theo hướng an toàn để Plan 03 có thể chạy song song mà ít chồng lấn nhất:

- Giữ nguyên hai file Excel HNMU tại vị trí hiện có, không di chuyển vào `original/`.
- Tạo `shared/raw_data/HNMU-teacher_dialog_samples/README.md` để quy định không sửa dữ liệu gốc.
- Tạo `shared/raw_data/HNMU-teacher_dialog_samples/manifest.csv` để đăng ký batch `20260714_initial`.
- Tạo khung `shared/learning_resources/` cho SGK/SGV, OCR, registry và fragment, nhưng chưa copy ảnh SGK và chưa crawl SGV.
- Tạo `shared/learning_resources/registries/learning_resource_file_manifest.csv` làm manifest rỗng cho Plan 03 điền tiếp.
- Tạo khung `src/edu_benchmark/` gồm các module dùng chung: `data_io`, `dialogue_audit`, `benchmark_conversion`, `learning_resources`, `benchmark_quality`.
- Tạo `experiments/20260709_155523/outputs/` để chứa output riêng của experiment.
- Cập nhật `README.md`, `ARCHITECTURE.md`, `roadmap.md` và `metadata.yaml`.

Quy ước chống chồng lấn với Plan 03:

- Plan 02 sở hữu layout, README nền và manifest raw data HNMU.
- Plan 03 sở hữu việc copy/đăng ký ảnh SGK, crawl SGV, tạo registry học liệu và cập nhật `learning_resource_file_manifest.csv`.
- Nếu Plan 03 cần sửa README nền trong `shared/learning_resources/`, chỉ bổ sung phần trạng thái học liệu, không đổi lại nguyên tắc layout đã chốt ở Plan 02.



## 5.2. Cập nhật đồng bộ ngày 18/07/2026

Plan 02 vẫn giữ nguyên vai trò: quản lý layout và manifest, không kiểm toán nội dung hội thoại. Sau khi HNMU gửi thêm lớp 8–9, đã cập nhật phần raw-data dùng chung như sau:

- Đăng ký `Lớp 8.xlsx` và `Lớp 9.xlsx` trong `shared/raw_data/HNMU-teacher_dialog_samples/manifest.csv`.
- Giữ nguyên file Excel gốc tại vị trí hiện có, không di chuyển vào thư mục con để tránh làm gãy đường dẫn.
- Cập nhật `shared/raw_data/HNMU-teacher_dialog_samples/README.md` để ghi rõ hai batch hiện có: `20260714_initial` và `20260718_grade8_9`.
- Trạng thái của lớp 8–9 là `raw_registered_no_audit`: đã đăng ký nhưng chưa chạy Plan 04 audit.

Như vậy Plan 02 đã hoàn thành cả phần đăng ký dữ liệu thô lớp 6–9. Các bước kiểm chất lượng/nhất quán vẫn thuộc Plan 04 hoặc các plan sau, không thuộc Plan 02.

## 6. Ngoài phạm vi

- Không xử lý nội dung dữ liệu HNMU.
- Không chuẩn hóa học liệu.
- Không viết logic audit benchmark.
- Không copy ảnh SGK hoặc crawl SGV; việc đó thuộc Plan 03.
