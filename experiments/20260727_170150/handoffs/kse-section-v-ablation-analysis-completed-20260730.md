# Specialist handoff

- Delegation ID: `none`
- Agent: `root`
- Status: `completed`
- Native thread ID/label: `single-agent`

## Delegation prompt

Không có delegation. Parent thread trực tiếp dùng hướng dẫn của
`research-methodologist` và `benchmark-specification-designer` để thực hiện
phân tích đã được UET khóa.

## Follow-up or steer messages

Người dùng yêu cầu tổng hợp ngay kết quả cho ba nội dung của Section V-C:
Instruction Ablation, Judge Robustness và Position Sensitivity.

## Inputs read

- `experiments/20260727_170150/outputs/benchmark_candidate_pool/eligible_without_plan03_review.csv`
- `experiments/20260727_170150/outputs/benchmark_evaluation/full_1400_v1/judge_full_batch_gold_answer_only_v4/gemini35/run_judgments.jsonl`
- `experiments/20260727_170150/outputs/benchmark_evaluation/full_1400_v1/judge_full_batch_gold_answer_only_v4/openai_gpt54_mini_medium/run_judgments.jsonl`
- `kse_submit_manuscript/notes/section-v-ablation-analysis-requirements.md`
- `kse_submit_manuscript/manuscript/main.tex`

## Outputs created

- `src/edu_benchmark/benchmark_evaluation/section_v_ablation.py`
- `scripts/benchmark_evaluation/analyze_section_v_ablation.py`
- `tests/benchmark_evaluation/test_section_v_ablation.py`
- `experiments/20260727_170150/outputs/benchmark_evaluation/section_v_ablation_analysis_v1/results.json`
- `experiments/20260727_170150/handoffs/kse-section-v-ablation-analysis-completed-20260730.md`

Các file được cập nhật:

- `kse_submit_manuscript/manuscript/main.tex`
- `kse_submit_manuscript/manuscript/main.pdf`
- `kse_submit_manuscript/notes/section-v-ablation-analysis-requirements.md`
- `kse_submit_manuscript/notes/manuscript_status.md`
- `kse_submit_manuscript/README.md`
- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260727_170150/coordination/coordination_log.jsonl`

## Result summary

Analyzer chỉ đọc ba input đã khóa, không gọi model, và chỉ publish bundle
sau khi kiểm:

- 4.200 record duy nhất cho mỗi judge;
- đúng 1.400 comparison cho từng tutor configuration;
- 38.832 criterion judgment cho mỗi judge;
- cùng 4.200 `comparison_id` giữa hai judge;
- đúng contract `gold-answer-only-v4`;
- đúng overall agreement 80,45%, criterion agreement 73,24% và sáu
  position delta đã khóa.

Instruction ablation dùng 5.000 paired cluster-bootstrap draw theo 655
`sample_id`. Gemini judge cho thấy LearnLM làm giảm General 3,45 điểm,
Questioning 4,25 điểm và Overall Accuracy 2,52 điểm với CI không chứa 0.
GPT judge không có component nào có CI loại 0. Vì vậy, không có bằng chứng
cross-judge rằng instruction LearnLM cải thiện chất lượng.

`results.json` có đúng ba top-level key theo đặc tả. SHA-256:

```text
000839d69791b59066da838f0db581856e5a4bf99c957b62bdf9e117d7828919
```

## Orchestrator decision

Section V-C được hoàn thiện từ bundle đã validate. Judge Robustness báo cả
exact agreement, Cohen's kappa và Gwet's AC1; directional table giữ nhánh
Tie. Position Sensitivity báo N và win rate theo hai vị trí, nhưng chỉ được
diễn giải mô tả.

## Uncertainty

- Hai judge đều là LLM; agreement không phải accuracy so với human ground
  truth.
- Challenge chỉ có 8 candidate và Practice có 27 candidate.
- Position sensitivity không phải causal swap-order ablation.
- PDF biên dịch thành công nhưng vẫn dài chín trang, vượt giới hạn KSE sáu
  trang.

## Open questions and next human decisions

1. UET rà nội dung Section V-C và quyết định bảng nào chuyển sang
   supplementary khi rút xuống sáu trang.
2. UET cung cấp thông tin tác giả/đơn vị và tiếp tục rà Sections III–VI.

