# Plan 08 — OCR ảnh SGK Tin học và tạo đoạn học liệu v0

Trạng thái: `DRAFT` — chỉ là plan, chưa được duyệt để chạy OCR toàn bộ  
Experiment: `20260705_215045`  
Owner chính: `learning-resource-curator`  
Input chính: ảnh PNG SGK Tin học 6–9 đã crawl từ P02  
Có thể chạy độc lập: Có, sau khi P02 đã có `raw_page_images_manifest.csv`

## 1. Mục tiêu

Chuyển ảnh PNG SGK Tin học THCS đã crawl thành văn bản có thể đọc, tra cứu và tách thành các đoạn học liệu v0. Output của plan này sẽ giúp các plan sau có thể gắn câu hỏi, task, rubric và mẫu hội thoại với học liệu cụ thể thay vì chỉ trỏ chung vào cả cuốn sách.

Ưu tiên triển khai:

1. OCR thử nghiệm trên một tập trang nhỏ của SGK Tin học 9.
2. Chọn cách OCR đủ ổn cho tiếng Việt, bảng, mã Python và bố cục SGK.
3. OCR toàn bộ SGK Tin học 9 trước.
4. Sau khi cách làm ổn định, mở rộng sang SGK Tin học 6–8 để phục vụ tiền kiến thức.

Plan này không chốt kiến thức sư phạm, không thiết kế task/rubric, không triển khai database production, và không thay thế xác nhận chuyên môn từ HNMU.

## 2. Vì sao cần làm kỹ?

OCR học liệu SGK không chỉ là “nhận chữ từ ảnh”. Nếu làm vội, dữ liệu đầu ra có thể gây lỗi dây chuyền cho benchmark:

- Sai dấu tiếng Việt hoặc mất chữ làm tutor trả lời sai kiến thức.
- Nhận diện sai mã Python làm hỏng các mẫu liên quan đến lập trình.
- Bỏ sót tiêu đề bài/mục khiến mã đoạn học liệu không truy xuất được.
- Đọc sai bảng, chú thích hình hoặc bài tập làm mất ngữ cảnh.
- Không ghi rõ trang và nguồn khiến giáo viên khó kiểm tra lại.

Vì vậy, plan này ưu tiên pipeline có thể kiểm chứng: mỗi trang OCR phải trỏ về ảnh gốc, mỗi đoạn học liệu phải trỏ về trang/mục cụ thể, và mọi điểm chưa chắc phải có trạng thái chờ UET/HNMU rà soát.

## 3. Phạm vi input

Input đã có từ P02:

| Artifact | Vai trò |
|---|---|
| `source_scope/raw_page_images/` | Ảnh PNG thô của SGK Tin học 6–9. Ảnh thô đã được `.gitignore` để tránh commit dữ liệu nặng. |
| `source_scope/raw_page_images_manifest.csv` | Manifest từng ảnh, gồm mã học liệu, URL nguồn, đường dẫn local, dung lượng, sha256, trạng thái tải. |
| `source_scope/raw_page_images_crawl_report.md` | Báo cáo crawl: 356 ảnh, 0 lỗi tải, tổng dung lượng khoảng 225.54 MB. |
| `source_scope/sgk_sgv_source_registry.csv` | Registry nguồn SGK/SGV v0, dùng để tra mã học liệu. |

Nguồn ưu tiên OCR trước:

```text
LM-SGK-TIN9-4700233123 — SGK Tin học 9 — 94 trang ảnh
```

Sau khi Tin học 9 ổn định, mở rộng:

```text
LM-SGK-TIN6-4699918592 — SGK Tin học 6 — 78 trang ảnh
LM-SGK-TIN7-4700056620 — SGK Tin học 7 — 86 trang ảnh
LM-SGK-TIN8-4700157933 — SGK Tin học 8 — 98 trang ảnh
```

## 4. Phạm vi output và lý do tạo từng thư mục/file

Plan này chỉ được ghi vào các vùng sau:

```text
experiments/20260705_215045/ocr_outputs/
experiments/20260705_215045/learning_resource_fragments/
experiments/20260705_215045/reports/P08-*.md
experiments/20260705_215045/handoffs/P08-*.md
```

