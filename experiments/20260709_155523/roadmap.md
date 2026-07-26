# Roadmap — đánh giá chất lượng benchmark, học liệu SGK/SGV và dữ liệu HNMU

Experiment: `20260709_155523`
Ngày tạo: 09/07/2026
Ngày cập nhật: 22/07/2026
Trạng thái: `ACTIVE` — Plan 04 có output canonical repaired cho lớp 6–9; Plan 08b đã thu gọn file 05 root thành một câu hỏi HNMU, giữ summary theo lớp và phụ lục kỹ thuật, rebuild và validate toàn bộ bundle v2, đang chờ project lead review local.

## 1. Mục tiêu cập nhật

Experiment này tập trung vào việc chuẩn bị nền tảng để đánh giá **chất lượng của chính bộ benchmark** trước khi dùng benchmark để đánh giá model gia sư AI.

Sau trao đổi ngày 10/07/2026 và cập nhật ngày 14/07/2026, mục tiêu không chỉ là chuyển hội thoại thô HNMU thành mẫu benchmark. Ta cần trả lời trước các câu hỏi:

1. Benchmark có được thiết kế dựa trên bằng chứng nghiên cứu đủ chắc không?
2. Dữ liệu thô HNMU có đủ phủ, nhất quán và ít trùng lặp không?
3. Học liệu SGK/SGV Tin học THCS có được chuẩn hóa đủ tốt để làm thước đo độ phủ, kiểm đáp án và sau này làm nguồn truy vấn cho model không?
4. Sau khi chuyển đổi thành benchmark hoàn chỉnh, benchmark có khả năng phân biệt gia sư tốt, trung bình và kém không?

Tình hình mới:

- HNMU đã gửi batch dữ liệu thô tại `shared/raw_data/HNMU-teacher_dialog_samples/`. Experiment này đã xử lý chính thức `Lớp 6.xlsx`, `Lớp 7.xlsx`, và sau đó chạy một lượt follow-up riêng cho `Lớp 8.xlsx`, `Lớp 9.xlsx`.
- Plan 04 audit v0 đã đọc 462 dòng lớp 6–7 trong output chính. Lượt follow-up ngày 19/07/2026 xử lý thêm 588 dòng lớp 8–9 trong thư mục output riêng, gồm kiểm cơ học và 3-shard specialist audit. Sau khi sửa mapping bài học bằng regex-only, coverage lớp 8–9 không còn nhóm `Không rõ chủ đề`, review queue cơ học giảm còn 3 mẫu. Đây chưa phải xác nhận chuyên môn cuối cùng của HNMU/UET.
- Dữ liệu HNMU hiện có các trường chính: `STT`, `Bài`, `Vị trí`, `Câu hỏi`, `Mức Bloom`, `Đáp án (SGV)`, `Hội thoại gia sư (Theo phương pháp Dàn giáo)`.
- Vì có trường `Đáp án (SGV)`, SGV phải được đưa vào phạm vi học liệu dài hạn. SGK dùng để kiểm câu hỏi/chủ đề/bài học; SGV dùng để kiểm đáp án và căn cứ giải thích.

## 2. Nguyên tắc tổ chức file

1. `experiments/<id>/` chỉ lưu plan, báo cáo, handoff, slide và kết quả chạy gắn với một experiment cụ thể.
2. Dữ liệu thô dùng chung không đặt trong experiment. Dữ liệu hội thoại HNMU đặt ở `shared/raw_data/HNMU-teacher_dialog_samples/`.
3. Học liệu dùng chung, ảnh SGK đã crawl, ảnh SGV tương ứng hoặc bản đã chuẩn hóa nên dần được đưa về vùng `shared/learning_resources/` sau khi có plan được duyệt.
4. Code dùng chung để kiểm tra dữ liệu, đánh giá benchmark, chuyển đổi mẫu hoặc chuẩn hóa học liệu phải đặt trong `src/`, không đặt rải trong experiment.
5. Experiment chỉ giữ output của một lần chạy code, ví dụ báo cáo độ phủ, bảng thống kê, log chạy, hoặc handoff.
6. Không sửa nội dung hội thoại thô HNMU. Mọi chuẩn hóa phải tạo bản dẫn xuất có truy vết.
7. Không triển khai code, di chuyển dữ liệu hoặc crawl thêm học liệu khi plan còn `DRAFT`.
8. Ảnh SGK/SGV có thể là tài nguyên có bản quyền. Trước mắt chỉ quản lý local và manifest; không mặc định push ảnh lên GitHub nếu chưa rõ quyền.

