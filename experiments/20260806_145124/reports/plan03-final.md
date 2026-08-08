# Báo cáo cuối — Plan 03

Experiment: `20260806_145124`
Baseline: `plans/03-shared-benchmark-artifact-registry-and-promotion.md`
Trạng thái kết luận: `completed`

## 1. Kết quả

Plan 03 đã tạo `shared/benchmark/` làm discovery và consumption surface chuẩn,
trong khi các experiment lịch sử vẫn giữ nguyên làm provenance. Registry có bảy
bundle versioned; mỗi bundle có manifest ghi source, checksum, transformation,
count invariant, authority, access policy và limitation.

Promotion chạy qua staging và swap có rollback. Cùng source tạo output
byte-identical; clean-trackable snapshot không chứa raw `run_full.jsonl` vẫn tái
tạo chính xác registry SHA-256
`69567b2ae70ab61f625af716edcec5272f697b5d165400c528bfdfc02ae4d648`.

## 2. Source và artifact inventory

Trong bảng này, **file nguồn lịch sử** là đúng file mà promotion của Plan 03 đã
đọc; **bundle canonical** là đường dẫn dùng chung sau promotion. Các mô tả cấp
experiment trước đây không được coi là source locator.

| Bundle | File nguồn lịch sử đã khóa | Bundle canonical | Count/status |
|---|---|---|---|
| Raw-dialogue checklist | [`raw-dialogue-audit-criteria-v0.csv`](../../20260722_000940/inherited_resources/from_20260709_155523/checklists/raw-dialogue-audit-criteria-v0.csv)<br>[`raw-dialogue-quality-checklist-v0.md`](../../20260722_000940/inherited_resources/from_20260709_155523/checklists/raw-dialogue-quality-checklist-v0.md) | [`checklists/raw_dialogue/v1/`](../../../shared/benchmark/checklists/raw_dialogue/v1/) | 18 criteria; HNMU confirmation pending |
| Phase-1 pass dialogues | [`conversion_input_pass_samples.csv`](../../20260722_000940/outputs/benchmark_conversion/conversion_input_pass_samples.csv) | [`datasets/phase1_pass_dialogues/v1/`](../../../shared/benchmark/datasets/phase1_pass_dialogues/v1/) | 665 dialogue/family; operational pass |
| Candidate pool | [`benchmark_candidate_splits.csv`](../../20260722_000940/outputs/benchmark_conversion/full_v0/benchmark_candidate_splits.csv)<br>[`conversion_trace.csv`](../../20260722_000940/outputs/benchmark_conversion/full_v0/conversion_trace.csv)<br>[`conversion_dispositions.csv`](../../20260722_000940/outputs/benchmark_conversion/full_v0/conversion_dispositions.csv) | [`datasets/candidate_pool/v1/`](../../../shared/benchmark/datasets/candidate_pool/v1/) | 2.028 candidate, 2.028 trace, 665 disposition |
| Provisional evaluation pool | [`eligible_without_plan03_review.csv`](../../20260727_170150/outputs/benchmark_candidate_pool/eligible_without_plan03_review.csv)<br>[`full_run_analysis.json`](../../20260727_170150/outputs/principle_requirement_scoring/full_gemini35_medium_v1/full_run_analysis.json)<br>[`full_run_review_queue.csv`](../../20260727_170150/outputs/principle_requirement_scoring/full_gemini35_medium_v1/full_run_review_queue.csv)<br>[`run_manifest.json`](../../20260727_170150/outputs/principle_requirement_scoring/full_gemini35_medium_v1/run_manifest.json) | [`selections/provisional_evaluation_pool/v1/`](../../../shared/benchmark/selections/provisional_evaluation_pool/v1/) | 1.400 selected/655 family; 628 review; 0 blocked |
| Tutor capabilities | [`tutor_capabilities.csv`](../../20260727_170150/inherited_resources/from_20260722_000940/benchmark_specification/capability_model/tutor_capabilities.csv)<br>[`tutor_capability_model.md`](../../20260727_170150/inherited_resources/from_20260722_000940/benchmark_specification/capability_model/tutor_capability_model.md) | [`specifications/tutor_capabilities/v0/`](../../../shared/benchmark/specifications/tutor_capabilities/v0/) | 6; `needs_hnmu_review` |
| Pedagogical principles | [`pedagogical_principles.csv`](../../20260727_170150/inherited_resources/from_20260722_000940/benchmark_specification/principle_foundation/pedagogical_principles.csv) | [`specifications/pedagogical_principles/v0/`](../../../shared/benchmark/specifications/pedagogical_principles/v0/) | 6; `needs_hnmu_review` |
| Rubric library | [`benchmark_tasks.csv`](../../20260727_170150/outputs/benchmark_rubric/benchmark_tasks.csv)<br>[`rubrics.csv`](../../20260727_170150/outputs/benchmark_rubric/rubrics.csv)<br>[`serious_errors.csv`](../../20260727_170150/outputs/benchmark_rubric/serious_errors.csv)<br>[`provenance_matrix.csv`](../../20260727_170150/outputs/benchmark_rubric/provenance_matrix.csv)<br>[`rubric_review_packet.md`](../../20260727_170150/outputs/benchmark_rubric/rubric_review_packet.md) | [`specifications/rubric_library/v0/`](../../../shared/benchmark/specifications/rubric_library/v0/) | 1 task, 22 rubric, 6 serious errors; `needs_hnmu_review` |

