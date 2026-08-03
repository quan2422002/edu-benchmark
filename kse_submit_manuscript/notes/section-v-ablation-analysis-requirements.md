# Yêu cầu tổng hợp kết quả cho Section V-C — Ablation Study

Ngày lập: 30/07/2026  
Phạm vi đã chốt: `C-1 Instruction Ablation`, `C-2 Judge Robustness` và
`C-5 Position Sensitivity`  
Trạng thái: `COMPLETED` — bundle đã qua validation và số liệu đã được chèn
vào Section V-C

## 1. Mục tiêu

Section V-C phải trả lời ba câu hỏi:

1. Thay instruction baseline bằng LearnLM-oriented trên cùng Gemini base
   model làm kết quả thay đổi như thế nào?
2. Kết luận chính có bền vững khi thay Gemini judge bằng GPT judge hay
   không?
3. Kết quả có thay đổi theo vị trí ẩn danh `response_1`/`response_2`
   không?

Ba phân tích dùng lại artifact full run hiện có, không gọi thêm model.
`Instruction Ablation` là ablation đúng nghĩa. `Judge Robustness` và
`Position Sensitivity` là phân tích độ bền vững; không được mô tả như thí
nghiệm nhân quả.

## 2. Input duy nhất được phép dùng

- Candidate pool:
  `experiments/20260727_170150/outputs/benchmark_candidate_pool/eligible_without_plan03_review.csv`
- Gemini judge:
  `experiments/20260727_170150/outputs/benchmark_evaluation/full_1400_v1/judge_full_batch_gold_answer_only_v4/gemini35/run_judgments.jsonl`
- GPT judge:
  `experiments/20260727_170150/outputs/benchmark_evaluation/full_1400_v1/judge_full_batch_gold_answer_only_v4/openai_gpt54_mini_medium/run_judgments.jsonl`
- Report kiểm chứng số liệu full:
  `experiments/20260727_170150/reports/plan05-full-judge-results-analysis-20260730.md`

Không dùng kết quả pilot để thay số liệu full. Pilot chỉ có thể được nhắc
như bằng chứng thiết kế giao thức.

## 3. Quy ước chung

### 3.1. Đơn vị và join

- Đơn vị phán quyết: `comparison_id`.
- Đơn vị benchmark: `benchmark_candidate_id`.
- Đơn vị bootstrap: cụm `sample_id`.
- Hai judge phải có cùng 4.200 `comparison_id`.
- Mỗi tutor configuration phải có đúng 1.400 candidate.
- Mọi phép so sánh baseline–LearnLM phải ghép cùng
  `benchmark_candidate_id` trong cùng judge.

### 3.2. Phán quyết dùng để tính

- Dùng `overall_judgment.target_judgment` cho Overall Judgement.
- Dùng `adjusted_criterion_judgments`; trong v4 trường này phải bằng raw
  vì không áp lỗi nghiêm trọng.
- Không dùng `confidence` làm trọng số.
- Không loại phán quyết chỉ vì confidence thấp.

### 3.3. Win rate

```text
Win Rate = Win / (Win + Tie + Lose)
```

`Tie` nằm trong mẫu số và không được quy đổi thành 0,5.

```text
General-Level Acc.
  = trung bình win rate của 4 rubric chung

Principle-Level Acc._p
  = trung bình win rate của 3 rubric thuộc nguyên tắc p

Overall Acc.
  = (General-Level Acc.
     + trung bình macro của 6 Principle-Level Acc.) / 2
```

### 3.4. Khoảng tin cậy

- Dùng 5.000 lần bootstrap theo cụm `sample_id`.
- Cùng một bootstrap draw phải được dùng cho hai configuration trong
  phép so sánh paired.
- Báo percentile CI 95%.
- Ghi số bootstrap hợp lệ nếu một draw không chứa nguyên tắc hiếm.
- Không gọi một chênh lệch là ổn định nếu CI chứa 0.

## 4. C-1 — Instruction Ablation

### 4.1. Biến can thiệp

```text
Control: target_gemini35
Treatment: target_gemini35_learnlm_prompted
```

