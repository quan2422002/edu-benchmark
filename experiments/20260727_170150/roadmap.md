# Roadmap — Chấm yêu cầu sư phạm và xây benchmark đánh giá phản hồi gia sư

Experiment: `20260727_170150`  
Trạng thái: `ACTIVE_PLAN05_FULL_JUDGE_ANALYSIS_DRAFTED`
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
Tập bắt buộc duy nhất (≥4)
điểm 3 chỉ là dữ liệu chẩn đoán, không dùng từ Plan 05
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
| [Plan 02 — Pipeline, calibration và full run](plans/02-vertex-ai-requirement-scoring-pilot.md) | `COMPLETED — FULL_BUNDLE_VALIDATED` | Giữ calibration làm chẩn đoán; chạy một lần trên 2.028 candidate bằng Gemini 3.5 Flash, concurrency 20 | `full_gemini35_medium_v1/run_full.jsonl` và manifest | Plan 01 |
| [Plan 03 — Thống kê và phân tích full run](plans/03-full-run-statistics-and-analysis.md) | `COMPLETED — UET REVIEW DEFERRED` | Kiểm toàn vẹn, phân bố theo tập nguyên tắc, thống kê mẫu đủ điều kiện đi tiếp, candidate/family macro và review queue | Một JSON thống kê, một báo cáo Markdown, một CSV review | Full run Plan 02 |
| [Plan 04 — Bộ tiêu chí hai tầng](plans/04-two-tier-rubric-library.md) | `IMPLEMENTED — AWAITING UET/HNMU REVIEW` | Rubric chung từ sáu năng lực; rubric riêng từ sáu nguyên tắc; lỗi nghiêm trọng; dùng 1.400 candidate eligible làm pool ưu tiên | Năm artifact rubric và review tối thiểu | Plan 03 |
| [Plan 05 — Cấu hình đánh giá gia sư AI](plans/05-benchmark-evaluation-configuration.md) | `FULL_JUDGE_BATCH_COMPLETED — ANALYSIS_DRAFTED` | Ba target full × hai judge; contract v4; Batch API tách provider; phân tích KMP-compatible và agreement | Hai bundle 4.200 phán quyết, báo cáo pilot và báo cáo full judge | Plan 04 |
| Plan 06 — Audit gold và chất lượng candidate | `NOT_DRAFTED` | Kiểm gold theo instruction/rubric, evidence, leakage, trùng và giá trị đánh giá | Candidate audit và review queue | Plan 04–05 |
| Plan 07 — Sinh và chấm response nhiều mô hình | `NOT_DRAFTED` | Pilot, kiểm judge, chồng lấn rubric và khả năng phân biệt rồi mới xét full evaluation | Response bundle và validity analysis | Plan 06 |
| Plan 08 — HNMU/UET review và freeze benchmark | `NOT_DRAFTED` | Review gói tích hợp, phân xử, coverage, split và publication | Spec/dataset v1 có truy vết | Plan 07 |

Cost-pilot v2 đã hoàn thành cho cả Gemini và GPT. Vì phát hiện lỗi nghiêm
trọng thay đổi theo response đối đầu, UET chuyển lần chạy kế tiếp sang
contract `rubric-only-v3`: chỉ chấm rubric và overall, giữ trường lỗi rỗng
để tương thích. Wrapper chung đã hoàn thành 90/90 phép chấm cho mỗi judge
trên đúng 30 candidate × 3 target configuration. Agreement đạt 86,7% ở
overall và 77,2% ở rubric. Đây là trạng thái lịch sử trước v4 và quyết
định full batch ở bước 27.

Audit 30 candidate sau đó phát hiện liên kết fragment raw-audit không đủ làm
evidence cấp candidate. UET chọn ablation `gold-answer-only-v4`: không gửi
fragment, không đổi catalog/ID rubric, chỉ thay tên và anchor hiển thị của
`RUB-GEN-ACC` trong request v4. Preflight offline đã đạt 90 phép so sánh cho
mỗi judge; chưa gọi API.

Plan viết paper KSE tại `kse_submit_manuscript/` tiếp tục nhận snapshot
bằng chứng sau mỗi gate; không đợi Plan 05 mới viết.

