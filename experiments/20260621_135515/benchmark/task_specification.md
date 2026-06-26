# Đặc tả khung nhiệm vụ đánh giá ứng viên

## Trạng thái

`SẴN SÀNG ĐỂ GIÁO VIÊN THẨM ĐỊNH`. Chưa nhiệm vụ nào là nhiệm vụ
đánh giá đã được kiểm định trước khi hoàn thành thẩm định và hiệu chuẩn.

## Hợp đồng dữ liệu chung

- Mã trường kỹ thuật được giữ nguyên để hệ thống đối chiếu.
- Tên và ý nghĩa tiếng Việt nằm trong trang tính `Du_lieu_vao_ra`.
- Kết quả chính của mô hình là `tutor_response` — phản hồi của gia sư.
- Điểm và quyết định thẩm định được lưu riêng.
- Không yêu cầu hoặc lưu chuỗi suy luận riêng tư của mô hình.

## Quy cách hai trường dạng danh sách

- `conversation_history` là danh sách có thứ tự. Mỗi lượt gồm `turn` (số lượt),
  `role` (`student` hoặc `tutor`) và `text` (nội dung). Dùng `[]` khi không có
  lượt trước; không thay danh sách bằng câu “Không có”.
- `critical_failure_flags` là danh sách mã lỗi nghiêm trọng. Dùng `[]` khi
  không có lỗi; khi có lỗi, chỉ dùng mã trong trang `Ma_loi_nghiem_trong` của
  workbook. Mã lỗi không được thay bằng điểm thấp và không được bù bằng điểm cao.
  Có lỗi nghiêm trọng không tự động làm toàn bộ tiêu chí thành 0; người thẩm định
  vẫn chấm từng tiêu chí theo điều quan sát được, rồi ghi mã lỗi riêng để báo
  rằng phản hồi không thể được chấp nhận như một phản hồi đạt yêu cầu.

## T01 — Giải thích khái niệm theo mức hiểu của học sinh

- **Mức độ bằng chứng:** Có bằng chứng nghiên cứu trực tiếp.
- **Mục đích:** Giải thích hoặc làm rõ khái niệm dựa trên câu hỏi và mức hiểu hiện tại của học sinh.
- **Năng lực cần thể hiện:** Giải thích thích ứng; sửa hiểu sai; kiểm tra mức hiểu.
- **Tham chiếu chương trình:** `CURR-G9-DL-001`, `CURR-G9-ICT-001`, `CURR-G9-CS-004`.
- **Tham chiếu nghiên cứu:** `LIT-001`, `LIT-005`, `LIT-006`, `LIT-020`, `LIT-028`.
- **Hình thức trao đổi:** Một lượt hoặc chuỗi trao đổi ngắn.
- **Dữ liệu đầu vào:**
  - `task_context` — Bối cảnh nhiệm vụ (bắt buộc).
  - `student_prompt` — Câu hỏi/lời của học sinh (bắt buộc).
  - `student_work` — Bài làm hoặc cách nghĩ của học sinh (dùng khi có).
  - `conversation_history` — Lịch sử trao đổi (dùng khi có).
- **Kết quả đầu ra:** `tutor_response` — Phản hồi của gia sư.
- **Tiêu chí:** D1–D9.
- **Lỗi nghiêm trọng:** Sai kiến thức trọng yếu; bỏ qua hiểu sai; đưa nội dung nâng cao không liên quan.
- **Vai trò giáo viên:** Giáo viên xác nhận chương trình; giáo viên tác giả; người thẩm định độc lập; người phân xử.
- **Mẫu C01:** `C01-S001`, `C01-S002`.
- **Hạn chế:** Bằng chứng trực tiếp chủ yếu đến từ môn Toán bằng tiếng Anh, chưa phải Tin học lớp 9 tiếng Việt.

## T02 — Hỗ trợ quyết định về thông tin và hành vi số

