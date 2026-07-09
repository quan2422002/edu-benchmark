# Handoff — P04 plan revision từ P02/P03

## Trạng thái

Đã cập nhật plan P04 để phù hợp với P02 bản thu gọn và P03 synthesis. Chưa triển khai P04 vì plan vẫn ở trạng thái `DRAFT_REVISED`, cần người phụ trách dự án duyệt.

## Thay đổi chính

- Đổi trọng tâm từ “task theo Bloom” sang “task theo hành vi gia sư”.
- Chuyển `Mức độ nhận thức` thành metadata/cột riêng với 3 giá trị: `Biết`, `Hiểu`, `Vận dụng`.
- Cập nhật input P02 đúng hiện trạng: dùng `tin9_sgk_topics_v0.csv`, `cognitive_level_seed_map.md`, `scaffolding_function_notes.md`, và `LM-SGK-TIN9-4700233123`.
- Cập nhật input P03 đúng hiện trạng: dùng synthesis 3 paper tier A và các claim P03-C001...P03-C012.
- Bổ sung yêu cầu P04 không được hiểu bài học như node độc lập ngoài chủ đề; phải đọc quan hệ qua `parent_id`.
- Bổ sung serious-error policy: không tự động chấm 0 toàn task nếu chưa có mapping cụ thể tới rubric/policy.

## File đã sửa

- `experiments/20260705_215045/plans/04-bloom-task-taxonomy-and-compact-rubric.md`

## Cần người phụ trách dự án duyệt trước khi triển khai

- Có giữ 4 task tạm `T1–T4` như plan đề xuất không?
- `T4` chẩn đoán lỗi/hiểu lầm là task riêng hay nhãn phụ cho `T2/T3`?
- Rubric nên giữ 5 tiêu chí tạm `R1–R5` hay trình bày thành 4 nhóm gọn hơn?
- Serious error nào cần cap điểm rubric, lỗi nào cần loại mẫu, lỗi nào chỉ cần review lại?
