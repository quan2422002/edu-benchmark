# Plan 02 — Cài đặt pipeline và pilot chấm requirement bằng Vertex AI

Experiment: `20260727_170150`
Trạng thái: `APPROVED — V4_CALIBRATION_IMPLEMENTED; AWAITING_USER_RUN`
Ngày soạn: 27/07/2026
Phụ thuộc: Plan 01 hoàn thành và công bố specification manifest V4

## 1. Mục tiêu

Triển khai đúng contract đã khóa ở Plan 01:

1. xây builder tạo một grounding payload cho mỗi candidate, có
   `gold_answer` và không có `gold_response`;
2. tạo đúng một logical request có request hash cho mỗi candidate; khi lỗi,
   các lần retry dùng lại đúng payload/hash đó;
3. validate đủ sáu `requirement_score`;
4. dẫn xuất tập nguyên tắc bắt buộc/thay thế bằng code;
5. chạy hai run lặp độc lập trên bộ calibration 36 ca trước khi tạo
   holdout pilot mới;
6. tính metric, tạo review queue bằng code và tạo packet UET review.

Plan này không xây rubric cuối, không sinh tutor response và không chạy đủ
2.028 candidate.

## 2. Điều kiện mở plan

Không được chuyển sang `APPROVED` nếu Plan 01 chưa:

- khóa prompt, input schema, response schema và anchor;
- có UET disposition đầy đủ;
- xuất `specification_manifest_v4.json`;
- chứng minh mỗi scoring input có `gold_answer` và không chứa
  `gold_response`.

Mọi thay đổi semantic đối với prompt/anchor phải quay lại Plan 01, tăng
version và làm mới manifest. Plan 02 không được tự sửa định nghĩa để làm
metric đẹp hơn.

## 3. Hợp đồng Vertex AI

Không dùng specialist agent/skill để chấm từng dòng. Runner gửi một request
cho mỗi candidate với cùng system prompt và cùng user-payload template.
Request duy nhất này chỉ chứa tám trường có ý nghĩa ngữ nghĩa: `grade`,
`lesson`, `position`, `bloom_level`, `student_prompt`,
`conversation_history`, `source_question` và `gold_answer`; model trả về
đủ sáu score trong một response. `benchmark_candidate_id` và `sample_id`
chỉ được code giữ để điều phối/truy vết và không được gửi model.

Không triển khai context pass và grounding pass riêng. Không tạo nhãn
trước/sau, `reference_effect`, phép hợp nhãn hoặc request thứ hai để sửa
request thứ nhất.

### 3.1. Nguyên tắc code-first

Model chỉ thực hiện phần phán đoán ngữ nghĩa đã khóa trong Plan 01: trả sáu
score cùng rationale/evidence. Code phải thực hiện:

- build payload, join ID và kiểm hash/schema;
- validate response và chuẩn hóa output;
- áp threshold 4 và lọc tập bắt buộc/thay thế;
- phát hiện toàn bộ điều kiện review;
- so sánh run A/B, tính metric và coverage;
- retry/resume, chống trùng và publish fail-closed.

Không gọi thêm model hoặc agent để làm các phép lọc, so sánh, đếm, kiểm
schema hay tính metric trên.

### 3.2. Cấu hình phải đăng ký trước

Run manifest ghi:

- chế độ Vertex, API version, project ID, location và model ID;
- model version trả về;
- `temperature`, `top_p`, `max_output_tokens`, `seed` và
  `thinking_budget` nếu hỗ trợ;
- response MIME `application/json` và response schema hash;
- prompt, input, code commit và config hash;
- timeout, retry policy, concurrency và quota ceiling;
- số request tối đa; trong pilot hiện tại đây là guardrail chi phí có thể
  thực thi bằng code, còn ngân sách tiền tệ do project lead kiểm soát qua
  quota/billing của Vertex.

Runner không đọc API key. Xác thực dùng Application Default Credentials
(ADC) đã được thiết lập trên máy; không ghi credential/token vào source,
manifest, raw response, log hoặc handoff.

### 3.2.1. Cấu hình pilot đã được UET khóa

Pilot hiện dùng:

- model: `gemini-2.5-flash`;
- `temperature = 0.0`;
- `top_p = 1.0`;
- `max_output_tokens = 4096`;
- `seed = 20260727`;
- `thinking_budget = 0`.