Hai configuration dùng cùng `gemini-3.5-flash`; khác biệt chủ đích là
instruction bundle. Mọi kết luận phải gọi đây là **instruction effect**,
không phải khác biệt giữa hai base model.

### 4.2. Phép tính bắt buộc

Tính riêng cho Gemini judge và GPT judge:

1. `Overall Judgement Acc.` của baseline và LearnLM-oriented.
2. `General-Level Acc.` của hai configuration.
3. Sáu `Principle-Level Acc.` của hai configuration.
4. `Overall Acc.` của hai configuration.
5. Chênh lệch paired:

```text
Delta = LearnLM-oriented - Gemini baseline
```

6. CI 95% theo cụm cho từng Delta.
7. Số candidate áp dụng cho từng nguyên tắc.

Tạo thêm bảng chi tiết theo 22 rubric để truy vết, nhưng manuscript chỉ
cần chín thành phần: Overall Judgement, General, sáu nguyên tắc và
Overall Acc.

### 4.3. Bảng đầu ra bắt buộc

| Judge | Component | N candidate | Baseline | LearnLM | Delta | 95% CI |
| --- | --- | ---: | ---: | ---: | ---: | --- |

`Component` nhận một trong:

```text
Overall Judgement
General
Challenge
Explanation
Modelling
Practice
Questioning
Feedback
Overall Acc.
```

### 4.4. Quy tắc diễn giải

- `Delta > 0`, CI không chứa 0: LearnLM-oriented cải thiện thành phần đó
  theo judge tương ứng.
- `Delta < 0`, CI không chứa 0: LearnLM-oriented làm giảm thành phần đó.
- CI chứa 0: chưa có bằng chứng về khác biệt ổn định.
- Hai judge khác dấu hoặc chỉ một CI loại 0: instruction effect phụ thuộc
  judge.
- Chỉ gọi hiệu ứng là bền vững khi hai judge cùng dấu và kết luận CI
  tương thích.

Không dùng việc một hàng có điểm cao hơn đơn thuần để nói LearnLM
“tốt hơn toàn diện”.

## 5. C-2 — Judge Robustness

### 5.1. Phép tính bắt buộc

Tính agreement Gemini–GPT trên cùng `comparison_id`:

1. Overall Judgement:
   - toàn bộ 4.200 cặp;
   - từng tutor configuration.
2. Criterion judgement:
   - toàn bộ rubric;
   - bốn rubric chung;
   - sáu nhóm nguyên tắc;
   - từng rubric chung.
3. Mỗi phạm vi phải có:
   - số cặp;
   - exact agreement;
   - Cohen's kappa;
   - Gwet's AC1.
4. Ma trận bất đồng có hướng theo tutor configuration:
   - Gemini Lose / GPT Win;
   - Gemini Win / GPT Lose;
   - mọi nhánh có Tie.
5. Chênh lệch điểm judge:

```text
Judge severity gap
  = score của Gemini judge - score của GPT judge
```

Tính gap cho General, sáu nguyên tắc, Overall Acc. và Overall Judgement.

### 5.2. Bảng đầu ra bắt buộc

Bảng agreement:

| Scope | N pairs | Exact agreement | Cohen's kappa | Gwet's AC1 |
| --- | ---: | ---: | ---: | ---: |

Bảng bất đồng có hướng:

| Tutor configuration | Gemini Lose / GPT Win | Gemini Win / GPT Lose | Có Tie |
| --- | ---: | ---: | ---: |

Bảng severity:

| Tutor configuration | Component | Gemini judge | GPT judge | Gap |
| --- | --- | ---: | ---: | ---: |

### 5.3. Quy tắc diễn giải

- Báo cả exact agreement, kappa và AC1; không chọn một hệ số thuận lợi.
- Agreement không phải accuracy so với human ground truth.
- Cùng thứ hạng nhưng khác mạnh giá trị điểm chỉ hỗ trợ
  **rank robustness**, không hỗ trợ score interchangeability.
- Bất đồng bất đối xứng trên Llama tương thích với khác biệt độ nghiêm
  khắc hoặc same-family effect, nhưng không xác định được nguyên nhân.
