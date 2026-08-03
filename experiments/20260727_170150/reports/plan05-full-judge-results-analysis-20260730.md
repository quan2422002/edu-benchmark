# Phân tích kết quả full judge trên 1.400 benchmark candidate — Plan 05

Ngày phân tích: 30/07/2026  
Experiment: `20260727_170150`  
Trạng thái: **bản phân tích để UET review; chưa phải kết luận đánh giá bởi
chuyên gia con người**

## 1. Kết luận chính

Kết quả hiện tại cung cấp bằng chứng khá rõ rằng bộ rubric có thể phân
biệt một khoảng cách chất lượng lớn: cả Gemini 3.5 Flash judge và
GPT-5.4-mini judge đều xếp Llama 4 Maverick thấp hơn đáng kể so với hai
cấu hình Gemini trên chỉ số tổng hợp kiểu KMP-Bench.

Tuy nhiên, dữ liệu **chưa chứng minh được ba mức chất lượng tuyệt đối
“tốt – trung bình – không tốt”**:

- hai judge cùng đặt Llama cuối bảng;
- Gemini judge xếp Gemini baseline cao hơn LearnLM-oriented 2,52 điểm
  phần trăm;
- GPT judge lại xếp LearnLM-oriented cao hơn baseline 0,77 điểm phần
  trăm, và khoảng tin cậy của chênh lệch này chứa 0.

Vì vậy, kết luận mạnh nhất hiện có là **rubric phân biệt được khác biệt
lớn giữa hai nhóm chất lượng trong panel này**. Chưa nên tuyên bố rubric
đã phân giải ổn định các khác biệt nhỏ hoặc đã hiệu chỉnh được ba mức
chất lượng tuyệt đối.

Hai judge có thể được coi là hai judge chính ngang hàng, với điều kiện:

1. báo riêng toàn bộ kết quả của từng judge;
2. không chọn judge cho kết luận có lợi hơn;
3. kết luận “bền vững giữa judge” chỉ dựa trên phần giao nhau giữa hai
   bộ kết quả;
4. không lấy trung bình điểm của hai judge để che mất bất đồng.

## 2. Dữ liệu và giao thức

### 2.1. Quy mô

| Thành phần | Quy mô |
| --- | ---: |
| Benchmark candidate | 1.400 |
| Hội thoại thô khác nhau (`sample_id`) | 655 |
| Cấu hình tutor model | 3 |
| Phản hồi tutor model | 4.200 |
| LLM judge chính | 2 |
| Phán quyết tổng thể | 8.400 |
| Phán quyết theo tiêu chí | 77.664 |

Ba cấu hình tutor model:

- `target_gemini35`: Gemini 3.5 Flash với instruction baseline;
- `target_gemini35_learnlm_prompted`: cùng base model Gemini 3.5 Flash
  nhưng dùng instruction LearnLM-oriented;
- `target_llama4_maverick`: Llama 4 Maverick.

Hai judge:

- Gemini 3.5 Flash;
- GPT-5.4-mini với reasoning effort `medium`.

Mỗi tutor response được so sánh mù với `gold_response`. Vị trí
`response_1`/`response_2` được làm mù và có thể truy ngược sau hậu xử lý.
Judge chỉ chấm:

- bốn rubric chung;
- ba rubric của từng nguyên tắc có `requirement_score >= 4`;
- một phán quyết tổng thể độc lập.

Contract đang dùng là `gold-answer-only-v4`: judge nhận `gold_answer`
nhưng không nhận fragment học liệu và không áp dụng catalog lỗi nghiêm
trọng.

### 2.2. Artifact nguồn

- Pool 1.400 mẫu:
  [`eligible_without_plan03_review.csv`](../outputs/benchmark_candidate_pool/eligible_without_plan03_review.csv)
- System prompt judge:
  [`system_prompt_gold_answer_only_v4.md`](../../../shared/prompts/benchmark_response_judging/system_prompt_gold_answer_only_v4.md)
