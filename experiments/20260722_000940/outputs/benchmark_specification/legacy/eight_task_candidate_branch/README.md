# Legacy — nhánh tám nhiệm vụ ứng viên Workstream C

Trạng thái: **legacy theo quyết định của đại diện UET ngày 26/07/2026**.

Nhánh này được giữ để truy vết, không còn là đầu vào hoạt động của Plan 03. Không dùng các tệp trong thư mục này để:

- gán nhãn ứng viên;
- hiệu chỉnh người mã hóa;
- tính độ phủ hoặc bão hòa;
- xây hệ phân loại nhiệm vụ;
- yêu cầu UET/HNMU review riêng tám nhiệm vụ.

## Lý do chuyển legacy

Tám nhãn cũ trộn nhiều tầng: mục tiêu nhận thức, nguyên tắc sư phạm, chức năng hội thoại và cách điều tiết hỗ trợ. UET quyết định đơn giản hóa thành:

- một task `TASK-NEXT-TUTOR-RESPONSE`;
- sáu nguyên tắc KMP gắn đa nhãn cấp mẫu;
- sáu năng lực A–B làm nền xây tiêu chí.

Disposition chính thức được lưu tại:

`../../task_discovery/legacy_spec_dispositions.csv`

## Nội dung lưu trữ

- `benchmark_tasks.csv`, `task_candidate_matrix.csv`, `task_discovery_codebook.md`: bản C1 từng công bố;
- `specialist_preparation/`: bản làm việc, 20 nhãn thử và các bảng rỗng chưa hiệu chỉnh;
- `uet_review_packet/`: gói review cũ đã hủy trước khi UET điền quyết định;
- `plan03_workstream_c_c1_manifest.json`: manifest lịch sử tại thời điểm C1 cũ được tạo.

Hai mươi nhãn thử chưa bao giờ là nhãn chính thức và không được chuyển tự động sang sáu nguyên tắc. Nếu cần tái sử dụng, phải mã hóa lại từ đầu bằng sổ tay hiện hành.

## Khi nào được mở lại

Chỉ mở khi cần:

1. truy vết vì sao một ý nghĩa được chuyển sang nguyên tắc hoặc năng lực;
2. điều tra khoảng trống lặp lại mà sáu nguyên tắc chưa bao phủ;
3. đối chiếu lịch sử thiết kế trong báo cáo hoặc paper.

Việc mở lại không tự phục hồi bất kỳ nhãn nào thành task đang hoạt động.