## 3. Thứ tự ưu tiên

```text
Đọc paper về đánh giá benchmark và chốt checklist kiểm định
        ↓
Chốt layout shared/ và src/; đăng ký batch HNMU
        ↓
Chuẩn hóa học liệu SGK/SGV Tin học THCS v0
        ↓
Kiểm toán hội thoại HNMU: độ phủ, thiếu trường, nhất quán, trùng/gần trùng, điểm tự tin
        ↓
Chuyển đổi hội thoại thô thành mẫu benchmark hoàn chỉnh
        ↓
Đánh giá khả năng phân biệt tutor tốt / trung bình / kém
```

Điểm quan trọng: dữ liệu thô HNMU đã có batch ban đầu nhưng chưa đầy đủ toàn bộ khối lớp. Vì vậy, không nên vội chuyển đổi hàng loạt. Plan 01 đã hoàn thành checklist kiểm định chất lượng benchmark/dữ liệu. Plan 02 đã chốt layout `shared/`, `src/` và manifest raw data HNMU. Plan 03 đã tạo nguồn truy xuất học liệu lớp 6–9 từ OCR Markdown của Nguyên. Plan 04 v0 đã kiểm toán batch lớp 6–7 và có lượt follow-up riêng cho lớp 8–9; hai nhóm output được giữ tách biệt để tránh ghi đè. Plan 07 đã bổ sung specialist `hnmu-dialogue-auditor`. Plan 08/08b chỉ đóng gói output canonical đã có, không chạy lại audit và giữ nguyên bundle v1. Bản complete của Plan 08b chỉ đọc thêm registry 75 bài học để giữ cả bài có 0 mẫu pass; không dereference `source_file`.

## 4. Các plan nhỏ


