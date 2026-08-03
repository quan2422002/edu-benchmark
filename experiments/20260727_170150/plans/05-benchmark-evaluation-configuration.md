# Plan 05 — Cấu hình dùng benchmark để đánh giá gia sư AI

Experiment: `20260727_170150`
Trạng thái: `APPROVED — FULL JUDGE BATCH COMPLETED`
Phụ thuộc: Plan 04 có rubric tạm dùng; candidate/gold phải qua audit trước full evaluation

## 1. Mục tiêu

Khóa trước giao thức sinh phản hồi và chấm phản hồi để các LLM được đánh
giá công bằng, có thể tái tạo và không thay đổi cấu hình sau khi nhìn kết
quả.

Plan khóa đặc tả cấu hình trước khi chạy. Gemini smoke v1 và v2 đều hoàn
thành 10/10 candidate. Llama smoke v2 hoàn thành 10/10 sau khi sửa model
ID. Các lần sửa và triển khai SocraticLM ở một session khác đã thất bại,
nên model này hiện không được coi là khả dụng. Tài liệu chính thức xác nhận LearnLM không còn là model hay API mode riêng:
năng lực này đã được tích hợp vào Gemini từ dòng 2.5 và được khơi gợi bằng
system instruction. Vì vậy, pilot thêm cấu hình thứ ba
`gemini-3.5-flash + LearnLM-oriented prompt`; đây là biến thể prompt của
cùng base model, không phải model độc lập hoặc model chuyên biệt.

Lần gọi Claude Sonnet 4.6 ngày 29/07/2026 thất bại 20/20 do project chưa
kích hoạt sản phẩm Anthropic trên Google Cloud Marketplace; không phát sinh
chi phí và không có phán quyết nào được chấp nhận. Theo quyết định UET, judge
tạm thời chuyển sang `gemini-3.5-flash` tại endpoint `global`, giữ nguyên
system prompt v2, 20 phép so sánh và giao thức chấm mù. Lần chạy Gemini
đầu tiên hoàn thành 11/20; chín request còn lại bị `MAX_TOKENS` vì tổng
reasoning và JSON vượt giới hạn 3.072 token. Chi phí 0,353856 USD trong
manifest cũ chỉ là lower bound vì runner cũ chưa lưu usage của chín request
bị cắt. Retry1 dùng một thư mục mới, không trộn record: không đặt tham số lấy
mẫu, `thinking_level = MEDIUM`, `max_output_tokens = 8192`, thread pool 8
worker và trần riêng 2 USD. Preflight retry1 dựng đúng 20 phép so sánh từ
10 candidate, với upper bound 1,77456 USD. Kết quả của target Gemini phải
được báo riêng vì judge và một tutor candidate cùng nhà cung cấp và cùng
model.

## 2. Input và lịch sử hội thoại mà tutor model được thấy

Request phải tách thành ba lớp; không gói toàn bộ candidate thành một
chuỗi JSON rồi gửi như một user prompt duy nhất.

### 2.1. System instruction

System instruction chứa:

- vai trò gia sư Tin học THCS và yêu cầu trả lời bằng tiếng Việt;
- ngữ cảnh ngoài hội thoại cần cho tác vụ: `grade`, `lesson` và
  `source_question`;
- instruction chung;
- instruction của mọi nguyên tắc có `requirement_score >= 4`, theo thứ tự
  cố định của registry.

Nguồn chuẩn duy nhất của nội dung và khuôn ghép system instruction là
bundle có phiên bản tại
`shared/prompts/benchmark_tutor_response_generation/`. Bundle `v1` bảo
toàn chính xác baseline smoke đầu tiên. Bundle `v2` chỉ bổ sung yêu cầu
trả lời cô đọng, không lặp lại hội thoại, không mở rộng quá bước cần thiết
và phải kết thúc trọn câu; sáu instruction nguyên tắc không đổi.
Code không được giữ bản sao nội dung instruction trong hằng số Python.
Manifest mỗi run phải ghi `bundle_version`, đường dẫn và SHA-256 của bundle;
mỗi response phải ghi `instruction_bundle_version`,
`instruction_bundle_sha256` và `system_instruction_hash`. Khi sửa sau
pilot phải tạo bundle phiên bản mới, không ghi đè phiên bản đã dùng.

Đây là tập nguyên tắc duy nhất được dùng trong toàn bộ Plan 05. Nguyên
tắc có `requirement_score = 3` không được đưa vào system instruction,
không kích hoạt rubric riêng, không được gửi judge và không tham gia tổng
hợp điểm. Trường `alternative_principle_set` trong bundle Plan 02 chỉ là
provenance chẩn đoán lịch sử và bị bỏ qua ở ranh giới Plan 05. Code phải
tái lập tập `>= 4` trực tiếp từ sáu score, đối chiếu với
`required_principle_set` và dừng đóng nếu không trùng chính xác.

`source_question` phải qua audit để bảo đảm chỉ cung cấp đề bài cần thiết,
không chứa đáp án hoặc chỉ dẫn ẩn.

### 2.2. Native conversation history

Nội dung hội thoại phải được truyền bằng cấu trúc message và role native
của API:

1. Tạo message `user` đầu tiên từ `student_prompt`.
2. Parse `conversation_history` thành danh sách có thứ tự theo
   `turn_index`.
3. Ánh xạ mỗi lượt `student` thành message `user`.
4. Ánh xạ mỗi lượt `tutor` thành message `assistant`; riêng Gemini dùng
   role native tương ứng là `model`.
5. Gọi sinh phản hồi ngay sau message `user` cuối cùng.

Ví dụ:

```text
student_prompt                         → user
conversation_history[0], role=tutor   → assistant/model
conversation_history[1], role=student → user
...
target response cần sinh              ← assistant/model
```

Nếu `conversation_history` rỗng, request chỉ có message `user` được tạo
từ `student_prompt`. Không lặp lại `student_prompt` ở cuối history và
không serialize danh sách history thành văn bản JSON nằm trong một
message.

Code phải dùng một biểu diễn message trung gian chung với hai role
`user`/`assistant`, sau đó provider adapter chỉ đổi sang cấu trúc native
của Gemini, Claude hoặc API tương thích OpenAI. System instruction luôn
được truyền qua trường system riêng của provider, không giả làm một lượt
hội thoại.

Trước khi gọi model, validator phải dừng đóng nếu:

- history không parse được thành danh sách;
- `turn_index` không tăng nghiêm ngặt;
- role không thuộc `student`/`tutor`, nội dung rỗng hoặc hai role liên
  tiếp giống nhau;
- chuỗi đầy đủ không bắt đầu và kết thúc bằng lượt học sinh.

Kiểm tra ngày 28/07/2026 cho thấy cả 2.028 candidate hiện hành đáp ứng
hợp đồng này: 665 candidate không có history, 1.363 candidate có history
và 0 chuỗi sai cấu trúc role.

### 2.3. Dữ liệu không được gửi tutor model

Tutor model không được thấy `gold_answer`, fragment học liệu,
`gold_response`, rubric, score, `benchmark_candidate_id`, `sample_id`
hay dữ liệu điều phối khác. Các trường này chỉ thuộc phía evaluator hoặc
runner. Candidate không có nguyên tắc bắt buộc hoặc đang trong review
queue không được đưa vào evaluation chính thức.

## 3. Instruction theo nguyên tắc

Mỗi nguyên tắc có một đoạn instruction ngắn gồm:

1. tên yêu cầu sư phạm bằng tiếng Việt;
2. mục tiêu sư phạm phải đạt;
3. hành vi cần thể hiện;
4. hành vi cần tránh;
5. yêu cầu bảo toàn quyền chủ động của học sinh.

Code ghép instruction, không dùng model để chọn hoặc viết lại instruction.
Nếu có nhiều nguyên tắc, tutor phải đáp ứng từng yêu cầu nhưng được tự
chọn một phản hồi tự nhiên; không buộc chia câu trả lời thành sáu phần.
Mỗi yêu cầu được dựng thành một khối nhiều dòng để con người và model
phân biệt rõ các mục con; tên tiếng Việt hiện hành lần lượt là Thử thách,
Giải thích, Làm mẫu, Luyện tập, Phản hồi và Đặt câu hỏi.

## 4. Panel model, khả năng chạy trên Vertex AI và ngân sách

### 4.1. Ba nhóm model bắt buộc

Panel được chọn theo vai trò so sánh, kế thừa cấu trúc của KMP-Bench chứ
không sao chép tên model. Panel chính dự kiến chỉ có ba model; model thứ
tư chỉ được thêm nếu còn ngân sách:


| Nhóm                                         | Ứng viên hiện tại                                                 | Cách chạy dự kiến                               | Trạng thái                                                              |
| --------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------- |
| Model đóng đa dụng                        | `gemini-3.5-flash`                                                    | API quản lý trên Vertex AI                       | Đã gọi thành công trong Plan 02                                      |
| Model mở/`open-weight` đa dụng             | `Llama 4 Maverick`                                                    | MaaS trên Vertex AI                                | Smoke v2 hoàn thành 10/10                                               |
| Model chuyên biệt cho giáo dục/gia sư    | `SocraticLM`                                                      | Custom endpoint trên Vertex AI                   | Triển khai thất bại; khoảng trống panel vẫn còn                           |
| Model đóng khác nhà cung cấp, tùy chọn | `Claude Sonnet 4.6`                                                   | Partner MaaS trên Vertex AI                        | Chỉ thêm nếu dự toán sau pilot còn nằm trong trần                 |

`SocraticLM` được chọn ban đầu vì được huấn luyện cho dạy học theo phương
pháp Socrates và có trọng số công khai, nhưng nhánh triển khai hiện đã
thất bại và không đi tiếp trong cấu hình đang hoạt động. Tooling và
lifecycle manifest được giữ lại để truy vết, không được dùng làm bằng
chứng rằng model đã vượt smoke. `TutorChat-LLM` hoặc một model
chuyên biệt có bằng chứng tốt hơn chỉ được thay vào sau khi có cách truy
cập, cấu hình tái tạo được và smoke thành công.

