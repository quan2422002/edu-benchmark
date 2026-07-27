# Specialist handoff

- Delegation ID: `PLAN03-C-C0A-FORWARD-V3-001`
- Agent: `pedagogical-principle-annotator`
- Status: `completed_with_failed_semantic_gate`
- Native thread ID/label: `/root/plan03_c0a_forward_v3`

## Delegation prompt

Chạy forward test năm ca theo schema v3 chỉ từ hai input
context/grounding đã khóa, không đọc tập nhãn kỳ vọng, run lịch sử,
dual-run cũ, dữ liệu thô hoặc `gold_response`.

## Follow-up or steer messages

Orchestrator khóa thread vào vùng ghi riêng
`method_revision_v3/forward_test/run_v3/`. Không có thay đổi task sau khi
specialist bắt đầu.

## Inputs read

- `agents/pedagogical-principle-annotator/SKILL.md`;
- `agents/pedagogical-principle-annotator/references/two_pass_annotation_contract.md`;
- hai input context/grounding và grounding manifest trong
  `method_revision_v3/forward_test/`.

## Outputs created

- bốn bảng metadata/nhãn của hai vòng;
- `principle_annotation_review_queue.csv`;
- `principle_annotation_run_manifest.json`;
- handoff riêng của specialist;
- `forward_test_validation_v3.json`;
- báo cáo `reports/plan03-workstream-c-v3-implementation-c0a-summary.md`.

## Result summary

Bundle gồm 5 candidate và 7 dòng nhãn, đạt validator cấu trúc. Kết quả
ngữ nghĩa khớp 3/5 tập kỳ vọng. `FT-C02` khác ở ranh giới
Questioning–Explanation; `FT-C04` khác ở ranh giới
Questioning–Modelling và đã được specialist đưa vào review queue.

## Orchestrator decision

Giữ C0a ở trạng thái chưa đạt và không spawn hai instance A/B cho C0b.
Không dùng một kỳ vọng kế thừa từ quy trình cũ để tự động phủ nhận một
luận giải v3 có căn cứ; chuyển đúng hai ca biên cho UET phân xử.

## Uncertainty

Hai tập kỳ vọng chưa khớp được chuyển từ bộ ví dụ trước khi
`gold_response` bị loại khỏi gán nguyên tắc. Vì vậy chưa thể kết luận lỗi
nằm ở specialist hay ở ngữ cảnh/kỳ vọng tổng hợp.

## Open questions and next human decisions

- UET quyết định tập nguyên tắc hoặc sửa ngữ cảnh cho `FT-C02`.
- UET quyết định tập nguyên tắc hoặc sửa ngữ cảnh cho `FT-C04`.
- Sau quyết định, chạy lại C0a trong thread mới; chỉ mở C0b nếu đạt 5/5.
