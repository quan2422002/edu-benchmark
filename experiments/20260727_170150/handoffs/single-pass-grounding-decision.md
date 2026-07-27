# Specialist handoff

- Delegation ID: `EXP-20260727-SINGLE-GROUNDING-001`
- Agent: orchestrator single-agent với `benchmark-specification-designer`
- Status: `completed_planning_only`
- Native thread ID/label: không có

## Delegation prompt

Đơn giản hóa giao thức chấm nguyên tắc: bỏ cách gán nhãn hai vòng và chỉ
dùng một lượt grounding có `gold_answer`.

## Inputs read

- README, ARCHITECTURE và active roadmap;
- Plans 01–02 của experiment `20260727_170150`;
- active grounding pool và tài liệu chuyển trạng thái;
- skill `benchmark-specification-designer`.

## Outputs updated

- Plan 01 khóa một grounding payload và một output duy nhất;
- Plan 02 khóa đúng một request cho mỗi candidate;
- roadmap, README, ARCHITECTURE, inherited-resource guide và state-transfer
  report được đồng bộ.

## Result summary

Mỗi candidate được model đọc đúng một lần với context,
`source_question` và `gold_answer`. Model trả đủ sáu
`requirement_score` trong một response. Schema dùng một trường `evidence`,
không còn nhãn trước/sau, `reference_effect` hoặc evidence tách theo vòng.

Hai run A/B trong pilot vẫn được giữ để đo độ ổn định, nhưng là hai lần
chạy lặp độc lập của cùng một phép chấm một lượt; A không cấp input cho B.

## Orchestrator decision

`gold_answer` là neo chuyên môn, không phải phản hồi gia sư mẫu và không tự
quyết định nguyên tắc. `gold_response` tiếp tục bị cấm trong input chấm.

## Open questions and next human decisions

- UET review Plan 01 sau khi đã đơn giản hóa.
- Chỉ sau khi Plan 01 hoàn thành mới review và duyệt Plan 02.