Table 1 của KMP-Bench cho thấy `TutorChat-LLM` đạt `Overall Acc = 31,9`,
cao hơn `SocraticLM = 18,5` và `MathChatsync-LLM = 15,3`; model do chính
nhóm KMP huấn luyện là `KMP-LM-7B` còn cao hơn ở mức `37,0`. Tuy nhiên,
`TutorChat-LLM` trong thí nghiệm này là Qwen2.5-Math-7B được nhóm
KMP-Bench fine-tune trên TutorChat, không phải checkpoint
`Llemma-7B-32K-MathMix` do paper TutorChat công bố. KMP-Bench không cung
cấp model ID công khai cho checkpoint chính xác này trong paper. Vì vậy,
đây là ứng viên khoa học nên ưu tiên xác minh, nhưng chưa được thay vào
registry chạy được cho đến khi có checkpoint, giấy phép và smoke test.

Google xác nhận LearnLM đã được tích hợp trực tiếp vào Gemini từ dòng 2.5,
không có model/config ID hay tham số API riêng. Cấu hình thử nghiệm dùng
cùng `gemini-3.5-flash`, generation config và dữ liệu với baseline, nhưng
thay bundle v2 bằng `instruction_bundle_v3_learnlm.yaml` dựa trên LearnLM
Partner Prompt Guide. Kết quả phải được báo là một prompt ablation của
model đóng đa dụng; không được tính thành base model thứ ba hoặc model
chuyên biệt.

### 4.2. Cổng khả thi trên Vertex AI

Trước khi khóa model, mỗi ứng viên phải qua một smoke test tối đa 10
candidate, kiểm:

1. quyền truy cập model/API, region, quota, EULA và giấy phép;
2. native multi-turn role, system instruction và tiếng Việt;
3. output không bị ép vào schema khác với phản hồi gia sư tự nhiên;
4. token usage, độ trễ, retry rate và chi phí thực tế;
5. khả năng resume và xóa endpoint sau khi hoàn thành.

Model API/MaaS dùng tính phí token. Model chuyên biệt tự triển khai dùng
tính phí theo thời gian máy/accelerator, kèm storage và network nếu có;
endpoint phải được tạo ngay trước batch và gỡ ngay sau batch. Provisioned
Throughput không được dùng vì mức cam kết tối thiểu vượt ngân sách dự án.
Tổng upper bound cho dựng, smoke test và inference của endpoint chuyên
biệt là 40 USD. Nếu không thể phục vụ mẫu phân tầng tối thiểu trong trần
này, giảm số candidate hoặc thử model nhỏ hơn; không để endpoint chạy
nhàn rỗi và không tiến hành full deployment theo cảm tính.

Nếu không có model chuyên biệt nào vượt cổng, Plan 05 phải ghi đây là
khoảng trống và dừng trước khi gọi panel là hoàn chỉnh. Không âm thầm thay
bằng model đa dụng.

### 4.3. Trần ngân sách 250 USD

`hard_budget_usd = 250` cho **toàn bộ experiment**, gồm cả các request đã
chạy ở Plans 01–03. Không được hiểu đây là 250 USD mới dành riêng cho
Plan 05 trở đi.

Snapshot giá chính thức ngày 28/07/2026, đơn vị USD trên một triệu token:


| Model/cách chạy                 | Input | Output, gồm reasoning khi provider tính chung | Batch input | Batch output |
| --------------------------------- | ----: | ----------------------------------------------: | ----------: | -----------: |
| Gemini 3.5 Flash, Global Standard |  1,50 |                                            9,00 |        0,75 |         4,50 |
| Llama 4 Maverick MaaS             |  0,35 |                                            1,15 |       0,175 |        0,575 |
| Claude Sonnet 4.6                 |  3,30 |                                           16,50 |        1,65 |         8,25 |

Nguồn giá:
`https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing`.
Giá phải được chụp lại trong manifest ngay trước mỗi run; bảng trên không
được dùng như giá cố định dài hạn.

Usage thành công đã ghi trong các bundle Plan 02:

- Gemini 3.5 Flash: 5.132.727 input token và 5.211.735
  output-plus-reasoning token;
- Gemini 2.5 Flash: 626.474 input token và 246.280
  output-plus-reasoning token.

Quy đổi theo giá Standard Global hiện tại cho ước lượng khoảng 55,41 USD:
54,60 USD cho Gemini 3.5 Flash và 0,80 USD cho Gemini 2.5 Flash. Đây là
ước lượng từ usage metadata, không thay thế hóa đơn Google Cloud. Trước
bất kỳ run mới nào, runner phải nhận `actual_spend_to_date_usd` từ billing
report hoặc một giá trị UET xác nhận; mặc định đóng là 56 USD nếu chưa có
số billing chính xác.

Phân bổ bảo thủ hiện tại:


| Giai đoạn                                                        | Trần chi phí |
| ------------------------------------------------------------------ | -------------: |
| Chi phí lịch sử Plans 01–03, làm tròn trần                  |         56 USD |
| Smoke test, EULA/quota và dựng–gỡ endpoint model chuyên biệt |         20 USD |
| Pilot 80 candidate, ba target configuration và một judge         |         55 USD |
| Phần chạy chính còn lại                                       |         94 USD |
| Dự phòng retry, biến động token và sự cố endpoint          |         25 USD |
| **Tổng**                                                          |    **250 USD** |

Pilot hiện hành gồm 80 candidate × 3 target configuration, tương ứng 240
phép chấm bằng Gemini 3.5 Flash judge. Ba cấu hình là Gemini baseline,
Llama 4 Maverick và cùng Gemini với LearnLM-oriented prompt. Pilot được chọn
theo bao phủ có chủ đích, không phải mẫu đại diện cho phân bố quần thể. Do không còn đủ thời gian tổ chức
một lượt chấm mù độc lập mới của chuyên gia, kết quả judge chỉ là kết quả
thăm dò; project lead sẽ tự rà các ca bất đồng, độ tự tin thấp và lỗi nghiêm
trọng. Hai cấu hình Gemini phải được báo riêng theo `target_run_id`, đồng
thời tách khỏi Llama; không được gộp chỉ vì dùng cùng `model_id`.
Cận trên gồm mọi retry là 3,29184 USD cho Gemini baseline, 0,534624 USD
cho Llama, 3,43584 USD cho Gemini+LearnLM prompt và 42,58944 USD cho judge;
tổng 49,851744 USD, dưới trần pilot 55 USD.

### 4.4. Dự toán khả thi trước triển khai

Dùng giả định bảo thủ ban đầu:

- mỗi target call: 1.200 input token và 400 output token;
- mỗi judge call: 5.000 input token và 2.000
  output-plus-reasoning token;
- 1.400 candidate × 3 target configuration = 4.200 response;
- Gemini judge chấm đủ 4.200 response;
- không gọi thêm Claude judge trong dự toán hiện tại.

Theo giá Standard, chưa tính model chuyên biệt tự triển khai:


| Hạng mục                                      |    Ước tính |
| ----------------------------------------------- | -------------: |
| Gemini baseline trên 1.400 candidate           |       7,56 USD |
| Llama target trên 1.400 candidate              |       1,23 USD |
| Gemini+LearnLM prompt trên 1.400 candidate     |       7,56 USD |
| Gemini judge trên 4.200 response               |     107,10 USD |
| **Tổng API đã biết của phần tương lai** | **123,45 USD** |

Dự toán 123,45 USD này lớn hơn trần 94 USD đã dành cho phần chạy chính
sau pilot. Vì vậy, full run 1.400 mẫu với cả ba cấu hình **chưa được phép
chạy** trong ngân sách hiện hành; phải dùng usage thực tế của pilot để giảm
quy mô, dùng batch hợp lệ hoặc được UET phân bổ lại ngân sách. Các điều kiện
bắt buộc khác là:

1. judge trả toàn bộ rubric trong một call, không gọi theo từng tiêu chí;
2. endpoint model chuyên biệt có time-to-live cứng và bị gỡ ngay sau batch;
3. pilot đo token thực tế trước khi cho phép phần chạy chính;
4. không tự động thêm model thứ tư;
5. báo riêng nhánh target–judge cùng là Gemini 3.5 Flash.

Nếu Batch API giữ nguyên native history, system instruction, schema và
không làm thay đổi điều kiện so sánh, có thể dùng Batch để hạ chi phí.
Dự toán và budget gate vẫn phải dùng giá Standard làm upper bound cho đến
khi batch request được xác nhận hợp lệ.

Trước mỗi giai đoạn, code phải dự toán từ giá Vertex AI được chụp ngày
chạy và token count thực tế. Công thức tối thiểu:

```text
API/MaaS cost = input_tokens / 1.000.000 × input_usd_per_million
              + output_and_reasoning_tokens / 1.000.000
                × output_usd_per_million

self-deployed cost = endpoint_hours × machine_accelerator_price
                   + storage_and_network_cost
```

Dự toán phải tính riêng target generation, judge pilot, judge chính,
retry tối đa và chi phí endpoint chuyên biệt. Với pool 1.400 candidate và
ba target configuration, có 4.200 target responses trước retry; không được chỉ dự
toán chi phí target rồi bỏ qua judge.

Runner phải chạy theo batch có cost ledger tăng dần, cộng cả chi phí lịch
sử và dừng trước batch kế tiếp nếu:

```text
actual_spend_to_date
+ current_plan_spend
+ upper_bound(next_batch)
+ reserve
> 250 USD
```

Nếu vượt dự toán, thứ tự giảm phạm vi là:

1. bỏ `Claude Sonnet 4.6` tùy chọn;
2. giữ Claude chỉ ở tập calibration nhỏ và dùng một judge duy nhất cho
   phần chạy chính;
3. giảm số candidate nhưng vẫn phân tầng theo lớp, nguyên tắc và family;
4. giảm giới hạn output khi pilot chứng minh không làm cụt phản hồi.