- Kết quả Gemini judge:
  [`run_judgments.jsonl`](../outputs/benchmark_evaluation/full_1400_v1/judge_full_batch_gold_answer_only_v4/gemini35/run_judgments.jsonl)
- Kết quả GPT judge:
  [`run_judgments.jsonl`](../outputs/benchmark_evaluation/full_1400_v1/judge_full_batch_gold_answer_only_v4/openai_gpt54_mini_medium/run_judgments.jsonl)
- Paper KMP-Bench:
  [`18426-AAAI26.ShiW-NLP.pdf`](../../../document/paper/source_paper/18426-AAAI26.ShiW-NLP.pdf)
- Báo cáo pilot dùng để khóa giao thức trước full run:
  [`plan05-judge-pilot-results-analysis-20260730.md`](plan05-judge-pilot-results-analysis-20260730.md)

SHA-256:

| Artifact | SHA-256 |
| --- | --- |
| Pool candidate | `7dec13c3cc3a53337bc6c5fdf800e6c89856f49a3b6b0626dca885e59cb0fed9` |
| Gemini judgments | `4c2e7f5b9ffd68a1dad5f6999700864683536386df6331ec16a0c6e279902936` |
| GPT judgments | `ebfc8bd0276b105ef3348c2ec0227571ce7267b186d60490fc2107633a104ab9` |
| System prompt v4 | `9753b361b1f46aa9063d4e808a7c47b36099b319636016f06c9cc2462c93fec0` |

Hai bundle judge đều có đủ 4.200 `comparison_id` duy nhất. Không còn
phán quyết thiếu hoặc không hợp lệ sau recovery. Các lỗi lịch sử vẫn được
giữ trong log để bảo toàn provenance.

## 3. Cách tính chỉ số

Phần `Metrics` và `Table 1` của KMP-Bench quy định các accuracy trong
KMP-Dialogue là win rate; báo riêng phán quyết tổng thể, trung bình bốn
tiêu chí chung, sáu điểm theo nguyên tắc và điểm tổng hợp.

Nghiên cứu này vận hành hóa cách tính như sau:

```text
Criterion Win Rate_r = Win_r / (Win_r + Tie_r + Lose_r)

General-Level
  = trung bình win rate của 4 rubric chung

Principle-Level_p
  = trung bình win rate của 3 rubric thuộc nguyên tắc p

Overall
  = (General-Level
     + trung bình macro của 6 Principle-Level) / 2

Holistic
  = số phán quyết tổng thể Win / tổng số phán quyết tổng thể
```

`Tie` nằm trong mẫu số nhưng không được tính là nửa điểm. Đây là quy ước
vận hành của dự án dựa trên nghĩa “win rate”; KMP-Bench không in thành
một phương trình riêng.

Điểm chính được tính ở mức candidate. Phân tích nhạy cảm tính thêm
family-macro để kiểm tra ảnh hưởng của việc nhiều candidate cùng sinh từ
một hội thoại thô. Khoảng tin cậy 95% dùng 5.000 lần bootstrap theo cụm
`sample_id`; 4.995 lần có đủ quan sát cho cả sáu nguyên tắc.

## 4. Bảng kết quả chi tiết theo cấu trúc KMP-Bench

### Chú thích ý nghĩa các cột

Các tên `Holistic`, `General` và `Overall` trong bảng là dạng viết gọn.
Chúng tương ứng với các cột của KMP-Bench như sau:

| Tên cột trong report | Tên tương ứng trong KMP-Bench | Ý nghĩa |
| --- | --- | --- |
| `Tutor configuration` | `Model` | Cấu hình sinh phản hồi đang được đánh giá. Report dùng “configuration” vì Gemini baseline và LearnLM-oriented dùng cùng base model nhưng khác system instruction. |
| `Holistic` | `Overall Judgement Acc.` | Tỷ lệ candidate mà phán quyết tổng thể độc lập của judge chọn phản hồi tutor model thắng `gold_response`. Cột này lấy trực tiếp từ `overall_judgment`, không được tính bằng cách cộng hay bỏ phiếu từ các rubric. |
| `General` | `General-Level Acc.` | Trung bình không trọng số của win rate trên bốn rubric chung: chính xác chuyên môn, bám trạng thái và mục tiêu học sinh, mức hỗ trợ và quyền chủ động, giao tiếp phù hợp. |
| `Challenge` đến `Feedback` | Sáu cột thuộc nhóm `Principle-Level Acc.` | Mỗi cột là trung bình không trọng số của win rate trên ba rubric riêng của nguyên tắc tương ứng. Chỉ những candidate có nguyên tắc đó trong tập `requirement_score >= 4` mới tham gia tính cột. |
| `Overall` | `Overall Acc.` | Trung bình của `General-Level Acc.` và trung bình macro của sáu `Principle-Level Acc.`. Đây là điểm tổng hợp từ rubric, khác với phán quyết tổng thể độc lập ở cột `Holistic`. |
| `Family-macro` | Không có trong bảng KMP-Bench | Phân tích độ nhạy bổ sung của dự án: chuẩn hóa để mỗi hội thoại thô (`sample_id`) có ảnh hưởng ngang nhau trước khi tổng hợp `Overall Acc.`, tránh hội thoại sinh nhiều candidate chi phối kết quả. |

Toàn bộ các cột mang tên `Acc.` ở đây thực chất là **win rate trong phép
so sánh cặp** giữa phản hồi tutor model và `gold_response`, không phải tỷ
lệ trả lời đúng theo nghĩa phân loại thông thường. `Win` nằm trong tử số;
`Win`, `Tie` và `Lose` đều nằm trong mẫu số. Vì vậy:

- `Holistic` trả lời: “judge tổng thể chọn phản hồi tutor model thắng ở
  bao nhiêu phần trăm candidate?”;
- `General` và sáu cột nguyên tắc trả lời: “phản hồi tutor model thắng
  trên các nhóm rubric tương ứng với tỷ lệ bao nhiêu?”;
- `Overall` trả lời: “điểm tổng hợp từ hai tầng rubric là bao nhiêu?”;
- `Family-macro` trả lời: “kết quả `Overall` có giữ nguyên khi mỗi hội
  thoại thô được trao trọng số ngang nhau hay không?”.

### 4.1. Gemini 3.5 Flash judge

Đơn vị: phần trăm.

| Tutor configuration | Holistic | General | Challenge | Explanation | Modelling | Practice | Questioning | Feedback | Overall | Family-macro |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Gemini baseline | **93,43** | **83,27** | **100,00** | **97,88** | **98,92** | **91,36** | **76,65** | **90,03** | **87,87** | **88,49** |
| LearnLM-oriented | 93,21 | 79,82 | **100,00** | 97,10 | **98,92** | 87,65 | 72,40 | 89,16 | 85,35 | 85,91 |
| Llama 4 Maverick | 55,21 | 43,07 | 87,50 | 62,96 | 54,48 | 41,98 | 35,84 | 52,94 | 49,51 | 49,40 |

Khoảng tin cậy 95% theo cụm cho `Overall`:

- Gemini baseline: **86,46–89,19**;
- LearnLM-oriented: **83,76–86,83**;
- Llama 4 Maverick: **46,54–52,37**.

Chênh lệch:

- baseline trừ LearnLM-oriented: **+2,52 điểm phần trăm**,
  CI 95% **+1,53 đến +3,57**;
- baseline trừ Llama: **+38,36**, CI **+35,53 đến +41,21**;
- LearnLM-oriented trừ Llama: **+35,84**, CI
  **+32,89 đến +38,82**.

### 4.2. GPT-5.4-mini judge

Đơn vị: phần trăm.

| Tutor configuration | Holistic | General | Challenge | Explanation | Modelling | Practice | Questioning | Feedback | Overall | Family-macro |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Gemini baseline | 90,79 | 78,32 | 95,83 | 94,82 | **98,21** | **91,36** | 66,97 | 90,98 | 84,01 | 84,72 |
| LearnLM-oriented | **91,86** | **79,09** | **100,00** | **95,44** | **98,21** | 90,12 | **67,84** | **91,19** | **84,78** | **85,32** |
| Llama 4 Maverick | 81,86 | 72,43 | 87,50 | 90,23 | 75,27 | 87,65 | 41,42 | 78,04 | 74,56 | 75,98 |