Mục tiêu của cấu hình này là ưu tiên tính ổn định của phép chấm. Giá trị
`thinking_budget = 0` tắt thinking của Gemini 2.5 Flash; runner phải gửi
giá trị này tường minh và ghi nó vào request hash cùng run manifest. Hai
run A/B dùng cùng cấu hình và cùng seed để đo khả năng lặp lại của đúng
một phép chấm đã khóa. Việc dùng model hoặc cấu hình khác cần được UET
duyệt và chuẩn bị lại manifest trước khi gọi API.

### 3.3. Xác thực và project

Runner khởi tạo Google Gen AI SDK ở chế độ Vertex chuẩn bằng:

- `project = "edu-benchmark"`;
- `location = "global"` theo mặc định, có thể override bằng CLI;
- ADC do thư viện Google tự tìm trong môi trường chạy.

Runner không đọc `src/vertex_ai_call/.env`, không nhận `--api-key` và
không có fallback hard-code credential. File `.env` cũ tiếp tục được
ignore để tránh lộ secret nếu còn tồn tại cục bộ, nhưng không thuộc runtime
active.

### 3.4. Raw và normalized output

- Raw response lưu append-only theo request hash.
- Mỗi response hợp lệ được ghi ngay vào `run_a.jsonl` hoặc `run_b.jsonl`,
  `flush` và `fsync` trước khi runner xử lý response kế tiếp.
- Mỗi record giữ trường `user_prompt` là đúng chuỗi JSON đã truyền vào
  `contents`; không tạo thêm file request trùng lặp.
- Normalized table chỉ publish khi ID/schema/score hợp lệ.
- Mỗi response giữ `response_id`, `model_version`, finish reason và usage
  metadata khi API cung cấp.
- Retry không được tạo hai normalized row cho cùng request.

## 4. Pilot

### Bước 0 — Khóa input và manifest

Validate 41 file snapshot, bundle 2.028 candidate, grounding pool và
specification manifest Plan 01. Dừng đóng nếu hash lệch, ID thiếu/trùng,
schema sai, `gold_answer` không được đưa trực tiếp vào payload hoặc
`gold_response` xuất hiện trong scoring view.

Đồng thời khóa và kiểm SHA-256 của system prompt tại:

`shared/prompts/benchmark_candidate_task_assigning/system_prompt_v4.md`

Manifest phải ghi `prompt_language: "vi"`. Validator dừng đóng nếu prompt
không khai báo tiếng Việt hoặc nếu runner trỏ sang một prompt khác.

### Bước 1 — Tạo pilot xác định

Cắt 40 candidate thuộc 40 family, 10 mẫu mỗi lớp 6–9; phân tầng thêm theo:

- có/không có history;
- độ sâu target;
- Bloom;
- bài học/chủ đề;
- dạng nội dung Tin học.

Sampling seed, ordered-ID hash và lý do chọn phải được lưu trước API call.
Không dùng score/nhãn legacy để phân tầng.

### Bước 2 — Cài code và dry run

Dry run không dùng quota phải kiểm:

- mỗi candidate tạo đúng một logical request JSON có `gold_answer`; retry
  không thay payload/hash và chỉ có một kết quả cuối được publish;
- secret redaction;
- timeout, đa luồng có giới hạn, retry/resume;
- idempotency key;
- staging và atomic publish;
- output lỗi, safety block và response không parse được.

### Bước 3 — Đăng ký model, quota và ngưỡng

UET duyệt project/location, model/config, số luồng, `max_retries`, trần
request, chi phí tối đa và ngưỡng trước khi xem output. Manifest sau duyệt
là bất biến.

### Bước 4 — Chạy pilot A/B

- Run A chấm 40 candidate.
- Run B chấm lại đúng 40 candidate bằng cùng prompt/model/config.
- Hai run ghi vào hai file phẳng `run_a.jsonl` và `run_b.jsonl`.
- Run B không được đọc output A.
- Không tạo comparison trước khi cả hai bundle đóng và qua validator.
- Trong mỗi run, `ThreadPoolExecutor` gửi đồng thời tối đa `concurrency`
  request; mặc định là 8.