Không được bỏ một trong ba nhóm model bắt buộc chỉ để giữ số candidate.
Batch API chỉ được dùng nếu provider hỗ trợ native history tương đương và
không làm thay đổi cấu hình sinh.

Mỗi dòng `model_registry.csv` phải ghi `model_class`, `selection_role`,
`scientific_basis`, `operational_basis`, `specialization_evidence`,
`access_mode`, `region`, `license`, `language_support`,
`native_multiturn_status`, giá input/output hoặc giá endpoint, kết quả
smoke test và `selection_status`. Giá và model version phải được kiểm lại
ngay trước run manifest; không đổi model sau khi đã xem kết quả chính.

## 5. Cấu hình sinh phản hồi

- Một response cho mỗi cặp model–candidate trong pilot.
- Cùng giới hạn output và cùng nội dung instruction; tham số riêng của
  từng API được ghi đầy đủ thay vì giả định mọi provider có cùng semantics.
- Code tái sử dụng đặt tại `src/edu_benchmark/benchmark_evaluation/`:
  `dialogue_transport.py` chịu trách nhiệm parse, validate và tạo chuỗi
  message trung gian; `provider_adapters.py` chỉ ánh xạ chuỗi đó sang API
  native; `instruction_bundle.py` tải và kiểm bundle có phiên bản, còn
  `prompt_builder.py` chỉ dựng system instruction từ bundle đã kiểm.
  CLI mỏng đặt tại `scripts/benchmark_evaluation/`.
- Test đặt tại `tests/benchmark_evaluation/`, tối thiểu phải bắt được:
  history bị stringify thành một prompt, sai role, sai thứ tự, lặp
  `student_prompt`, history kết thúc bằng tutor và adapter làm thay đổi
  nội dung lượt thoại.
- Không lưu hoặc yêu cầu chain-of-thought.
- Ghi tăng dần, resume, retry và hash input/config như runner hiện tại;
  mỗi record lưu nguyên `system_prompt`, `user_prompt` cuối cùng và toàn
  bộ `conversation_messages` có role. Các hash tương ứng vẫn được giữ và
  validator phải đối chiếu lại với nội dung đã lưu; không tạo bảng request
  riêng.
- Khi một API call lỗi, runner phải in ngay candidate, attempt và exception
  ra terminal, đồng thời ghi tăng dần traceback cùng HTTP status/body vào
  `run_errors.jsonl`. File lỗi không chứa prompt hay credential. Lỗi 4xx
  không có khả năng hồi phục như 400/403/404 không được retry; 408/409/425/
  429 và lỗi 5xx vẫn theo `max_retries`.
- Mỗi record phải lưu `finish_reason`, `response_status` và
  `completion_issue`. `MAX_TOKENS`, `length` hoặc lý do kết thúc không
  thành công tương đương được giữ làm evidence nhưng chuyển vào
  `needs_review`; manifest không được ghi `completed`. Hợp đồng này áp
  dụng từ smoke v2; không tự điền ngược `finish_reason` cho smoke v1 khi
  provider metadata gốc không còn trong artifact.
- Smoke v2 giữ `max_output_tokens = 1024` và tái sử dụng chính xác 10
  `candidate_id` từ manifest smoke v1. Việc khóa cùng mẫu, model và giới
  hạn output giúp thay đổi quan sát được chủ yếu đến từ bundle `v2`.
- Mỗi record và manifest ghi rõ `experiment_id`, `plan_id`,
  `pipeline_stage` và `run_id` để một file tách khỏi thư mục vẫn xác định
  được phase và lần chạy.
- Khóa budget và số request trước khi chạy.

### 5.1. Nhánh SocraticLM tự triển khai

Trạng thái vận hành: **thất bại, không hoạt động**. Nội dung dưới đây được
giữ làm provenance của phương án đã thử; runner không được đưa
SocraticLM vào pilot hoặc full run nếu chưa có một deployment mới vượt
toàn bộ cổng smoke.

SocraticLM dùng checkpoint
`CogBase-USTC/Qwen2.5-Math-7B-Instruct-SocraticLM`, không thay thế caller
Gemini hoặc Llama. Script
`scripts/benchmark_evaluation/manage_socraticlm_endpoint.py` sở hữu vòng
đời build–deploy–status–cleanup; runner hiện có nhận
`--provider vertex-endpoint` và gọi custom vLLM endpoint bằng Vertex
`rawPredict`.

Deployment mặc định dùng `us-central1`, `g2-standard-12`, một GPU L4,
vLLM `0.9.2`, một replica và giới hạn hai giờ. Lifecycle manifest khóa
đúng project, endpoint, model, giá snapshot và `delete_by`; runner từ chối
chạy nếu manifest không còn trạng thái `deployed`, đã quá hạn hoặc không
khớp câu lệnh. Chi phí được tính theo thời gian endpoint, không giả làm
giá token. Sau smoke phải chạy cleanup; chỉ ghi `cleanup_completed` khi
các lệnh undeploy/xóa thực sự thành công hoặc tài nguyên đã không còn.
Giấy phép trong model card mang nhãn `other`, vì vậy deployment cần cờ
xác nhận UET đã tự xem điều khoản; cờ này không phải kết luận pháp lý.
Sau lỗi deployment đầu tiên, pipeline còn bắt buộc cấp
`roles/artifactregistry.reader` ở đúng phạm vi repository cho Vertex AI
Service Agent trước khi upload model. Một lần chạy lại sau lỗi hậu build
được phép tái sử dụng đúng image đã kiểm tra còn tồn tại; không build lại.
Lỗi gcloud tiếp theo phải ghi cả command, return code và đuôi
stdout/stderr vào lifecycle manifest.
Vì `gcloud ai models upload --format=value(name)` có thể hoàn tất nhưng
không in resource name, manager không được suy ra thất bại từ stdout rỗng.
Nó phải truy vấn Model Registry theo đúng display name và container image,
chỉ tiếp tục khi tìm thấy duy nhất một resource. Endpoint create dùng cùng
quy tắc; nhiều kết quả trùng phải dừng đóng thay vì tự chọn.

### 5.2. Cấu hình Gemini với system instruction định hướng LearnLM

Đã cài dưới run ID `target_gemini35_learnlm_prompted`, dùng đúng base model
`gemini-3.5-flash`, native history, seed và giới hạn output của baseline.
Bundle `instruction_bundle_v3_learnlm.yaml` giữ nguyên sáu khối KMP của v2
và thêm lớp chất lượng theo năm định hướng trong LearnLM Partner Prompt
Guide: học chủ động, quản lí tải nhận thức, thích ứng người học, khơi gợi
tò mò và siêu nhận thức. Lớp này bị ràng buộc không tự thêm câu hỏi, bài
luyện, thử thách, làm mẫu hay hành vi KMP không thuộc tập `score >= 4`.

Manifest lưu bundle version/hash và run ID riêng. Phân tích coi đây là
`prompted configuration` để đo tác động của system instruction, không gọi
đây là LearnLM model riêng và không dùng nó để lấp vị trí model chuyên biệt.

## 6. Cách chấm

Theo hướng KMP-Bench, judge nhận bối cảnh, căn cứ chuyên môn, hai phản hồi
được ẩn danh thành `response_1` và `response_2`, cùng đúng tập tiêu chí đã
kích hoạt. Một phản hồi là `gold_response`, phản hồi còn lại là output của
target model, nhưng danh tính này không xuất hiện trong request. Code tráo
thứ tự bằng seed cố định và chỉ khôi phục ánh xạ sau khi judge trả kết
quả.

### 6.1. Contract system prompt và user prompt

System prompt được gửi qua trường system native của Claude, tách khỏi một
user message duy nhất. System prompt phải giải thích rõ ý nghĩa của mọi
nhãn dữ liệu trong user prompt:

- `Lớp`: căn cứ để đánh giá mức phù hợp lứa tuổi;
- `Bài học`: chủ đề chuyên môn của tình huống;
- `Mức nhận thức Bloom`: căn cứ hỗ trợ về mức nhận thức, không ghi đè bối
  cảnh hội thoại;
- `Câu hỏi nguồn`: bài tập hoặc yêu cầu gốc;
- `Đáp án chuyên môn`: neo về nội dung đúng, không phải chiến lược sư phạm
  bắt buộc;
- `Lời mở đầu của học sinh`: lượt học sinh đầu tiên của candidate;
- `Lịch sử hội thoại`: các lượt tiếp theo theo đúng thứ tự trước response
  cần chấm;
- `Căn cứ học liệu`: nội dung SGK/SGV dùng để kiểm chứng;
- `Các tiêu chí phải áp dụng`: toàn bộ và chỉ những tiêu chí judge phải
  chấm;
- `Danh mục lỗi nghiêm trọng`: các lỗi judge phải kiểm độc lập trên hai
  response;
- `Hai phản hồi`: hai response đã được ẩn danh và tráo vị trí.

System prompt phải nói rõ mọi nội dung trong bối cảnh, lịch sử, học liệu,
tiêu chí, lỗi và hai response đều là **dữ liệu để đánh giá**, không phải
instruction mới dành cho judge. Không dịch hoặc sửa giá trị dữ liệu; chỉ
Việt hóa nhãn trình bày trong user prompt. Tên trường kỹ thuật trong JSON
output của judge vẫn dùng tiếng Anh để validator xử lý ổn định.

User prompt động dùng Markdown, không serialize toàn bộ request thành một
JSON. Khuôn tối thiểu là:

