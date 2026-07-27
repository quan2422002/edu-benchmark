# Giao thức rà soát mở rộng cho Plan 03: nền tảng đo lường

Ngày rà soát: 25/07/2026  
Thử nghiệm: `20260722_000940`  
Phạm vi: Workstream A của Plan 03; bổ sung căn cứ khoa học về đo lường, không thiết kế hoặc chốt hệ thống nhiệm vụ và tiêu chí cuối. Ngày 25/07/2026, phạm vi được bổ sung có truy vết bằng một nguồn nền tảng sư phạm về dàn giáo để làm rõ ranh giới năng lực; đây là phụ lục mở rộng sau rà soát chính, không được trình bày như một phần của truy vấn đo lường ban đầu.

## 1. Câu hỏi rà soát

Câu hỏi chính:

> Những nguồn phương pháp nào hỗ trợ việc thiết kế một benchmark gia sư Tin học THCS có truy vết, bao gồm định nghĩa năng lực cần đo, hiệu lực nội dung, độ nhất quán giữa người chấm, độ khó và khả năng phân biệt của mẫu, hiệu ứng sàn/trần, kiểm định LLM chấm điểm cùng giới hạn của ưu tiên theo cặp khi phản hồi tham chiếu không duy nhất?

Câu hỏi phụ:

1. Làm sao tổ chức lập luận theo chuỗi **năng lực cần đo → nhiệm vụ → bằng chứng**?
2. Hiệu lực nội dung cần những bằng chứng nào ngoài một nhận xét chung rằng “chuyên gia đã rà soát”?
3. Khi nào nên báo tỷ lệ đồng thuận, Cohen’s kappa, ICC hoặc chỉ số tương đương?
4. Độ khó, khả năng phân biệt và hiệu ứng sàn/trần giúp gì cho bộ phản hồi mở?
5. Cần kiểm tra thiên lệch nào trước khi dùng LLM chấm điểm trong thí điểm nội bộ?
6. Vì sao ưu tiên theo cặp có thể đánh giá sai một phản hồi hợp lệ khi `gold_response` không phải cách trả lời duy nhất?
7. Nguồn gốc Allison–Tharby phân biệt và kết nối sáu nguyên tắc thế nào, và KMP-Bench đã chuyển chúng thành nhãn cấp lượt ra sao?

## 2. Phạm vi nguồn

### Bao gồm

- Nguồn về thiết kế lấy bằng chứng làm trung tâm, bằng chứng hiệu lực, hiệu lực nội dung, độ tin cậy và đồng thuận, phân tích câu hỏi, hiệu ứng sàn/trần, thiên lệch mô hình chấm.
- Nguồn về đánh giá phản hồi mở có nhiều đáp án hợp lệ, nhiều phản hồi tham chiếu, nhiều mức chi tiết và giới hạn của so sánh theo cặp.
- Nguồn tổng quan sư phạm chất lượng cao được bổ sung sau rà soát chính nếu cần làm rõ trực tiếp một ranh giới năng lực và được ghi riêng trong nhật ký tìm kiếm.
- Sách gốc, bản xem trước chính thức và nguồn của chính tác giả được bổ sung có mục tiêu để kiểm tra cấu trúc/rành giới sáu nguyên tắc; đối chiếu với KMP-Bench, không coi sách thực hành là một nghiên cứu kiểm định taxonomy.
- Bài báo đã bình duyệt, bản tiền công bố hoặc báo cáo phương pháp có DOI/URL ổn định và vị trí bằng chứng rõ.

### Loại trừ

- Nguồn chỉ nói về tiến bộ học tập dài hạn.
- Nguồn chỉ mô tả benchmark nhưng không có phương pháp đo lường dùng được cho Plan 03.
- Nguồn không có vị trí đủ rõ để kiểm tra phát biểu chính.
- Nguồn không liên quan đến phản hồi mở, tiêu chí đánh giá, đồng thuận người chấm hoặc kiểm định bộ đánh giá.

## 3. Tìm kiếm và trích xuất

- Dùng arXiv và ACL Anthology cho LLM chấm điểm, hỏi–đáp mở và nhiều phản hồi tham chiếu.
- Dùng PMC, trang DOI và trang nhà xuất bản cho hiệu lực, độ tin cậy, lý thuyết kiểm tra và hiệu ứng sàn/trần.
- Dùng trang nhà xuất bản và DOI để kiểm tra nguồn bổ sung về dàn giáo; ghi rõ đây là tìm kiếm có mục tiêu sau rà soát chính.
- Ghi mỗi nguồn vào `source_registry.csv` và `evidence_matrix.csv`.
- Gắn mỗi phát biểu thiết kế trong `claim_matrix.csv` là `evidence` (được nguồn hỗ trợ trực tiếp), `inference` (suy luận của dự án) hoặc `open_question` (câu hỏi mở).
- Chỉ đưa vào nguồn có DOI hoặc URL ổn định.
- Không dùng một nguồn riêng lẻ để chốt hệ thống nhiệm vụ hay tiêu chí.

Việc rà soát dừng khi mỗi câu hỏi phụ có ít nhất một nguồn trực tiếp, có nguồn bổ trợ khi cần, và nguồn mới không còn bổ sung một loại bằng chứng mới cho Plan 03.

`search_log.csv` giữ nguyên câu truy vấn để bảo đảm khả năng tái kiểm. Do các công cụ tìm kiếm không cung cấp cùng một cách đếm kết quả, nhật ký ưu tiên khả năng truy vết truy vấn, nguồn và quyết định chọn/loại. Vì nhật ký không lưu đầy đủ số kết quả và mọi nguồn bị loại, sản phẩm này được mô tả là **rà soát có mục tiêu và có truy vết**, không phải tổng quan hệ thống.

## 4. Kiểm soát chất lượng

- Đọc đúng vị trí nguồn trước khi tổng hợp.
- Tách hiệu lực, độ tin cậy, phân tích câu hỏi và thiên lệch mô hình chấm.
- Không biến ví dụ từ miền khác thành chuẩn bắt buộc cho Tin học THCS.
- Không suy ra hệ tiêu chí cuối từ một số ít nguồn phương pháp.
- Dừng Workstream A khi ma trận bằng chứng qua kiểm tra tự động và mọi điểm còn mở đã được ghi cho HNMU/UET.