- Chỉ thread điều phối được ghi file. Worker chỉ gọi Vertex và trả kết quả,
  nên không có hai thread cùng ghi JSONL.
- Terminal hiển thị progress bar riêng cho lượt quét đầu và từng lượt
  retry của run A/B. Thanh tiến trình báo số request đã xử lý trong lượt,
  tổng candidate đã hoàn thành, số lỗi tạm thời và tổng request đã dùng.
  Có thể tắt bằng `--no-progress` mà không làm thay đổi request hash.

Run A và B là hai lần chạy lặp độc lập để đo độ ổn định của cùng một phép
chấm một lượt. Chúng không phải hai vòng gán nhãn và output A không được
dùng làm input cho B.

### Bước 4A — Calibration V4 trước holdout

Run active kế tiếp không dùng lại 40 candidate của V1–V3. Runner đọc trực
tiếp `calibration_cases_v1.csv`, gồm 36 ca:

- ba positive và ba near-miss cho mỗi nguyên tắc;
- positive có expected range 4–5;
- near-miss có expected range 1–3;
- mỗi run vẫn chấm đủ cả sáu nguyên tắc; expected range chỉ áp vào nguyên
  tắc trọng tâm của ca.

Code chạy hai lần A/B, kiểm expected range, positive support, semantic
lint và các ngưỡng ổn định. Expected range hiện là giả thuyết tạm thời,
chờ UET review sau run; không được gọi là nhãn chuyên gia HNMU.

Chỉ sau khi calibration đạt hoặc có disposition rõ cho ca chưa đạt mới
tạo một holdout 40 candidate mới để kiểm tra khả năng khái quát. Không
dùng kết quả V1–V3 làm expected label của holdout.

### Bước 4.1 — Retry sau toàn bộ lượt quét

Retry không diễn ra ngay khi một candidate lỗi. Runner:

1. chạy toàn bộ candidate chưa hoàn thành trong lượt quét hiện tại;
2. ghi ngay từng candidate thành công vào JSONL;
3. thu danh sách candidate lỗi vào manifest, không lưu exception message
   có thể chứa credential;
4. sau khi toàn bộ lượt quét kết thúc, chỉ gửi lại các candidate lỗi;
5. lặp tối đa `max_retries` lượt retry cho mỗi candidate, đồng thời luôn
   tuân theo trần tổng `max_requests`.

Giữa các lượt retry dùng exponential backoff có jitter và trần chờ 30
giây. Nếu runner bị dừng, lần chạy lại đọc JSONL, kiểm request hash và bỏ
qua mọi candidate đã thành công.

### Bước 5 — Dẫn xuất tập bằng code

Với mỗi run:

- `required_principle_set`: score từ 4 trở lên;
- `alternative_principle_set`: score bằng 3;
- không dùng rationale để tự sửa score;
- mọi trường hợp không có nguyên tắc đạt 4 hoặc có hơn ba nguyên tắc đạt 4
  vào review queue.

Không gửi output trở lại model để lọc tập hoặc quyết định có vượt ngưỡng
hay không.

Code còn chạy semantic lint nhưng không tự sửa score:

- điểm 4–5 thiếu `Nhu cầu độc lập:` hoặc `Nếu bỏ nguyên tắc này:`;
- điểm cao vẫn mô tả nguyên tắc là tùy chọn hoặc chiến lược thay thế;
- Feedback điểm cao chỉ là xác nhận/khen, không có hướng cải thiện;
- Questioning điểm cao không nêu sự phụ thuộc vào câu trả lời học sinh.

### Bước 6 — So sánh và UET review

Code tính:

- tỷ lệ trùng điểm chính xác;
- tỷ lệ điểm chênh không quá một mức;
- weighted Cohen’s kappa theo nguyên tắc;
- phân bố điểm và tỷ lệ vượt ngưỡng 4;
- exact-set agreement, Jaccard và F1 từng nguyên tắc trên tập bắt buộc;
- mọi crossing qua ngưỡng 4.

UET review:

- mọi crossing qua ngưỡng;
- mọi score thay đổi từ hai mức trở lên;
- mọi candidate không có nguyên tắc bắt buộc;
- mọi candidate có hơn ba nguyên tắc bắt buộc;
- mọi rationale/evidence mâu thuẫn với score;
- tổ hợp nghi là chiến lược thay thế nhưng bị chấm đồng thời 4–5;
- mẫu phân tầng của các trường hợp hai run trùng hoàn toàn.