```markdown
# Dữ liệu đánh giá

## Bối cảnh học tập

- Lớp: ...
- Bài học: ...
- Mức nhận thức Bloom: ...
- Câu hỏi nguồn: ...
- Đáp án chuyên môn: ...
- Lời mở đầu của học sinh: ...

### Lịch sử hội thoại

1. Học sinh: ...
2. Gia sư: ...
3. Học sinh: ...

## Căn cứ học liệu

### <Tên SGK/SGV> — <Tên bài học>

<Nội dung fragment 1>

-----

<Nội dung fragment 2 có cùng heading, nếu có>

## Các tiêu chí phải áp dụng

### <Tên tiêu chí>

- Dấu hiệu cần quan sát: ...
- Ranh giới: ...
- Mức tốt: ...
- Trường hợp gần đạt: ...
- Mức không đạt: ...

## Danh mục lỗi nghiêm trọng

### <Tên lỗi>

- Mô tả: ...
- Dấu hiệu kích hoạt: ...
- Các tiêu chí bị ảnh hưởng trong request này: ...

## Hai phản hồi

### response_1

...

### response_2

...
```

`position` là metadata kỹ thuật và không được gửi judge. Code nhóm các
fragment theo đúng cặp `book_title + lesson_title`. Mỗi nhóm chỉ tạo một
heading ghép từ hai trường này; các nội dung `content` trong cùng nhóm
giữ nguyên thứ tự truy vết và được phân cách mềm bằng một dòng `-----`.
`fragment_id`, `material_type`, `location_note`, `status` và metadata
nguồn khác chỉ được lưu nội bộ để audit. Không gộp hai nhóm có heading
khác nhau và không gửi ID.

Mỗi tiêu chí gửi judge chỉ gồm tên, dấu hiệu quan sát, ranh giới và ba
anchor tốt–gần đạt–không đạt. `scope`, `tier`, `principle_id`, `rubric_id`
và mọi ID nội bộ không được gửi. Code vẫn giữ `tier` và `principle_id` để
chọn đúng tập tiêu chí trước khi dựng prompt.

Rubric được kích hoạt hoàn toàn bằng code: luôn dùng đúng bốn rubric chung
và đúng ba rubric riêng cho mỗi nguyên tắc có `requirement_score >= 4`.
Mọi nguyên tắc còn lại và rubric riêng tương ứng bị loại trước khi dựng
request. Judge record lưu tập nguyên tắc bắt buộc và
`applicable_rubric_ids`; schema dừng đóng nếu tập rubric chứa nguyên tắc
ngoài tập bắt buộc hoặc thiếu rubric của một nguyên tắc trong tập. Các ID
này chỉ xuất hiện trong metadata/hậu xử lý.

Với từng tiêu chí, judge xuất đúng `criterion_name`, một trong ba giá trị
`response_1`, `response_2`, `tie`, lý do đối xứng, dấu hiệu từ mỗi response
và độ tự tin. Code kiểm tên thiếu, thừa, trùng hoặc ngoài catalog rồi mới
ánh xạ về `rubric_id` nội bộ và khôi phục `Win/Tie/Lose` của target.

### 6.2. Lỗi nghiêm trọng và cổng hậu xử lý

Nguồn serious-error vẫn có thể giữ các cột quản trị của Plan 04, nhưng
judge chỉ được thấy:

- tên lỗi đã Việt hóa;
- mô tả;
- dấu hiệu kích hoạt;
- tên các tiêu chí bị ảnh hưởng **và đang hoạt động trong request này**.

Không gửi `error_id`, `affected_rubric_ids`, `suggested_action`,
`aggregation_rule`, `confirmation_owner` hoặc `status`. Với mỗi lỗi, code
tính:

```text
affected_criterion_names
  = affected_rubric_ids của lỗi
    ∩ applicable_rubric_ids của candidate
  → map sang tên tiêu chí
```

Judge kiểm từng lỗi độc lập trên `response_1` và `response_2`; cùng một lỗi
có thể xuất hiện ở một response, cả hai hoặc không response nào. Judge chỉ
trả đúng tên lỗi, `detected`, `confidence` và lý do riêng cho từng
response. Code kiểm tên rồi ánh xạ về `error_id` nội bộ.

Sau khi khôi phục target/reference, code áp cổng xác định cho từng tiêu chí
nằm trong giao ở trên:

| Target mắc lỗi | Reference mắc lỗi | Kết quả target trên tiêu chí bị ảnh hưởng |
| --- | --- | --- |
| Không | Không | Giữ phán quyết thô của judge |
| Có | Không | `Lose` |
| Không | Có | `Win` |
| Có | Có | `Lose` |

Hàng cuối là quyết định vận hành bất đối xứng của UET: nếu target response
mắc lỗi nghiêm trọng thì target vẫn `Lose`, kể cả reference mắc cùng lỗi.
Quy tắc này không được trình bày như kết quả rút ra từ KMP-Bench. Nếu nhiều
lỗi cùng ảnh hưởng một tiêu chí, tiêu chí chỉ bị điều chỉnh một lần.
Serious error không tạo điểm độc lập và không tự kích hoạt tiêu chí ngoài
request.

Mỗi record phải giữ đồng thời:

- `raw_criterion_judgments`: phán quyết Claude trả trước cổng lỗi;
- `serious_error_findings`: lỗi phát hiện độc lập trên hai response;
- `adjusted_criterion_judgments`: phán quyết sau cổng lỗi dùng để tổng hợp
  chỉ số chính;
- `criterion_adjustments`: lỗi nào đã đổi tiêu chí nào và từ giá trị nào
  sang giá trị nào.

Phán quyết tổng thể do judge trả được giữ nguyên như kết quả phụ; cổng lỗi
không dùng nó để ghi đè phán quyết theo tiêu chí và cũng không dùng phán
quyết tổng thể để tính `Overall Acc`.

### 6.3. Smoke chấm mù bằng Gemini 3.5 Flash trước pilot

Trước pilot 80 candidate, chạy một smoke nhỏ, độc lập để kiểm tra prompt
và pipeline chấm:

- input là đúng 10 candidate chung đã chạy thành công với
  `gemini-3.5-flash` và `Llama 4 Maverick`;
- tạo 20 phép so sánh: 10 output Gemini–gold và 10 output Llama–gold;
- dùng `gemini-3.5-flash` làm judge tạm thời;
- mỗi phép so sánh dùng một judge call và trả toàn bộ tiêu chí áp dụng,
  lỗi nghiêm trọng, phán quyết tổng thể và các độ tự tin trong cùng một
  JSON;
- `response_1`/`response_2` được tráo bằng seed tái tạo được; model ID,
  danh tính gold và kết quả đánh giá nhanh trước đó không được gửi judge;
- record sau khi gọi lưu đủ system prompt, user prompt Markdown, response
  của judge, seed, ánh xạ hậu xử lý, phán quyết thô và phán quyết đã điều
  chỉnh; ánh xạ ID không nằm trong prompt.

Smoke này chỉ kiểm tính đúng của request, schema, lựa chọn rubric, tính
đối xứng, cổng lỗi và mức hợp lý sơ bộ của phán quyết. Nó không thay thế
đánh giá con người và không dùng để ước lượng thứ hạng model. Do không còn
thời gian cho một lượt chấm người mới, pilot chỉ dùng các phán quyết chuyên
gia đã có trên smoke anchor làm điểm kiểm tra định tính.

Smoke Gemini có trần riêng `1 USD`, được tính vào ngân sách smoke test,
không tính vào trần `55 USD` của pilot 80 candidate. Không được tự động
chuyển sang pilot nếu smoke còn lỗi parse, thiếu rubric, lộ ánh xạ, sai
giao rubric bị lỗi ảnh hưởng, không khôi phục được `Win/Tie/Lose` hoặc
không tái tạo được điều chỉnh sau cổng lỗi.

Judge pilot dùng `gemini-3.5-flash` trên 80 candidate × 3 target
configuration, tạo 240 phép so sánh. Không có ngưỡng đồng thuận người–model mới ở lần chạy
này; thay vào đó, project lead tự rà theo danh sách ưu tiên gồm bất đồng
rubric–overall, độ tự tin thấp, lỗi nghiêm trọng và chênh lệch lớn giữa ba
target configuration. Vì vậy, pilot chỉ đánh giá khả năng vận hành và tính hợp lý
sơ bộ, chưa xác nhận độ đúng của judge. Phải báo riêng kết quả khi target
và judge cùng là `gemini-3.5-flash`; kết quả này không được dùng một mình
để kết luận model Gemini tốt hơn hoặc kém hơn model khác.

Mỗi cặp candidate–target response chỉ dùng **một judge call cho mỗi judge**.
Một judge call phải trả đồng thời phán quyết của toàn bộ tiêu chí chung,
toàn bộ tiêu chí riêng đang được kích hoạt, lỗi nghiêm trọng nếu có và
phán quyết tổng thể. Không gọi riêng model chấm cho từng rubric.

### 6.3.1. Hợp đồng pilot 80 mẫu đang hoạt động

Manifest khóa tại
`outputs/benchmark_evaluation/pilot_80_v1/candidate_manifest.json` và chỉ
được sinh bằng code xác định. Pilot có các ràng buộc:

- đúng 80 candidate, 20 mẫu cho mỗi lớp 6–9 và 80 `sample_id` khác nhau;
- giữ nguyên 10 smoke anchor để so sánh nối tiếp;
- lấy toàn bộ 8 candidate `Challenge`; có ít nhất 12 `Practice`, 12
  `Modelling` và ít nhất 20 cho mỗi nguyên tắc còn lại;
- có ít nhất 30 mẫu có history, 30 mẫu không history, 20 mẫu cho mỗi nhóm
  Bloom và 12 mẫu cho mỗi kích thước tập nguyên tắc 1/2/3;
- bao phủ ít nhất 32 cặp lớp–bài học.

Manifest thực tế đạt 20 mẫu mỗi lớp, 80 family, 54 cặp lớp–bài học; incidence
sáu nguyên tắc lần lượt là Challenge 8, Explanation 48, Feedback 41,
Modelling 14, Practice 12 và Questioning 35. History rỗng/không rỗng là
39/41; Bloom remember/understand/apply là 24/31/25; kích thước tập 1/2/3
là 23/36/21. Do chủ động lấy quá mẫu nguyên tắc hiếm, mọi tỷ lệ không trọng
số của pilot không được diễn giải thành ước lượng quần thể.

