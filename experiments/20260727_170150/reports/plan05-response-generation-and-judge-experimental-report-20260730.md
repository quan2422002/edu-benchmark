# Báo cáo cấu hình sinh phản hồi và chấm phản hồi — Plan 05

Ngày lập: 30/07/2026  
Experiment: `20260727_170150`  
Mục đích: cung cấp căn cứ có truy vết cho phần phương pháp và thiết lập
thực nghiệm của paper KSE

> Full judge và recovery đã hoàn tất đủ 4.200 record trên mỗi provider.
> Mọi kết quả judge vẫn là phán quyết của mô hình, không phải nhãn đúng do
> chuyên gia xác nhận.
>
> Phân tích định lượng sau full run được tách tại
> [báo cáo full judge](plan05-full-judge-results-analysis-20260730.md).
> Phân tích riêng về thiết kế, chi phí, ablation và khả năng dự báo của
> pilot 30 mẫu nằm tại
> [báo cáo judge pilot](plan05-judge-pilot-results-analysis-20260730.md).

## 1. Tóm tắt thiết kế thực nghiệm

Thực nghiệm đánh giá một nhiệm vụ: sinh phản hồi tiếp theo của gia sư AI
môn Tin học THCS. Đầu vào ưu tiên gồm 1.400 benchmark candidate ở trạng
thái `eligible_without_plan03_review`, được lấy từ pool 2.028 candidate
chuyển đổi từ 665 hội thoại thô.

Đối với mỗi candidate, pipeline:

1. dùng đúng tập nguyên tắc sư phạm có `requirement_score >= 4` để dựng
   system instruction cho gia sư;
2. sinh ba phản hồi từ ba cấu hình target;
3. so sánh mù từng phản hồi target với `gold_response` bằng bốn rubric
   chung và ba rubric cho mỗi nguyên tắc bắt buộc.

| Run ID | Base model | Vai trò | Prompt |
| --- | --- | --- | --- |
| `target_gemini35` | `gemini-3.5-flash` | baseline đóng | bundle v2 |
| `target_llama4_maverick` | `meta/llama-4-maverick-17b-128e-instruct-maas` | model mở qua Vertex MaaS | bundle v2 |
| `target_gemini35_learnlm_prompted` | `gemini-3.5-flash` | ablation prompt LearnLM-oriented | bundle v3-learnlm |

LearnLM-oriented là một biến thể prompt trên cùng base model Gemini, không
phải model độc lập. Vì vậy, phép so sánh hai cấu hình Gemini đo tác động
của system instruction.

Full target đã hoàn thành 1.400 candidate cho mỗi cấu hình, tổng 4.200
phản hồi. Ba manifest cuối đều không còn record lỗi, bị cắt hoặc cần
review và đều qua kiểm toàn vẹn ở mức 1.400 ID duy nhất.

## 2. Cách dựng prompt sinh phản hồi gia sư

### 2.1. Ba lớp request

Request không biến toàn bộ candidate thành một chuỗi JSON. Pipeline tách:

1. system instruction động;
2. lịch sử hội thoại theo role native;
3. lượt `user` cuối cùng mà model phải trả lời.

System instruction nhận lớp, bài học và câu hỏi/nhiệm vụ nguồn. Các trường
đánh giá như `gold_answer`, `gold_response`, `requirement_score`,
`benchmark_candidate_id` và `sample_id` bị cấm xuất hiện trong instruction
dành cho tutor model.

Lịch sử được chuyển như sau:

```text
student_prompt                         → user
conversation_history: tutor            → assistant/model
conversation_history: student          → user
...
phản hồi cần sinh                      ← assistant/model
```

Do đó, lịch sử được truyền bằng đúng cấu trúc nhiều lượt của provider,
không bị serialize thành JSON rồi nhúng vào một prompt văn bản. Mỗi record
lưu system prompt, user prompt cuối, toàn bộ `conversation_messages`, các
hash, phiên bản bundle và tập nguyên tắc bắt buộc.

### 2.2. Cổng nguyên tắc bắt buộc

Code tái lập tập nguyên tắc từ sáu `requirement_score` và chỉ lấy các
nguyên tắc có điểm từ 4 trở lên. Nguyên tắc điểm 3 không được đưa vào
system instruction, không kích hoạt rubric riêng, không được gửi judge và
không tham gia tổng hợp điểm.