| Plan | Tên                                                                                                                                          | Trạng thái                 | Mục tiêu                                                                                                                                                                                     | Phụ thuộc                                                                            |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| 01   | [Đọc paper về cách đánh giá chất lượng benchmark](plans/01-benchmark-quality-literature-review.md)                                  | HOÀN THÀNH | Rút ra tiêu chí/logic đánh giá benchmark từ 3 paper tutor và V-Legal; tạo checklist kiểm định v0 cho dữ liệu HNMU.                                                               | Không phụ thuộc dữ liệu HNMU, nhưng output dùng trực tiếp cho Plan 04.        |
| 02   | [Quy ước layout dữ liệu dùng chung và code dùng chung](plans/02-shared-data-and-code-layout.md)                                        | HOÀN THÀNH                   | Chốt nơi đặt raw data, học liệu SGK/SGV, code và output experiment; tạo manifest cho batch HNMU đã nhận.                                                                            | Đã hoàn thành; Plan 03/04/06 dùng lại layout này.                              |
| 03   | [Chuẩn hóa học liệu SGK/SGV và thiết kế hệ thống học liệu](plans/03-learning-resource-normalization-and-retrieval-system.md)       | HOÀN THÀNH V0 CHO LỚP 6–9             | Đã dùng OCR Markdown của Nguyên cho SGK/SGV Tin học 6–9, đồng bộ topic/lesson/position registry, tạo 154 OCR units, 2.750 fragment và SQLite FTS index; các artifact OCR/MinerU cũ được đánh dấu là thử nghiệm.         | Học liệu vẫn ở trạng thái `draft`, chưa thay thế xác nhận chuyên môn của HNMU/UET. Report sync: `reports/learning-resource-registries-sync-20260718.md`.                  |
| 04   | [Tiếp nhận, kiểm tra độ phủ, nhất quán và trùng lặp hội thoại HNMU](plans/04-hnmu-dialogue-intake-coverage-consistency-dedup.md) | HOÀN THÀNH V0 CHO LỚP 6–7; FOLLOW-UP LỚP 8–9                        | Đã kiểm toán cơ học/truy xuất sơ bộ lớp 6–7: 462 dòng. Lượt follow-up lớp 8–9: 588 dòng, 1 cặp trùng chính xác, 3 mẫu vào review queue cơ học sau regex-only lesson mapping, 3-shard agent checklist đủ 18 tiêu chí/mẫu. File chính cấp mẫu sau agent audit của cả hai batch là `agent_shard_audit/merged/quality_check_suggestions.csv` với schema canonical.                                                        | Dùng checklist Plan 01, layout Plan 02, retrieval học liệu Plan 03 và specialist Plan 07. Output lớp 8–9 nằm riêng tại `outputs/hnmu_dialogue_audit_grade8_9/`.                           |
| 07   | [Tạo specialist agent kiểm toán dữ liệu thô HNMU](plans/07-hnmu-dialogue-auditor-specialist.md) | APPROVED — ĐÃ TRIỂN KHAI V0 | Tạo specialist `hnmu-dialogue-auditor` để kiểm ngữ nghĩa/sư phạm từng mẫu thô bằng checklist, học liệu SGK/SGV và phương pháp dàn giáo; output là checklist chi tiết và gợi ý review. | Mở rộng trực tiếp phần agent của Plan 04; dùng checklist Plan 01 và học liệu Plan 03. |
| 08   | [Đóng gói kết quả kiểm toán hội thoại HNMU cho giáo viên](plans/08-hnmu-dialogue-audit-teacher-bundle.md) | APPROVED — ĐÃ TRIỂN KHAI, CHỜ DUYỆT BUNDLE LOCAL | Đã tạo và validate bốn workbook lớp 6–9 có cùng cấu trúc từ đúng 15 output canonical, giữ truy vết `source_file` và loại mọi artifact debug khỏi bundle. | Chờ người dùng duyệt trước mọi thao tác Git hoặc upload; không chạy lại experiment hoặc specialist audit. |
| 08b  | [Đóng gói lại Phase 1 theo loại deliverable và theo lớp](plans/08b-hnmu-dialogue-audit-teacher-bundle-v2.md) | APPROVED — ĐÃ TÁCH REPORT HNMU VÀ BẢNG KỸ THUẬT DỄ KIỂM TRA, CHỜ DUYỆT LOCAL | Root có report Markdown trả lời một câu hỏi và workbook kỹ thuật sáu sheet; sheet mở đầu có 8 kết quả dễ đọc, sheet cuối giữ nguyên 396 × 29 ô kỹ thuật. | Dùng checklist repaired/regex-repaired, registry 75 bài học; 1.050 mẫu × 18 tiêu chí, nguồn canonical và bundle v1 không thay đổi. |
| 06   | [Chuyển hội thoại thô HNMU thành mẫu benchmark hoàn chỉnh](plans/06-raw-dialogue-to-benchmark-sample-conversion.md)                   | DRAFT                        | Ánh xạ dữ liệu thô đã qua audit sang phiếu tác giả/mẫu benchmark, tách `student_prompt`, `conversation_history`, `gold_response`, `Đáp án`, gán task/rubric và giữ truy vết. | Cần Plan 04; cần task/rubric v0 từ experiment trước; cần học liệu registry v0. |
| 05   | [Đánh giá khả năng áp dụng và phân biệt của benchmark](plans/05-benchmark-usability-and-discriminative-evaluation.md)              | DRAFT                        | Sau khi có mẫu benchmark hoàn chỉnh, kiểm tra benchmark có phân biệt tutor tốt/trung bình/kém không.                                                                               | Cần Plan 06; cần tập mẫu đã được UET/HNMU xác nhận.                         |

## 5. Vai trò của từng lớp công việc

### 5.1. Lớp nghiên cứu

Plan 01 tạo nền lý luận cho việc đánh giá benchmark. Output của plan này sẽ giúp ta không chỉ nói “benchmark có vẻ tốt”, mà có tiêu chí rõ ràng hơn về:

- độ phủ;
- độ chính xác/tính nhất quán;
- độ đa dạng;
- độ khó;
- độ tin cậy chấm điểm;
- khả năng phân biệt năng lực model/tutor.

