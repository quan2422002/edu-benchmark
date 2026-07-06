# Specialist handoff

- Delegation ID: `p03-step4A-rubric-split-revision-009`
- Agent: `benchmark-specification-designer`
- Status: `completed via single-agent fallback`
- Native thread ID/label: `null` / parent thread
- Completed at: `2026-07-06T09:56:28+07:00`

## Delegation prompt

Điều chỉnh phần rubric trong synthesis P03 sau phản hồi của người phụ trách dự án: R4 cũ đang gộp quá nhiều ý; cần tách rõ độ chính xác kiến thức và tính tuân thủ ranh giới theo phiếu tác giả `review_form.xlsx`.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260705_215045/roadmap.md`
- `agents/benchmark-specification-designer/SKILL.md`
- `agents/benchmark-specification-designer/references/rubric-and-serious-error-guidelines.md`
- `agents/benchmark-specification-designer/references/benchmark-spec-schema.md`
- `agents/benchmark-specification-designer/references/provenance-matrix-guidelines.md`
- `experiments/20260705_215045/reports/P03-literature-synthesis-for-design.md`
- `experiments/20260705_215045/literature_notes/evidence_to_design_matrix.csv`
- `experiments/20260701_100006/drive_snapshot/review_form.extracted.txt`
- `experiments/20260701_100006/author_form/author_form_field_matrix.csv`

## Outputs updated

- `experiments/20260705_215045/reports/P03-literature-synthesis-for-design.md`
- `experiments/20260705_215045/literature_notes/evidence_to_design_matrix.csv`
- `experiments/20260705_215045/plans/03-targeted-paper-review-bloom-tutoring.md`
- `experiments/20260705_215045/metadata.yaml`

## Result summary

Updated the P03 synthesis from a 4-rubric suggestion to a provisional 5-rubric compact set:

1. R1 — độ chính xác về kiến thức và bám học liệu.
2. R2 — hiểu đúng trạng thái/lỗi/nhu cầu của học sinh.
3. R3 — hỗ trợ sư phạm phù hợp.
4. R4 — tuân thủ mục tiêu, phạm vi và ràng buộc của task.
5. R5 — tuân thủ ranh giới an toàn, đạo đức, pháp lý và không định kiến.

The serious-error catalog remains a separate policy that should map errors to affected rubrics rather than automatically zeroing the whole task unless HNMU/professor confirms such a rule.

## Orchestrator decision

Keep P03 Step 4A scoped to three tier-A papers. This revision does not close P03 and does not finalize P04; it only makes the P03 synthesis less ambiguous before P04 consumes it.

## Open questions and next human decisions

- Should P04 keep R1–R5 as five separate rubrics, or group R4/R5 under one displayed section while still scoring them separately?
- Should `truthfulness_score` and `boundary_adherence_score_list` remain separate author-form fields, or become derived summaries from official rubric scores?
- What score-cap/exclusion policy should each serious error trigger?
