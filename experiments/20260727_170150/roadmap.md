# Roadmap — Chấm yêu cầu sư phạm và xây benchmark đánh giá phản hồi gia sư

Experiment: `20260727_170150`  
Trạng thái: `ACTIVE_V4_CALIBRATION_AWAITING_USER_RUN`  
Nguồn kế thừa chính: `20260722_000940`

## 1. Lý do mở experiment mới

Experiment trước đã hoàn tất conversion, nền tảng đo lường, mô hình sáu
năng lực và grounding pool. Tuy nhiên, Workstream C đã thay đổi nhiều lần:
task loại trừ, nguyên tắc chính–phụ, tập nguyên tắc không thứ tự và
forward test v3. Các run này giúp phát hiện một vấn đề cốt lõi: context có
thể hỗ trợ nhiều chiến lược, còn chọn trực tiếp tập nhãn làm mất thông tin
về mức độ cần thiết.

Experiment mới khởi động ở ranh giới phương pháp rõ ràng:

- chấm cả sáu nguyên tắc trên thang thứ bậc 1–5;
- dùng một lượt grounding duy nhất cho mỗi candidate, trong đó model nhận
  đồng thời context, câu hỏi nguồn và `gold_answer`;
- chỉ gửi tám trường ngữ nghĩa; ID candidate/sample được code giữ để join,
  không gửi model;
- dùng `requirement_score >= 4` để tạo tập nguyên tắc bắt buộc;
- dùng API Vertex AI trực tiếp với system prompt tiếng Việt và schema cố
  định;
- dành model cho chấm ngữ nghĩa; mọi threshold, lọc tập, validation, join
  và metric xác định đều do code thực hiện;
- đặt code chạy tại `src/vertex_ai_call/`, system prompt tại
  `shared/prompts/benchmark_candidate_task_assigning/` và kết quả tại
  `experiments/20260727_170150/outputs/`;
- coi khả năng review của con người là ràng buộc: chỉ thêm file máy đọc
  khi runner thực sự dùng, mỗi run dùng một bundle phẳng và không nhân bản
  raw/normalized/report theo nhiều thư mục;
- đưa tập bắt buộc vào instruction của tutor trước khi áp rubric riêng;
- không dùng `gold_response` để chọn nguyên tắc.
- lưu đúng chuỗi user prompt ngay trong mỗi record kết quả, không tạo thêm
  bảng request riêng.

## 2. Nền tảng đã kế thừa

| Thành phần | Trạng thái kế thừa | Vai trò mới |
|---|---|---|
| 665 hội thoại thô `pass` → 2.028 candidate | Hoàn thành | Pool ứng viên và provenance |
| Quy tắc mỗi lượt AI tạo một candidate | Hoàn thành | Đơn vị benchmark |
| Grounding pool có `source_question`, `gold_answer`, không có `gold_response` | Hoàn thành | Active scoring input |
| Tổng quan bốn paper và nền tảng đo lường | Hoàn thành | Căn cứ phương pháp/paper |
| Sáu năng lực gia sư | UET phê duyệt tạm thời | Nền xây rubric chung |
| Sáu nguyên tắc KMP | Tạm thời, chờ HNMU | Đối tượng chấm requirement |
| Run A/B và forward test cũ | Không đạt/chẩn đoán | Legacy; cấm dùng làm nhãn |

Snapshot có 41 file và manifest SHA-256 tại
`inherited_resources/snapshot_manifest.csv`.

## 3. Kiến trúc benchmark đích

```text
Một grounding payload
(context + source_question + gold_answer)
              ↓
Requirement scoring cho 6 nguyên tắc
              ↓
Tập bắt buộc (≥4) + tập thay thế (=3)
              ↓
Instruction riêng của mẫu
              ↓
Tutor model response
              ↓
Rubric chung + rubric theo nguyên tắc bắt buộc
              ↓
Model response ↔ gold_response
              ↓
Win / Tie / Lose theo tiêu chí + overall judgement
```

`gold_response` chỉ xuất hiện sau khi nguyên tắc, instruction và rubric đã
được khóa.

## 4. Các plan

