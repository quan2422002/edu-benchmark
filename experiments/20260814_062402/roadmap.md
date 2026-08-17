# Roadmap — Thử nghiệm bốn tuần về kiểm định bằng con người

Experiment: `20260814_062402`
Trạng thái: `PLANNING — AWAITING PLAN 01 APPROVAL`
Nguồn hiện trạng chính: `20260727_170150`, `20260806_145124`

## 1. Mục tiêu

Trong ba tuần bắt buộc và một tuần mở rộng, nhóm sẽ:

1. đưa Hiếu, Hoàng, Thủy và Triệu vào cùng một quy trình làm việc có thể kiểm tra;
2. thử nghiệm truy xuất học liệu theo ý định do tác tử AI rút ra từ dữ liệu thô,
   thay vì mặc định chọn fragment đầu tiên cùng bài;
3. phát hiện fragment không đủ giá trị làm bằng chứng mà vẫn giữ nguyên truy vết nguồn v0;
4. kiểm tra tính toàn vẹn, nhất quán, thiên lệch vị trí và độ phù hợp với con người
   của hai bộ chấm mô hình hiện có;
5. dùng tác tử AI để giảm việc đọc lặp cho Thủy và Triệu, nhưng giữ một tập chấm
   mù độc lập để đo độ tin cậy thật sự của con người;
6. kết luận dự án đủ điều kiện mở rộng rà soát, cần sửa cục bộ hay phải quay lại
   thiết kế trước khi khóa phiên bản benchmark.

Experiment này không có thẩm quyền tự xác nhận rubric, điểm số, candidate hoặc
phán quyết mô hình là nhãn tham chiếu đã được chuyên gia xác nhận.

## 2. Lịch và tài liệu bắt đầu

- Ba tuần bắt buộc: 17/08/2026–04/09/2026.
- Tuần mở rộng: 07/09/2026–11/09/2026.
- [Gantt chart Excel của nhóm](planning/team-gantt.xlsx) — bản theo dõi chính.
- [Sổ mô tả nhiệm vụ theo thành viên](planning/member-task-cards.md).
- [Plan 01 để người phụ trách dự án duyệt](plans/01-four-week-human-validation-pilot.md).

## 3. Hai luồng công việc

```text
Luồng A — Bằng chứng Phase 1
kiểm chất lượng fragment → truy xuất theo ý định → thử nghiệm truy xuất

Luồng B — Hiệu lực đánh giá
kiểm toàn vẹn phán quyết → chấm mù của con người → phân tích bất đồng/thiên lệch

Hai luồng hội tụ tại cổng đánh giá mức sẵn sàng ở tuần 4.
```

Hiếu dẫn Luồng A về kỹ thuật; Nguyên giữ thẩm quyền nội dung Tin học. Hoàng dẫn
Luồng B về kỹ thuật. Thủy và Triệu là hai người rà soát sư phạm độc lập; họ không
phải đọc toàn bộ dữ liệu và không phải thao tác mã nguồn.

## 4. Trình tự plan

| Thứ tự | Plan | Trạng thái | Cổng |
|---:|---|---|---|
| 01 | [Thử nghiệm phối hợp và kiểm định trong bốn tuần](plans/01-four-week-human-validation-pilot.md) | `DRAFT` | Người phụ trách dự án duyệt lịch, khối lượng, vai trò, thẩm quyền và tiêu chí dừng. |

## 5. Cổng theo tuần

| Cổng | Thời điểm | Điều kiện tối thiểu |
|---|---|---|
| `G1` | 21/08 | Mọi thành viên hoàn tất làm quen; sổ hướng dẫn chấm, trường quyết định và ranh giới thẩm quyền được hiểu thống nhất. |
| `G2` | 28/08 | Có bộ phiếu thử nghiệm hợp lệ cho truy xuất và bộ chấm; fragment v0 không bị sửa; không gọi mô hình trả phí. |
| `G3` | 04/09 | Tập chấm mù, tập có tác tử hỗ trợ và các phép thử truy xuất đều hoàn tất; bất đồng được giữ nguyên để phân xử. |
| `G4` | 11/09 | Có báo cáo mức sẵn sàng và một quyết định: mở rộng, sửa cục bộ hoặc thiết kế lại. |

Nếu nhóm chỉ có ba tuần, dừng tại `G3` và chuyển phân xử/báo cáo sang đợt kế tiếp;
không bỏ tập chấm mù để ép hoàn thành `G4`.

## 6. Ngoài phạm vi

- Không chạy lại toàn bộ target hoặc toàn bộ bộ chấm.
- Không gọi API trả phí nếu chưa có phê duyệt riêng.
- Không sửa trực tiếp 2.750 fragment v0 hoặc sản phẩm lịch sử.
- Không đưa sản phẩm mới vào `shared/benchmark/` trong thử nghiệm nhỏ.
- Không để tác tử AI tự xác nhận nhãn sư phạm hoặc nội dung Tin học.
- Không yêu cầu Thủy và Triệu thao tác mã nguồn, cấu hình kỹ thuật hoặc lịch sử Git.

## 7. Cổng dừng hiện tại

Chỉ Plan 01 đang được đưa ra xem xét. Gantt và sổ nhiệm vụ là tài liệu lập kế
hoạch, không phải sự cho phép để bắt đầu triển khai.