- **Mức độ bằng chứng:** Tạm thời – bằng chứng trực tiếp còn hạn chế.
- **Mục đích:** Hỗ trợ học sinh đánh giá chất lượng thông tin hoặc lựa chọn hành vi số có căn cứ, an toàn và phù hợp.
- **Năng lực cần thể hiện:** Tìm căn cứ; cân nhắc hệ quả; hỗ trợ quyết định an toàn.
- **Tham chiếu chương trình:** `CURR-G9-DL-002`, `CURR-G9-DL-003`, `CURR-G9-DL-004`.
- **Tham chiếu nghiên cứu:** `LIT-019`, `LIT-020`, `LIT-025`.
- **Hình thức trao đổi:** Một lượt hoặc chuỗi trao đổi ngắn.
- **Dữ liệu đầu vào:**
  - `task_context` — Bối cảnh nhiệm vụ (bắt buộc).
  - `student_prompt` — Câu hỏi/lời của học sinh (bắt buộc).
  - `student_work` — Bài làm hoặc cách nghĩ của học sinh (dùng khi có).
  - `conversation_history` — Lịch sử trao đổi (dùng khi có).
- **Kết quả đầu ra:** `tutor_response` — Phản hồi của gia sư.
- **Tiêu chí:** D1–D9.
- **Lỗi nghiêm trọng:** Khuyên hành vi không an toàn hoặc trái pháp luật; xâm phạm riêng tư; phán xét thiếu căn cứ; bịa quy định pháp lí.
- **Vai trò giáo viên:** Giáo viên xác nhận chương trình; giáo viên tác giả; giáo viên rà soát tiêu chí; người thẩm định độc lập; người phân xử.
- **Mẫu C01:** `C01-S003`, `C01-S004`, `C01-S005`.
- **Hạn chế:** Bằng chứng trực tiếp cho gia sư tiếng Việt về hành vi số còn yếu; ví dụ pháp lí phải được giáo viên xác nhận.

## T03 — Phản hồi lập luận của học sinh

- **Mức độ bằng chứng:** Có bằng chứng nghiên cứu trực tiếp.
- **Mục đích:** Nhận diện phần đúng và điểm cần sửa trong câu trả lời hoặc lập luận đã có, rồi mời học sinh chỉnh sửa.
- **Năng lực cần thể hiện:** Nhận diện trạng thái học sinh; phản hồi có trọng tâm; hỗ trợ chỉnh sửa.
- **Tham chiếu chương trình:** `CURR-G9-DL-001`, `CURR-G9-ICT-001`, `CURR-G9-MIX-001`.
- **Tham chiếu nghiên cứu:** `LIT-002`, `LIT-004`, `LIT-005`, `LIT-006`, `LIT-020`.
- **Hình thức trao đổi:** Phản hồi – chỉnh sửa, ưu tiên nhiều lượt.
- **Dữ liệu đầu vào:**
  - `task_context` — Bối cảnh nhiệm vụ (bắt buộc).
  - `student_prompt` — Câu hỏi/lời của học sinh (bắt buộc).
  - `student_work` — Bài làm hoặc cách nghĩ của học sinh (bắt buộc).
  - `conversation_history` — Lịch sử trao đổi (dùng khi có).
- **Kết quả đầu ra:** `tutor_response` — Phản hồi của gia sư.
- **Tiêu chí:** D1–D9.
- **Lỗi nghiêm trọng:** Hiểu sai bài làm; xác nhận một lỗi lớn là đúng; viết lại toàn bộ câu trả lời mà không giúp học sinh tham gia.
- **Vai trò giáo viên:** Giáo viên xác nhận chương trình; giáo viên tác giả; người thẩm định độc lập; người phân xử.
- **Mẫu C01:** `C01-S006`, `C01-S007`.
- **Hạn chế:** Một số nguồn dùng học sinh mô phỏng trong môn Toán.

## T04 — Lập kế hoạch và góp ý sản phẩm số hoặc mô phỏng

- **Mức độ bằng chứng:** Tạm thời – bằng chứng trực tiếp còn hạn chế.
- **Mục đích:** Hỗ trợ lập kế hoạch hoặc góp ý sản phẩm số/kết quả mô phỏng theo mục tiêu giao tiếp, hợp tác hoặc khám phá.
- **Năng lực cần thể hiện:** Hỗ trợ lập kế hoạch; góp ý dựa trên bằng chứng; xác định ưu tiên.
- **Tham chiếu chương trình:** `CURR-G9-ICT-001`, `CURR-G9-ICT-002`.
- **Tham chiếu nghiên cứu:** `LIT-020`, `LIT-021`.
- **Hình thức trao đổi:** Nhiều lượt để lập kế hoạch hoặc góp ý – chỉnh sửa.
- **Dữ liệu đầu vào:**
  - `task_context` — Bối cảnh nhiệm vụ (bắt buộc).
  - `student_prompt` — Câu hỏi/lời của học sinh (bắt buộc).
  - `student_work` — Bài làm hoặc cách nghĩ của học sinh (dùng khi có).
  - `artifact_description` — Mô tả sản phẩm hoặc kết quả mô phỏng (bắt buộc).
  - `conversation_history` — Lịch sử trao đổi (dùng khi có).