## 5. Trình tự gần nhất

1. Plan 01 đã hoàn thành và khóa manifest V4; schema dữ liệu V2 được dùng
   lại vì hình dạng input/output không đổi.
2. Code, validator, client và CLI Plan 02 đã chuyển sang ADC với project
   `edu-benchmark`, đa luồng, ghi output tăng dần và retry sau lượt quét.
3. Calibration nền bằng Gemini 2.5 Flash đã hoàn tất: hai run trùng nhau,
   nhưng chỉ 32/36 ca nằm trong expected range tạm thời và còn 13
   candidate bị semantic lint.
4. Runner đã được chuyển sang cấu hình so sánh
   `gemini-3.5-flash`: không gửi tham số sampling, dùng
   `thinking_level=MEDIUM`, không trả thought summary và giữ nguyên prompt,
   schema cùng dữ liệu.
5. Calibration Gemini 3.5 đã hoàn tất: 34/36 ca đúng expected range nhưng
   chỉ 75% candidate có cùng tập nguyên tắc bắt buộc giữa hai run.
6. UET quyết định dừng calibration tại đây, chấp nhận giới hạn về độ lặp
   lại và chốt một full run Gemini 3.5 Flash.
7. Người dùng chạy lệnh `full`; hai candidate còn lỗi sau các retry ban
   đầu được UET cho phép chạy bù riêng bằng `retry-failed`.
8. Runner chỉ gửi lại hai candidate thiếu, nối thêm đúng hai record rồi
   validate đủ 2.028 record duy nhất và 12.168 score. Bundle đã chuyển
   sang `completed_awaiting_analysis`.
9. Plan 03 đã dùng code thống kê candidate/family macro, phân tầng và kiểm
   rủi ro ngữ nghĩa: 1.400 candidate không bị cờ, 628 cần UET review và
   không có candidate bị chặn.
10. UET quyết định đóng Plan 03, hoãn review 628 candidate thành backlog
    và dùng 1.400 candidate `eligible_without_plan03_review` làm pool ưu
    tiên cho các plan tiếp theo.
11. Plan 04 được UET duyệt để chuyển sang xây bộ tiêu chí hai tầng. Pool
    ưu tiên được dùng để chọn ví dụ và kiểm ranh giới; rubric vẫn phải bao
    phủ đủ sáu nguyên tắc, kể cả `Challenge` và `Practice` đang hiếm.
12. Plan 04 đã tạo một task, 4 tiêu chí chung, 18 tiêu chí riêng, 6 lỗi
    nghiêm trọng và ma trận provenance. Validator đạt; output đang chờ
    UET/HNMU review, chưa phải rubric đã freeze.
13. Plan 05 đã chuyển instruction gia sư sang bundle tiếng Việt có phiên
    bản tại `shared/prompts/benchmark_tutor_response_generation/`.
    Bundle `v1` là nguồn chuẩn duy nhất; registry là output review được
    sinh lại. Prompt theo nguyên tắc có tên tiếng Việt và bốn mục con
    xuống dòng; preflight lưu version, SHA-256 của bundle và hash prompt.
14. Smoke Gemini 3.5 Flash đã hoàn thành 10/10 candidate. Cấu hình và run
    được gom dưới `outputs/benchmark_evaluation/`. Mỗi record lưu trực
    tiếp system prompt, user prompt cuối, toàn bộ message có role và bốn
    trường định danh phase/run; 10 response cũ được backfill mà không gọi
    lại API.
15. Audit smoke v1 phát hiện một response bị cắt nhưng runner cũ không lưu
    lý do kết thúc. Smoke v2 đã được cài đặt trên đúng 10 ID của v1, vẫn
    giữ giới hạn 1.024 output token, dùng bundle `v2` chỉ bổ sung yêu cầu
    trả lời cô đọng. Runner mới lưu `finish_reason`, đưa `MAX_TOKENS` và
    `length` vào review và không báo `completed` khi có response bị cắt.
