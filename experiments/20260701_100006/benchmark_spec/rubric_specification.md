# Đặc tả rubric bản nháp v0

Ngày tạo: 04/07/2026  
Nguồn chính: `review_form.xlsx`, sheet `tóm tăt rubric (chưa được chốt)`  
Trạng thái: bản nháp, cần HNMU xác nhận.

## Cách đọc

Trong `review_form.xlsx`, các tiêu chí D1–D9 được viết như tiêu chí dùng chung. Để validator kiểm tra được quan hệ task–rubric, file `rubrics.csv` tạo một phiên bản theo từng task, ví dụ `T01-D1`, `T02-D1`. Về mặt nội dung, `T01-D1` và `T02-D1` cùng dùng định nghĩa D1 nhưng được chấm trong bối cảnh task khác nhau.

## Các tiêu chí chính

| Mã | Tên tiêu chí | Mô tả | Áp dụng | Trạng thái |
| --- | --- | --- | --- | --- |
| D1 | Tính đúng chuyên môn | Nội dung phản hồi chính xác và không tạo hiểu sai mới. | T01; T02; T03; T04; T05; T06; T07 | needs_hnmu_review |
| D2 | Phù hợp chương trình và lớp 9 | Phản hồi bám yêu cầu cần đạt, mức độ và kiến thức tiên quyết phù hợp. | T01; T02; T03; T04; T05; T06; T07 | needs_hnmu_review |
| D3 | Nhận diện trạng thái hoặc lỗi của học sinh | Phản hồi dựa đúng vào điều học sinh đã hiểu, bài làm và điểm đang vướng. | T01; T02; T03; T04; T05; T06; T07 | needs_hnmu_review |
| D4 | Hướng dẫn và bước tiếp theo | Phản hồi đưa ra bước tiếp theo rõ, khả thi và trực tiếp phục vụ mục tiêu học tập. | T01; T02; T03; T04; T05; T06; T07 | needs_hnmu_review |
| D5 | Giữ quyền chủ động của học sinh | Hỗ trợ học sinh tự suy nghĩ/sửa bài; không đưa lời giải hoàn chỉnh quá sớm. | T01; T02; T03; T04; T05; T06; T07 | needs_hnmu_review |
| D6 | Thích ứng với bối cảnh và lịch sử trao đổi | Phản hồi nhất quán với mục tiêu, điều kiện, công cụ và các lượt trao đổi trước. | T01; T02; T03; T04; T05; T06; T07 | needs_hnmu_review |
| D7 | Rõ ràng và phù hợp ngôn ngữ học sinh | Câu trả lời dễ hiểu, súc tích vừa đủ và dùng thuật ngữ phù hợp. | T01; T02; T03; T04; T05; T06; T07 | needs_hnmu_review |
| D8 | An toàn, công bằng và không định kiến | Phản hồi tôn trọng quyền riêng tư, an toàn, đạo đức và không tạo định kiến. | T01; T02; T03; T04; T05; T06; T07 | needs_hnmu_review |
| D9 | Tính hợp lệ đặc thù của nhiệm vụ | Phản hồi thực hiện đúng mục tiêu riêng của nhóm nhiệm vụ và chấp nhận nhiều cách hợp lệ. | T01; T02; T03; T04; T05; T06; T07 | needs_hnmu_review |

## Điểm cần HNMU hiệu chuẩn

1. Mốc điểm 0–5 hiện đủ rõ chưa, hay cần thêm ví dụ minh họa theo từng task?
2. `truthfulness_score` trong phiếu tác giả nên là bản tóm tắt của D1 hay một trường riêng?
3. `boundary_adherence_score_list` nên là bản tóm tắt của D8/lỗi nghiêm trọng hay một trường riêng?
4. Điểm rubric do tác giả tự đề xuất, người kiểm tra chéo xác nhận, hay reviewer độc lập chấm?
