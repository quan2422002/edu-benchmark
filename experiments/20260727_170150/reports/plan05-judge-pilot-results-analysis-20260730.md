# Phân tích kết quả judge pilot 30 mẫu — Plan 05

Ngày phân tích: 30/07/2026  
Experiment: `20260727_170150`  
Contract phân tích chính: `gold-answer-only-v4`  
Trạng thái: **báo cáo hồi cứu sau khi pilot và full judge đã hoàn thành**

## 1. Kết luận chính

Judge pilot đã hoàn thành đúng vai trò chính là kiểm tra giao thức, chi
phí và khả năng vận hành trước khi scale:

- khóa 30 candidate thuộc 30 hội thoại khác nhau;
- chạy ba tutor configuration, tạo 90 phép so sánh trên mỗi judge;
- hoàn thành 90/90 phán quyết hợp lệ cho cả Gemini 3.5 Flash và
  GPT-5.4-mini;
- phát hiện fragment raw-audit không đủ làm evidence cấp candidate;
- cho thấy contract `gold-answer-only-v4` cải thiện agreement của rubric
  chính xác chuyên môn so với v3;
- cung cấp usage thực tế để thiết kế cổng ngân sách và chuyển full judge
  sang Batch API.

Trên điểm tổng hợp kiểu KMP-Bench, cả hai judge trong pilot cùng xếp:

```text
LearnLM-oriented > Gemini baseline > Llama 4 Maverick
```

Tuy nhiên, pilot **không phải mẫu đại diện để ước lượng chất lượng trên
1.400 candidate**. Khi so với full run:

- kết luận thô “Llama đứng cuối” vẫn giữ;
- Gemini judge trong full run đảo thứ hạng baseline và LearnLM-oriented;
- pilot đánh giá agreement trên Llama cao hơn full run 13,46 điểm phần
  trăm;
- khoảng cách điểm, đặc biệt dưới Gemini judge, thay đổi đáng kể.

Do đó, pilot hỗ trợ tính khả thi và phát hiện tín hiệu phân biệt ban đầu,
nhưng mọi kết luận chất lượng chính phải lấy từ full run.

## 2. Mục tiêu và phạm vi pilot

### 2.1. Câu hỏi pilot

Pilot được thiết kế để trả lời:

1. pipeline có dựng đúng 90 phép chấm từ cùng 30 candidate hay không;
2. Gemini và GPT có tuân thủ cùng prompt/schema và trả kết quả hợp lệ hay
   không;
3. chi phí, token, retry và giới hạn output có phù hợp để scale không;
4. hai judge có đạt mức đồng thuận ban đầu đủ để tiếp tục điều tra không;
5. fragment và catalog lỗi nghiêm trọng có làm kết quả thiếu ổn định
   không.

Pilot không được thiết kế để:

- ước lượng điểm chất lượng của toàn bộ 1.400 candidate;
- xác nhận judge nào đúng;
- thay thế human evaluation;
- chứng minh ba mức chất lượng tốt – trung bình – không tốt.

### 2.2. Quy mô

| Thành phần | Quy mô |
| --- | ---: |
| Candidate | 30 |
| `sample_id` khác nhau | 30 |
| Tutor configuration | 3 |
| Phản hồi tutor được chấm | 90 |
| LLM judge | 2 |
| Phán quyết tổng thể | 180 |
| Phán quyết theo rubric | 1.692 |

Ba tutor configuration:

- Gemini 3.5 Flash baseline;
- Gemini 3.5 Flash với instruction LearnLM-oriented;
- Llama 4 Maverick.

Hai judge:

- Gemini 3.5 Flash, `thinking_level=MEDIUM`;
- `gpt-5.4-mini-2026-03-17`, `reasoning_effort=medium`.

Hai judge dùng cùng system prompt v4, cùng user-prompt builder, cùng
candidate, rubric, blind order và hậu xử lý. Judge chỉ thấy hai phản hồi
ẩn danh; ánh xạ target/reference được code khôi phục sau khi nhận output.

## 3. Thiết kế lấy mẫu và độ bao phủ