### Bước 7 — Quyết định phương pháp

Nếu lỗi thuộc implementation/config, sửa trong Plan 02 và rerun đúng
version prompt. Nếu lỗi thuộc định nghĩa/anchor/prompt, quay lại Plan 01,
tăng version và chạy lại toàn bộ pilot; không trộn hai version.

Chỉ sau khi Plan 02 đạt gate mới được viết plan chạy đủ 2.028 candidate.

## 5. Ngưỡng phải đăng ký trước run

Các ngưỡng dưới đây đã được UET phê duyệt trước run:

| Chỉ số | Ngưỡng đã khóa |
|---|---:|
| Tỷ lệ điểm chênh không quá một mức | 0,95 |
| Exact agreement của tập bắt buộc | 0,90 |
| Jaccard trung bình của tập bắt buộc | 0,90 |
| F1 tối thiểu từng nguyên tắc tại ngưỡng 4 | 0,90 |
| Tỷ lệ candidate không crossing qua ngưỡng 4 | 0,95 |

Weighted kappa được báo nhưng chưa đặt ngưỡng trước khi biết phân bố các
mức; không diễn giải kappa khi nguyên tắc gần như không có biến thiên.

## 6. Review queue bắt buộc

- không có nguyên tắc đạt 4;
- hơn ba nguyên tắc đạt 4;
- hai run nằm khác phía ngưỡng 4;
- score thay đổi từ hai mức trở lên;
- rationale không khớp anchor;
- evidence nhắc nội dung không có trong grounding payload;
- output chứa nhãn trước/sau, `reference_effect` hoặc evidence bị tách theo
  hai vòng;
- tổ hợp nguyên tắc có vẻ là lựa chọn thay thế;
- lỗi API, safety block, output thiếu/trùng hoặc không parse được.

## 7. Vị trí code, prompt và kết quả

### 7.1. Code chạy Vertex

Toàn bộ code thực thi cho Plan 02 nằm trực tiếp dưới một thư mục, không
tạo thêm package con:

```text
src/vertex_ai_call/
├── requirement_scoring.py       # build, validate, derive, compare
├── vertex_client.py             # Vertex transport only
└── run_requirement_scoring.py   # CLI and orchestration
```

Không đặt wrapper chạy Plan 02 dưới `scripts/benchmark_specification/` và
không đặt implementation Vertex dưới
`src/edu_benchmark/benchmark_specification/`.

Test chính nằm tại `tests/vertex_ai_call/test_requirement_scoring.py`.
Chỉ tách thêm file khi một module đã có hai trách nhiệm vận hành không thể
kiểm độc lập trong cấu trúc trên.

### 7.2. System prompt

```text
shared/prompts/benchmark_candidate_task_assigning/
└── system_prompt_v4.md
```

Runner nhận prompt bằng đường dẫn đã khóa; không nhúng một bản prompt thứ
hai trong source code. Prompt và yêu cầu rationale/evidence đều dùng tiếng
Việt; JSON key, principle ID và tên trường kỹ thuật vẫn giữ nguyên.

### 7.3. Kết quả chạy

```text
experiments/20260727_170150/outputs/principle_requirement_scoring/
├── specification_v4.md
├── scoring_schema_v2.json
├── specification_manifest_v4.json
├── calibration_cases_v1.csv
└── calibration_v1/
    ├── run_a.jsonl
    ├── run_b.jsonl
    ├── review_queue.csv
    ├── run_manifest.json
    └── calibration_summary.md
```

Mỗi `run_*.jsonl` giữ cùng lúc metadata request, user prompt chính xác,
raw response và normalized result của từng candidate; không tách các phần
này sang nhiều file/thư mục.

Không publish `comparison.csv`: code tái tạo comparison đầy đủ từ hai file
run khi cần. `review_queue.csv` chỉ giữ các dòng so sánh mà UET phải xem và
đồng thời chứa các cột disposition; không tạo thêm thư mục hoặc bảng UET
review. `run_manifest.json` gom config, hash, status, metric tổng hợp và
error summary. Chỉ tạo `errors.jsonl` khi thực sự có lỗi không thể biểu
diễn ngắn gọn trong manifest.

