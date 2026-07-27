# Báo cáo chuyển trạng thái từ experiment `20260722_000940`

Ngày: 27/07/2026  
Experiment đích: `20260727_170150`

## Kết quả

Đã snapshot 41 file, tổng dung lượng khoảng 4,6 MB, thuộc các nhóm:

- bundle conversion 2.028 candidate;
- grounding pool 2.028 candidate;
- nền tảng đo lường và tổng quan bốn paper;
- mô hình sáu năng lực cùng truy vết;
- registry sáu nguyên tắc;
- báo cáo/decision đã hoàn thành;
- bốn artifact chẩn đoán của phương pháp cũ.

Mỗi file có SHA-256 trong `inherited_resources/snapshot_manifest.csv`.
Bundle active và diagnostic legacy đã được tách vật lý.

## Trạng thái phương pháp

Không chuyển nhãn A/B hoặc expected forward test thành ground truth. Plan
mới thay việc chọn trực tiếp tập nguyên tắc bằng chấm đủ sáu
`requirement_score` trong một lượt grounding có `gold_answer`, rồi chỉ dẫn
xuất tập bằng code. Giao thức hai vòng của experiment nguồn chỉ còn là
bằng chứng chẩn đoán.

## Công việc tiếp theo

Người phụ trách dự án review
`plans/01-principle-requirement-score-specification.md`, rồi mới review
`plans/02-vertex-ai-requirement-scoring-pilot.md`. Không API call hoặc
implementation nào được phép khi Plan 01 chưa hoàn thành và Plan 02 chưa
chuyển rõ sang `APPROVED`.