Tập pilot được chọn xác định từ `pilot_80_v1` để bao phủ vận hành, không
phải lấy mẫu ngẫu nhiên từ 1.400 candidate.

| Trục bao phủ | Phân bố |
| --- | --- |
| Lớp | lớp 6: 8; lớp 7: 8; lớp 8: 7; lớp 9: 7 |
| Hội thoại có/không có history | có: 19; không: 11 |
| Bloom | Remember: 10; Understand: 9; Apply: 11 |
| Số nguyên tắc bắt buộc | 1 nguyên tắc: 12; 2: 12; 3: 6 |
| Độ dài context | ngắn: 8; trung bình: 11; dài: 11 |
| Cặp lớp–bài học khác nhau | 26 |
| Smoke anchor được giữ lại | 10 |

Số candidate có từng nguyên tắc bắt buộc:

| Challenge | Explanation | Modelling | Practice | Questioning | Feedback |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 15 | 5 | 5 | 12 | 15 |

Đây là lấy mẫu có chủ đích nhằm đưa các nguyên tắc hiếm vào pilot.
`Challenge` chiếm 2/30 pilot nhưng chỉ có 8/1.400 trong full pool. Vì vậy,
điểm principle-level của pilot không phản ánh phân bố quần thể.

## 4. Contract judge v4 và cấu hình chạy

Contract `gold-answer-only-v4`:

- không gửi fragment học liệu;
- không gửi hoặc áp dụng catalog lỗi nghiêm trọng;
- dùng `gold_answer` làm neo chuyên môn duy nhất;
- chấm bốn rubric chung và chỉ các rubric riêng của nguyên tắc có
  `requirement_score >= 4`;
- trả Win/Tie/Lose theo từng rubric và một phán quyết tổng thể độc lập.

| Thuộc tính | Gemini judge | GPT judge |
| --- | --- | --- |
| Model | `gemini-3.5-flash` | `gpt-5.4-mini-2026-03-17` |
| Provider | Vertex AI `global` | OpenAI Responses API |
| Reasoning | `thinking_level=MEDIUM` | `reasoning_effort=medium` |
| Sampling | không đặt `temperature` | không đặt `temperature` |
| Max output | 8.192; hai request recovery dùng 12.288 | 8.192 |
| Structured output | schema gọn + validator local | strict JSON Schema |
| Concurrency | 8 | 4 |
| Kết quả cuối | 90/90 | 90/90 |

## 5. Cách đọc các bảng điểm

| Tên cột | Ý nghĩa |
| --- | --- |
| `Overall Judgement Acc.` | Win rate của phán quyết tổng thể độc lập; không được suy ra bằng bỏ phiếu các rubric. |
| `General-Level Acc.` | Trung bình win rate của bốn rubric chung. |
| Sáu `Principle-Level Acc.` | Mỗi cột là trung bình win rate của ba rubric thuộc nguyên tắc; chỉ dùng candidate kích hoạt nguyên tắc đó. |
| `Overall Acc.` | Trung bình của `General-Level Acc.` và trung bình macro của sáu `Principle-Level Acc.`. |

Mọi `Acc.` trong bảng là **win rate khi phản hồi tutor model đấu với
`gold_response`**, không phải tỷ lệ đúng tuyệt đối:

```text
Win Rate = Win / (Win + Tie + Lose)
```

`Tie` nằm trong mẫu số nhưng không được quy đổi thành 0,5. Vì 30
candidate thuộc 30 `sample_id` khác nhau, candidate-macro và family-macro
trùng nhau trong pilot.

## 6. Kết quả theo cấu trúc KMP-Bench

### 6.1. Gemini 3.5 Flash judge

Đơn vị: phần trăm.

| Tutor configuration | Overall Judgement Acc. | General-Level Acc. | Challenge | Explanation | Modelling | Practice | Questioning | Feedback | Overall Acc. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Gemini baseline | 93,33 | 84,17 | **100,00** | 93,33 | **100,00** | **100,00** | 83,33 | 88,89 | 89,21 |
| LearnLM-oriented | **96,67** | **85,83** | **100,00** | **100,00** | **100,00** | **100,00** | **86,11** | **95,56** | **91,39** |
| Llama 4 Maverick | 80,00 | 60,00 | 50,00 | 77,78 | 46,67 | 80,00 | 41,67 | 66,67 | 60,23 |