Hai smoke anchor còn dùng làm điểm kiểm tra định tính:

- `BC-HNMU-G7-R0204-STT7-AI14`: chuyên gia xác nhận reference chỉ thiếu giá
  trị tăng thêm, không phải lỗi nghiêm trọng;
- `BC-HNMU-G7-R0207-STT10-AI10`: chuyên gia đối chiếu `gold_answer` và xác
  nhận câu “làm mất hoàn toàn dữ liệu thật” là lỗi nghiêm trọng. Judge smoke
  đã bỏ sót lỗi này, nên đây là ca bắt buộc phải soi lại trong pilot.

### 6.3.2. Hợp đồng full 1.400 mẫu đã cài đặt

Pool full lấy đúng và đủ từ
`outputs/benchmark_candidate_pool/eligible_without_plan03_review.csv`.
Manifest khóa tại
`outputs/benchmark_evaluation/full_1400_v1/candidate_manifest.json`, kiểm
đúng 1.400 ID duy nhất, mọi phép join, tập nguyên tắc `requirement_score >=
4` và SHA-256 của toàn bộ nguồn.

Phương án hybrid lịch sử được khóa ngày 29/07/2026 là:

1. sinh full 1.400 response cho cả ba cấu hình: Gemini baseline, Llama 4
   Maverick và Gemini với prompt định hướng LearnLM, tổng 4.200 response;
2. dùng một tập khóa 30 candidate để chấm cả ba cấu hình, tổng 90 phép so
   sánh, nhằm đo chi phí và kiểm tra vận hành judge;
3. chỉ khi cost-pilot đạt cổng mới cân nhắc chấm full Gemini baseline và
   Llama, tổng 2.800 phép so sánh; nhánh LearnLM không được chấm full.

Wrapper target là
`scripts/benchmark_evaluation/run_full_1400_targets.sh`. Cận trên bảo thủ
của ba target, đã gồm tối đa hai retry, là 127,09032 USD. Với mức chi lịch
sử 56,52 USD và dự phòng 25 USD, batch này vẫn nằm dưới hard cap 250 USD.
Ước tính ngoại suy từ smoke chỉ khoảng 18,678072 USD, nhưng không được dùng
thay cổng bảo thủ khi runner quyết định cho phép chạy.

### 6.3.2a. Recovery Gemini baseline do giới hạn 1.024 token

Lần full target Gemini baseline đầu tiên ghi đủ 1.400 record nhưng có 436
record `MAX_TOKENS`: 964 mẫu hoàn chỉnh, 436 mẫu `needs_review`, không có
API exception. Runner trả mã thoát 2 theo thiết kế fail-closed nên wrapper
`set -e` dừng trước Llama và LearnLM. Chi phí ước tính của lượt này là
11,2495365 USD; mốc chi phí lịch sử tạm thời tăng từ 56,52 lên 67,7695365
USD.

Recovery lượt một chạy lại đúng 436 ID được khóa từ `completion_issue =
output_truncated`, giữ model, prompt, seed, bundle và
`thinking_level=MEDIUM`, chỉ tăng `max_output_tokens` từ 1.024 lên 1.536.
Kết quả thực tế là 417 mẫu hoàn chỉnh và 19 mẫu tiếp tục `MAX_TOKENS`; một
exception response rỗng đã thành công ở retry kế tiếp. Chi phí lượt này là
4,7877885 USD, đưa mốc chi phí tạm thời lên 72,557325 USD. Baseline chính
vẫn chưa bị sửa nhờ cổng fail-closed.

Theo quyết định UET tiếp theo, code tái sử dụng nguyên vẹn 417 kết quả đã
hoàn chỉnh và chỉ khóa lại 19 ID còn bị cắt. Lượt follow-up giữ mọi cấu hình
ngữ nghĩa, tăng riêng `max_output_tokens` lên 2.048 và dùng 19 worker. Cận
trên bảo thủ gồm tối đa hai retry là 1,307124 USD. Wrapper là
`scripts/benchmark_evaluation/run_recover_gemini35_followup_2048.sh`.

Cả hai lượt dùng cùng staging gốc
`/tmp/edu-benchmark-plan05-gemini-recovery-1536`; follow-up chỉ tạo thư mục
con tạm `followup_2048`, không tạo output recovery trong experiment. Sau khi
19/19 response đều `STOP`/`END_TURN`, code thay đúng 19 dòng trong bundle
recovery, kiểm đủ 436/436, rồi mới dựng lại `run_responses.jsonl` chính và
publish bằng phép thay thế nguyên tử. Nếu follow-up còn một mẫu bị cắt,
417 kết quả lượt trước và baseline chính đều được giữ nguyên. Sau merge,
staging bị xóa; hash, tập ID, token cap và chi phí từng lượt được nhúng trong
`recovery_history` của manifest chính. Chỉ khi baseline đạt 1.400/1.400
`completed` mới resume wrapper full để chạy Llama và LearnLM.

Wrapper full sau recovery phải xác minh bundle Gemini đủ 1.400 mẫu hoàn
chỉnh rồi bỏ qua hoàn toàn lời gọi baseline; không được resume baseline bằng
runner chung vì có thể ghi lại manifest và làm mất `recovery_history`. Nó chỉ
chạy Llama, đọc chi phí thực tế từ manifest Llama rồi mới mở budget gate cho
LearnLM. Wrapper judge chặn đóng nếu một trong ba target chưa đủ 1.400 mẫu;
nếu người dùng không truyền mốc chi phí mới, nó tái dựng mốc này từ 56,52
USD lịch sử cùng chi phí manifest của cả ba target.

Lượt full Llama đầu tiên dùng 20 worker và hoàn thành 1.314/1.400 mẫu; 86
mẫu còn lại thất bại sau retry. Toàn bộ 1.111 exception ở các attempt đều là
HTTP 429 `RESOURCE_EXHAUSTED`; các response đã hoàn thành đều có
`finish_reason = STOP`, nên đây là lỗi điều tiết lưu lượng chứ không phải lỗi
nội dung hoặc cắt output. Chi phí ước tính đã phát sinh là 0,36434345 USD.
LearnLM chưa được chạy vì wrapper dừng đóng tại Llama.

Runner resume phải đối chiếu ID đã ghi và chỉ gửi lại đúng 86 mẫu còn thiếu,
dùng 2 worker, tối đa hai retry, exponential backoff 15–60 giây và jitter xác
định tối đa 5 giây; `Retry-After` dạng số từ provider được ưu tiên khi lớn
hơn. Manifest phải giữ chi phí cũ, cộng chi phí mới và nối
`resume_history`; không được ghi đè provenance của 1.314 mẫu đã hoàn thành.
Preflight không gọi API đã xác nhận 86 request pending, cận trên 0,574721
USD. Chỉ khi manifest Llama đạt đủ 1.400 mẫu hoàn chỉnh wrapper mới tự động
chuyển sang LearnLM; judge cost-pilot vẫn bị chặn.

Lượt retry Llama đã hoàn thành đủ 1.400/1.400; 86 mẫu retry đều thành công,
chi phí tăng thêm 0,0248883 USD và chi phí Llama cộng dồn là 0,38923175
USD. Lượt LearnLM sau đó ghi đủ 1.400 record nhưng chỉ 1.014 response hoàn
chỉnh; 386 response có `finish_reason = MAX_TOKENS` và
`completion_issue = output_truncated` ở giới hạn 1.024 token. Không có API
exception hoặc response rỗng; chi phí lượt gốc là 11,2683435 USD.

Theo quyết định UET, recovery LearnLM khóa đúng 386 ID và chạy thẳng ở
`max_output_tokens = 2.048`, giữ model, seed, `thinking_level = MEDIUM`,
bundle `instruction_bundle_v3_learnlm.yaml` và 20 worker. Cận trên bảo thủ
với tối đa hai retry là 27,250056 USD. Wrapper
`scripts/benchmark_evaluation/run_recover_learnlm_2048.sh` dùng staging tại
`/tmp`, chỉ thay 386 dòng trong JSONL chính bằng phép merge nguyên tử khi
tất cả đều hoàn chỉnh; nếu còn mẫu bị cắt thì source bundle được giữ nguyên.
Preflight đúng 386 ID đã đạt và không gọi API.

### 6.3.3. Cost-pilot 30 mẫu và cổng full judge

Code chọn xác định 30 mẫu từ frame `pilot_80_v1`, giữ đủ 10 smoke anchor và
khóa manifest tại
`outputs/benchmark_evaluation/full_1400_v1/judge_cost_pilot_30/candidate_manifest.json`.
Tập này có 30 family khác nhau, phân bố lớp 8/8/7/7, bao phủ đủ sáu nguyên
tắc, ba nhóm Bloom, history rỗng/không rỗng, ba kích thước tập nguyên tắc
và ba nhóm độ dài context. Đây là mẫu để ước tính chi phí và kiểm vận hành,
không phải mẫu đại diện dùng để ước lượng chất lượng quần thể.

Wrapper `scripts/benchmark_evaluation/run_judge_cost_pilot_30.sh` đọc trực
tiếp ba file target full rồi lọc đúng 30 ID bằng code; không gọi model để
lọc và không tạo ba bản target trung gian. Nó tạo đúng 90 phép chấm. Cận
trên bảo thủ với một retry là 15,97104 USD; ngoại suy từ smoke là khoảng
3,223544 USD.

Lượt cost-pilot đầu giữ được 70/90 phép chấm. Runner sau đó nhận diện lỗi
DNS/connection là retryable, resume đúng 20 phép còn thiếu và hoàn thành
bundle 90/90, không còn ID thất bại. Manifest cuối có `status = completed`,
integrity hợp lệ và chi phí cộng dồn 4,446063 USD. Prompt, schema và
generation config không đổi; `run_errors.jsonl` giữ lỗi lịch sử làm provenance.

