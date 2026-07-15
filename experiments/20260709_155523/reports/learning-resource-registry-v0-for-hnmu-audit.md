# Danh mục học liệu v0 phục vụ kiểm toán HNMU

Ngày thực hiện: 15/07/2026
Experiment: `20260709_155523`

## 1. Mục tiêu

Tạo danh mục học liệu v0 ở mức khối lớp, sách, chủ đề/bài học và vị trí/trang để Plan 04 có thể kiểm độ phủ dữ liệu HNMU.

Đây là bản **v0 thận trọng**, chưa phải danh mục chính thức được HNMU xác nhận.

## 2. Output đã tạo

- `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv`
- `shared/learning_resources/registries/sgk_thcs_lesson_position_registry_v0.csv`
- `shared/learning_resources/registries/sgk_sgv_source_registry.csv` được bổ sung URL/source key SGK từ registry cũ.

## 3. Nguồn dùng trong Pha 2

- Dữ liệu hội thoại HNMU lớp 6–7: `shared/raw_data/HNMU-teacher_dialog_samples/`.
- Topic map Tin học 9 từ experiment trước: `experiments/20260705_215045/topic_taxonomy/tin9_sgk_topics_v0.csv`.
- Source registry và ảnh/PDF SGK/SGV đã có trong `shared/learning_resources/`.

## 4. Thống kê topic/lesson map

Theo lớp và loại item:

- `('6', 'bai_hoc')`: 17
- `('6', 'chu_de')`: 5
- `('7', 'bai_hoc')`: 16
- `('7', 'chu_de')`: 4
- `('8', 'scope_placeholder')`: 1
- `('9', 'bai_hoc')`: 22
- `('9', 'chu_de')`: 6
- `('9', 'chu_de_con')`: 2
- `('9', 'phu_luc')`: 1

Theo trạng thái:

- `needs_hnmu_review`: 73
- `needs_uet_review`: 1

## 5. Thống kê lesson-position registry

Theo lớp:

- `6`: 181
- `7`: 160
- `9`: 27

Theo trạng thái:

- `needs_hnmu_review`: 368

## 6. Quyết định bảo thủ

- Với lớp 6–7, tên bài và vị trí lấy từ dữ liệu HNMU thật, nhưng nhóm chủ đề là suy luận từ thứ tự/tên bài nên gắn `needs_hnmu_review`.
- Với lớp 9, dùng lại OCR mục lục từ experiment `20260705_215045`, vẫn giữ trạng thái `needs_hnmu_review`.
- Với lớp 8, hiện chỉ có ảnh/PDF học liệu; Pha 2 không bịa danh sách bài học khi chưa OCR mục lục hoặc chưa có dữ liệu HNMU.
- Cột `source_image_path` của vị trí lớp 6–7 để trống vì chưa xác nhận offset giữa số trang in trong SGK/SGV và số thứ tự ảnh.
- Trong `sgk_thcs_lesson_position_registry_v0.csv`, cột `lesson_item_id` hiện được dùng như tham chiếu tới `item_id` trong topic/lesson map. Phần lớn là bài học, nhưng có 7 dòng Tin học 9 trỏ tới cấp chủ đề/chủ đề con/phụ lục vì nguồn OCR mục lục có vị trí trang cho các mục này. Đây là quyết định v0 để giữ thông tin mục lục, không phải xác nhận rằng các dòng đó là bài học.

## 7. Việc cần làm tiếp

- Pha 3: OCR mục lục/trang trọng điểm để map chắc hơn từ trang in sang ảnh.
- HNMU/UET cần rà soát nhóm chủ đề lớp 6–7 và toàn bộ danh mục Tin học 9 OCR.
- Cần tạo danh mục lớp 8 bằng OCR mục lục hoặc nguồn xác nhận từ HNMU trước khi dùng để kiểm phủ đầy đủ THCS.
