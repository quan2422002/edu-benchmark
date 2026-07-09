# Sprint 02 summary — phiếu tác giả, học liệu, rubric/task v0

Ngày cập nhật: 04/07/2026  
Experiment: `20260701_100006`  
Trạng thái: bản nháp triển khai nhanh, cần HNMU/UET xác nhận trước khi dùng đại trà.

## Đã hoàn thành trong lượt này

1. Đóng băng input Drive ở `drive_snapshot/`, gồm 4 folder và 14 file tải/export.
2. Rà soát phiếu tác giả ở `author_form/`.
3. Tạo mapping học liệu/chủ đề ở `learning_resources/`:
   - `learning_resource_source_map.csv`
   - `learning_resource_fragments_v0.csv`
   - `topic_map_grade6_9.csv`
   - `grade9_prerequisite_map.csv`
4. Tạo đặc tả benchmark nháp ở `benchmark_spec/`:
   - `benchmark_tasks.csv`
   - `rubrics.csv`
   - `serious_errors.csv`
   - `provenance_matrix.csv`
   - các bản đọc bằng mắt tương ứng.
5. Cập nhật danh sách câu hỏi cần HNMU xác nhận ở `reports/hnmu-open-questions.md`.

## Cảnh báo quan trọng

- Các artifact hiện tại là **bản nháp v0**, chưa phải benchmark chính thức.
- Mapping chủ đề lớp 6–8 hiện chỉ là placeholder/suy luận, chưa có bóc tách SGK lớp 6–8 đầy đủ.
- T02, T04, T07 cần thận trọng vì bằng chứng nghiên cứu trực tiếp còn hạn chế.
- Mã lỗi nghiêm trọng hiện được map tới rubric liên quan; không mặc định làm 0 toàn bộ task nếu HNMU chưa chốt chính sách khác.

## Việc nên làm tiếp

1. Cho HNMU review `hnmu-open-questions.md` và các bảng CSV quan trọng.
2. Nếu cần giáo viên bắt đầu tạo mẫu ngay, sinh bản Google Sheet/Excel thân thiện từ `task_code_registry.csv`, `learning_resource_source_map.csv`, `learning_resource_fragments_v0.csv`.
3. Chạy rà soát nghiên cứu sâu riêng cho T02/T04/T07 nếu vẫn giữ trong pilot.
4. Bóc tách/OCR học liệu lớp 6–9 kỹ hơn trước khi scale tạo mẫu.