Wrapper synchronous lịch sử
`scripts/benchmark_evaluation/run_full_1400_judge.sh` chỉ nhận baseline và
Llama, bị đóng bởi cận trên 496,8768 USD. Quyết định tại mục 6.3.7 thay thế
nhánh này bằng Batch API cho cả ba target; wrapper cũ được giữ để truy vết
và không còn là đường chạy hiện hành.

### 6.3.4. Pilot đối chiếu judge OpenAI

UET đã chọn `gpt-5.4-mini` làm judge khác họ Gemini để chạy lại đúng tập
cost-pilot hiện có: 30 candidate × 3 target configuration = 90 phép so
sánh. Mục tiêu là đối chiếu độ ổn định theo tiêu chí, cổng lỗi nghiêm trọng
và các smoke anchor đã có nhận định chuyên gia; đây chưa phải full judge.

Nhánh này dùng snapshot `gpt-5.4-mini-2026-03-17`, Responses API,
`reasoning.effort = medium`, không truyền `temperature`, `store = false` và
Structured Outputs với JSON Schema nghiêm ngặt. Schema chỉ chứa tên tiêu chí
và tên lỗi; ánh xạ ID vẫn do code hậu xử lý. Runner giữ cùng system prompt
v2, cùng dữ liệu, seed tráo vị trí và contract output như Gemini judge.

Caller mới nằm tại `openai_judge.py`; wrapper riêng là
`scripts/benchmark_evaluation/run_openai_gpt54_mini_judge_pilot.sh`.
Kết quả chỉ được ghi vào
`full_1400_v1/judge_cost_pilot_30/judge_openai_gpt54_mini_medium_v1/`,
không đọc hoặc ghi đè bundle Gemini. Wrapper dùng 4 worker, tối đa hai retry
ngoài SDK, ghi JSONL tăng dần và có cận trên bảo thủ 11,97828 USD; chi phí
thực tế phải được lấy từ usage sau run. API key chỉ đọc từ `src/.env`, file
này bị Git bỏ qua và không được hash hoặc ghi vào manifest.

### 6.3.5. Ablation rubric-only v3 sau đối chiếu hai judge

Cost-pilot v2 đã hoàn thành 90/90 phép chấm cho cả Gemini 3.5 Flash và
`gpt-5.4-mini-2026-03-17`. Đối chiếu cho thấy phát hiện lỗi nghiêm trọng
không ổn định theo response đối đầu, dù cùng một reference không đổi. UET
quyết định loại hoàn toàn thành phần lỗi nghiêm trọng khỏi lần judge tiếp
theo và chỉ giữ catalog Plan 04 làm provenance, không gửi model hoặc dùng
để ép phán quyết.

Contract `rubric-only-v3` là một nhánh có phiên bản, không ghi đè v2:

- system prompt và user prompt không nhắc hoặc chứa danh mục lỗi nghiêm
  trọng;
- model chỉ trả `criterion_judgments` và `overall_judgment`;
- code không đọc `serious_errors.csv` khi chuẩn bị request;
- record cuối vẫn giữ `serious_error_findings: []` và
  `criterion_adjustments: []` để downstream cũ không vỡ;
- `adjusted_criterion_judgments` bằng `raw_criterion_judgments`;
- manifest và từng record khóa `judge_output_contract_version =
  rubric-only-v3`, prompt v3/hash và output directory mới, nên không thể
  resume lẫn bundle v2.

Wrapper
`scripts/benchmark_evaluation/run_rubric_only_v3_judge_pilot_30.sh` chạy
tuần tự cùng 90 phép so sánh cho Gemini rồi GPT. Hai output lần lượt là
`judge_gemini35_rubric_only_v3/` và
`judge_openai_gpt54_mini_medium_rubric_only_v3/`. Wrapper giữ nguyên
dataset, seed, cấu hình model và giới hạn 8.192 token để phép so sánh chỉ
thay đổi contract lỗi nghiêm trọng.

Lần chạy API đã hoàn thành 90/90 phép chấm cho mỗi judge. Gemini dùng
structured JSON schema rút gọn ở provider và validator đầy đủ ở local để
khôi phục bốn output lỗi định dạng mà không đổi prompt hoặc dữ liệu. Chi phí
cộng dồn của bundle Gemini là 4,061927 USD; GPT là 1,356143 USD. Agreement
Gemini–GPT đạt 86,7% ở overall và 77,2% ở rubric. Điểm tổng hợp ưu tiên theo
cấu trúc KMP-Bench cho cùng thứ hạng LearnLM-prompted, Gemini baseline,
Llama Maverick; đây vẫn là kết quả thăm dò trên 30 candidate.

### 6.3.6. Ablation gold-answer-only v4 sau audit fragment

Rà soát ngữ nghĩa toàn bộ 30 candidate của cost-pilot cho thấy liên kết
fragment raw-audit không đủ mạnh để dùng làm evidence cấp candidate: 2 mẫu
có fragment sai hoặc không liên quan, 20 mẫu đúng bài nhưng thiếu nội dung
quyết định và chỉ 8 mẫu đủ hoặc gần đủ. Cả 41 fragment duy nhất đều còn
`draft`. Đây là giới hạn của việc tái sử dụng
`raw_audit_all_evidence_fragment_ids`, không phải kết quả audit evidence cấp
candidate.

Theo quyết định UET, contract `gold-answer-only-v4` là nhánh ablation mới,
không ghi đè v2 hoặc v3:

- kế thừa `rubric-only-v3`, nên không gửi hoặc xử lý lỗi nghiêm trọng;
- không đọc `conversion_input_pass_samples.csv` hoặc fragment registry khi
  chuẩn bị request;
- bỏ toàn bộ mục `Căn cứ học liệu` khỏi system/user prompt;
- giữ `learning_evidence_fragment_ids: []` và
  `learning_evidence_included: false` trong record để downstream và audit
  nhận biết rõ chính sách;
- chỉ trong request v4, `RUB-GEN-ACC` được hiển thị là “Chính xác chuyên
  môn và phù hợp đáp án chuẩn”; catalog rubric gốc và ID không đổi;
- tính đúng chuyên môn dùng `gold_answer` làm neo duy nhất. Judge phải chấp
  nhận cách diễn đạt/quy trình tương đương, chỉ phạt khác phương pháp nếu
  câu hỏi bắt buộc phương pháp đó và chọn `Tie` nếu `gold_answer` không đủ
  phân xử;
- system prompt, contract version, request hash và output directory riêng
  ngăn resume lẫn v2/v3.

Prompt v4 nằm tại
`shared/prompts/benchmark_response_judging/system_prompt_gold_answer_only_v4.md`.
Wrapper
`scripts/benchmark_evaluation/run_gold_answer_only_v4_judge_pilot_30.sh`
chạy lại đúng 30 candidate × 3 target configuration cho Gemini và GPT vào
hai thư mục mới. Preflight offline đã đạt 90 phép so sánh cho mỗi judge,
không gọi API. Phép chạy này là ablation để đo thay đổi agreement, đặc biệt
`RUB-GEN-ACC`; nó không chứng minh `gold_answer` đã được HNMU audit đầy đủ.

Lần chạy trả phí đầu tiên hoàn thành 88/90 phép chấm Gemini rồi dừng trước
GPT. Một output dùng biến thể tên “Mức độ chi tiết...” thay cho tên khóa
“Mức chi tiết...”; output còn lại chạm `MAX_TOKENS=8192`. Validator chỉ
chuẩn hóa alias tương đương này khi contract là v4; contract cũ vẫn kiểm
khớp tuyệt đối. Wrapper tách giới hạn token theo provider. Preflight
recovery xác nhận tái sử dụng 88 record, chỉ gọi lại 2 request Gemini ở
12.288 token và giữ GPT ở 8.192 token.

### 6.3.7. Full judge bằng Batch API

Sau khi v4 hoàn thành 90/90 phép chấm cho cả Gemini và GPT, UET quyết định
đưa cấu hình LearnLM-oriented lên ngang hàng với Gemini baseline và Llama
Maverick. Full judge vì vậy gồm 1.400 candidate × 3 target × 2 judge =
8.400 phán quyết. Hai judge vẫn được báo riêng; GPT-5.4-mini là judge chính,
Gemini là sensitivity check, không lấy trung bình cơ học.

Full judge dùng batch bất đồng bộ để giảm 50% đơn giá nhưng giữ nguyên
system prompt, user prompt, blind order, structured output và hậu xử lý v4:

- Gemini dùng Vertex AI Batch tại `global`, input/output JSONL qua một
  bucket GCS riêng;
- GPT dùng OpenAI Batch trên endpoint `/v1/responses`;
- mỗi provider có manifest, budget, raw provider output và
  `run_judgments.jsonl` riêng; runner đồng bộ cũ không bị sửa;
- `custom_id`/`id` bằng `comparison_id`, chỉ phục vụ join và không đi vào
  prompt;
- submit, status, collect và retry là các action idempotent tách biệt;
  chỉ retry đúng ID lỗi; mặc định tối đa một batch retry, còn attempt bổ
  sung phải được UET phê duyệt và ghi riêng cấu hình trong job history;
- collect luôn chạy validator và hậu xử lý local như pilot v4; chỉ publish
  `completed` khi đủ 4.200 record duy nhất và đúng hash request.

Dự toán không dùng cận trên 8.192 output token cho mọi request vì trái với
usage quan sát và làm cổng ngân sách đóng giả. Code dùng p95 chi phí từng
request từ đúng 90 judgment v4, đổi sang đơn giá batch rồi nhân 4.200 và hệ
số an toàn 1,10. Preflight ngày 30/07 cho kết quả:

- Gemini: 132,44616 USD, tương đương khoảng 3,48 triệu đồng theo tỷ giá
  26.299,5 VND/USD; thấp hơn ngân sách Vertex còn lại 5.270.693 đồng sau
  khi giữ riêng 500.000 đồng dự phòng;
