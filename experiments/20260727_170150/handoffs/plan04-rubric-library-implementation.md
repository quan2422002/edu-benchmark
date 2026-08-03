# Handoff — Triển khai thư viện rubric Plan 04

- Delegation ID: `EXP-20260728-PLAN04-RUBRIC-001`
- Agent: `benchmark-specification-designer` ở chế độ single-agent
- Status: `implemented_awaiting_uet_hnmu_review`
- Native thread ID/label: không áp dụng

## Delegation prompt

Triển khai Plan 04 đã được UET duyệt: xây rubric chung và rubric riêng theo
sáu nguyên tắc trên pool ưu tiên 1.400 candidate, không gọi API và không
sửa score Plan 02–03.

## Inputs read

- Plan 04, roadmap, README và ARCHITECTURE;
- KMP-Bench cùng ma trận claim/evidence;
- mô hình sáu năng lực và provenance nghiên cứu;
- sáu nguyên tắc Allison–Tharby/KMP;
- phương pháp dàn giáo và mức nhận thức HNMU;
- registry SGK/SGV Tin học 6–9;
- kết quả Plan 03 và context/gold_response của các mẫu biên.

## Outputs created

- `outputs/benchmark_rubric/benchmark_tasks.csv`;
- `outputs/benchmark_rubric/rubrics.csv`;
- `outputs/benchmark_rubric/serious_errors.csv`;
- `outputs/benchmark_rubric/provenance_matrix.csv`;
- `outputs/benchmark_rubric/rubric_review_packet.md`.

## Result summary

- 1 task, 4 rubric chung và 18 rubric riêng;
- đúng 3 rubric cho mỗi nguyên tắc;
- 6 lỗi nghiêm trọng;
- 29 quan hệ provenance;
- bao phủ 6/6 năng lực và 6/6 nguyên tắc;
- 6 ca biên dùng context thật để UET/HNMU review.

## Orchestrator decision

Giữ cấu trúc `4 + 3 × n` ở trạng thái provisional. `gold_response` là đối
chứng, không phải đáp án duy nhất; judge sau này phải được phép kết luận
response mô hình tốt hơn reference.

## Uncertainty

Desk check chưa chứng minh độ tin cậy, khả năng phân biệt mô hình hoặc độ
đồng thuận. Challenge và Practice có coverage thấp. Các hành động của lỗi
nghiêm trọng chưa được HNMU xác nhận.

## Open questions and next human decisions

- UET review cấu trúc, ranh giới và phép chấm dự kiến.
- HNMU xác nhận tiêu chí, ví dụ Tin học và cổng lỗi nghiêm trọng.
- Chỉ sau review mới chuyển Plan 05 sang trạng thái triển khai.

## Follow-up disposition — chống tính trùng

UET đã duyệt ba quy tắc:

- rubric chung đo điều kiện nền, rubric riêng đo giá trị tăng thêm;
- serious error là cổng, không phải rubric;
- mỗi error chỉ áp một lần theo `suggested_action`;
  `affected_rubric_ids` chỉ phục vụ truy vết và không tự nhân phạt.

Do hạn thời gian, pilot chồng lấn và khả năng phân biệt không chạy trong
Plan 04; việc này được chuyển sang Plan 07.
