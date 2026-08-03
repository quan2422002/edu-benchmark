# Bàn giao — Tăng cỡ chữ sơ đồ pipeline minh họa

- Delegation ID: `EXP-20260730-KSE-PIPELINE-TYPOGRAPHY-001`
- Agent: parent thread ở chế độ single-agent
- Status: hoàn thành
- Native thread ID/label: không tạo specialist thread

## Delegation prompt

Giữ bố cục người dùng vừa format, tăng cỡ chữ và duy trì sự hài hòa của flow.

## Follow-up or steer messages

Không có.

## Inputs read

- `kse_submit_manuscript/diagrams/overall_pipeline_illustrated.drawio` phiên
  bản đã được người dùng format lại.

## Outputs created

- Cập nhật tại chỗ
  `kse_submit_manuscript/diagrams/overall_pipeline_illustrated.drawio`.

## Result summary

Áp dụng typography phân cấp: title phase 20 pt; process chính 17 pt; output cuối
19 pt; card phụ 14--16 pt; nhãn mũi tên và token 14 pt. Toàn bộ text dùng
Helvetica. Chỉ nới năm geometry có nguy cơ tràn: title Phase 2, title Phase 3,
book Adaptive Scaffolding, card sáu principles và card sáu capabilities. Các
vị trí và flow còn lại của người dùng được giữ nguyên. XML hiện có 65 cell, 45
vertex và 18 edge; ID, source/target và màu hợp lệ.

## Orchestrator decision

Chấp nhận chỉnh sửa typography tại chỗ, không phục hồi bố cục trước khi người
dùng format.

## Uncertainty

Máy chưa có Draw.io CLI nên chưa export ảnh để kiểm tra pixel-level; cần người
dùng mở file trong diagrams.net để duyệt trực quan lần cuối.

## Open questions and next human decisions

Sau khi UET duyệt typography, export PNG/PDF và thay Figure 1 nếu được yêu cầu.