### 6.2. GPT-5.4-mini judge

Đơn vị: phần trăm.

| Tutor configuration | Overall Judgement Acc. | General-Level Acc. | Challenge | Explanation | Modelling | Practice | Questioning | Feedback | Overall Acc. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Gemini baseline | 83,33 | **75,83** | **100,00** | 91,11 | **86,67** | 93,33 | 63,89 | 91,11 | 81,76 |
| LearnLM-oriented | **93,33** | **75,83** | **100,00** | **97,78** | 80,00 | **100,00** | **72,22** | **95,56** | **83,38** |
| Llama 4 Maverick | 86,67 | 70,83 | 66,67 | 93,33 | 73,33 | **100,00** | 36,11 | 82,22 | 73,06 |

### 6.3. Phán quyết tổng thể Win/Tie/Lose

| Judge | Tutor configuration | Win | Tie | Lose |
| --- | --- | ---: | ---: | ---: |
| Gemini | Gemini baseline | 28 | 1 | 1 |
| Gemini | LearnLM-oriented | 29 | 0 | 1 |
| Gemini | Llama 4 Maverick | 24 | 1 | 5 |
| GPT | Gemini baseline | 25 | 0 | 5 |
| GPT | LearnLM-oriented | 28 | 0 | 2 |
| GPT | Llama 4 Maverick | 26 | 0 | 4 |

GPT judge có `Overall Judgement Acc.` của Llama cao hơn Gemini baseline,
nhưng `Overall Acc.` tổng hợp từ rubric lại xếp Llama thấp nhất. Đây không
phải lỗi số học: hai cột đo hai phán quyết khác nhau. Kết quả này cho thấy
không nên dùng phán quyết tổng thể làm đại diện duy nhất cho hồ sơ rubric.

## 7. Độ đồng thuận giữa hai judge

### 7.1. Phán quyết tổng thể

| Phạm vi | Exact agreement | Cohen's κ | Gwet's AC1 |
| --- | ---: | ---: | ---: |
| Cả ba configuration | 85,56% | 0,280 | 0,840 |
| Gemini baseline | 83,33% | 0,231 | 0,814 |
| LearnLM-oriented | 96,67% | 0,651 | 0,963 |
| Llama 4 Maverick | 76,67% | 0,180 | 0,728 |

Có 13/90 bất đồng tổng thể:

- 7 trường hợp Gemini chọn Win, GPT chọn Lose;
- 4 trường hợp Gemini chọn Lose, GPT chọn Win;
- 2 trường hợp Gemini chọn Tie còn GPT chọn Win hoặc Lose.

Tỷ lệ Win cao tạo `prevalence paradox`, nên phải đọc exact agreement
cùng Cohen's κ và Gwet's AC1 thay vì chỉ chọn một hệ số.

### 7.2. Phán quyết theo rubric

Trên 846 cặp phán quyết rubric, hai judge đồng thuận 635 trường hợp:
**75,06%**, Cohen's κ = **0,269**, Gwet's AC1 = **0,700**.

| Nhóm rubric | Số cặp | Exact agreement | Cohen's κ | Gwet's AC1 |
| --- | ---: | ---: | ---: | ---: |
| Chung | 360 | 68,89% | 0,229 | 0,611 |
| Challenge | 18 | 94,44% | 0,769 | 0,927 |
| Explanation | 135 | 86,67% | 0,092 | 0,856 |
| Modelling | 45 | 75,56% | 0,253 | 0,708 |
| Practice | 45 | 91,11% | −0,017 | 0,907 |
| Questioning | 108 | 63,89% | 0,318 | 0,512 |
| Feedback | 135 | 80,74% | 0,203 | 0,781 |

Agreement cao không luôn đi cùng κ cao vì phân bố Win/Lose/Tie lệch
mạnh. `Challenge` và `Practice` còn có số quan sát rất nhỏ, nên không được
diễn giải là hai nhóm rubric đã ổn định hơn một cách chắc chắn.