Mỗi nguyên tắc bắt buộc có tên tiếng Việt và bốn mục: mục tiêu, hành vi
cần thể hiện, hành vi cần tránh và cách bảo toàn quyền chủ động của học
sinh. Sáu khối tương ứng `Challenge`, `Explanation`, `Modelling`,
`Practice`, `Feedback` và `Questioning`.

### 2.3. Các phiên bản instruction bundle

| Phiên bản | Thay đổi chính | Vai trò |
| --- | --- | --- |
| v1 | Vai trò gia sư, ngữ cảnh bài học, tập yêu cầu bắt buộc và sáu khối nguyên tắc | baseline smoke đầu tiên |
| v2 | Giữ sáu khối; yêu cầu cô đọng, không lặp hội thoại, không mở rộng quá bước cần thiết và kết thúc trọn câu | prompt chính cho Gemini baseline và Llama |
| v3-learnlm | Giữ sáu khối v2; thêm học chủ động, quản lí tải nhận thức và thích ứng; cấm tự thêm hành vi ngoài tập bắt buộc | ablation LearnLM-oriented |

| File | SHA-256 |
| --- | --- |
| `instruction_bundle_v1.yaml` | `f8390c493ef30b9eb791a18955da8aba7c8a2cca310fd2b598ee3e5add8ce4a1` |
| `instruction_bundle_v2.yaml` | `711256237b0d23923e516b974e498ff51dbd3251666512c6acfc3889b8329510` |
| `instruction_bundle_v3_learnlm.yaml` | `9433f4864cbb6e831aaa42fabe96b68130944f5a50bb90cd79b1fa4221c8c16b` |

Link tới nguồn prompt chuẩn:

- [instruction bundle v1](../../../shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v1.yaml);
- [instruction bundle v2](../../../shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v2.yaml);
- [instruction bundle v3-learnlm](../../../shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v3_learnlm.yaml);
- [code dựng system instruction theo candidate](../../../src/edu_benchmark/benchmark_evaluation/prompt_builder.py).

Smoke khóa prompt:

| Run | Kết quả | Chi phí ước tính từ usage |
| --- | ---: | ---: |
| Gemini + v1 | 10/10 | 0,070458 USD |
| Gemini + v2 | 10/10 | 0,065493 USD |
| Llama + v2 | 10/10 | 0,0024288 USD |

### 2.4. Cấu hình sinh phản hồi full

| Thuộc tính | Gemini baseline | Llama Maverick | Gemini LearnLM-oriented |
| --- | --- | --- | --- |
| Endpoint | Vertex AI `global` | Vertex MaaS `us-east5` | Vertex AI `global` |
| Max output ban đầu | 1.024 | 1.024 | 1.024 |
| Thinking | `MEDIUM`, không trả thought | không áp dụng | `MEDIUM`, không trả thought |
| Sampling override | không đặt temperature/top-p | không đặt temperature/top-p | không đặt temperature/top-p |
| Seed gửi provider | `20260728` | không gửi generation seed | `20260728` |
| Concurrency full | 20 | 2 ở recovery cuối | 20 |
| Max retries | 2 | 2, backoff 15–60 giây | 2 |

Runner vẫn dùng seed `20260728` để khóa việc chọn mẫu, thứ tự và request
hash. Tuy nhiên, caller MaaS của Llama không truyền seed sinh vào provider;
đây là giới hạn tái lập cần báo trong paper.

Recovery giữ nguyên model, prompt, lịch sử và tập nguyên tắc, chỉ tăng
giới hạn output:

- Gemini baseline: 436 candidate ở 1.536 token, sau đó 19 candidate ở
  2.048 token;
- LearnLM-oriented: 386 candidate ở 2.048 token;
- Llama: chạy lại 86 request HTTP 429 với concurrency 2, backoff và jitter.

| Target | Chi phí cộng dồn theo usage |
| --- | ---: |
| Gemini baseline | 16,306311 USD |
| Llama Maverick | 0,38923175 USD |
| Gemini LearnLM-oriented | 15,60312 USD |
| Tổng | 32,29866275 USD |

