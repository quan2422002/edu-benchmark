# Specialist handoff

- Delegation ID: `none`
- Agent: `root`
- Status: `completed`
- Native thread ID/label: `single-agent`

## Delegation prompt

Không có delegation. Parent thread trực tiếp dùng
`research-methodologist` và `benchmark-specification-designer`.

## Follow-up or steer messages

Người dùng duyệt cấu trúc mới cho Section V: giữ nguyên A
`Experimental Setup`, viết ngay B `Main Results`, và chỉ giữ ba nhánh cho
C `Ablation Study`: instruction ablation, judge robustness và position
sensitivity. Người dùng yêu cầu một đặc tả kết quả để tự tổng hợp phần C.

## Inputs read

- `kse_submit_manuscript/manuscript/main.tex`
- `kse_submit_manuscript/PLAN.md`
- `experiments/20260727_170150/reports/plan05-full-judge-results-analysis-20260730.md`
- `experiments/20260727_170150/reports/plan05-judge-pilot-results-analysis-20260730.md`
- hai full judge JSONL v4 và candidate pool được chỉ trong requirements.

## Outputs created

- `kse_submit_manuscript/notes/section-v-ablation-analysis-requirements.md`
- `experiments/20260727_170150/handoffs/kse-section-v-main-results-and-ablation-requirements-20260730.md`

Các file được cập nhật:

- `kse_submit_manuscript/manuscript/main.tex`
- `kse_submit_manuscript/README.md`
- `kse_submit_manuscript/notes/manuscript_status.md`
- `experiments/20260727_170150/coordination/coordination_log.jsonl`

## Result summary

Section V hiện có:

```text
A. Experimental Setup
B. Main Results
   1. Pairwise Separation and Family-Level Robustness
C. Ablation Study
   1. Judge Robustness
   2. Position Sensitivity
```

Main Results dùng bảng KMP-compatible đã chú giải đầy đủ, chênh lệch
cluster-bootstrap, family-macro và holistic outcomes. Instruction
Ablation chưa được chèn hiển thị; một comment LaTeX giữ vị trí cho đến khi
bundle yêu cầu được tính.

Requirements khóa input, join, win-rate, bootstrap, bảng đầu ra và ranh
giới diễn giải cho:

- C-1 Instruction Ablation;
- C-2 Judge Robustness;
- C-5 Position Sensitivity.

## Orchestrator decision

Không chạy model hoặc tự tạo kết quả ablation. Main Results được viết từ
artifact full đã validate. Section C chỉ hoàn thiện sau khi một
`results.json` tinh gọn tái lập được các anchor đã khóa.

## Uncertainty

- Position sensitivity hiện là mô tả, không phải causal swap-order
  ablation.
- Same-family effect không thể xác định nguyên nhân chỉ từ hai judge.
- Instruction effect chỉ được gọi là bền vững nếu hai judge có kết luận
  tương thích.
- PDF hiện biên dịch thành công nhưng dài chín trang, vượt giới hạn KSE
  sáu trang.

## Open questions and next human decisions

1. Người dùng tổng hợp hoặc yêu cầu code tạo
   `section_v_ablation_analysis_v1/results.json`.
2. Parent thread chèn Instruction Ablation và rút gọn C-2/C-5 sau khi
   bundle được validate.
3. UET quyết định cắt bảng/đưa chi tiết sang supplementary để manuscript
   không quá sáu trang.