Bốn rubric chung:

| Rubric | Exact agreement | Cohen's κ | Gwet's AC1 |
| --- | ---: | ---: | ---: |
| Chính xác chuyên môn | 72,22% | 0,412 | 0,640 |
| Bám trạng thái và mục tiêu | 70,00% | 0,132 | 0,639 |
| Mức hỗ trợ và quyền chủ động | 73,33% | 0,172 | 0,682 |
| Giao tiếp phù hợp | 60,00% | 0,121 | 0,485 |

Pilot đã chỉ đúng hai vùng cần chú ý sau này: rubric chung và
`Questioning` có agreement thấp. Full run tiếp tục xác nhận xu hướng này.

## 8. Ablation từ v3 sang v4

| Contract | Overall agreement | Rubric agreement | Rubric chính xác |
| --- | ---: | ---: | ---: |
| `rubric-only-v3`, còn fragment | 86,7% | 77,2% | 61,1% |
| `gold-answer-only-v4` | 85,6% | 75,1% | 72,2% |
| Thay đổi v4 trừ v3 | −1,1 điểm % | −2,1 điểm % | **+11,1 điểm %** |

Việc bỏ fragment:

- cải thiện rõ agreement trên rubric chính xác chuyên môn;
- không cải thiện agreement tổng thể hoặc toàn bộ rubric;
- không chứng minh `gold_answer` là căn cứ hoàn chỉnh;
- chỉ cho thấy fragment raw-audit đang gây thêm bất đồng ở cấp candidate.

Đây là bằng chứng vận hành hỗ trợ chọn v4 cho full judge, không phải bằng
chứng rằng mọi bài toán grounding đã được giải quyết.

## 9. Độ tự tin, overall và rubric

| Chỉ số | Gemini judge | GPT judge |
| --- | ---: | ---: |
| Confidence tổng thể trung bình | 0,951 | 0,914 |
| Confidence rubric trung bình | 0,937 | 0,873 |
| Confidence trung bình trên 13 bất đồng tổng thể | 0,938 | 0,851 |
| Số bất đồng có confidence ≥ 0,9 | 12/13 | 5/13 |

Gemini vẫn rất tự tin khi bất đồng với GPT. Do đó, confidence tự báo
không thể dùng để tự động chọn judge hoặc loại phán quyết.

So phán quyết tổng thể với nhãn chiếm đa số trong các rubric của cùng
request:

- Gemini có 6/90 trường hợp overall không thuộc nhóm rubric chiếm đa số,
  trong đó 1 trường hợp ngược hướng Win/Lose;
- GPT có 2/90 trường hợp, cả hai ngược hướng Win/Lose.

Đây không mặc nhiên là mâu thuẫn vì overall là phán quyết độc lập, nhưng
các trường hợp ngược hướng là mẫu hữu ích cho kiểm tra định tính.

## 10. Chi phí và vận hành

| Chỉ số | Gemini judge | GPT judge | Tổng |
| --- | ---: | ---: | ---: |
| Input token | 367.738 | 395.982 | 763.720 |
| Output token do provider báo | 348.523 | 218.752 | 567.275 |
| Chi phí thực tế pilot | 3,835701 USD | 1,281370 USD | **5,117071 USD** |
| Chi phí trung bình/phán quyết | 0,042619 USD | 0,014237 USD | 0,056856 USD cho hai judge |

Token output bao gồm reasoning/thinking token theo cách từng provider báo;
không nên dùng chênh lệch token thô để kết luận model nào suy luận hiệu
quả hơn.

Nếu ngoại suy tuyến tính giá on-demand của pilot lên 4.200 phán quyết cho
mỗi judge:

- Gemini: khoảng 178,999 USD;
- GPT: khoảng 59,797 USD;
- tổng: khoảng 238,797 USD.

Full judge được chuyển sang Batch API và có chi phí thực tế:

- Gemini: 85,734333 USD;
- GPT: 30,430355 USD;
- tổng: 116,164688 USD.