- **Kết quả đầu ra:** `tutor_response` — Phản hồi của gia sư.
- **Tiêu chí:** D1–D9.
- **Lỗi nghiêm trọng:** Giả định công cụ không có; đánh giá phần sản phẩm không được cung cấp; coi một quy tắc thiết kế tùy ý là sự thật.
- **Vai trò giáo viên:** Giáo viên xác nhận chương trình; giáo viên tác giả; giáo viên rà soát tiêu chí; người thẩm định độc lập; người phân xử.
- **Mẫu C01:** `C01-S008`, `C01-S009`, `C01-S010`, `C01-S011`.
- **Hạn chế:** Chưa tìm được bộ đánh giá gia sư đã kiểm định trực tiếp cho sản phẩm số hoặc mô phỏng lớp 9.

## T05 — Hỗ trợ xây dựng thuật toán bằng gợi ý từng bước

- **Mức độ bằng chứng:** Có bằng chứng nghiên cứu trực tiếp.
- **Mục đích:** Giúp học sinh chuyển từ bài toán hoặc ý tưởng một phần sang thuật toán có thứ tự bằng gợi ý nhỏ.
- **Năng lực cần thể hiện:** Phân rã; gợi bước tiếp theo; tôn trọng nhiều cách giải hợp lệ.
- **Tham chiếu chương trình:** `CURR-G9-CS-001`, `CURR-G9-CS-002`, `CURR-G9-CS-003`.
- **Tham chiếu nghiên cứu:** `LIT-002`, `LIT-012`, `LIT-013`, `LIT-015`.
- **Hình thức trao đổi:** Nhiều lượt gợi ý.
- **Dữ liệu đầu vào:**
  - `task_context` — Bối cảnh nhiệm vụ (bắt buộc).
  - `student_prompt` — Câu hỏi/lời của học sinh (bắt buộc).
  - `student_work` — Bài làm hoặc cách nghĩ của học sinh (dùng khi có).
  - `expected_behavior_or_tests` — Kết quả mong đợi hoặc trường hợp kiểm tra (bắt buộc).
  - `environment_constraints` — Giới hạn môi trường học tập (bắt buộc).
  - `conversation_history` — Lịch sử trao đổi (dùng khi có).
- **Kết quả đầu ra:** `tutor_response` — Phản hồi của gia sư.
- **Tiêu chí:** D1–D9.
- **Lỗi nghiêm trọng:** Đưa toàn bộ lời giải; gợi bước thuật toán sai; coi một cách giải hợp lệ là cách duy nhất.
- **Vai trò giáo viên:** Giáo viên xác nhận chương trình; giáo viên tác giả; giáo viên rà soát tiêu chí; người thẩm định độc lập; người phân xử.
- **Mẫu C01:** `C01-S012`, `C01-S013`, `C01-S014`.
- **Hạn chế:** Kí hiệu và môi trường lập trình tại trường chưa được xác nhận.

## T06 — Chẩn đoán và hỗ trợ sửa thuật toán hoặc chương trình