16. Judge v2 đã cài đặt trên 20 phép so sánh. Lần gọi Claude thất bại
    20/20 do project chưa kích hoạt sản phẩm Anthropic trên Marketplace,
    không phát sinh phí. UET chuyển smoke tạm thời sang Gemini 3.5 Flash,
    giữ nguyên prompt/dataset và dùng `thinking_level=MEDIUM`, không đặt
    tham số lấy mẫu. Lần đầu hoàn tất 11/20 và có chín lỗi `MAX_TOKENS`;
    cost 0,353856 USD chỉ là lower bound. Retry1 dùng 8 worker, giới hạn
    8.192 token và đã hoàn thành đủ 20/20 phán quyết, không lỗi. Rà nhanh
    cùng chuyên gia cho thấy kết quả nhìn chung hợp lý, nhưng judge bỏ sót
    lỗi nghiêm trọng ở `BC-HNMU-G7-R0207-STT10-AI10`; reference của
    `BC-HNMU-G7-R0204-STT7-AI14` chỉ thiếu giá trị tăng thêm, không phải
    lỗi nghiêm trọng.
17. UET quyết định chuyển thẳng sang pilot 80 mẫu. Manifest xác định đã
    khóa 20 mẫu mỗi lớp, 80 family, 54 cặp lớp–bài học, đủ toàn bộ 8 mẫu
    Challenge và bao phủ có chủ đích các trục còn lại. Wrapper target hiện
    chạy ba cấu hình trên cùng manifest: Gemini baseline, Llama 4 Maverick
    và Gemini với system instruction định hướng LearnLM. LearnLM đã được
    tích hợp trong Gemini nên cấu hình thứ ba là prompt ablation, không phải
    model độc lập hoặc model chuyên biệt. Cả ba target đã preflight offline;
    judge runner đã qua test, chờ đúng 240 response và khóa cận trên chi phí.
    API run chờ người dùng.
18. Tooling full khóa đúng 1.400 mẫu trong manifest `full_1400_v1`.
    UET cho phép phương án hybrid: sinh full ba cấu hình target, tổng 4.200
    response; cận trên bảo thủ 127,09032 USD vẫn nằm trong hard cap khi cộng
    mức chi lịch sử và dự phòng.
19. Judge cost-pilot khóa 30 candidate thuộc 30 family và tạo 90 phép so
    sánh cho ba cấu hình. Phương án synchronous lịch sử chỉ xét baseline +
    Llama và bị đóng bởi cận trên 496,8768 USD; bước 27 đã thay thế phương
    án này bằng full batch ba target sau khi có usage v4.

20. Full Gemini baseline lần đầu ghi đủ 1.400 record nhưng 436 mẫu chạm
    `MAX_TOKENS` ở cap 1.024; runner trả mã 2 và chặn Llama/LearnLM đúng
    fail-closed. Recovery đã khóa đúng 436 ID, giữ MEDIUM thinking và tăng
    cap lên 1.536. Chỉ merge khi 436/436 hoàn chỉnh; cận trên 23,967792 USD.
21. Recovery 1.536 hoàn thành 417/436 mẫu, còn 19 mẫu `MAX_TOKENS`; chi phí
    thực tế là 4,7877885 USD. Follow-up đã được cài để tái sử dụng 417 kết
    quả này, chỉ gọi lại 19 mẫu ở cap 2.048 với cận trên 1,307124 USD. Khi
    19/19 hoàn chỉnh, code hợp nhất đủ 436 recovery record rồi mới thay thế
    nguyên tử vào bundle chính. Preflight đúng 19 ID đã đạt; API run đã
    hoàn thành 19/19 và baseline hiện đạt 1.400/1.400.
22. Wrapper target đã được gia cố để xác minh rồi bỏ qua Gemini baseline,
    chỉ chạy Llama và LearnLM, tránh ghi mất `recovery_history`. Preflight
    hai target còn lại đã đạt. Judge cost-pilot tự chặn nếu ba target chưa
    hoàn chỉnh và tự tính mốc chi phí từ manifest khi không có override.
23. Lượt Llama full đầu hoàn thành 1.314/1.400 mẫu; 86 mẫu thất bại và toàn
    bộ 1.111 exception theo attempt đều là HTTP 429. Runner đã được sửa để
    resume đúng 86 ID với 2 worker, exponential backoff 15–60 giây và jitter
    tối đa 5 giây, đồng thời cộng dồn chi phí và `resume_history`. Preflight
    đạt; LearnLM và judge vẫn bị chặn đến khi Llama đủ 1.400 mẫu.