Batch API giảm khoảng 51% so với ngoại suy tuyến tính từ pilot on-demand.
Pilot vì vậy có giá trị cho budget gate, nhưng không thể lấy đơn giá
on-demand làm chi phí full cuối cùng.

Về độ tin cậy vận hành:

- Gemini ban đầu hoàn thành 88/90; một lỗi tên tiêu chí được chuẩn hóa
  bằng code và một lỗi `MAX_TOKENS` được chạy lại;
- recovery cuối chạy đúng hai request còn thiếu ở giới hạn 12.288;
- GPT hoàn thành 90/90;
- cả hai bundle cuối không còn ID thất bại.

## 11. Pilot dự báo full run tốt đến đâu?

### 11.1. Điểm `Overall Acc.`

`Δ` dưới đây là pilot trừ full run, đơn vị điểm phần trăm.

| Judge | Tutor configuration | Pilot | Full | Δ |
| --- | --- | ---: | ---: | ---: |
| Gemini | Gemini baseline | 89,21 | 87,87 | +1,34 |
| Gemini | LearnLM-oriented | 91,39 | 85,35 | +6,04 |
| Gemini | Llama 4 Maverick | 60,23 | 49,51 | **+10,72** |
| GPT | Gemini baseline | 81,76 | 84,01 | −2,25 |
| GPT | LearnLM-oriented | 83,38 | 84,78 | −1,40 |
| GPT | Llama 4 Maverick | 73,06 | 74,56 | −1,50 |

GPT pilot gần full hơn trên cả ba configuration. Gemini pilot đánh giá
cao hơn full, đặc biệt đối với Llama. Pilot chỉ dự báo đúng kết luận chung
Llama đứng cuối; nó không dự báo được việc Gemini judge ở full run xếp
baseline cao hơn LearnLM-oriented.

### 11.2. Agreement giữa judge

| Chỉ số | Pilot | Full | Pilot trừ full |
| --- | ---: | ---: | ---: |
| Overall agreement | 85,56% | 80,45% | +5,10 điểm % |
| Rubric agreement | 75,06% | 73,24% | +1,82 điểm % |
| Rubric chính xác chuyên môn | 72,22% | 65,55% | +6,67 điểm % |
| Agreement overall trên Llama | 76,67% | 63,21% | **+13,46 điểm %** |

Pilot đã dự báo tương đối gần agreement cấp rubric, nhưng đánh giá quá cao
độ đồng thuận ở cấp overall, nhất là với Llama.

### 11.3. Position bias

Mỗi target trong pilot chỉ có 30 candidate và vị trí không cân bằng trong
từng target:

- baseline: target ở `response_1` 10 lần, `response_2` 20 lần;
- LearnLM-oriented: 14 và 16;
- Llama: 18 và 12.

Chênh lệch win rate theo vị trí trong pilot không nhất quán về hướng và
không phát hiện được dấu hiệu ưu tiên `response_1` của Gemini judge xuất
hiện ở full run. Vì vậy pilot quá nhỏ để kiểm position bias.

## 12. Đối chiếu định tính với ý kiến chuyên gia

Một số candidate pilot đã được chuyên gia xem trong quá trình gỡ lỗi:

- `BC-HNMU-G7-R0204-STT7-AI14`: reference chỉ thiếu giá trị tăng thêm,
  không phải lỗi nghiêm trọng;
- `BC-HNMU-G6-R0042-STT13-AI04`: overall và hồ sơ rubric khác nhau không
  mặc nhiên là mâu thuẫn; cách thao tác khác vẫn phải đối chiếu
  `gold_answer`;
- `BC-HNMU-G7-R0164-STT9-AI08`: chuyên gia xác nhận quy trình có ba bước;
- `BC-HNMU-G8-R0186-STT3-AI06`: chuyên gia đồng tình với nội dung mẫu;
- `BC-HNMU-G7-R0207-STT10-AI10`: phát biểu làm mất hoàn toàn dữ liệu thật
  được xác nhận là lỗi nghiêm trọng.

Các nhận định này giúp sửa giao thức nhưng không phải một human evaluation
có lấy mẫu, chấm mù và đo agreement. Không được tính chúng thành tỷ lệ
đúng của judge.