Khoảng tin cậy 95% theo cụm cho `Overall`:

- Gemini baseline: **82,36–85,51**;
- LearnLM-oriented: **83,28–86,14**;
- Llama 4 Maverick: **71,62–76,97**.

Chênh lệch:

- baseline trừ LearnLM-oriented: **−0,77 điểm phần trăm**,
  CI 95% **−2,14 đến +0,45**;
- baseline trừ Llama: **+9,45**, CI **+7,43 đến +11,71**;
- LearnLM-oriented trừ Llama: **+10,22**, CI
  **+8,04 đến +13,04**.

### 4.3. Phán quyết tổng thể Win/Tie/Lose

| Judge | Tutor configuration | Win | Tie | Lose |
| --- | --- | ---: | ---: | ---: |
| Gemini | Gemini baseline | 1.308 (93,43%) | 6 (0,43%) | 86 (6,14%) |
| Gemini | LearnLM-oriented | 1.305 (93,21%) | 7 (0,50%) | 88 (6,29%) |
| Gemini | Llama 4 Maverick | 773 (55,21%) | 24 (1,71%) | 603 (43,07%) |
| GPT | Gemini baseline | 1.271 (90,79%) | 5 (0,36%) | 124 (8,86%) |
| GPT | LearnLM-oriented | 1.286 (91,86%) | 9 (0,64%) | 105 (7,50%) |
| GPT | Llama 4 Maverick | 1.146 (81,86%) | 7 (0,50%) | 247 (17,64%) |

## 5. Khả năng phân biệt chất lượng

### 5.1. Bằng chứng tích cực

Cả hai judge đều cho thấy:

- Llama có `Overall` thấp hơn rõ rệt hai cấu hình Gemini;
- khoảng tin cậy của cả bốn phép so sánh Gemini–Llama đều không chứa 0;
- thứ hạng này không đổi khi chuyển từ candidate-micro sang
  family-macro;
- khoảng cách xuất hiện ở cả rubric chung lẫn hầu hết rubric theo nguyên
  tắc, mạnh nhất ở `Questioning`, `Feedback` và `Modelling`.

Đây là bằng chứng ủng hộ **tính phân biệt đối với khác biệt chất lượng
lớn**. Kết luận không phụ thuộc vào chỉ một judge hoặc vào việc một hội
thoại thô tạo nhiều candidate.

### 5.2. Giới hạn của kết luận phân biệt

Hai cấu hình Gemini nằm rất gần nhau:

- Gemini judge nghiêng về baseline;
- GPT judge nghiêng nhẹ về LearnLM-oriented;
- chỉ phép so sánh của Gemini judge có khoảng tin cậy không chứa 0.

Do đó, rubric và giao thức hiện tại chưa chứng minh khả năng phân giải
ổn định một thay đổi instruction tương đối nhỏ trên cùng base model.

Quan trọng hơn, tên model không phải nhãn chất lượng đúng. Chưa có tập
response được con người khóa trước thành ba mức “tốt – trung bình – không
tốt”. Vì vậy, không được suy ngược rằng ba hàng model trong bảng chính là
ba mức chất lượng chuẩn.

## 6. Độ đồng thuận và tính bền vững giữa hai judge

### 6.1. Phán quyết tổng thể

| Phạm vi | Exact agreement | Cohen's κ | Gwet's AC1 |
| --- | ---: | ---: | ---: |
| Cả ba tutor configuration | 80,45% | 0,271 | 0,775 |
| Gemini baseline | 88,36% | 0,204 | 0,874 |
| LearnLM-oriented | 89,79% | 0,265 | 0,890 |
| Llama 4 Maverick | 63,21% | 0,221 | 0,529 |

Tỷ lệ Win rất cao ở hai cấu hình Gemini làm Cohen's κ chịu
`prevalence paradox`; vì vậy phải báo đồng thời exact agreement, κ và
Gwet's AC1. Không nên chỉ chọn AC1 vì cho con số cao hơn.