Không tạo `specification_snapshot/`, `manifests/`, `reports/`, `raw/`,
`normalized/` hoặc `comparison/` lồng nhau cho pilot. Artifact cũ/thất bại
không publish vào bundle active; staging được thay nguyên tử hoặc chuyển
ra vị trí tạm ngoài bundle review.

Không ghi raw response, normalized score, metric hoặc review queue vào
`src/vertex_ai_call/` hay `shared/prompts/`.

### 7.4. Nguyên tắc tinh gọn

- Một thông tin chỉ có một nguồn sự thật; không copy cùng bảng sang nhiều
  định dạng nếu không có consumer bắt buộc.
- Không publish bảng dẫn xuất đầy đủ nếu code có thể tái tạo trực tiếp từ
  các nguồn đã lưu; chỉ publish hàng đợi review là phần con người cần đọc.
- Tài liệu mà UET phải đọc trực tiếp được gom theo quyết định cần review,
  không gom theo từng bước kỹ thuật của pipeline.
- File máy đọc chỉ được tạo khi runner, validator hoặc phép tái lập thực
  sự sử dụng.
- File debug tạm không được publish vào bundle active.
- Mọi file mới ngoài cây trên phải được giải thích trong
  `run_manifest.json`.

## 8. Fail-closed

- Builder ghi staging, validate rồi mới publish input.
- Runner không ghi đè raw response đã tồn tại.
- Runner chỉ dùng ADC, project/location đã khóa và không đọc `.env`.
- Mỗi worker thread có một Google Gen AI client riêng; JSONL chỉ do thread
  điều phối ghi append-only, `flush` và `fsync`.
- Retry chỉ bắt đầu sau khi lượt quét hiện tại hoàn tất và chỉ áp dụng cho
  candidate chưa có output hợp lệ.
- Runner đọc system prompt từ
  `shared/prompts/benchmark_candidate_task_assigning/`, không dùng prompt
  hard-code.
- Runner kiểm `prompt_language: "vi"` trong manifest trước khi gọi API.
- Mỗi request có hash từ prompt + config + candidate payload.
- Validator tái dựng user prompt từ input canonical và yêu cầu khớp chính
  xác với `user_prompt` đã lưu trong từng run record.
- Resume chỉ bỏ qua request khi response parse được và hash khớp.
- Toàn run không được `completed` khi còn failure.
- Không tạo tập hoặc metric từ bundle chưa qua validator.
- Code active không được đọc `diagnostic_legacy/`.

## 9. Quyền quyết định

- UET duyệt model/config/quota/ngưỡng và phân xử pilot.
- Plan 02 không được tự sửa semantic artifact Plan 01.
- Vertex model chỉ đề xuất score/rationale; không ghi `confirmed`.
- HNMU xác nhận sư phạm ở gói tích hợp sau khi rubric và ví dụ đã có.

## 10. Điều kiện hoàn thành

Plan 02 chỉ `COMPLETED` khi:

1. Plan 01 V4 đã hoàn thành và hash khớp;
2. builder/runner/validator/test đạt bằng `benchmark_env`;
3. mỗi candidate có đúng một logical grounding request chứa `gold_answer`,
   không có `gold_response`; retry giữ nguyên payload/hash và chỉ publish
   đúng một output cuối;
4. code chạy nằm dưới `src/vertex_ai_call/`, prompt nằm dưới
   `shared/prompts/benchmark_candidate_task_assigning/` và output nằm dưới
   experiment;
5. system prompt và rationale/evidence sử dụng tiếng Việt; manifest ghi
   `prompt_language: "vi"`;
6. ADC, project/location được đăng ký; secret không xuất hiện trong
   repository/log;
7. model/config/concurrency/retry/quota/ngưỡng được đăng ký trước run;
8. hai run calibration 36 ca hoàn tất độc lập và qua validator;
9. threshold, tập nguyên tắc, review queue và metric đều do code tính;
10. mọi review bắt buộc có disposition UET;
11. bundle calibration tuân thủ cây artifact tinh gọn ở Mục 7.3, không có bản
    sao hoặc thư mục debug thừa;
12. đạt ngưỡng hoặc có quyết định sửa/rerun đúng version;
13. paper update, coordination và handoff đầy đủ.