Output quan trọng cần bổ sung là checklist kiểm định v0 để Plan 04 dùng cho batch HNMU thật. Checklist này cần phân biệt rõ phần code kiểm được, phần agent gợi ý, và phần HNMU/UET phải xác nhận.

### 5.2. Lớp tổ chức dữ liệu và code

Plan 02 tránh việc dữ liệu/code bị lẫn vào experiment. Đây là bước nhỏ nhưng quan trọng, vì dữ liệu HNMU, ảnh SGK/SGV và code audit/chuyển đổi sẽ được dùng lại nhiều lần ở nhiều experiment. Plan này đã hoàn thành ngày 15/07/2026: raw data HNMU có README/manifest, `shared/learning_resources/` có khung thư mục cho Plan 03, và `src/edu_benchmark/` có package khung cho code dùng chung.

### 5.3. Lớp học liệu

Plan 03 tạo thước đo để biết dữ liệu HNMU đã phủ đủ SGK/SGV Tin học THCS hay chưa. Tính đến 18/07/2026, bản dùng được ngay đã mở rộng đến lớp 6–9 ở mức source/file registry, topic/lesson map, lesson-position registry, OCR manifest, fragment và SQLite FTS index truy xuất. SGK dùng để kiểm câu hỏi, chủ đề, bài học và vị trí học liệu; SGV dùng để kiểm đáp án chuẩn và căn cứ giải thích. Về dài hạn, đây cũng là nền cho hệ thống học liệu dạng database/retrieval để model có thể truy vấn khi được đánh giá.

Sau probe OCR ngày 15/07/2026, hướng học liệu đã xử lý không phải là text thuần. Flow được chốt là: ảnh trang → PaddleOCR lấy vùng chữ/bbox → VietOCR GPU nhận dạng tiếng Việt → tái dựng bố cục từ tọa độ → xuất Markdown có front matter, bảng và anchor → build index truy xuất. Bước tái dựng bố cục là bắt buộc để giữ nghĩa của mục lục, bảng và các khung nội dung.

Về code/env, Pha 3–5 sẽ dùng code chung trong `src/edu_benchmark/learning_resources/`, không đặt logic xử lý trong experiment. `benchmark_env` chạy điều phối, tái dựng bố cục, xuất Markdown, fragment, index và validation. Riêng VietOCR GPU recognition chạy bằng `/home/quannda/miniconda3/envs/ocr_vietocr_gpu/bin/python`, rồi trả output trung gian cho các bước tiếp theo trong `benchmark_env`.

### 5.4. Lớp dữ liệu hội thoại HNMU

Plan 04 đã có audit v0 cho dữ liệu lớp 6 và lớp 7, và có lượt follow-up riêng cho lớp 8 và lớp 9. Plan này không quyết định benchmark cuối cùng, mà kiểm tra dữ liệu thô đã đủ tin cậy để chuyển đổi thử chưa. Ngoài độ phủ/trùng lặp, Plan 04 có checklist chi tiết theo tiêu chí, `confidence_score`, file chính cấp mẫu `agent_shard_audit/merged/quality_check_suggestions.csv` và hàng đợi gửi HNMU kiểm lại. Lớp 8–9 đã xử lý nhóm `Không rõ chủ đề` bằng regex-only lesson mapping; nhãn gợi ý tổng hợp đã được chuẩn hóa về `pass`, `need_human_review`, `failed` trước khi dùng cho Plan 06.

### 5.5. Lớp chuyển đổi thành mẫu benchmark

Plan 06 lấp khoảng trống giữa dữ liệu thô và benchmark hoàn chỉnh. Plan này ánh xạ cột HNMU sang phiếu tác giả, tách hội thoại theo đúng quy ước `student_prompt` → `conversation_history` → `gold_response`, giữ riêng `Đáp án`, gán task/rubric và giữ truy vết tới file gốc, dòng gốc, học liệu và quyết định kiểm toán.

### 5.6. Lớp đánh giá benchmark sau chuyển đổi