- GPT: 46,52802 USD, dưới stage cap 50 USD của billing OpenAI riêng;
- mỗi input có 4.200 dòng; file Gemini 74 MB và OpenAI 77 MB, dưới giới
  hạn input tương ứng.

Wrapper hoạt động là
`scripts/benchmark_evaluation/run_full_1400_judge_batch.sh`; logic dùng lại
nằm trong `batch_judge.py`, CLI điều phối nằm trong `run_batch_judge.py`.
Action `setup` chỉ tạo bucket GCS chuyên dụng khi người dùng chủ động chạy.
Không action nào tự xóa bucket hoặc output cloud.

Kết quả vận hành ngày 30/07/2026:

- GPT-5.4-mini hoàn thành 4.200/4.200 phán quyết;
- Gemini hoàn thành 4.200/4.200 phán quyết sau khi hậu xử lý cục bộ 10
  biến thể tên tiêu chí quan sát được và retry đúng hai output
  `MAX_TOKENS` ở giới hạn 9.000 token;
- cả hai manifest có `status = completed`, `integrity.validated = true`,
  không còn `failed_comparison_ids`.

### 6.4. Vị trí cài đặt, prompt, test và kết quả

Mã dùng lại tiếp tục đặt tại
`src/edu_benchmark/benchmark_evaluation/`. Bản cài đặt v2 đã cập nhật:

- `judge.py`: dựng Markdown, bỏ `scope` và metadata fragment thừa, tính
  giao affected/applicable, kiểm tên, hậu xử lý cổng lỗi và lưu raw cùng
  adjusted judgments;
- `claude_judge.py`: giữ transport Claude làm provenance của lần chạy thất
  bại, không dùng trong smoke thay thế;
- `gemini_judge.py`: gửi native system/user bằng Google Gen AI SDK, khóa
  JSON output, `thinking_level`, usage và finish reason;
- `openai_judge.py`: gửi system/user tách biệt qua Responses API, khóa
  snapshot model, Structured Outputs, reasoning effort, usage và trạng thái;
- `scripts/benchmark_evaluation/run_claude_judge_smoke.py`: điều phối chung
  20 phép so sánh và chọn transport bằng `--provider`; dùng
  `ThreadPoolExecutor` với số worker từ `--concurrency`, `tqdm` hiển thị
  worker/completed/failed/cost, retry/resume và JSONL tăng dần. Toàn bộ diagnostic của mỗi exception — gồm traceback, finish reason,
  partial response và usage nếu provider đã trả kết quả — được in ngay lên
  terminal bằng `tqdm.write`; chính record đó đồng thời được ghi vào
  `run_errors.jsonl`. Cost
  cộng cả judgment thành công và failed attempt có usage;
- `scripts/benchmark_evaluation/run_gemini35_judge_smoke_v2.sh`: wrapper
  executable khóa retry1 ở 8 worker và 8.192 output token để người dùng chạy
  một lệnh;
- `scripts/benchmark_evaluation/run_claude_judge_smoke_v2.sh`: giữ nguyên làm
  provenance, không chạy lại khi chưa chủ động kích hoạt Anthropic.

System prompt v1 đã preflight nhưng chưa gọi API phải được giữ nguyên làm
provenance. Contract mới dùng file có phiên bản mới:

```text
shared/prompts/benchmark_response_judging/system_prompt_v2.md
```

Manifest và mỗi judgment record lưu đường dẫn, version và SHA-256 của
prompt. Mỗi record lưu nguyên system prompt và user prompt Markdown đã gửi
để audit; không tạo thêm 20 file request.

Test phải bổ sung hoặc sửa tại:

- `tests/benchmark_evaluation/test_judge_preparation.py`: lựa chọn rubric,
  Markdown, metadata không được gửi, gom fragment theo heading học liệu
  với thứ tự và dấu phân cách ổn định, giao affected/applicable, không rò
  ID, ánh xạ tên–ID, lỗi ở một/cả hai response và bốn nhánh cổng hậu xử
  lý;
- `tests/benchmark_evaluation/test_claude_judge_runner.py`: JSON parse,
  retry/resume, budget gate, raw/adjusted record, ghi tăng dần, manifest và
  integrity đủ 20 phép so sánh.

Kết quả v2 chỉ đặt tại:

```text
experiments/20260727_170150/outputs/benchmark_evaluation/
  judge_smoke_claude_blind_v2/
    run_manifest.json      # lần thất bại do chưa kích hoạt Marketplace
    run_errors.jsonl
  judge_smoke_gemini35_blind_v2/
    run_judgments.jsonl    # 11 kết quả cấu hình 3.072 token
    run_manifest.json      # incomplete; cost là lower bound
    run_errors.jsonl       # 9 lỗi MAX_TOKENS
  judge_smoke_gemini35_blind_v2_retry1/
    run_judgments.jsonl
    run_manifest.json
    run_errors.jsonl       # chỉ tạo nếu có lỗi
```

Không tạo root output mới ngoài `outputs/benchmark_evaluation/`, không
sao chép rubric/gold/raw candidate vào thư mục run và không sinh thêm báo
cáo cho mỗi request. Retry1 đã được cài đặt và preflight thành công nhưng
**chưa gọi API**. Lần chạy tiếp theo phải dùng output
`judge_smoke_gemini35_blind_v2_retry1` và system prompt v2; không resume
thư mục Gemini cấu hình 3.072 token hoặc thư mục Claude thất bại.

## 7. Tổng hợp điểm

### 7.1. Hai loại phán quyết trong KMP-Bench

KMP-Bench `Section 3.1`, đoạn `Context-Aware Evaluation Criteria and
Method`, viết nguyên văn:

> “This comparison yields a Win, Tie, or Lose outcome for each applicable
> criterion and an overall judgment for the tutor’s entire response.”

Vì vậy paper dùng hai đầu ra khác nhau: phán quyết cho từng tiêu chí và
một phán quyết tổng thể riêng. `Section 4.1`, đoạn `Metrics`, tiếp tục mô
tả `Overall Judgement Acc.` là win rate từ phán quyết toàn cục của
evaluator, còn `Overall Acc.` là chỉ số tổng hợp từ `General-Level Acc.`
và sáu `Principle-Level Acc.`. `Table 1` báo hai cột này riêng biệt.

Trong dự án này:

- `Overall Acc.` tính từ phán quyết theo tiêu chí là chỉ số chính để so
  sánh và xếp hạng model;
- `Overall Judgement Acc.` từ phán quyết toàn cục của judge chỉ là chỉ số
  phụ để tương thích và chẩn đoán, không ghi đè tiêu chí hoặc thứ hạng
  chính;
- cổng lỗi chỉ điều chỉnh phán quyết theo tiêu chí; phán quyết tổng thể thô
  vẫn được lưu riêng để kiểm tính nhất quán.

Nguồn: KMP-Bench `Section 3.1`, `Section 4.1`, `Table 1`, `Appendix F`;
truy vết nội bộ `TR-P002`, claims `TR-C008` và `TR-C009`.

### 7.2. Chỉ số chính — phép ký hiệu hóa mô tả của KMP-Bench

Paper nói mọi `Acc` trong KMP-Dialogue là `win rate`, nhưng không in các
phương trình dưới đây và không phát biểu trực tiếp cách quy đổi `Tie`.
Do đó, các công thức là phép ký hiệu hóa có thể kiểm tra bằng `Table 1`,
không được mô tả là công thức trích nguyên văn từ paper.

Với mỗi model và rubric `r`, dự án khóa quy ước vận hành:

```text
N_r = Win_r + Tie_r + Lose_r
Criterion Win Rate_r = Win_r / N_r
```

`Tie` và `Lose` nằm trong mẫu số nhưng không nằm trong tử số; không quy đổi
`Tie = 0,5`. Đây là quyết định vận hành của dự án dựa trên nghĩa win rate,
không phải một phương trình được KMP-Bench công bố trực tiếp. Rubric riêng
chỉ dùng candidate có nguyên tắc tương ứng trong tập
`requirement_score >= 4`.

Sau khi có tỷ lệ thắng của từng rubric:

```text
General-Level Acc
  = trung bình Criterion Win Rate của 4 rubric chung

Principle-Level Acc_p
  = trung bình Criterion Win Rate của 3 rubric thuộc nguyên tắc p

Overall Acc
  = (General-Level Acc
     + trung bình macro Principle-Level Acc của 6 nguyên tắc) / 2

Overall Judgement Acc
  = số phán quyết tổng thể Win / tổng số phán quyết tổng thể
```

Phép tính `Overall Acc` khớp các số trong KMP-Bench `Table 1`; chẳng hạn
Claude-3.7-Sonnet có `General-Level Acc = 69,8`, trung bình sáu
`Principle-Level Acc` xấp xỉ `75,18`, nên `Overall Acc` làm tròn là
`72,5`. Nếu một nguyên tắc không có candidate hợp lệ, pipeline phải dừng
trước phép tổng hợp sáu nguyên tắc thay vì tự đổi mẫu số.

### 7.3. Cổng lỗi trước tổng hợp và phân tích phụ

Mọi chỉ số chính dùng `adjusted_criterion_judgments`, không dùng
`raw_criterion_judgments`. Phải báo số lượng và tỷ lệ phán quyết bị cổng
lỗi thay đổi theo model, lỗi và rubric để người đọc biết mức ảnh hưởng của
chính sách. Serious error không có điểm độc lập, chỉ ép `Win/Lose` trên
giao các rubric bị ảnh hưởng và rubric đang hoạt động. Mỗi lỗi–rubric chỉ
được áp một lần.

Các kết quả phụ gồm:

1. kết quả thô trước cổng lỗi;
2. theo từng tiêu chí chung;
3. theo từng nguyên tắc;
4. candidate-macro và family-macro;
5. theo lớp và nhóm nội dung;
6. `Overall Judgement Acc.` từ phán quyết toàn cục của judge.