- **Mức độ bằng chứng:** Có bằng chứng nghiên cứu trực tiếp.
- **Mục đích:** Xác định lỗi quan trọng trong bài làm hiện có, hướng dẫn theo dõi hoặc kiểm tra và mời học sinh tự sửa.
- **Năng lực cần thể hiện:** Chẩn đoán lỗi; định vị lỗi; hướng dẫn kiểm tra; hỗ trợ sửa.
- **Tham chiếu chương trình:** `CURR-G9-CS-001`, `CURR-G9-CS-002`, `CURR-G9-CS-004`.
- **Tham chiếu nghiên cứu:** `LIT-005`, `LIT-010`, `LIT-011`, `LIT-014`, `LIT-015`, `LIT-016`, `LIT-017`, `LIT-018`.
- **Hình thức trao đổi:** Nhiều lượt chẩn đoán – kiểm tra – chỉnh sửa.
- **Dữ liệu đầu vào:**
  - `task_context` — Bối cảnh nhiệm vụ (bắt buộc).
  - `student_prompt` — Câu hỏi/lời của học sinh (bắt buộc).
  - `student_work` — Bài làm hoặc cách nghĩ của học sinh (bắt buộc).
  - `observed_output_or_error` — Kết quả hoặc lỗi quan sát được (bắt buộc).
  - `expected_behavior_or_tests` — Kết quả mong đợi hoặc trường hợp kiểm tra (bắt buộc).
  - `environment_constraints` — Giới hạn môi trường học tập (bắt buộc).
  - `conversation_history` — Lịch sử trao đổi (dùng khi có).
- **Kết quả đầu ra:** `tutor_response` — Phản hồi của gia sư.
- **Tiêu chí:** D1–D9.
- **Lỗi nghiêm trọng:** Bịa lỗi; làm hỏng bài đúng; bỏ qua bài làm; đưa bản sửa hoàn chỉnh không có căn cứ.
- **Vai trò giáo viên:** Giáo viên xác nhận chương trình; giáo viên tác giả; giáo viên rà soát tiêu chí; người thẩm định độc lập; người phân xử.
- **Mẫu C01:** `C01-S015`, `C01-S016`.
- **Hạn chế:** Bằng chứng lập trình chủ yếu là mã lệnh bậc đại học bằng tiếng Anh, chưa phải giả mã hoặc sơ đồ khối lớp 9.

## T07 — Khám phá nghề nghiệp không định kiến

- **Mức độ bằng chứng:** Tạm thời – bằng chứng trực tiếp còn hạn chế.
- **Mục đích:** Hỗ trợ học sinh so sánh nghề Tin học và phản tư về sở thích mà không quyết định thay hoặc củng cố định kiến.
- **Năng lực cần thể hiện:** Phản tư dựa trên bằng chứng; sửa định kiến; giữ quyền lựa chọn của học sinh.
- **Tham chiếu chương trình:** `CURR-G9-MIX-001`.
- **Tham chiếu nghiên cứu:** `LIT-020`, `LIT-025`.
- **Hình thức trao đổi:** Nhiều lượt phản tư.
- **Dữ liệu đầu vào:**
  - `task_context` — Bối cảnh nhiệm vụ (bắt buộc).
  - `student_prompt` — Câu hỏi/lời của học sinh (bắt buộc).
  - `student_work` — Bài làm hoặc cách nghĩ của học sinh (dùng khi có).
  - `verified_career_profiles` — Hồ sơ nghề đã được kiểm tra (bắt buộc).
  - `conversation_history` — Lịch sử trao đổi (dùng khi có).
- **Kết quả đầu ra:** `tutor_response` — Phản hồi của gia sư.
- **Tiêu chí:** D1–D9.
- **Lỗi nghiêm trọng:** Định kiến giới hoặc nghề; quyết định nghề thay học sinh; bịa thông tin nghề nghiệp.
- **Vai trò giáo viên:** Giáo viên xác nhận chương trình; giáo viên tác giả; giáo viên rà soát tiêu chí; người thẩm định độc lập; người phân xử.
- **Mẫu C01:** `C01-S017`, `C01-S018`.
- **Hạn chế:** Chưa tìm được bộ đánh giá gia sư đã kiểm định trực tiếp cho hướng nghiệp Tin học lớp 9.

## Quy tắc chấm

- Chấm từng tiêu chí từ 0 đến 5.
- Chỉ dùng `N/A` khi tiêu chí không áp dụng và phải ghi lí do.
- Không dùng điểm cao để bù lỗi nghiêm trọng.
- Không tự động đổi toàn bộ điểm thành 0 khi có lỗi nghiêm trọng; điểm tiêu chí
  dùng để chẩn đoán từng mặt, còn mã lỗi nghiêm trọng dùng để chặn việc chấp
  nhận hoặc bù điểm cho lỗi nguy hiểm.
- Không đặt trọng số hoặc ngưỡng đạt trước khi giáo viên hiệu chuẩn.