Riêng raw-dialogue checklist, các link trên trỏ tới snapshot inherited mà
promotion thực sự đọc. Nguồn upstream ban đầu nằm trong experiment
`20260709_155523` và vẫn được ghi bằng `source_experiment` trong manifest.

Raw HNMU XLSX, raw model JSONL, provider output và evaluation output lớn không
được copy vào shared. Selection giữ 1.400 ID tối giản; `requirement_scores.csv`
giữ đủ 2.028 status/score compact để tái lập phép chọn 1.400/628/0.

## 3. Consumer migration và equivalence

Consumer đại diện
`scripts/benchmark_specification/build_principle_grounding_pool.py` đã đổi default
candidate input sang shared candidate pool. Chạy explicit source cũ và canonical
mới đều sinh đúng 2.028 dòng/665 family và cùng SHA-256 output:

`c8c480312b8abac3b6ca9a46ca5eae0a70aa52cc810bec77be2358710cfc756a`.

Source path cũ chưa bị xóa và được ghi trong deprecation map để rollback.

## 4. Validation

- Exact interpreter:
  `/home/quannda/miniconda3/envs/benchmark_env/bin/python`
- Shared validator: `passed`, 7 bundle, duplicate candidate ID `0`.
- Promotion idempotence: byte-identical sau hai lần chạy.
- Clean-trackable regeneration: byte-identical với working-tree promotion.
- Targeted registry/specification/packaging tests: `17 passed`.
- Full repository suite: `274 passed`.
- Governance validator, `pip check` và `git diff --check`: passed.

## 5. Giới hạn

- `shared` chỉ có nghĩa canonical để tìm và tiêu thụ, không tự nâng authority.
- 665 dialogue chưa phải mẫu được HNMU xác nhận cuối cùng.
- 2.028 candidate là output conversion đã validate, chưa phải benchmark freeze.
- 1.400 candidate là selection vận hành tạm; requirement score là kết quả một
  model run, không phải expert label hoặc accuracy.
- Capability, principle và rubric vẫn cần HNMU review.
- Consumer lịch sử khác chưa bị rewrite hàng loạt; Plan 03 chỉ migrate một
  consumer đại diện và giữ deprecation map.

## 6. Gate tiếp theo

Plan 03 hoàn tất. Plan 04 có thể được project lead đọc và quyết định duyệt nhưng
vẫn là `DRAFT`; closeout này không tự động cấp quyền triển khai Plan 04.