- Kết luận chính của paper chỉ được gọi là bền vững nếu cùng hướng dưới
  cả hai judge.

## 6. C-5 — Position Sensitivity

### 6.1. Phép tính bắt buộc

Với mỗi judge × tutor configuration × vị trí target:

1. số request;
2. Win, Tie, Lose;
3. target Win rate;
4. chênh lệch:

```text
Position delta
  = WinRate(target ở response_1)
    - WinRate(target ở response_2)
```

Tính thêm phân bố vị trí toàn bộ và theo từng configuration để kiểm mức
cân bằng.

### 6.2. Bảng đầu ra bắt buộc

| Judge | Tutor configuration | N response_1 | WR response_1 | N response_2 | WR response_2 | Delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: |

Có thể kèm Win/Tie/Lose trong artifact máy đọc; manuscript chỉ cần N,
hai win rate và Delta.

### 6.3. Ranh giới diễn giải bắt buộc

Đây là **descriptive position sensitivity**, không phải causal position
ablation, vì cùng một cặp response chưa được chấm ở cả hai thứ tự.

Không được viết:

> Gemini có position bias bằng X điểm phần trăm.

Chỉ được viết:

> Target Win rates differed descriptively by X percentage points between
> requests where the target occupied response 1 and response 2; because
> identical pairs were not evaluated in both orders, the difference may
> also reflect sample composition.

Muốn kết luận nhân quả cần một run mới đảo thứ tự trên cùng cặp response;
run đó nằm ngoài phạm vi tổng hợp hiện tại.

## 7. Validation bắt buộc

Trước khi bàn giao kết quả:

- hai input có đúng 4.200 record duy nhất;
- join có đúng 4.200 cặp judge;
- mỗi judge × configuration có đúng 1.400 phán quyết overall;
- mỗi rubric chung có đúng 4.200 cặp;
- tổng criterion pair là 38.832;
- mọi `target_judgment` thuộc `Win|Tie|Lose`;
- tổng Win+Tie+Lose bằng đúng N ở mọi bảng;
- hash input và phiên bản contract được ghi lại;
- các số đã có phải tái lập:
  - overall agreement: 80,45%;
  - rubric agreement: 73,24%;
  - Gemini position delta: +8,04; +6,60; +14,61 điểm phần trăm;
  - GPT position delta: +0,88; +1,51; +0,31 điểm phần trăm.

Nếu không tái lập được các anchor trên, dừng và điều tra trước khi viết
manuscript.

## 8. Output tinh gọn

Chỉ tạo một bundle máy đọc:

```text
experiments/20260727_170150/outputs/benchmark_evaluation/
  section_v_ablation_analysis_v1/
    results.json
```

`results.json` chứa ba top-level key:

```text
instruction_ablation
judge_robustness
position_sensitivity
```

Không tạo CSV riêng cho từng bảng. Bảng LaTeX sẽ được dựng trực tiếp từ
bundle đã validate hoặc copy có đối chiếu hash vào manuscript.

## 9. Điều kiện để viết Section V-C

Chỉ viết Section V-C sau khi:

1. `results.json` qua toàn bộ validation ở mục 7;
2. C-1 có Delta và CI cho đủ chín component dưới cả hai judge;
3. C-2 có đủ agreement, directional disagreement và severity gap;
4. C-5 có N và win rate theo hai vị trí;
5. mọi câu kết luận được gắn một trong:
   - bằng chứng trực tiếp;
   - diễn giải có điều kiện;
   - hạn chế/câu hỏi mở.

## 10. Kết quả thực thi

Bundle đã validate:

```text
experiments/20260727_170150/outputs/benchmark_evaluation/
  section_v_ablation_analysis_v1/results.json
```

SHA-256 của bundle tại lần tổng hợp này:

```text
000839d69791b59066da838f0db581856e5a4bf99c957b62bdf9e117d7828919
```

Script tái lập:

```text
scripts/benchmark_evaluation/analyze_section_v_ablation.py
```

Validation tái lập đúng 4.200 cặp overall, 38.832 cặp rubric, overall
agreement 80,45%, rubric agreement 73,24% và sáu position delta đã khóa.