| Plan | Trạng thái | Phạm vi | Output chính | Phụ thuộc |
|---|---|---|---|---|
| [Plan 01 — Đặc tả requirement score](plans/01-principle-requirement-score-specification.md) | `COMPLETED — SPECIFICATION_V4_PUBLISHED` | Một lượt grounding, anchor, prompt, schema và ranh giới model–code; V4 siết lập luận 4–5 cùng ranh giới Feedback/Questioning | Specification V4, schema V2 dùng lại, 36 ca calibration, manifest V4 và prompt tiếng Việt | Snapshot kế thừa |
| [Plan 02 — Pipeline và Vertex pilot](plans/02-vertex-ai-requirement-scoring-pilot.md) | `APPROVED — V4_CALIBRATION_IMPLEMENTED; AWAITING_USER_RUN` | Vertex chuẩn qua ADC; đa luồng; ghi JSONL tăng dần; retry sau lượt quét; semantic lint; hai run trên 36 ca calibration | Runner trỏ sang `calibration_v1`; chưa gọi API V4 | Plan 01 |
| Plan 03 — Instruction và thư viện rubric hai tầng | `NOT_DRAFTED` | Rubric chung từ sáu năng lực; rubric riêng từ sáu nguyên tắc; item instruction | Rubric registry, instruction builder, error catalog | Plan 02 |
| Plan 04 — Audit gold và chất lượng candidate | `NOT_DRAFTED` | Kiểm gold theo instruction/rubric, evidence, leakage, trùng và giá trị đánh giá | Candidate audit, gold dispositions, review queue | Plan 03 |
| Plan 05 — Sinh và chấm response nhiều mô hình | `NOT_DRAFTED` | Gọi các tutor model, chấm Win/Tie/Lose theo tiêu chí, kiểm judge | Response bundle, criterion judgements, validity analysis | Plan 04 |
| Plan 06 — HNMU/UET review và freeze benchmark | `NOT_DRAFTED` | Review gói tích hợp, phân xử, coverage, split và publication | Spec/dataset v1 có truy vết | Plan 05 |

Plan viết paper KSE tại `kse_submit_manuscript/` tiếp tục nhận snapshot
bằng chứng sau mỗi gate; không đợi Plan 05 mới viết.

## 5. Trình tự gần nhất

1. Plan 01 đã hoàn thành và khóa manifest V4; schema dữ liệu V2 được dùng
   lại vì hình dạng input/output không đổi.
2. Code, validator, client và CLI Plan 02 đã chuyển sang ADC với project
   `edu-benchmark`, đa luồng, ghi output tăng dần và retry sau lượt quét.
3. Người dùng review command, location/model, concurrency, `max_retries`
   và request ceiling.
4. Người dùng tự chạy lệnh calibration; Codex không gọi API trong lượt
   cài đặt.
5. Code đọc 36 ca cố định, kiểm cân bằng 3 positive + 3 near-miss cho mỗi
   nguyên tắc và khóa hash trước request.
6. Code chạy hai run độc lập, kiểm expected range, positive support,
   semantic lint và độ ổn định.
7. UET review `calibration_summary.md` và `review_queue.csv`.
8. Sau disposition, tạo holdout 40 candidate mới và chạy lại V4 để kiểm
   khả năng khái quát.
9. Chỉ sau khi đạt các gate mới viết Plan 03 cho instruction và rubric.

## 6. Cổng dừng hiện tại

Plan 01 V4 đã hoàn thành; Plan 02 đã cài và đang chờ người dùng chạy
calibration V4. Trước
khi có run do người dùng thực hiện, không được:

- để Codex gọi Vertex AI; chỉ người dùng chạy lệnh bàn giao sau khi review;
- tạo output score chính thức;
- chạy đủ 2.028 candidate;
- đưa API key hoặc credential vào repository;
- xây rubric như specification đã xác nhận;
- gọi run cũ là ground truth.

## 7. Phạm vi và thẩm quyền

- Phạm vi dữ liệu: Tin học THCS lớp 6–9.
- UET: duyệt phương pháp, prompt, ngưỡng và review kết quả.
- HNMU: xác nhận sư phạm/nội dung trong gói tích hợp.
- Model/API: tạo đề xuất có truy vết, không xác nhận benchmark.
- Mọi coverage phải báo cả candidate-macro và family-macro.