Đây là chi phí ước tính từ token usage, không phải hóa đơn thanh toán.

### 2.5. Ví dụ request sinh phản hồi thực tế

Ví dụ là input thật của Gemini baseline cho candidate
[BC-HNMU-G6-R0048-STT5-AI04](../outputs/benchmark_evaluation/full_1400_v1/target_gemini35/run_responses.jsonl#L1).

System instruction được dựng từ bundle v2:

```text
Bạn là gia sư Tin học cho học sinh trung học cơ sở lớp 6–9. Hãy trả lời
bằng tiếng Việt, đúng chuyên môn, bám sát điều học sinh vừa nói, hỗ trợ
vừa đủ để học sinh tiến thêm một bước, giữ quyền chủ động của học sinh và
giao tiếp rõ ràng, tôn trọng, phù hợp lứa tuổi.

Ngữ cảnh bài học:
- Lớp: 6
- Bài học: Bài 4. Mạng máy tính
- Câu hỏi hoặc nhiệm vụ nguồn: Tại sao chúng ta cần mạng máy tính?

Yêu cầu sư phạm bắt buộc cho phản hồi tiếp theo:

### Yêu cầu sư phạm: Phản hồi
- Mục tiêu: Dùng điều học sinh đã trả lời, thao tác hoặc tạo ra để dẫn hướng cải thiện.
- Hành vi cần thể hiện: Chỉ ra chi tiết quan sát được, phân biệt phần đúng với điểm cần sửa và đề xuất bước tiếp theo khả thi.
- Cần tránh: Chỉ khen, xác nhận chung chung hoặc nhận xét không dựa trên sản phẩm của học sinh.
- Bảo toàn quyền chủ động: Giúp học sinh tự chỉnh sửa thay vì sửa thay toàn bộ.

### Yêu cầu sư phạm: Đặt câu hỏi
- Mục tiêu: Dùng câu hỏi để chẩn đoán hiểu biết, giữ mạch suy luận hoặc thúc đẩy suy nghĩ sâu hơn.
- Hành vi cần thể hiện: Đặt câu hỏi rõ, vừa sức, bám ngữ cảnh và thực sự cần câu trả lời của học sinh để cuộc học tiến lên.
- Cần tránh: Câu hỏi xã giao, tu từ, mơ hồ hoặc tự trả lời ngay.
- Bảo toàn quyền chủ động: Chờ học sinh trả lời và dùng câu trả lời đó cho bước hỗ trợ tiếp theo.

Hãy trả lời tự nhiên và cô đọng trong một lượt, không chia phản hồi thành
các mục theo tên yêu cầu sư phạm. Chỉ đưa những nội dung cần thiết cho
bước tiếp theo của học sinh; không lặp lại toàn bộ hội thoại, không mở
rộng sang nhiều bước khi học sinh chưa cần và phải kết thúc trọn câu.
```

Messages được gửi theo role native:

```yaml
- role: user
  content: >
    Thầy ơi, nếu không có mạng thì máy tính vẫn hoạt động được mà, tại sao phải cần mạng ạ?
- role: assistant
  content: >
    Đúng là máy vẫn chạy, nhưng em thử nghĩ xem: Nếu cả lớp có 30 máy tính
    mà chỉ có 1 máy in, ta phải làm sao để máy nào cũng in được?
- role: user
  content: >
    Chắc là phải copy vào USB rồi mang ra máy có nối máy in ạ.
```

Trong request provider, system instruction nằm ở trường system riêng;
message `user` cuối là điểm model phải sinh lượt `assistant` tiếp theo.
`gold_answer` và `gold_response` không xuất hiện trong request này.

## 3. Rubric được gửi judge

Mỗi phép chấm nhận đúng bốn rubric chung và ba rubric cho mỗi nguyên tắc
bắt buộc. Với \(k\) nguyên tắc, số rubric là \(4+3k\).

Mỗi rubric trong user prompt gồm tên tiêu chí, dấu hiệu cần quan sát, ranh
giới và ba anchor tốt–gần đạt–không đạt. `rubric_id`, `principle_id`,
`tier` và `scope` không được gửi model; code giữ chúng để chọn rubric và
ánh xạ tên trong output về ID nội bộ.

## 4. Prompt chấm phản hồi và các ablation

### 4.1. Giao thức chấm mù

Mỗi target response được so sánh với `gold_response`. Hai phản hồi bị ẩn
danh thành `response_1` và `response_2`; vị trí được tráo xác định bằng
seed `20260728`. Judge không nhận model tạo phản hồi, danh tính reference,
ID nội bộ hoặc phán quyết trước đó.

Judge trả `response_1`, `response_2` hoặc `tie` cho từng tiêu chí. Code
khôi phục kết quả target thành `Win`, `Lose` hoặc `Tie`. Phán quyết tổng
thể là kết quả holistic phụ trợ, không ghi đè rubric và không dùng để tính
chỉ số chính.

### 4.2. User prompt động

User prompt Markdown gồm lớp, bài học, Bloom, câu hỏi nguồn,
`gold_answer`, `student_prompt`, lịch sử hội thoại, toàn bộ và chỉ các
rubric áp dụng, cùng hai phản hồi ẩn danh. System prompt nói rõ mọi nội
dung trong user message là dữ liệu cần đánh giá, không phải instruction
mới.

### 4.3. Tiến hóa prompt judge

| Phiên bản | Input/contract | Lý do thay đổi |
| --- | --- | --- |
| v1 | bối cảnh, căn cứ, rubric, lỗi nghiêm trọng, hai response | đặc tả ban đầu |
| v2 | Markdown; giải thích metadata; fragment nhóm theo sách–bài; lỗi kiểm độc lập trên hai response | làm rõ dữ liệu và hậu xử lý |
| rubric-only v3 | bỏ danh mục/cổng lỗi nghiêm trọng; còn fragment | phát hiện lỗi không ổn định giữa hai judge |
| gold-answer-only v4 | bỏ fragment; dùng `gold_answer` làm neo chuyên môn duy nhất | fragment raw-audit chưa đủ tin cậy cấp candidate |

Audit đúng 30 candidate pilot tìm thấy 2 mẫu có fragment sai/không liên
quan, 20 mẫu đúng bài nhưng thiếu nội dung quyết định và chỉ 8 mẫu đủ hoặc
gần đủ; cả 41 fragment duy nhất đều còn `draft`.

V4 không còn mục căn cứ học liệu. Judge phải chấp nhận cách diễn đạt hoặc
quy trình tương đương; không ưu tiên phản hồi chỉ vì giống từ ngữ của
`gold_answer`; chỉ phạt khác phương pháp nếu đề bắt buộc; chọn `Tie` khi
`gold_answer` không đủ phân xử.

| File | SHA-256 file |
| --- | --- |
| `system_prompt_v1.md` | `d78b2b650bf6b0baaef08aa6a45affe5d0ea3e18f7636fde27f34089f86d557e` |
| `system_prompt_v2.md` | `8ef17c6fb4bf08477ebbf77535bc657ed827dabda2284bca48230d444cfb9a84` |
| `system_prompt_rubric_only_v3.md` | `881a0e2f80905b60ff188ed3d30f21d07384d99d5ac5f73105a1f13b98cd3bb8` |
| `system_prompt_gold_answer_only_v4.md` | `9753b361b1f46aa9063d4e808a7c47b36099b319636016f06c9cc2462c93fec0` |

Link tới system prompt judge:

- [system prompt v1](../../../shared/prompts/benchmark_response_judging/system_prompt_v1.md);
- [system prompt v2](../../../shared/prompts/benchmark_response_judging/system_prompt_v2.md);
- [system prompt rubric-only v3](../../../shared/prompts/benchmark_response_judging/system_prompt_rubric_only_v3.md);
- [system prompt gold-answer-only v4 đang dùng](../../../shared/prompts/benchmark_response_judging/system_prompt_gold_answer_only_v4.md);
- [code dựng user prompt và tráo mù hai response](../../../src/edu_benchmark/benchmark_evaluation/judge.py).

Manifest v4 còn lưu hash nội dung sau khi trim là
`dc6b5475f3ccd491bc1e2e7753f9330a2915989867fb152214a31f34bea55553`.
Một giá trị là hash file, một giá trị là hash đúng chuỗi gửi provider.

### 4.4. Ví dụ request judge v4 thực tế

Ví dụ là phép so sánh Llama–reference cho candidate
`BC-HNMU-G7-R0074-STT3-AI02`. System prompt là
[gold-answer-only v4](../../../shared/prompts/benchmark_response_judging/system_prompt_gold_answer_only_v4.md).
User prompt nguyên văn và output judge nằm tại
[dòng 41 của run_judgments.jsonl](../outputs/benchmark_evaluation/full_1400_v1/judge_cost_pilot_30/judge_openai_gpt54_mini_medium_gold_answer_only_v4/run_judgments.jsonl#L41).

Dưới đây là bản trình bày gọn của đúng request đó. Bản gửi provider mở
rộng mỗi rubric bằng đủ năm trường: dấu hiệu, ranh giới và ba anchor.

```markdown
Hãy chấm mù hai phản hồi dưới đây theo đúng system prompt.
Mỗi tiêu chí trong phần "Các tiêu chí phải áp dụng" phải có đúng một
phán quyết. Không áp dụng tiêu chí nào không xuất hiện trong phần đó.

# Dữ liệu đánh giá

## Bối cảnh học tập

- **Lớp:** 7
- **Bài học:** Bài 6: Làm quen với phần mềm bảng tính
- **Mức nhận thức Bloom:** Nhận biết (Nêu được tên thành phần)

### Câu hỏi nguồn

Các cột của trang tính được đặt tên như thế nào?

### Đáp án chuyên môn

Các cột được đặt tên theo bảng chữ cái A, B, C... từ trái sang phải.

### Lời mở đầu của học sinh

Vậy còn các chữ cái A, B, C ở phía trên là gì hả thầy?

### Lịch sử hội thoại

(Không có)

## Các tiêu chí phải áp dụng

1. Chính xác chuyên môn và phù hợp đáp án chuẩn
2. Bám đúng trạng thái và mục tiêu trước mắt của học sinh
3. Mức hỗ trợ vừa đủ và bảo toàn phần việc có ý nghĩa cho học sinh
4. Giao tiếp rõ ràng, tôn trọng và phù hợp học sinh THCS
5. Làm rõ ý cốt lõi và quan hệ quyết định
6. Mạch giải thích có liên kết và căn cứ
7. Mức chi tiết và cách diễn đạt phù hợp người học

## Hai phản hồi

### response_1

Em đã biết hàng được đánh số rồi. Vậy các chữ cái nằm ở phía trên cùng,
theo chiều dọc, sẽ đại diện cho thành phần nào đối lập với hàng?

### response_2

Các chữ cái A, B, C,... ở hàng trên cùng của trang tính là tên của các
cột đấy em. Tên cột được đánh thứ tự từ trái qua phải bằng các chữ cái,
bắt đầu từ A, B, C,... đến Z, sau đó tiếp tục là AA, AB, AC,...
```

Ánh xạ nội bộ của ví dụ là `response_1 = reference` và
`response_2 = target`, nhưng thông tin này không xuất hiện trong request
gửi judge. Sau khi judge trả tên tiêu chí và lựa chọn
`response_1|response_2|tie`, code mới khôi phục `rubric_id` và
`Win|Lose|Tie` của target.
## 5. Hai judge và cấu hình pilot v4

Pilot khóa 30 candidate × 3 target = 90 phép so sánh trên mỗi judge.

| Thuộc tính | Gemini judge | GPT judge |
| --- | --- | --- |
| Model | `gemini-3.5-flash` | `gpt-5.4-mini-2026-03-17` |
| Provider | Vertex AI `global` | OpenAI Responses API |
| Reasoning | `thinking_level=MEDIUM` | `reasoning_effort=medium` |
| Sampling | không đặt temperature | không đặt temperature |
| Max output | 8.192; recovery ở 12.288 | 8.192 |
| Structured output | schema gọn + validator local | strict JSON Schema |
| Concurrency | 8 | 4 |
| Kết quả | 90/90 | 90/90 |
| Chi phí manifest | 3,835701 USD | 1,28137 USD |

Hai judge dùng cùng system prompt v4, cùng user-prompt builder, candidate,
rubric, seed tráo vị trí và hậu xử lý.

## 6. Kết quả pilot judge

### 6.1. Mức đồng thuận Gemini–GPT

| Mức so sánh | Đồng thuận | Tỷ lệ |
| --- | ---: | ---: |
| Phán quyết tổng thể | 77/90 | 85,6% |
| Phán quyết theo rubric | 635/846 | 75,1% |
| Riêng rubric chính xác chuyên môn | 65/90 | 72,2% |

| Contract | Overall agreement | Rubric agreement | Accuracy agreement |
| --- | ---: | ---: | ---: |
| v3, còn fragment | 86,7% | 77,2% | 61,1% |
| v4, chỉ `gold_answer` | 85,6% | 75,1% | 72,2% |

Việc bỏ fragment làm agreement của rubric chính xác tăng 11,1 điểm phần
trăm, nhưng không chứng minh `gold_answer` đã hoàn chỉnh hay được HNMU xác
nhận ở cấp candidate.

| Target | Overall | Tất cả rubric | Accuracy rubric |
| --- | ---: | ---: | ---: |
| Gemini baseline | 83,3% | 81,2% | 80,0% |
| Gemini LearnLM-oriented | 96,7% | 81,9% | 70,0% |
| Llama Maverick | 76,7% | 62,1% | 66,7% |

Có 13/90 bất đồng overall, trong đó 11 trường hợp là `Win`–`Lose`.
Confidence tự báo không đủ để tự động bỏ qua bất đồng.

### 6.2. Chỉ số theo cấu trúc KMP-Bench

Dự án dùng:

\[
\mathrm{WR}_r=\frac{\mathrm{Win}_r}
{\mathrm{Win}_r+\mathrm{Tie}_r+\mathrm{Lose}_r}.
\]

`Tie` nằm trong mẫu số nhưng không được quy đổi thành 0,5. Sau đó:

\[
\mathrm{Overall}=\frac{1}{2}
\left(\operatorname{mean}_{4\ rubric\ chung}\mathrm{WR}_r+
\operatorname{mean}_{6\ nguyên\ tắc}
\operatorname{mean}_{3\ rubric\ của\ p}\mathrm{WR}_r\right).
\]

Đây là phép ký hiệu hóa vận hành được đối chiếu với KMP-Bench, không phải
phương trình được paper đó in nguyên văn.

| Target | Gemini judge | GPT judge |
| --- | ---: | ---: |
| Gemini LearnLM-oriented | 0,9139 | 0,8338 |
| Gemini baseline | 0,8921 | 0,8176 |
| Llama Maverick | 0,6023 | 0,7306 |

Hai judge cùng xếp:

```text
Gemini LearnLM-oriented > Gemini baseline > Llama Maverick
```

Gemini tạo khoảng cách lớn hơn giữa Llama và hai cấu hình Gemini. Vì thế,
GPT-5.4-mini được dùng làm judge chính; Gemini là sensitivity check; hai
judge được báo riêng và không lấy trung bình cơ học.

## 7. Full judge đang chạy

```text
1.400 candidate × 3 target × 2 judge = 8.400 judgment
```

Gemini dùng Vertex AI Batch; GPT dùng OpenAI Batch `/v1/responses`. Cả hai
giữ nguyên prompt v4, blind order, structured output và hậu xử lý pilot.

| Judge | Request | Dự toán p95 × 1,10 |
| --- | ---: | ---: |
| Gemini 3.5 Flash | 4.200 | 132,44616 USD |
| GPT-5.4-mini | 4.200 | 46,52802 USD |

Snapshot manifest cuối sau collect và recovery:

| Provider | Hợp lệ | Còn lỗi | Chi phí usage đã ghi |
| --- | ---: | ---: | ---: |
| Gemini | 4.200/4.200 | 0 | 85,734333 USD |
| OpenAI | 4.200/4.200 | 0 | 30,430355 USD |

Cả hai manifest có `status = completed` và
`integrity = {"validated": true, "record_count": 4200}`:

- GPT retry thành công toàn bộ 1.306 request còn thiếu;
- 10 output Gemini đầy đủ nhưng chép sai một từ trong tên tiêu chí được
  ánh xạ cục bộ bằng ba alias quan sát được; không gọi lại API;
- hai output Gemini `MAX_TOKENS` được retry đúng ID ở giới hạn 9.000 token
  và đều thành công;
- mỗi judge có đúng 1.400 judgment cho từng target, không có ID trùng,
  fragment học liệu không xuất hiện trong prompt v4.

## 8. Đoạn có thể dùng cho paper

### 8.1. Response generation

> For each benchmark candidate, we programmatically activated only the
> pedagogical principles with a requirement score of at least four. The
> tutor system instruction comprised a Vietnamese middle-school
> Informatics tutoring role, lesson metadata, and one structured
> instruction block for each activated principle. Student prompts and
> preceding dialogue turns were transmitted using native multi-turn
> user/assistant roles rather than serialized as a single textual prompt.
> We evaluated Gemini 3.5 Flash, Llama 4 Maverick, and a LearnLM-oriented
> prompt ablation of Gemini 3.5 Flash on the same 1,400 candidates.

### 8.2. Pairwise judging

> Each generated response was compared against the reference response
> under a source-blind Win/Tie/Lose protocol. Response order was
> deterministically randomized. The judge received four general criteria
> and three additional criteria for every activated pedagogical
> principle. Internal criterion IDs and model identities were withheld.
> In the final judging contract, subject-matter accuracy was anchored to
> the source question and gold answer; raw-audit learning fragments and
> serious-error gates were excluded following pilot ablations.

### 8.3. Judge sensitivity

> We used GPT-5.4-mini as the primary judge and Gemini 3.5 Flash as a
> separately reported sensitivity judge. On a locked 30-candidate pilot
> covering three target configurations, the two judges agreed on 85.6%
> of holistic decisions and 75.1% of criterion-level decisions. Both
> judges produced the same model ranking, while their score margins
> differed substantially; therefore, we did not average their judgments.

Các đoạn trên mô tả phương pháp và kết quả pilot. Kết quả full judge đã
hoàn tất nhưng cần được tổng hợp ở bước phân tích riêng trước khi thay các
số liệu pilot trong paper.

## 9. Giới hạn phải công bố

1. Pool 1.400 candidate qua cổng agent-assisted, chưa được HNMU duyệt từng
   mẫu.
2. Requirement scoring full chỉ có một run.
3. Rubric và instruction chưa hoàn thành xác nhận HNMU.
4. `gold_answer` chưa được audit lại toàn bộ ở cấp 1.400 candidate.
5. `gold_response` là reference, không mặc nhiên là phản hồi tối ưu.
6. Gemini judge cùng họ với hai target Gemini.
7. LearnLM-oriented là prompt ablation, không phải model giáo dục độc lập.
8. Llama target không nhận generation seed từ provider adapter.
9. Pilot agreement là đồng thuận giữa hai judge model, không phải accuracy
   so với nhãn chuyên gia.
10. Full batch chưa hoàn tất recovery tại thời điểm báo cáo; các record
    hiện có chưa được dùng để tính kết quả full.

## 10. Ma trận truy vết

| Nội dung | Artifact nguồn |
| --- | --- |
| Candidate pool | `outputs/benchmark_candidate_pool/eligible_without_plan03_review.csv` |
| Prompt tutor v1–v3 | `shared/prompts/benchmark_tutor_response_generation/` |
| Dựng system instruction | `src/edu_benchmark/benchmark_evaluation/prompt_builder.py` |
| Native conversation | `src/edu_benchmark/benchmark_evaluation/dialogue_transport.py` |
| Ba target full | `outputs/benchmark_evaluation/full_1400_v1/target_*/` |
| Rubric | `outputs/benchmark_rubric/rubrics.csv` |
| Prompt judge v1–v4 | `shared/prompts/benchmark_response_judging/` |
| Dựng request/ẩn danh/ánh xạ | `src/edu_benchmark/benchmark_evaluation/judge.py` |
| Pilot v4 | `full_1400_v1/judge_cost_pilot_30/*gold_answer_only_v4/` |
| Full batch | `full_1400_v1/judge_full_batch_gold_answer_only_v4/` |
| Giao thức và metric | `plans/05-benchmark-evaluation-configuration.md` |
