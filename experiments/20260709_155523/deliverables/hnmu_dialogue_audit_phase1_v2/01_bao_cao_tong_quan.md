# Báo cáo tổng quan kết quả rà soát Phase 1

## Quy mô và trạng thái

| Khối | Tổng | Pass chính thức | Cần xem lại | Failed | Non-pass |
|---:|---:|---:|---:|---:|---:|
| 6 | 238 | 106 (44.54%) | 131 (55.04%) | 1 (0.42%) | 132 (55.46%) |
| 7 | 224 | 132 (58.93%) | 91 (40.63%) | 1 (0.45%) | 92 (41.07%) |
| 8 | 280 | 209 (74.64%) | 70 (25.00%) | 1 (0.36%) | 71 (25.36%) |
| 9 | 308 | 218 (70.78%) | 90 (29.22%) | 0 (0.00%) | 90 (29.22%) |

Kiểm định bảng khối × ba trạng thái loại trừ nhau:

- Chi-square: 61.795094
- Bậc tự do: 6
- p-value: 1.9421247e-11
- Cramér’s V: 0.171541

## Độ phủ bài học của mẫu pass

- Lớp 6: 17 bài trong danh mục; 6 bài không có mẫu pass.
- Lớp 7: 16 bài trong danh mục; 5 bài không có mẫu pass.
- Lớp 8: 20 bài trong danh mục; 4 bài không có mẫu pass.
- Lớp 9: 22 bài trong danh mục; 3 bài không có mẫu pass.

Bảng độ phủ bắt đầu từ danh mục bài học đầy đủ rồi mới nối số mẫu và trạng thái. Vì vậy bài có 0 mẫu pass vẫn xuất hiện và được ghi “không có mẫu pass”.

## Dữ liệu tổng hợp và ứng viên trùng lặp

Bốn CSV root cho phép tra toàn bộ lớp 6–9. File ứng viên trùng lặp có 1 dòng và được chạy lại trên toàn bộ dữ liệu, không phải chỉ nối file lớp.

## Fragment đầy đủ hơn có đi kèm tỷ lệ đạt cao hơn không?

Các mẫu có “Tỷ lệ tiêu chí có dẫn fragment” cao hơn có tỷ lệ đạt chính thức cao hơn không?

**Chưa thể khẳng định.**

Khi xem toàn bộ dữ liệu, các mẫu có “Tỷ lệ tiêu chí có dẫn fragment” cao hơn có xu hướng đạt nhiều hơn. Tuy nhiên, trong những nhóm có đủ dữ liệu để so sánh giữa các mẫu cùng khối lớp và cùng nhóm chấm, xu hướng này không còn rõ ràng.

Phép so sánh trong cùng khối lớp và nhóm chấm chỉ sử dụng được 350 trong tổng số 1.050 mẫu, vì nhiều nhóm không có đủ sự khác biệt để thực hiện phép tính. Do đó, kết quả cần được diễn giải thận trọng.

File `05_report_fragment_va_ty_le_dat.md` là report dễ hiểu dành cho HNMU. File `05_phu_luc_ky_thuat_phan_tich_fragment.xlsx` là bảng chi tiết phục vụ kiểm tra kỹ thuật và vẫn giữ dữ liệu gốc để truy vết.

## Giới hạn và quyền quyết định

Các trạng thái và phân tích là kết quả rà soát hiện tại. Chúng hỗ trợ giáo viên tìm mẫu cần xem, không thay thế phán quyết chuyên môn của HNMU/UET.
