# Handoff — P04 revision task/rubric-only

## Trạng thái

Đã thu hẹp plan P04 theo phản hồi của người phụ trách dự án ngày 06/07/2026. P04 hiện chỉ tập trung vào hai phần không thể thiếu của benchmark: task và rubric.

## Thay đổi chính

- Bỏ mã lỗi nghiêm trọng khỏi phạm vi P04.
- Bỏ `serious_error_policy_v0.md`, `serious_errors.csv`, `provenance_matrix.csv` khỏi output chính của P04.
- Giữ task theo hành vi gia sư, không theo Bloom/mức nhận thức.
- Giữ 3 mức nhận thức `Biết`, `Hiểu`, `Vận dụng` như metadata/cột phiếu tác giả.
- Rubric tạm thời gồm 5 tiêu chí: R1 độ chính xác kiến thức, R2 hiểu trạng thái/yêu cầu/lỗi học sinh, R3 hỗ trợ sư phạm/giàn giáo, R4 tuân thủ task/yêu cầu/phạm vi Tin học 9, R5 tuân thủ ranh giới an toàn/đạo đức/pháp lý.
- Bổ sung luận giải kỹ vì sao task và rubric là hai phần phải làm trước.

## File đã sửa

- `experiments/20260705_215045/plans/04-bloom-task-taxonomy-and-compact-rubric.md`
- `experiments/20260705_215045/roadmap.md`
- `experiments/20260705_215045/metadata.yaml`

## Cần người phụ trách dự án duyệt trước khi triển khai

- Có giữ 4 task T1–T4 không?
- T4 chẩn đoán lỗi/hiểu lầm là task riêng hay nhãn phụ cho T2/T3?
- Rubric R1–R5 đã đủ gọn và đủ phân biệt chưa? Đặc biệt cần chốt ranh giới R4 và R5.
- Thang Likert 1–5 đã chốt cho `rubrics.csv`; cần HNMU/giáo sư xác nhận mô tả chi tiết từng mức 1–5 cho từng rubric.

## Correction 2026-07-06 - Khôi phục R5

R5 được khôi phục vì R5 là rubric về tuân thủ ranh giới an toàn, đạo đức và pháp lý, không phải catalog mã lỗi nghiêm trọng. P04 vẫn không tạo `serious_errors.csv`; catalog mã lỗi nghiêm trọng sẽ để plan sau.
