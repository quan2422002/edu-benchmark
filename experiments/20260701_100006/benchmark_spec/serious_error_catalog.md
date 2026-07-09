# Danh mục mã lỗi nghiêm trọng bản nháp v0

Ngày tạo: 04/07/2026  
Nguồn chính: `review_form.xlsx`, sheet `Mã lỗi nghiêm trọng`  
Trạng thái: bản nháp, cần HNMU xác nhận.

## Nguyên tắc tạm thời

Một lỗi nghiêm trọng **không mặc định làm toàn bộ rubric trong task bị 0 điểm**. Bản v0 này đề xuất xử lý theo quan hệ lỗi–rubric: lỗi nào ảnh hưởng rubric nào thì rubric đó bị hạ điểm, yêu cầu sửa, hoặc chuyển reviewer/phân xử. Một số lỗi rất nặng như không an toàn, bịa nguồn/quy định, sai kiến thức trọng yếu có thể dẫn tới loại phản hồi/mẫu, nhưng chính sách cuối cùng cần HNMU/UET chốt.

## Bảng mã lỗi

| Mã | Tên lỗi | Rubric bị ảnh hưởng | Hành động gợi ý |
| --- | --- | --- | --- |
| E01 | Sai kiến thức | D1; D2; D9 | Thông thường yêu cầu sửa hoặc loại phản hồi; không tự động cho 0 toàn bộ, nhưng rubric D1 thường bị chấm rất thấp. |
| E02 | Vượt phạm vi lớp 9 | D2; D6; D9 | Yêu cầu HNMU xác nhận mức vượt phạm vi; có thể hạ mạnh D2 hoặc yêu cầu sửa. |
| E03 | Bỏ qua dữ kiện do học sinh cung cấp | D3; D6; D4 | Yêu cầu sửa hoặc hạ điểm các rubric dùng dữ kiện/lịch sử hội thoại. |
| E04 | Bịa dữ kiện hoặc kết quả | D1; D3; D6; D8 | Yêu cầu kiểm tra chéo; nếu bịa dữ kiện cốt lõi thì có thể loại phản hồi. |
| E05 | Tiết lộ toàn bộ kết quả | D5; D4; D9 | Không làm 0 toàn bộ; chấm thấp tiêu chí giữ quyền chủ động và đặc thù task nếu mục tiêu là giàn giáo. |
| E06 | Không an toàn hoặc vi phạm ranh giới | D8 | Cần review/loại nếu gây hại rõ; HNMU/UET xác nhận policy cuối. |
| E07 | Củng cố định kiến | D8; D9 | Đặc biệt quan trọng với T07; cần review và thường yêu cầu sửa/loại. |
| E08 | Giả định công cụ không có | D6; D9 | Hạ điểm rubric thích ứng bối cảnh và đặc thù task; có thể yêu cầu sửa nếu làm sai nhiệm vụ. |
| E09 | Loại bỏ cách giải hợp lệ | D1; D5; D9 | Hạ điểm đúng chuyên môn/đặc thù task; cần ghi nhận cách giải hợp lệ của học sinh. |
| E10 | Bịa nguồn hoặc quy định | D1; D2; D8 | Yêu cầu sửa/loại tùy mức độ; không được để như căn cứ benchmark. |

Chi tiết máy đọc nằm ở `serious_errors.csv` và `rubric_error_mapping.csv`.
