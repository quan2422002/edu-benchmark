# Plan 04 — Tiếp nhận, kiểm tra độ phủ, nhất quán và trùng lặp hội thoại HNMU

Experiment: `20260709_155523`
Trạng thái: `DRAFT` — chưa triển khai code, chưa tự chạy kiểm toán chính thức trên dữ liệu thật.
Ngày lập: 09/07/2026
Ngày cập nhật: 14/07/2026
Người phụ trách dự kiến: Quân, Nguyên, Codex hỗ trợ kỹ thuật.

## 1. Bối cảnh

HNMU đã bắt đầu chuyển giao dữ liệu hội thoại thô. Batch ban đầu hiện nằm ở:

```text
shared/raw_data/HNMU-teacher_dialog_samples/
  Lớp 6.xlsx
  Lớp 7.xlsx
```

Kiểm tra nhẹ bằng thư viện chuẩn Python cho thấy khoảng 462 dòng có hội thoại. Đây chưa phải báo cáo kiểm toán chính thức.

Dữ liệu có dùng AI hỗ trợ tạo và được thầy cô rà soát. Vì vậy cần kiểm toán trước khi chuyển đổi thành mẫu benchmark.

Plan này chỉ nên triển khai sau khi:

- Plan 01 có checklist kiểm định v0;
- Plan 02 chốt cách quản lý raw data, manifest và code dùng chung;
- Plan 03 có ít nhất danh mục học liệu v0 để kiểm độ phủ, hoặc chấp nhận kiểm sơ bộ bằng cột `Bài` và `Vị trí` trong dữ liệu HNMU.

## 2. Mục tiêu

Kiểm tra dữ liệu hội thoại HNMU theo năm nhóm:

1. Độ phủ: khối lớp, chủ đề, bài học, mức nhận thức, dạng câu hỏi/bài tập, hành vi gia sư.
2. Thiếu trường và lỗi định dạng: cột bắt buộc, format hội thoại, dòng trống, giá trị bất thường.
3. Tính nhất quán: hội thoại có khớp với metadata đi kèm không.
4. Trùng/gần trùng: phát hiện mẫu lặp hoặc quá giống nhau.
5. Chất lượng từng mẫu: checklist + điểm tự tin (`confidence_score`) + hàng đợi gửi HNMU kiểm lại.

## 3. Nguyên tắc lưu trữ

- Raw data HNMU đặt ở `shared/raw_data/HNMU-teacher_dialog_samples/`.
- Code kiểm toán đặt ở `src/edu_benchmark/dialogue_audit/`.
- Code đọc dữ liệu đặt ở `src/edu_benchmark/data_io/`.
- Kết quả chạy của experiment này đặt ở `experiments/20260709_155523/outputs/hnmu_dialogue_audit/` và báo cáo đặt ở `experiments/20260709_155523/reports/`.
- Không đặt raw data hoặc code dùng chung trong `experiments/20260709_155523/`.
- Không sửa nội dung hội thoại gốc.

## 4. Output dự kiến và lý do tạo

### 4.1. `shared/raw_data/HNMU-teacher_dialog_samples/manifest.csv`

Vai trò: đăng ký file gốc HNMU gửi theo từng batch.
Lý do tạo: cần biết mỗi batch có bao nhiêu mẫu, nguồn nào, ngày nhận nào, trạng thái ra sao.

### 4.2. `src/edu_benchmark/dialogue_audit/`

Vai trò: chứa code kiểm toán dữ liệu hội thoại.
Lý do tạo: code này sẽ được dùng lại ở nhiều experiment, không nên để trong thư mục experiment.

### 4.3. `experiments/20260709_155523/reports/hnmu-dialogue-audit-batch-YYYYMMDD.md`

Vai trò: báo cáo kết quả kiểm toán batch dữ liệu.
Lý do tạo: báo cáo là output của experiment, có thể gửi Quân/giáo sư/HNMU đọc.

### 4.4. Các bảng kết quả chạy

Các bảng dự kiến:

- `outputs/hnmu_dialogue_audit/coverage_summary.csv`
- `outputs/hnmu_dialogue_audit/missing_field_report.csv`
- `outputs/hnmu_dialogue_audit/metadata_consistency_flags.csv`
- `outputs/hnmu_dialogue_audit/duplicate_candidates.csv`
- `outputs/hnmu_dialogue_audit/quality_check_results.csv`
- `outputs/hnmu_dialogue_audit/hnmu_review_queue.csv`

Trong đó `hnmu_review_queue.csv` là output rất quan trọng: danh sách mẫu cần gửi lại HNMU kiểm tra, kèm lý do, mức nghiêm trọng và điểm tự tin.

## 5. Quy trình thực hiện