Plan 05 kiểm tra tiêu chí thứ ba mà giáo sư nêu: benchmark có khả năng phân biệt tutor tốt, trung bình và kém không. Đây là việc sau, không làm trước khi có mẫu benchmark hoàn chỉnh.

## 6. Cổng quyết định

### Cổng A — trước khi code kiểm toán dữ liệu HNMU

- Plan 01 đã có checklist kiểm định v0.
- Plan 02 đã chốt nơi đặt raw data, học liệu và code.
- Đã nhận ít nhất một batch dữ liệu HNMU thật.
- Checklist kiểm định v0 đã phân rõ phần code kiểm, phần agent kiểm, phần cần HNMU/UET xác nhận.

### Cổng B — trước khi đánh giá độ phủ theo SGK/SGV THCS

- Có danh mục học liệu SGK Tin học THCS v0.
- Có kế hoạch đưa SGV vào hệ học liệu; nếu chưa crawl/OCR SGV thì các kiểm tra đáp án phải gắn cờ `needs_sgv_verification`.
- Biết rõ danh mục nào chắc chắn, danh mục nào cần HNMU xác nhận.
- Không dùng OCR chưa kiểm tra làm nguồn chân lý.

### Cổng C — trước khi chuyển đổi hàng loạt hội thoại thành benchmark

- Dữ liệu thô qua kiểm tra thiếu trường, nhất quán và trùng/gần trùng.
- Có báo cáo vùng thiếu/lệch để phản hồi HNMU.
- Có `hnmu_review_queue.csv` hoặc báo cáo tương đương cho các mẫu cần HNMU kiểm lại.
- Có quyết định rõ mẫu nào dùng cho chuyển đổi thử.

### Cổng D — trước khi báo cáo benchmark tốt/xấu

- Có mẫu benchmark hoàn chỉnh.
- Có truy vết từ mẫu benchmark về hội thoại gốc, học liệu và kết quả kiểm toán.
- Có task/rubric ổn định.
- Có thử nghiệm cho thấy benchmark phân biệt được tutor tốt, trung bình, kém.

## 7. Phạm vi chưa làm

- Đã nhận batch dữ liệu HNMU trong `shared/raw_data/HNMU-teacher_dialog_samples/` và đã có manifest chính thức cho lớp 6–9. Đã kiểm toán v0 lớp 6–7; lượt follow-up lớp 8–9 đã chạy và lưu riêng tại `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/`.
- Đã copy ảnh SGK đã crawl từ experiment `20260705_215045` sang `shared/learning_resources/raw_page_images/sgk/` và đăng ký trong manifest.
- Đã crawl ảnh SGV tương ứng với SGK Tin học THCS từ các URL đã cung cấp, đăng ký trong manifest, tạo PDF dẫn xuất, tạo danh mục học liệu v0, chạy probe OCR, chốt hướng Markdown-first. Đã dùng OCR Markdown của Nguyên để tạo và đồng bộ manifest/topic map/position registry/fragment/index truy xuất cho SGK/SGV Tin học 6–9.
- Đã tạo package `src/edu_benchmark/`; đã có logic đọc XLSX, audit dialogue v0 và retrieval học liệu lớp 6–9. Logic chuyển đổi benchmark vẫn thuộc Plan 06.
- Không chạy OCR hàng loạt mới trong Plan 04; Plan 03 v0 hiện dùng OCR Markdown lớp 6–9 do Nguyên cung cấp.
- README/ARCHITECTURE đã được cập nhật cho layout Plan 02.
- Plan 04 đã được đánh dấu `APPROVED` và hoàn thành audit v0 cho lớp 6–7. Các plan 05/06 vẫn cần duyệt trước khi triển khai.


## Cập nhật Plan 04 ngày 19/07/2026

- Dữ liệu lớp 8–9 đã được rerun kiểm cơ học bằng mapping bài học regex-only, không còn dòng `Không rõ chủ đề` trong coverage.
- Đã repair checklist specialist cho 154 mẫu từng bị ảnh hưởng bởi lỗi mapping A/B, với 4 tiêu chí `RAW-CON-01`, `RAW-CON-02`, `RAW-CON-06`, `RAW-CON-07`.
- Bản checklist specialist nên dùng hiện tại: `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv`.
