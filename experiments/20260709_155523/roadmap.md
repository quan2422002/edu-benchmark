# Roadmap — đánh giá chất lượng benchmark, học liệu SGK/SGV và dữ liệu HNMU

Experiment: `20260709_155523`
Ngày tạo: 09/07/2026
Ngày cập nhật: 15/07/2026
Trạng thái: `DRAFT` — Plan 01 và Plan 02 đã hoàn thành; các plan còn lại cần duyệt trước khi cài đặt.

## 1. Mục tiêu cập nhật

Experiment này tập trung vào việc chuẩn bị nền tảng để đánh giá **chất lượng của chính bộ benchmark** trước khi dùng benchmark để đánh giá model gia sư AI.

Sau trao đổi ngày 10/07/2026 và cập nhật ngày 14/07/2026, mục tiêu không chỉ là chuyển hội thoại thô HNMU thành mẫu benchmark. Ta cần trả lời trước các câu hỏi:

1. Benchmark có được thiết kế dựa trên bằng chứng nghiên cứu đủ chắc không?
2. Dữ liệu thô HNMU có đủ phủ, nhất quán và ít trùng lặp không?
3. Học liệu SGK/SGV Tin học THCS có được chuẩn hóa đủ tốt để làm thước đo độ phủ, kiểm đáp án và sau này làm nguồn truy vấn cho model không?
4. Sau khi chuyển đổi thành benchmark hoàn chỉnh, benchmark có khả năng phân biệt gia sư tốt, trung bình và kém không?

Tình hình mới:

- HNMU đã gửi batch dữ liệu thô ban đầu tại `shared/raw_data/HNMU-teacher_dialog_samples/`, hiện có `Lớp 6.xlsx` và `Lớp 7.xlsx`.
- Kiểm tra nhẹ bằng thư viện chuẩn Python cho thấy có khoảng 461 dòng dữ liệu có hội thoại: 237 dòng ở lớp 6 và 224 dòng ở lớp 7. Đây mới là con số ước tính để định hướng plan, chưa phải báo cáo kiểm toán chính thức.
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

Điểm quan trọng: dữ liệu thô HNMU đã có batch ban đầu nhưng chưa đầy đủ toàn bộ khối lớp. Vì vậy, không nên vội chuyển đổi hàng loạt. Plan 01 đã hoàn thành checklist kiểm định chất lượng benchmark/dữ liệu. Plan 02 đã chốt layout `shared/`, `src/` và manifest raw data HNMU, tạo nền an toàn để Plan 03 chuẩn hóa học liệu mà không chồng lấn.

## 4. Các plan nhỏ


| Plan | Tên                                                                                                                                          | Trạng thái                 | Mục tiêu                                                                                                                                                                                     | Phụ thuộc                                                                            |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| 01   | [Đọc paper về cách đánh giá chất lượng benchmark](plans/01-benchmark-quality-literature-review.md)                                  | HOÀN THÀNH | Rút ra tiêu chí/logic đánh giá benchmark từ 3 paper tutor và V-Legal; tạo checklist kiểm định v0 cho dữ liệu HNMU.                                                               | Không phụ thuộc dữ liệu HNMU, nhưng output dùng trực tiếp cho Plan 04.        |
| 02   | [Quy ước layout dữ liệu dùng chung và code dùng chung](plans/02-shared-data-and-code-layout.md)                                        | HOÀN THÀNH                   | Chốt nơi đặt raw data, học liệu SGK/SGV, code và output experiment; tạo manifest cho batch HNMU đã nhận.                                                                            | Đã hoàn thành; Plan 03/04/06 dùng lại layout này.                              |
| 03   | [Chuẩn hóa học liệu SGK/SGV và thiết kế hệ thống học liệu](plans/03-learning-resource-normalization-and-retrieval-system.md)       | PHA 2 HOÀN THÀNH             | Đã có ảnh/PDF SGK/SGV và danh mục học liệu v0 cho topic/lesson/position. OCR, fragment và retrieval vẫn cần duyệt riêng.         | Cần duyệt tiếp Pha 3 nếu muốn OCR mục lục/trang trọng điểm.                  |
| 04   | [Tiếp nhận, kiểm tra độ phủ, nhất quán và trùng lặp hội thoại HNMU](plans/04-hnmu-dialogue-intake-coverage-consistency-dedup.md) | DRAFT                        | Kiểm toán batch HNMU theo độ phủ, thiếu trường, nhất quán, trùng/gần trùng, checklist chất lượng và `confidence_score`.                                                        | Cần Plan 01; cần Plan 02; nên có output v0 của Plan 03.                           |
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

Plan 03 tạo thước đo để biết dữ liệu HNMU đã phủ đủ SGK/SGV Tin học THCS hay chưa. SGK dùng để kiểm câu hỏi, chủ đề, bài học và vị trí học liệu; SGV dùng để kiểm đáp án chuẩn và căn cứ giải thích. Về dài hạn, đây cũng là nền cho hệ thống học liệu dạng database/retrieval để model có thể truy vấn khi được đánh giá.

### 5.4. Lớp dữ liệu hội thoại HNMU

Plan 04 hiện đã có điều kiện đầu vào ban đầu vì HNMU đã gửi dữ liệu lớp 6 và lớp 7. Plan này không quyết định benchmark cuối cùng, mà kiểm tra dữ liệu thô đã đủ tin cậy để chuyển đổi thử chưa. Ngoài độ phủ/trùng lặp, Plan 04 phải có checklist chất lượng từng mẫu, `confidence_score` và hàng đợi gửi HNMU kiểm lại.

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

- Đã nhận batch dữ liệu HNMU ban đầu trong `shared/raw_data/HNMU-teacher_dialog_samples/` và đã có manifest chính thức; chưa kiểm toán nội dung.
- Đã copy ảnh SGK đã crawl từ experiment `20260705_215045` sang `shared/learning_resources/raw_page_images/sgk/` và đăng ký trong manifest.
- Đã crawl ảnh SGV tương ứng với SGK Tin học THCS từ các URL đã cung cấp, đăng ký trong manifest, tạo PDF dẫn xuất và tạo danh mục học liệu v0; chưa OCR toàn văn/fragment.
- Đã tạo khung package `src/edu_benchmark/`; chưa viết logic xử lý/audit/chuyển đổi.
- Chưa chạy OCR/chuẩn hóa mới trên ảnh SGK/SGV.
- README/ARCHITECTURE đã được cập nhật cho layout Plan 02.
- Chưa đánh dấu các plan mới ngoài Plan 01 và Plan 02 là `APPROVED`.
