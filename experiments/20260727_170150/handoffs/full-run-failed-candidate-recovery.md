# Handoff — Chạy bù hai candidate lỗi của full run

- Delegation ID: `EXP-20260728-FULL-RECOVERY-001`
- Agent: orchestrator ở chế độ single-agent
- Trạng thái: hoàn thành
- Native thread: không áp dụng

## Phạm vi

Chỉ chạy lại hai candidate còn thiếu trong bundle
`full_gemini35_medium_v1`, không gửi lại 2.026 candidate đã thành công và
không thay đổi prompt, schema hay cấu hình model.

## Candidate đã chạy bù

- `BC-HNMU-G9-R0285-STT4-AI08`
- `BC-HNMU-G9-R0294-STT13-AI10`

## Kết quả

- Ba request bổ sung; tổng request tăng từ 2.057 lên 2.060.
- `run_full.jsonl` có 2.028 record và 2.028 ID duy nhất.
- Mỗi record có đủ sáu điểm; tổng cộng 12.168 score.
- Cả hai response phục hồi dùng `gemini-3.5-flash` và kết thúc bằng
  `FinishReason.STOP`.
- Manifest có `recovery_runs.status = completed`,
  `integrity.validated = true` và trạng thái
  `completed_awaiting_analysis`.
- Bộ test dự án đạt 160/160 bằng `benchmark_env`.

## Quyết định điều phối

Plan 02 hoàn thành. Bundle đủ điều kiện kỹ thuật để Plan 03 phân tích sau
khi UET duyệt plan; các score vẫn là đề xuất của model, không phải nhãn
chuyên gia.

## Điểm chưa chắc chắn

Manifest giữ một lỗi lịch sử của lượt full ban đầu để bảo toàn provenance;
đây không phải failure còn hiệu lực. Trạng thái cuối và kiểm toàn vẹn là
nguồn quyết định bundle có hoàn tất hay không.