Không sửa trực tiếp artifact P02 đã có, trừ khi có migration plan riêng.

| File/thư mục | Vai trò |
|---|---|
| `ocr_outputs/README.md` | Giải thích cấu trúc output OCR, cách đọc kết quả, engine đã dùng, và giới hạn bản quyền/dữ liệu thô. |
| `ocr_outputs/engine_trials/sample_page_selection.csv` | Danh sách trang pilot đại diện: trang nhiều chữ, trang có bảng, trang có mã Python, trang có bài tập, trang có hình/chú thích. Tạo file này để việc chọn mẫu thử không cảm tính. |
| `ocr_outputs/engine_trials/ocr_engine_trial_report.md` | So sánh kết quả thử giữa các engine OCR khả dụng. Tạo file này để chốt engine dựa trên bằng chứng thay vì đoán. |
| `ocr_outputs/engine_trials/sample_outputs/` | Kết quả OCR thô của các trang pilot. Tạo thư mục này để kiểm tra thủ công trước khi chạy toàn bộ. |
| `ocr_outputs/tin9_raw_ocr/` | OCR thô toàn bộ SGK Tin học 9, giữ gần nguyên output engine. Tạo thư mục này để có bản truy vết và tái xử lý được. |
| `ocr_outputs/tin9_clean_text/` | Văn bản Tin học 9 đã hậu xử lý nhẹ: chuẩn hóa khoảng trắng, nối dòng hợp lý, giữ tiêu đề/trang. Tạo thư mục này để đọc và chia đoạn dễ hơn. |
| `ocr_outputs/ocr_quality_review.csv` | Bảng rà soát chất lượng OCR theo trang: tiếng Việt, mã Python, bảng, tiêu đề, bài tập, lỗi cần sửa. Tạo file này để biết trang nào đáng tin, trang nào cần người kiểm tra. |
| `learning_resource_fragments/learning_resource_fragments_v0.csv` | Bảng đoạn học liệu v0: fragment ID, mã học liệu, trang bắt đầu/kết thúc, nhãn mục, thứ tự, ghi chú vị trí, trạng thái. Tạo file này để benchmark có thể trỏ đến đoạn học liệu cụ thể. |
| `learning_resource_fragments/fragment_examples_tin9.md` | Một số ví dụ đoạn học liệu Tin học 9 đã tách. Tạo file này để UET/HNMU kiểm tra style chia đoạn trước khi mở rộng. |
| `reports/P08-ocr-open-questions.md` | Câu hỏi cần UET/HNMU quyết định: mức chấp nhận lỗi OCR, cách xử lý bảng/hình, cách chia fragment. |
| `reports/P08-ocr-completion-report.md` | Báo cáo cuối plan: số trang xử lý, engine, thời gian, lỗi còn lại, khuyến nghị bước tiếp. |
| `handoffs/P08-*.md` | Handoff theo từng mốc để plan sau biết artifact nào đã sẵn sàng dùng. |

## 5. Quy trình thực hiện tuần tự

### Bước 0 — Kiểm tra điều kiện chạy và không gian lưu trữ

Mục tiêu: xác nhận máy hiện tại có đủ điều kiện chạy OCR và không ghi nhầm vào môi trường Python khác.

Việc cần làm:

- Kiểm tra Python executable là `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.
- Kiểm tra GPU bằng `nvidia-smi` nếu có.
- Kiểm tra package OCR đã có trong `benchmark_env`; nếu thiếu, phải xin phép trước khi cài.
- Kiểm tra dung lượng trống vì OCR có thể tạo thêm nhiều file text/json.
- Không commit ảnh PNG thô; chỉ commit manifest, text output nếu được phép, và báo cáo.

Output:

- Ghi kết quả vào `ocr_outputs/README.md`.
- Nếu thiếu package quan trọng, dừng ở đây và đề xuất lựa chọn engine/cài đặt.

### Bước 1 — Chọn tập trang pilot của SGK Tin học 9

Mục tiêu: chọn một tập nhỏ nhưng đại diện để đánh giá OCR trước khi chạy toàn bộ.

Nguyên tắc chọn khoảng 10–15 trang:

- Trang mục lục hoặc đầu bài để kiểm tra tiêu đề/mục.
- Trang nhiều chữ liên tục để kiểm tra tiếng Việt.
- Trang có bảng để kiểm tra cấu trúc.
- Trang có mã Python để kiểm tra ký tự đặc biệt, thụt dòng, dấu ngoặc.
- Trang có bài tập/câu hỏi để kiểm tra số thứ tự và lệnh hỏi.
- Trang có hình/chú thích để kiểm tra vùng text quanh hình.

Output:

- `ocr_outputs/engine_trials/sample_page_selection.csv`

### Bước 2 — Thử engine OCR trên tập pilot

Mục tiêu: chọn engine OCR thực dụng nhất cho SGK Tin học.

Ứng viên ban đầu:

| Engine | Dùng GPU? | Lý do cân nhắc |
|---|---:|---|
| PaddleOCR | Có thể dùng GPU | Thường mạnh với OCR đa ngôn ngữ và layout ảnh; đáng thử trước nếu cài đặt không quá nặng. |
| EasyOCR | Có thể dùng GPU | Dễ chạy thử, hỗ trợ tiếng Việt, phù hợp làm baseline nhanh. |
| Tesseract | Chủ yếu CPU | Baseline nhẹ, nhưng có thể yếu hơn với layout SGK và không tận dụng GPU. |

Quy tắc:

- Không cài thêm package khi chưa có xác nhận.
- Nếu đã có engine trong môi trường, chạy thử ngay.
- Nếu chưa có engine phù hợp, tạo đề xuất cài đặt riêng kèm rủi ro dung lượng/thời gian.

Output:

- `ocr_outputs/engine_trials/sample_outputs/`
- `ocr_outputs/engine_trials/ocr_engine_trial_report.md`

### Bước 3 — Đánh giá chất lượng OCR pilot và chốt hướng chạy

Mục tiêu: không chạy toàn bộ nếu kết quả pilot chưa đủ dùng.

Tiêu chí đánh giá tối thiểu:

| Nhóm kiểm tra | Câu hỏi đánh giá |
|---|---|
| Tiếng Việt | Có mất dấu, nhầm ký tự, đứt câu nghiêm trọng không? |
| Tiêu đề/mục | Có nhận được bài, mục, tiểu mục đủ để chia đoạn không? |
| Mã Python | Có giữ được thụt dòng, dấu ngoặc, dấu nháy, toán tử không? |
| Bảng | Có đọc được nội dung chính của bảng không, dù chưa hoàn hảo layout? |
| Bài tập | Có giữ được số thứ tự, câu hỏi, lựa chọn nếu có không? |
| Truy vết | Mỗi output có trỏ được về ảnh gốc và trang không? |

Ngưỡng chấp nhận v0:

- Dùng được cho đọc hiểu nội dung chính.
- Các trang có mã Python/bảng được đánh dấu cần rà soát nếu lỗi nặng.
- Không yêu cầu layout hoàn hảo ở v0, nhưng không được mất thông tin cốt lõi.

Output:

- `ocr_outputs/ocr_quality_review.csv`
- Quyết định trong `ocr_outputs/engine_trials/ocr_engine_trial_report.md`: chạy toàn bộ, đổi engine, hoặc dừng để xử lý cài đặt.

### Bước 4 — OCR toàn bộ SGK Tin học 9

Mục tiêu: tạo bản OCR thô đầy đủ cho học liệu trọng tâm lớp 9.

Việc cần làm:

- Chạy OCR trên 94 trang Tin học 9.
- Ghi output theo từng trang, không gộp mất ranh giới trang.
- Mỗi file output phải có mã học liệu và số trang trong tên hoặc metadata.
- Ghi log thời gian, lỗi, trang phải chạy lại.

Output:

- `ocr_outputs/tin9_raw_ocr/`
- Cập nhật `ocr_outputs/ocr_quality_review.csv`

Ước lượng:

- Nếu tận dụng được GPU: khoảng 10–30 phút cho OCR thô Tin học 9.
- Nếu chỉ dùng CPU: khoảng 30–90 phút.
- Chưa tính hậu xử lý và rà soát thủ công.

### Bước 5 — Hậu xử lý nhẹ văn bản Tin học 9

Mục tiêu: biến OCR thô thành text dễ đọc hơn nhưng vẫn giữ truy vết trang.

Việc cần làm:

- Chuẩn hóa khoảng trắng, dòng trống, lỗi xuống dòng rõ ràng.
- Giữ tiêu đề bài/mục nếu nhận diện được.
- Không tự sửa nội dung chuyên môn nếu không chắc.
- Đánh dấu vùng nghi ngờ, đặc biệt là mã Python, bảng và công thức/ký hiệu.

Output:

- `ocr_outputs/tin9_clean_text/`
- Cập nhật `ocr_outputs/ocr_quality_review.csv`

Ước lượng:

- Tự động hậu xử lý: 10–30 phút.
- Rà soát thủ công nhanh: vài giờ tùy tiêu chuẩn chất lượng.

### Bước 6 — Tạo đoạn học liệu v0 cho Tin học 9

Mục tiêu: chia văn bản đã OCR thành các đoạn có thể truy xuất trong benchmark.

Nguyên tắc chia đoạn v0:

- Ưu tiên theo bài, mục, tiểu mục, bài tập hoặc khối mã rõ ràng.
- Không nhồi quá nhiều thông tin vào ID.
- Ghi trang, nhãn mục, thứ tự và ghi chú vị trí trong bảng mapping.
- Nếu ranh giới mục không chắc, để trạng thái `needs_uet_review`.
- Nếu cần xác nhận chuyên môn về cách chia, để trạng thái `needs_hnmu_review`.

Output:

- `learning_resource_fragments/learning_resource_fragments_v0.csv`
- `learning_resource_fragments/fragment_examples_tin9.md`

### Bước 7 — Rà soát mẫu với UET/HNMU trước khi mở rộng

Mục tiêu: kiểm tra cách OCR và chia đoạn có đủ dễ dùng cho giáo viên và benchmark không.

Việc cần làm:

- Chọn 10–20 đoạn học liệu đại diện.
- Gửi/ghi báo cáo cho UET/HNMU xem:
  - văn bản OCR có đọc được không;
  - đoạn chia có quá ngắn/quá dài không;
  - mã học liệu có dễ trỏ tới không;
  - trang/mục có đủ để giáo viên kiểm chứng không.

Output:

- `reports/P08-ocr-open-questions.md`
- Cập nhật `learning_resource_fragments/fragment_examples_tin9.md`

### Bước 8 — Mở rộng OCR sang Tin học 6–8 nếu Tin học 9 đạt yêu cầu

Mục tiêu: tạo nền tiền kiến thức lớp 6–8 sau khi pipeline đã ổn.

Điều kiện để chạy:

- Tin học 9 OCR thô không có lỗi hệ thống nghiêm trọng.
- Cách đặt output và fragment ID đã được UET chấp nhận ở mức v0.
- Không có yêu cầu ưu tiên khác gấp hơn từ P04/P05.

Output:

- `ocr_outputs/tin6_raw_ocr/`, `ocr_outputs/tin7_raw_ocr/`, `ocr_outputs/tin8_raw_ocr/`
- `ocr_outputs/tin6_clean_text/`, `ocr_outputs/tin7_clean_text/`, `ocr_outputs/tin8_clean_text/`
- Bổ sung vào `learning_resource_fragments/learning_resource_fragments_v0.csv`

Ước lượng:

- Nếu dùng GPU: khoảng 40–120 phút cho OCR thô toàn bộ SGK Tin 6–9.
- Nếu dùng CPU: khoảng 2–5 giờ.
- Hậu xử lý và chia đoạn có thể mất thêm 0.5–2 ngày tùy mức sạch mong muốn.

### Bước 9 — Validate, báo cáo và handoff

Mục tiêu: đóng plan ở trạng thái có thể tiêu thụ bởi P04/P05/P06.

Việc cần làm:

- Kiểm tra số trang OCR khớp manifest.
- Kiểm tra mỗi fragment trỏ về mã học liệu tồn tại.
- Kiểm tra mỗi fragment có ít nhất một locator: trang, nhãn mục hoặc ghi chú vị trí.
- Chạy validator học liệu nếu schema hiện có hỗ trợ.
- Chạy `pytest tests/agents -q`.
- Tạo báo cáo hoàn thành và handoff.

Output:

- `reports/P08-ocr-completion-report.md`
- `handoffs/P08-ocr-and-fragmentation-*.md`

## 6. Tận dụng phần cứng GPU 16GB

GPU khoảng 16GB là đủ tốt cho OCR v0 nếu engine hỗ trợ CUDA. Tuy nhiên, plan này không mặc định rằng mọi engine đều dùng được GPU.

Hướng kiểm tra:

1. Dùng `nvidia-smi` để xác nhận GPU và VRAM.
2. Dùng Python trong `benchmark_env` để kiểm tra package hiện có.
3. Chạy pilot nhỏ trước để đo tốc độ thực tế.
4. Chỉ sau khi pilot ổn mới chạy toàn bộ Tin học 9.

Quan điểm thực dụng:

- Nếu PaddleOCR hoặc EasyOCR chạy được với GPU và chất lượng ổn, ưu tiên dùng GPU.
- Nếu GPU setup mất quá nhiều thời gian, có thể dùng CPU cho Tin học 9 trước để không kẹt tiến độ.
- Không dành quá nhiều thời gian tối ưu tốc độ khi chất lượng OCR/chia đoạn mới là phần quyết định khả năng dùng cho benchmark.

## 7. Ước lượng thời gian

| Hạng mục | Ước lượng |
|---|---:|
| Kiểm tra môi trường/GPU/package | 15–30 phút |
| Chọn trang pilot | 15–30 phút |
| OCR pilot và so sánh engine | 1–2 giờ, nếu không cần cài thêm |
| OCR thô SGK Tin học 9 | 10–30 phút với GPU; 30–90 phút với CPU |
| Hậu xử lý nhẹ Tin học 9 | 10–30 phút tự động; vài giờ nếu rà soát thủ công |
| Tạo fragment v0 Tin học 9 | 2–4 giờ cho bản nháp kỹ thuật |
| OCR thô toàn bộ SGK Tin 6–9 | 40–120 phút với GPU; 2–5 giờ với CPU |
| Làm sạch và chia đoạn toàn bộ 6–9 | 0.5–2 ngày tùy mức kiểm tra |

Nếu chỉ cần bản OCR thô Tin học 9 để đọc nhanh, có thể xong trong ngày. Nếu cần bản đủ sạch để làm nền benchmark có truy vết, nên tính thêm thời gian hậu xử lý và rà soát.

## 8. Rủi ro và cách kiểm soát

| Rủi ro | Cách kiểm soát |
|---|---|
| OCR sai tiếng Việt | Pilot trước, ghi chất lượng theo trang, không dùng trang lỗi nặng làm nguồn chắc chắn. |
| OCR sai mã Python | Đánh dấu riêng trang/code block; cần rà soát thủ công hoặc hậu xử lý chuyên biệt. |
| Bảng/hình bị mất cấu trúc | Chấp nhận v0 là text chính; bảng/hình quan trọng để `needs_uet_review`. |
| Engine cần cài package nặng | Dừng để xin phép cài đặt; không tự ý cài ngoài `benchmark_env`. |
| Dữ liệu ảnh/text có vấn đề bản quyền | Không commit ảnh thô; chỉ dùng nội bộ cho nghiên cứu, hỏi lại trước khi public/share. |
| Fragment chia sai ý sư phạm | Đánh dấu `needs_hnmu_review`; không coi suy luận kỹ thuật là quyết định chuyên môn. |

## 9. Tiêu chí hoàn thành plan

Plan này được coi là hoàn thành ở mức v0 khi:

- Có báo cáo chọn engine OCR dựa trên pilot.
- Có OCR thô và text hậu xử lý cho SGK Tin học 9.
- Có bảng chất lượng OCR theo trang.
- Có fragment v0 cho Tin học 9, trỏ được về mã học liệu/trang/mục.
- Có câu hỏi mở cho UET/HNMU về trang hoặc fragment chưa chắc.
- Validator liên quan chạy pass hoặc lỗi được báo rõ.
- `pytest tests/agents -q` pass.
- Có handoff cho P04/P05/P06 tiêu thụ.

