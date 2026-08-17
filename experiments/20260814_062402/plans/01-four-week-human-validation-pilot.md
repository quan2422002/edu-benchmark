# Plan 01 — Thử nghiệm phối hợp và kiểm định trong bốn tuần

Experiment: `20260814_062402`
Trạng thái: `DRAFT — AWAITING PROJECT-LEAD APPROVAL`
Phụ thuộc: sản phẩm hiện hành của `20260727_170150` và kiến trúc đã cải tổ trong `20260806_145124`

## 1. Mục tiêu

Thực hiện thử nghiệm nhỏ có giới hạn để kiểm tra truy xuất học liệu Phase 1 và hiệu lực
của bộ chấm mô hình, đồng thời tạo một quy trình làm việc phù hợp cho bốn thành
viên mới trong thời gian 3–4 tuần.

## 2. Phạm vi

Sau khi được duyệt, plan cho phép:

- hướng dẫn thành viên làm quen và khóa phiếu nhiệm vụ;
- tạo công cụ quét chất lượng fragment, bộ phiếu truy xuất và bộ phiếu chấm mù;
- dùng sản phẩm/đầu ra mô hình hiện có để thử nghiệm ngoại tuyến;
- chạy một tập chấm mù độc lập và một tập có tác tử hỗ trợ;
- tổng hợp độ đồng thuận, chất lượng truy xuất, bất đồng và mức sẵn sàng;
- tạo hàng đợi rà soát mới trong experiment này.

Plan không cho phép gọi API trả phí, sửa sản phẩm chuẩn, sửa fragment v0, thay
nhãn benchmark hoặc khóa phiên bản mới.

## 3. Input và giả định

- 2.750 fragment v0 và chỉ mục SQLite hiện hành là đầu vào tạm thời, chưa phải bằng chứng đã xác nhận.
- 665 hội thoại Phase 1, 2.028 candidate và pool tạm 1.400 giữ nguyên.
- Hai bộ kết quả chấm đầy đủ hiện có chỉ là đề xuất của mô hình.
- Nguyên hoặc người được người phụ trách dự án chỉ định giữ thẩm quyền nội dung Tin học.
- Thủy và Triệu giữ thẩm quyền đánh giá sư phạm trong phạm vi thử nghiệm.
- Khối lượng giả định: Hiếu/Hoàng 12–16 giờ mỗi tuần; Thủy/Triệu 6–8 giờ;
  Nguyên 6–8 giờ; người phụ trách dự án 3–5 giờ. Nếu khác đáng kể, phải điều chỉnh Gantt
  trước khi bắt đầu.

## 4. Các bước triển khai dự kiến

1. Hoàn tất làm quen, bài thử chung và khóa quy tắc quyết định.
2. Xây bộ phiếu và công cụ kiểm tra cho hai luồng; không gọi mô hình mới.
3. Chạy thử nghiệm truy xuất, chấm mù và rà soát có tác tử hỗ trợ.
4. Giữ nguyên mọi bất đồng đến phiên phân xử.
5. Báo cáo theo ba khả năng: mở rộng, sửa cục bộ hoặc thiết kế lại.

Lịch chi tiết nằm tại [Gantt chart Excel](../planning/team-gantt.xlsx); trách nhiệm và
sản phẩm từng người nằm tại [sổ nhiệm vụ](../planning/member-task-cards.md).

## 5. Phạm vi ghi dự kiến

- `experiments/20260814_062402/`
- `src/edu_benchmark/learning_resources/` và test tương ứng cho Luồng A
- `src/edu_benchmark/dialogue_audit/` và test tương ứng cho Luồng A
- `src/edu_benchmark/benchmark_evaluation/` và test tương ứng cho Luồng B
- CLI mỏng tương ứng dưới `scripts/`

Không ghi vào `shared/benchmark/`, dữ liệu lịch sử hoặc bản thảo trong plan này.

## 6. Nghiệm thu

- Mỗi nhiệm vụ có một người chịu trách nhiệm và một người rà soát.
- Tập chấm mù không để lộ đề xuất của tác tử hoặc danh tính mô hình trước khi khóa quyết định.
- Fragment chất lượng thấp được gắn cờ/ánh xạ, không bị xóa hoặc sửa tại chỗ.
- Truy xuất cho phép nhiều truy vấn và `unresolved`; không dùng cách dự phòng “fragment đầu tiên cùng bài” làm bằng chứng.
- Có kết quả người–người, người–bộ chấm và đảo vị trí A/B trên tập thử nghiệm đã khóa.
- Thủy/Triệu chỉ rà toàn bộ tập hiệu chỉnh nhỏ, mẫu bị chuyển tuyến và mẫu kiểm ngẫu nhiên.
- Báo cáo không gọi kết quả thử nghiệm là nhãn tham chiếu đã xác nhận hoặc benchmark đã khóa phiên bản.
- Kiểm thử, công cụ kiểm tra và kiểm tra quản trị đạt bằng `benchmark_env`.

## 7. Rủi ro và cách quay lui

- **Thiên lệch do tự động hóa:** giữ tập chấm mù riêng và khóa trước khi xem đề xuất tác tử.
- **Người rà soát mệt mỏi:** giới hạn khối lượng, chia phiên và theo dõi thời gian thực tế.
- **Sai chuyên môn Tin học:** chuyển cho Nguyên/HNMU/UET, không ép người rà soát sư phạm quyết định.
- **Fragment v1 làm mất truy vết nguồn:** chỉ tạo bảng eligibility/ánh xạ mới; v0 bất biến.
- **Không đủ bốn tuần:** đóng ở `G3`, giữ phần phân xử tồn đọng; không giảm việc hai người chấm độc lập.

Quay lui bằng cách bỏ các đầu ra thử nghiệm chưa được đưa vào kho dùng chung và giữ nguyên toàn bộ sản phẩm nguồn.

## 8. Quyết định cần duyệt

Người phụ trách dự án cần duyệt hoặc sửa:

1. lịch 17/08–11/09/2026;
2. giả định số giờ mỗi thành viên;
3. khối lượng 24 candidate chấm mù, 60 candidate có tác tử hỗ trợ và 48 nhiệm vụ so sánh cặp;
4. vai trò nội dung Tin học của Nguyên;
5. việc tuần 4 là bắt buộc hay tùy tình hình.

Việc duyệt plan này không tự động cho phép API trả phí hoặc đưa sản phẩm vào kho dùng chung.