24. Retry Llama đã đạt đủ 1.400/1.400. LearnLM ghi 1.400 record nhưng 386
    mẫu bị `MAX_TOKENS` ở cap 1.024. Recovery 2.048 đã khóa đúng 386 ID, giữ
    bundle v3 và cấu hình ngữ nghĩa, dùng staging `/tmp` và chỉ merge nguyên
    tử khi toàn bộ mẫu hoàn chỉnh. Preflight đạt; API run chờ người dùng.
25. LearnLM recovery đã đạt 1.400/1.400. Judge cost-pilot lượt đầu giữ được
    70/90 phán quyết, còn 20 lỗi: 16 DNS và 4 output không hợp lệ. Runner đã
    nhận diện DNS là retryable, hạ xuống 8 worker, thêm backoff+jitter và
    tính budget theo pending. Preflight resume đúng 20 phép chấm đã đạt.
26. Judge cost-pilot Gemini đã hoàn thành 90/90 phép chấm. UET chọn chạy
    đối chiếu cùng 90 request bằng snapshot `gpt-5.4-mini-2026-03-17` qua
    OpenAI Responses API, reasoning `medium`, Structured Outputs và không
    truyền temperature. Nhánh caller/output độc lập đã qua 81 regression
    test và preflight đúng 30 candidate, 90 comparison; chưa gọi API.
27. V4 đã hoàn thành 90/90 cho cả Gemini và GPT. UET mở full judge cho
    cả ba target, tổng 4.200 comparison mỗi judge. Pipeline batch bất đồng
    bộ đã được cài tách khỏi runner synchronous: Vertex Gemini dùng GCS và
    OpenAI dùng `/v1/responses`. Preflight offline tạo hai input 4.200 dòng
    (74 MB và 77 MB). Dự toán p95 theo usage v4, đơn giá batch và hệ số 1,10
    là 132,44616 USD cho Gemini và 46,52802 USD cho GPT; chưa submit API.
28. Hai full judge batch đã hoàn thành và recovery đạt đủ 4.200/4.200
    phán quyết hợp lệ cho mỗi judge. Báo cáo phân tích chính dùng bảng
    win-rate kiểu KMP-Bench, family-cluster bootstrap, exact agreement,
    Cohen's kappa và Gwet's AC1. Hai judge cùng xếp Llama sau hai cấu hình
    Gemini nhưng không thống nhất thứ hạng giữa Gemini baseline và
    LearnLM-oriented; báo cáo cũng phát hiện dấu hiệu position bias ở
    Gemini judge. Kết quả chưa được coi là human ground truth hoặc bằng
    chứng cho ba mức chất lượng tuyệt đối.


## 6. Cổng dừng hiện tại

Plan 01–03 đã hoàn thành. Review 628 candidate bị cờ cùng 8 mẫu đối chứng
được giữ làm backlog UET; chúng không được coi là đã duyệt, bị loại hoặc
được sửa nhãn. Plan 04 đã triển khai trên pool ưu tiên 1.400 candidate;
UET đã cho phép triển khai phần code và cấu hình của Plan 05 trong khi
rubric Plan 04 vẫn là bản tạm dùng chờ HNMU. Target, cost-pilot, v4 và
hai full judge batch đã hoàn thành. Bản phân tích full judge đang chờ UET
review; chưa có lượt calibration người–judge độc lập mới và
target/judge Gemini cùng họ model phải được báo riêng. Trong giai đoạn
này, không được:

- gọi score model là nhãn chính thức hoặc ground truth;
- đưa API key hoặc credential vào repository;
- gọi rubric đang xây là specification đã được HNMU xác nhận;
- gọi run cũ là ground truth.

## 7. Phạm vi và thẩm quyền

- Phạm vi dữ liệu: Tin học THCS lớp 6–9.
- UET: duyệt phương pháp, prompt, ngưỡng và review kết quả.
- HNMU: xác nhận sư phạm/nội dung trong gói tích hợp.
- Model/API: tạo đề xuất có truy vết, không xác nhận benchmark.
- Mọi coverage phải báo cả candidate-macro và family-macro.