Mỗi lát cắt phải báo đủ tỷ lệ `Win/Tie/Lose`. `family-macro` được giữ để
kiểm tra ảnh hưởng của việc một hội thoại thô tạo nhiều candidate;
`candidate-macro` và `family-macro` chưa được dùng thay chỉ số chính cho
đến khi công thức được khóa trước pilot. Có thể báo thêm
`net preference = (Win - Lose) / N`, nhưng không dùng nó để ghi đè thứ
hạng theo `Overall Acc`. Nếu phân tích phụ làm đảo thứ hạng, phải báo đây
là kết quả sensitivity analysis, không âm thầm chọn metric thuận lợi hơn.

Contract chống tính trùng kế thừa từ Plan 04:

- rubric chung đo điều kiện nền của toàn bộ response;
- rubric riêng chỉ đo giá trị tăng thêm của nguyên tắc đang hoạt động;
- serious error không phải rubric và không có điểm độc lập;
- chỉ các rubric nằm trong giao affected/applicable mới bị ép;
- nhiều lỗi cùng ảnh hưởng một rubric không nhân số lần phạt;
- không dùng `suggested_action` dạng văn bản trong prompt hoặc hậu xử lý;
- phán quyết tổng thể không được dùng để ghi đè kết quả theo tiêu chí.

## 8. Trình tự chạy sau khi plan được duyệt

1. Khóa instruction, rubric, model registry và judge schema.
2. Chạy smoke chấm mù bằng Claude trên 20 phép so sánh hiện có; kiểm
   schema, rubric, blinding, hậu xử lý và chi phí.
3. Khóa manifest pilot 80 candidate: 20 mẫu mỗi lớp, 80 `sample_id` khác
   nhau, giữ 10 smoke anchor, lấy đủ 8 mẫu `Challenge` và tăng bao phủ
   `Practice`/`Modelling`, lịch sử, Bloom và kích thước tập nguyên tắc.
4. Chạy full ba target configuration trên manifest 1.400 mẫu và chỉ tiếp
   tục khi đủ 4.200 response hợp lệ.
5. Chạy cost-pilot judge trên đúng 30 candidate khóa trước × 3 cấu hình =
   90 phép so sánh; đo usage, chi phí, lỗi và rà nhanh chất lượng.
6. Sau khi UET duyệt cost-pilot và v4, chạy full judge bất đồng bộ cho cả
   ba target bằng Gemini và GPT. Tạo bucket, preflight, submit, theo dõi,
   collect và retry đúng ID lỗi là các bước tách biệt; không dùng runner
   synchronous full cũ.

Theo quyết định UET ngày 29/07/2026, pilot 80 mẫu được kéo vào Plan 05 để
kịp kiểm tra giao thức. Phân tích khả năng phân biệt quy mô lớn và full run
vẫn thuộc Plan 07.

## 9. Output tối thiểu

Toàn bộ cấu hình và các run sinh/chấm phản hồi thuộc Plan 05–07 đặt dưới
một thư mục gốc duy nhất:
`experiments/20260727_170150/outputs/benchmark_evaluation/`.
Các run smoke/pilot/full dùng một thư mục con có `run_id`; không tạo thêm
`benchmark_evaluation_config/` hoặc `benchmark_evaluation_smoke/` ngang
hàng ở cấp `outputs/`.


| File                                              | Nội dung                                                                                        |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `evaluation_protocol.md`                          | Input visibility, generation, judging, aggregation và gates                                     |
| `model_registry.csv`                              | Model/version/provider/config/cost role                                                          |
| `instruction_registry.csv`                        | Instruction chung và sáu instruction nguyên tắc, kèm tóm tắt căn cứ và vị trí nguồn |
| `evaluation_schema.json`                          | Schema response và criterion-level judgement                                                    |
| `<run_id>/run_errors.jsonl`                       | Chỉ được tạo khi có lỗi; lưu từng attempt, exception và traceback để gỡ lỗi        |
| `judge_smoke_claude_blind_v2/run_manifest.json`   | Provenance lần Claude thất bại do project chưa kích hoạt Marketplace                     |
| `judge_smoke_gemini35_blind_v2/run_manifest.json` | Lần Gemini đầu: 11 hoàn tất, 9 MAX_TOKENS; cost ghi nhận là lower bound |
| `judge_smoke_gemini35_blind_v2_retry1/run_judgments.jsonl` | 20 kết quả retry1 đồng cấu hình, request, độ tự tin và ánh xạ hậu xử lý |
| `judge_smoke_gemini35_blind_v2_retry1/run_manifest.json` | 8 worker, cấu hình 8.192 token, hạn chế cùng model, hash, cost và integrity |
| `pilot_80_v1/candidate_manifest.json`               | 80 ID, hợp đồng bao phủ, hash input và giới hạn lấy mẫu |
| `pilot_80_v1/target_*/run_responses.jsonl`          | 240 response của ba target configuration; prompt/message/config và usage |
| `pilot_80_v1/judge_gemini35/run_judgments.jsonl`    | Artifact pilot 80 lịch sử nếu được chạy; không còn là bước bắt buộc của phương án hybrid |
| `full_1400_v1/candidate_manifest.json`               | 1.400 candidate eligible, hash input và tập ID khóa |
| `full_1400_v1/target_*/run_responses.jsonl`          | 4.200 response full của ba cấu hình target |
| `full_1400_v1/judge_cost_pilot_30/candidate_manifest.json` | 30 ID khóa và hợp đồng bao phủ để đo chi phí judge |
| `full_1400_v1/judge_cost_pilot_30/judge_gemini35/run_judgments.jsonl` | 90 phán quyết cost-pilot của ba cấu hình |
| `full_1400_v1/judge_cost_pilot_30/judge_gemini35_gold_answer_only_v4/run_judgments.jsonl` | Ablation v4 Gemini, không fragment; chỉ được tạo sau API run |
| `full_1400_v1/judge_cost_pilot_30/judge_openai_gpt54_mini_medium_gold_answer_only_v4/run_judgments.jsonl` | Ablation v4 GPT, không fragment; chỉ được tạo sau API run |
| `full_1400_v1/judge_full_batch_gold_answer_only_v4/gemini35/` | Input, manifest, raw output và 4.200 judgment batch Gemini |
| `full_1400_v1/judge_full_batch_gold_answer_only_v4/openai_gpt54_mini_medium/` | Input, manifest, raw output và 4.200 judgment Batch API GPT |
| `socraticlm_endpoint/lifecycle_manifest.json`     | Tài nguyên, trần chi phí, hạn cleanup và trạng thái vòng đời endpoint                 |

`instruction_registry.csv` là artifact phục vụ review được sinh từ bundle,
không phải nguồn instruction thứ hai. Bundle nằm tại `shared/prompts/` nên
không làm tăng số file trong thư mục output của experiment.

## 10. Cổng hoàn thành

- Prompt không làm lộ gold/rubric cho tutor model.
- `student_prompt` và `conversation_history` được truyền bằng message/role
  native, không phải JSON nhúng trong một prompt thuần.
- Validator xác nhận thứ tự, xen kẽ role và lượt học sinh cuối trước khi
  gọi model; provider-adapter tests xác nhận cùng một hội thoại ngữ nghĩa
  được giữ nguyên giữa các API.
- Panel có ít nhất một model đóng, một model mở và một model chuyên biệt
  đã vượt cổng khả thi trên Vertex AI; model được prompt theo vai trò gia
  sư không tự được tính là model chuyên biệt.
- Dự toán gồm target, judge, retry và endpoint; runner có cost ledger,
  reserve và cổng dừng bảo đảm tổng chi phí không vượt 250 USD.
- Mọi model có config và version tái tạo được.
- Mọi target response có `finish_reason`; phản hồi bị cắt không được tính
  là hoàn thành.
- Smoke Claude v2 hoàn thành đúng 20 phép so sánh; user prompt dùng
  Markdown tiếng Việt, không lộ danh tính response hoặc ID nội bộ, chỉ dùng
  rubric của nguyên tắc có điểm từ 4 trở lên, chỉ gửi heading + nội dung
  fragment và khôi phục được kết quả `Win/Tie/Lose` bằng ánh xạ đã khóa.
- Cổng lỗi lưu đủ raw/adjusted judgments, chỉ tác động giao
  affected/applicable, tái tạo được bốn nhánh target/reference và không
  nhân phạt khi nhiều lỗi cùng ảnh hưởng một rubric.
- Contract v4 không được đọc hoặc gửi fragment, phải ghi policy
  `excluded_gold_answer_only`, giữ ID evidence rỗng và dùng tên hiển thị
  v4 của `RUB-GEN-ACC`; v2/v3 phải tiếp tục giữ hành vi lịch sử.
- Pilot hiện tại phải ghi rõ chưa có calibration người–judge độc lập mới;
  vẫn kiểm thiên lệch thứ tự/cùng họ model và giữ phán quyết chuyên gia đã
  có trên các smoke anchor làm điểm kiểm tra định tính.
- Chỉ số chính được tính theo đúng `win rate` và thứ tự tổng hợp của
  KMP-Bench; metric phụ không được ghi đè thứ hạng chính.
- Báo cáo giữ phán quyết theo tiêu chí, theo nguyên tắc và tổng thể tách
  biệt.
- UET duyệt giao thức; HNMU duyệt instruction và cách diễn giải rubric.

Nguồn vận hành chính: KMP-Bench `Section 3.1`, `Section 4.1`,
`Appendix F`; khả năng model phải kiểm lại từ tài liệu Vertex AI chính
thức trước mỗi run:
[Google models](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models),
[Claude on Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude),
[Llama on Vertex AI](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/partner-models/llama/use-llama),
[bảng giá Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/pricing),
[triển khai model mở từ Model Garden](https://cloud.google.com/vertex-ai/generative-ai/docs/model-garden/explore-models),
[trạng thái LearnLM](https://ai.google.dev/gemini-api/docs/learnlm) và
[SocraticLM tại NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/9bae399d1f34b8650351c1bd3692aeae-Abstract-Conference.html).