Hai judge khá đồng thuận trên hai cấu hình Gemini nhưng bất đồng mạnh ở
Llama. Trong các bất đồng có hướng:

| Tutor configuration | Gemini: Lose, GPT: Win | Gemini: Win, GPT: Lose |
| --- | ---: | ---: |
| Gemini baseline | 57 | 95 |
| LearnLM-oriented | 54 | 73 |
| Llama 4 Maverick | **419** | 65 |

Gemini judge khắt khe hơn GPT judge rất rõ đối với Llama. Đây có thể là
thiên lệch cùng họ model hoặc khác biệt trong cách hai judge diễn giải
rubric, nhưng dữ liệu hiện tại chưa đủ để xác định nguyên nhân.

### 6.2. Phán quyết theo rubric

Trên toàn bộ 38.832 cặp phán quyết theo tiêu chí, exact agreement là
**73,24%**, Cohen's κ = **0,315** và Gwet's AC1 = **0,668**.

| Nhóm rubric | Số cặp | Exact agreement | Cohen's κ | Gwet's AC1 |
| --- | ---: | ---: | ---: | ---: |
| Chung | 16.800 | 67,33% | 0,253 | 0,583 |
| Challenge | 72 | 95,83% | 0,553 | 0,956 |
| Explanation | 7.767 | 84,69% | 0,196 | 0,831 |
| Modelling | 837 | 86,74% | 0,426 | 0,850 |
| Practice | 243 | 77,78% | 0,319 | 0,736 |
| Questioning | 5.859 | 68,12% | 0,429 | 0,558 |
| Feedback | 7.254 | 76,88% | 0,264 | 0,726 |

Bốn rubric chung:

| Rubric | Exact agreement | Cohen's κ | Gwet's AC1 |
| --- | ---: | ---: | ---: |
| Chính xác chuyên môn | 65,55% | 0,309 | 0,546 |
| Bám trạng thái và mục tiêu học sinh | 72,90% | 0,246 | 0,671 |
| Mức hỗ trợ và quyền chủ động | 68,98% | 0,221 | 0,613 |
| Giao tiếp phù hợp | 61,90% | 0,180 | 0,504 |

Các kết quả này cho thấy tính bền vững **không đồng đều giữa rubric**.
`Explanation` và `Modelling` có agreement cao; `Questioning` và toàn bộ
nhóm rubric chung khó chấm nhất. Riêng `Challenge` có agreement cao nhưng
mẫu quá nhỏ để kết luận ổn định.

## 7. Ba kiểm tra độ nhạy quan trọng

### 7.1. Candidate-macro và family-macro

`Overall` family-macro chỉ lệch candidate-micro khoảng 0,1–1,4 điểm phần
trăm và không đảo thứ hạng trong từng judge. Việc một hội thoại sinh
nhiều candidate chưa phải nguyên nhân chính tạo ra kết quả.

Tuy nhiên, các phép kiểm suy luận vẫn phải lấy `sample_id` làm cụm vì
1.400 candidate không phải 1.400 quan sát hoàn toàn độc lập.

### 7.2. Thiên lệch vị trí response

Tỷ lệ target Win khi target nằm ở `response_1` trừ khi nằm ở
`response_2`:

| Judge | Gemini baseline | LearnLM-oriented | Llama |
| --- | ---: | ---: | ---: |
| Gemini | +8,04 điểm % | +6,60 điểm % | **+14,61 điểm %** |
| GPT | +0,88 điểm % | +1,51 điểm % | +0,31 điểm % |

Vị trí được chia gần cân bằng trên toàn bộ request: target ở
`response_1` 2.124 lần và ở `response_2` 2.076 lần. Vì vậy thiên lệch có
thể được giảm một phần ở điểm tổng hợp, nhưng vẫn có thể ảnh hưởng đến
những so sánh sát nhau.

Đây mới là kiểm tra mô tả, chưa phải phép thử nhân quả. Muốn ước lượng
position bias đúng, cần chấm lại một tập phân tầng với vị trí response
được đảo ngược.