1. Nhận batch dữ liệu HNMU và lưu nguyên bản vào `shared/raw_data/HNMU-teacher_dialog_samples/`.
2. Tạo manifest cho batch.
3. Đọc dữ liệu thành bảng trung gian, không sửa nội dung hội thoại.
4. Kiểm tra thiếu trường và lỗi định dạng bằng code.
5. Kiểm tra độ phủ dựa trên danh mục học liệu v0 nếu có; nếu chưa có, kiểm sơ bộ theo cột `Bài`, `Vị trí`, `Mức Bloom`.
6. Lọc trùng/gần trùng bằng code.
7. Agent kiểm nhất quán ngữ nghĩa theo checklist từ Plan 01.
8. Gán `quality_decision`, `confidence_score`, `failure_reasons`, `suggested_reviewer_action`.
9. Sinh báo cáo cho UET/HNMU.
10. Chốt batch nào đủ điều kiện chuyển sang Plan 06.

## 6. Phân vai giữa code, agent và con người

### 6.1. Code kiểm các phần cơ học

- Thiếu trường bắt buộc.
- Số dòng, số mẫu theo lớp/bài/mức Bloom.
- Hội thoại có chứa nhãn lượt nói như `HS:` và `AI:` hay không.
- Dòng trống hoặc nội dung quá ngắn.
- Trùng/gần trùng ở mức văn bản.
- Phân bố độ phủ theo các cột đã có.

### 6.2. Agent kiểm các phần ngữ nghĩa

- Câu hỏi có khớp với `Bài` và `Vị trí` không.
- `Đáp án (SGV)` có trả lời đúng câu hỏi không.
- Hội thoại có bám câu hỏi và đáp án không.
- `Mức Bloom` có hợp lý với yêu cầu của câu hỏi không.
- Hội thoại có thể hiện phương pháp giàn giáo không.
- Gia sư có lộ đáp án quá sớm không.
- Có lượt hội thoại thừa hoặc thiếu giá trị sư phạm không.
- Có tình huống agent không đủ chắc và cần HNMU xác nhận không.

Khi chưa có SGV crawl/OCR, các kiểm tra liên quan đến `Đáp án (SGV)` chỉ được coi là kiểm tra sơ bộ và cần gắn cờ `needs_sgv_verification`.

### 6.3. HNMU/UET quyết định

- Mẫu nào giữ.
- Mẫu nào cần HNMU sửa hoặc xác nhận.
- Mẫu nào loại khỏi batch hiện tại.
- Mẫu nào đủ điều kiện chuyển sang Plan 06.

## 7. Quy tắc điểm tự tin

Mỗi mẫu nên có các trường dẫn xuất:

```text
quality_decision: pass / fail / needs_human_review
confidence_score: 0.00–1.00
failure_reasons: danh sách lý do
suggested_reviewer_action: keep / ask_hnmu_review / exclude_from_current_batch
needs_sgv_verification: true / false
```

Nguyên tắc:

- `pass`: chỉ dùng khi dữ liệu đủ trường, không có lỗi rõ, agent tự tin cao và không cần xác nhận chuyên môn đặc biệt.
- `fail`: dùng khi có lỗi rõ ràng, ví dụ thiếu hội thoại, câu hỏi không khớp đáp án, hội thoại lệch hoàn toàn.
- `needs_human_review`: dùng khi có rủi ro ngữ nghĩa, độ tự tin thấp, hoặc cần HNMU xác nhận.

Ngưỡng cụ thể sẽ chốt khi triển khai code, nhưng bản plan đề xuất:

- `confidence_score >= 0.80`: có thể tin tương đối nếu không có cờ lỗi nghiêm trọng.
- `0.50 <= confidence_score < 0.80`: cần UET/HNMU xem lại nếu mẫu quan trọng.
- `< 0.50`: đưa vào hàng đợi HNMU kiểm lại.

## 8. Tiêu chí hoàn thành

Plan hoàn thành khi có:

1. Ít nhất một batch thật được đăng ký bằng manifest.
2. Code audit chạy được bằng `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.
3. Báo cáo độ phủ/thiếu trường/nhất quán/trùng lặp cho batch đầu tiên.
4. Bảng `quality_check_results.csv` có `quality_decision` và `confidence_score`.
5. Danh sách `hnmu_review_queue.csv` để gửi lại HNMU.
6. Handoff nêu rõ dữ liệu nào đủ điều kiện chuyển đổi thử sang Plan 06.

## 9. Ngoài phạm vi

- Không tạo benchmark samples hoàn chỉnh; việc đó thuộc Plan 06.
- Không chấm model.
- Không sửa nội dung hội thoại gốc.
- Không xây database học liệu production.