## 13. Pilot đã chứng minh và chưa chứng minh điều gì?

### 13.1. Bằng chứng trực tiếp

Pilot chứng minh:

- hạ tầng có thể chấm cùng một tập bằng hai provider;
- schema, blinding, ánh xạ tên rubric và recovery hoạt động;
- v4 giảm bất đồng trên rubric chính xác so với v3;
- hai judge cùng phát hiện khoảng cách ban đầu giữa Llama và hai cấu hình
  Gemini trên `Overall Acc.`;
- chi phí full synchronous có rủi ro cao và Batch API là lựa chọn hợp lý.

### 13.2. Suy luận có điều kiện

Pilot gợi ý:

- `Questioning` và rubric chung khó chấm nhất;
- Llama có thể thấp hơn hai cấu hình Gemini;
- GPT có thể ít tạo khoảng cách cùng họ model hơn Gemini.

Các suy luận này chỉ được củng cố sau khi full run cho kết quả cùng hướng.

### 13.3. Chưa được hỗ trợ

Pilot không chứng minh:

- thứ hạng ổn định giữa Gemini baseline và LearnLM-oriented;
- ba mức chất lượng tuyệt đối;
- judge có độ chính xác tương đương chuyên gia;
- `gold_answer` đủ cho mọi biến thể chuyên môn;
- principle-level score của các nguyên tắc hiếm là ổn định;
- confidence cao đồng nghĩa với phán quyết đúng.

## 14. Vai trò của pilot trong paper

Khi viết paper, pilot nên xuất hiện trong phần thiết lập và kiểm định giao
thức, không dùng thay bảng kết quả full:

> A locked 30-candidate pilot covering all grades and pedagogical
> principles was used for operational validation, prompt ablation, cost
> measurement, and cross-judge screening. The subset was purposively
> stratified and was not treated as a population-quality estimate.

Có thể báo:

- 90/90 phán quyết hợp lệ cho mỗi judge;
- agreement v4: 85,56% overall và 75,06% rubric;
- agreement rubric chính xác tăng từ 61,1% lên 72,2% sau khi bỏ fragment;
- chi phí on-demand pilot 5,117071 USD;
- pilot dẫn đến quyết định dùng Batch API và báo hai judge riêng.

Kết quả chất lượng chính, khoảng tin cậy và hạn chế same-family/position
bias phải lấy từ
[báo cáo full judge](plan05-full-judge-results-analysis-20260730.md).

## 15. Provenance

- Manifest chọn mẫu:
  [`candidate_manifest.json`](../outputs/benchmark_evaluation/full_1400_v1/judge_cost_pilot_30/candidate_manifest.json)
- Gemini judgments:
  [`run_judgments.jsonl`](../outputs/benchmark_evaluation/full_1400_v1/judge_cost_pilot_30/judge_gemini35_gold_answer_only_v4/run_judgments.jsonl)
- GPT judgments:
  [`run_judgments.jsonl`](../outputs/benchmark_evaluation/full_1400_v1/judge_cost_pilot_30/judge_openai_gpt54_mini_medium_gold_answer_only_v4/run_judgments.jsonl)
- System prompt:
  [`system_prompt_gold_answer_only_v4.md`](../../../shared/prompts/benchmark_response_judging/system_prompt_gold_answer_only_v4.md)
- Báo cáo cấu hình và phiên bản prompt:
  [`plan05-response-generation-and-judge-experimental-report-20260730.md`](plan05-response-generation-and-judge-experimental-report-20260730.md)

SHA-256:

| Artifact | SHA-256 |
| --- | --- |
| Candidate manifest | `4cf05b1cc177511d5609f464cb392ab31df479d16a64ff6e0e1db6e9391208e4` |
| Gemini judgments | `cad63adab456968280d88731c7556a8e67ed965091f406ff955b1f61ba6e3b01` |
| GPT judgments | `e71ae60f1ec99b24e2de851c984cbbe13934e70426eb0443f966ce1892243b08` |
| System prompt file | `9753b361b1f46aa9063d4e808a7c47b36099b319636016f06c9cc2462c93fec0` |