### 7.3. Độ tự tin của judge

- Độ tự tin tổng thể trung bình: Gemini **0,950**, GPT **0,908**.
- Trên những mẫu hai judge bất đồng, Gemini vẫn có độ tự tin trung bình
  **0,910**; 76,37% bất đồng của Gemini có confidence từ 0,9 trở lên.
- GPT có độ tự tin trung bình **0,859** trên bất đồng; 48,60% từ 0,9 trở
  lên.

Vì vậy, confidence tự báo không đủ để nhận diện tự động phán quyết đáng
tin hoặc loại bỏ nhu cầu kiểm định độc lập.

## 8. Hạn chế cần công bố

### 8.1. Chưa có human ground truth độc lập

Hai judge đều là LLM. Agreement giữa hai LLM chỉ cho biết độ ổn định giữa
hai quy trình chấm, không chứng minh cả hai đều đúng. Những nhận định thủ
công ở smoke giúp phát hiện lỗi thiết kế nhưng chưa phải một nghiên cứu
agreement người–máy có lấy mẫu và khóa giao thức.

### 8.2. Thiên lệch cùng họ model

Gemini judge cùng họ với hai target Gemini và khắt khe hơn đáng kể với
Llama. Đây là một biến nhiễu có thể giải thích một phần khoảng cách 38
điểm mà Gemini judge quan sát, nhất là khi GPT judge chỉ quan sát khoảng
9–10 điểm.

### 8.3. Thiên lệch vị trí

Gemini judge có dấu hiệu ưu tiên `response_1`. Việc tráo vị trí gần cân
bằng không thay thế được swap-order evaluation trên cùng cặp response.

### 8.4. `gold_answer` không bao phủ mọi quyết định sư phạm

Contract v4 loại fragment để tránh grounding sai cấp candidate. Cách này
làm neo chuyên môn sạch và gọn hơn, nhưng `gold_answer` có thể không đủ
để phân xử:

- nhiều quy trình hoặc cách thao tác đều đúng;
- ví dụ, mã lệnh hoặc giao diện có biến thể;
- chiến lược sư phạm tốt nhưng khác `gold_response`.

Điều này đặc biệt liên quan đến agreement thấp của rubric chính xác
chuyên môn.

### 8.5. Mất cân bằng nguyên tắc

Số candidate áp dụng mỗi nguyên tắc trên một tutor configuration:

| Challenge | Explanation | Modelling | Practice | Questioning | Feedback |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 8 | 863 | 93 | 27 | 651 | 806 |

Chỉ số `Overall` kiểu KMP-Bench cho sáu nguyên tắc trọng số bằng nhau.
Như vậy, `Challenge` với 8 mẫu có trọng số macro bằng `Explanation` với
863 mẫu. Bảng KMP-compatible cần được báo để so sánh phương pháp, nhưng
không nên là chỉ số duy nhất dùng để kết luận.

### 8.6. Rubric chưa được HNMU freeze

Rubric hiện là bộ tiêu chí provisional đã được UET duyệt để triển khai,
chưa phải bộ tiêu chí được HNMU review và phân xử đầy đủ. Agreement thấp
ở rubric chung và `Questioning` là bằng chứng cần dùng cho vòng review
sau, không phải chi tiết cần che đi.

### 8.7. Tập nguyên tắc bắt buộc cũng do model suy ra

Rubric riêng được kích hoạt bởi `requirement_score >= 4` từ một full run
Gemini. Những mẫu không qua UET review đã được ưu tiên, nhưng tập nguyên
tắc này chưa phải nhãn chuyên gia. Sai số ở bước kích hoạt rubric có thể
ảnh hưởng chỉ số principle-level.

## 9. Kết luận nào có thể viết vào paper?

### 9.1. Được dữ liệu hiện tại hỗ trợ

Có thể viết:

> Trên 1.400 candidate thuộc 655 hội thoại thô, hai LLM judge độc lập
> cùng xếp Llama 4 Maverick thấp hơn hai cấu hình Gemini trên điểm tổng
> hợp kiểu KMP-Bench. Khoảng cách vẫn giữ nguyên khi bootstrap theo cụm
> hội thoại và khi chuyển sang family-macro, cho thấy bộ rubric có khả
> năng phát hiện khác biệt chất lượng tương đối lớn trong panel được
> khảo sát.

Có thể viết thêm, nhưng phải kèm số:

> Hai judge đạt 80,45% agreement ở phán quyết tổng thể và 73,24% ở cấp
> rubric; mức agreement thay đổi đáng kể theo tutor configuration và
> nhóm tiêu chí.

### 9.2. Chỉ nên viết như diễn giải có điều kiện

- Sự đồng thuận về việc Llama đứng cuối là bằng chứng về robustness của
  **thứ hạng thô**, không phải validity tuyệt đối.
- Khoảng cách giữa hai cấu hình Gemini có thể phản ánh tác động của
  instruction, nhưng không bền vững giữa judge.
- Agreement cao của `Explanation`/`Modelling` gợi ý ranh giới rubric rõ
  hơn; agreement thấp của rubric chung có thể đến từ cả rubric, judge và
  thiếu grounding.

### 9.3. Chưa được dữ liệu hỗ trợ

Chưa nên viết:

- rubric đã phân biệt đầy đủ ba mức tốt – trung bình – không tốt;
- GPT và Gemini judge có thể thay thế chuyên gia con người;
- Gemini baseline chắc chắn tốt hơn LearnLM-oriented;
- điểm `Overall` là thước đo tuyệt đối duy nhất;
- mọi bất đồng do chất lượng model, không phải position bias,
  same-family bias hoặc sự mơ hồ của rubric.

## 10. Cách trình bày đề xuất trong paper

Phần kết quả nên có:

1. hai panel bảng kiểu KMP-Bench, một panel cho mỗi judge;
2. một bảng agreement tổng thể và theo nhóm rubric;
3. khoảng tin cậy bootstrap theo `sample_id`;
4. một đoạn sensitivity analysis về family-macro;
5. một đoạn riêng về position bias và same-family bias;
6. số mẫu áp dụng mỗi nguyên tắc ngay dưới bảng chính.

Không nên gộp hai judge thành một cột điểm. Khi cần một kết luận chung,
dùng nguyên tắc giao:

```text
Kết luận bền vững
  = kết luận cùng hướng ở cả Gemini judge và GPT judge
```

Theo nguyên tắc này:

- **bền vững:** hai cấu hình Gemini cao hơn Llama;
- **không bền vững:** thứ hạng Gemini baseline so với
  LearnLM-oriented.

## 11. Các bước kiểm định tiếp theo

Ưu tiên theo giá trị khoa học:

1. human evaluation trên một tập phân tầng, tập trung vào:
   `RUB-GEN-ACC`, `RUB-GEN-COMM`, `RUB-GEN-SCAFF`,
   `Questioning` và các mẫu hai judge bất đồng;
2. swap-order test trên cùng cặp response để định lượng position bias;
3. review ranh giới rubric dựa trên các rationale bất đồng, không sửa
   rubric chỉ để tăng agreement;
4. bổ sung mẫu `Challenge`, `Practice` và `Modelling` trước khi diễn giải
   sâu principle-level;
5. nếu cần chứng minh ba mức chất lượng, tạo tập phản hồi đối chứng có
   kiểm soát và được con người khóa trước thành tốt – trung bình – không
   tốt.

## 12. Ghi chú đồng bộ manuscript

Manuscript hiện cần được rà lại trước khi dùng các con số này:

- judge v4 không nhận fragment học liệu;
- lỗi nghiêm trọng đã bị loại khỏi contract v4;
- Gemini và GPT được coi là hai judge chính ngang hàng;
- chưa có căn cứ để nói HNMU đã xác nhận toàn bộ rubric;
- kết quả chính phải báo cả hai panel judge và các hạn chế nêu trên.

Các thay đổi này chưa được tự động sửa vào manuscript trong lần phân tích
này.
