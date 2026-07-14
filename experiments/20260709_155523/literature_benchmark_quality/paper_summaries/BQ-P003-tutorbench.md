# BQ-P003 — TutorBench

Bài báo: `TutorBench: A Benchmark To Assess Tutoring Capabilities Of Large Language Models`
Tệp cục bộ: `document/paper/source_paper/2510.02663v1.pdf`
Đường dẫn ổn định: `https://arxiv.org/abs/2510.02663`
Trạng thái công bố: bản tiền công bố (`preprint`)
Vai trò trong Kế hoạch 01: bài báo lõi về tiêu chí chấm riêng cho từng mẫu, vai trò chuyên gia, lọc mẫu để giữ độ khó và kiểm tra bộ chấm tự động.

## 1. Bộ đánh giá được tạo từ nguồn dữ liệu nào?

**Bằng chứng.** TutorBench gồm 1,490 mẫu do chuyên gia con người xây dựng, tập trung vào chương trình STEM bậc trung học phổ thông và AP. Bộ dữ liệu phủ 6 môn: Sinh học, Vật lý, Hóa học, Thống kê, Giải tích và Khoa học máy tính. Bộ dữ liệu có cả mẫu chỉ văn bản và mẫu đa phương thức; 828 mẫu có ảnh. Vị trí nguồn: Abstract; Introduction; Appendix A.2/Figure 7.

**Bằng chứng.** Ba tình huống sử dụng chính là: giải thích thích ứng, đánh giá/phản hồi bài làm, và hỗ trợ học chủ động. Vị trí nguồn: Section 2.1; Figure 2.

## 2. Bài báo kiểm tra độ phủ của bộ đánh giá bằng cách nào?

**Bằng chứng.** TutorBench thể hiện độ phủ theo môn học và tình huống sử dụng. Figure 7 báo phân bố khá cân bằng theo 6 môn, đồng thời có ba nhóm tình huống: giải thích thích ứng, đánh giá/phản hồi, và hỗ trợ học chủ động. Vị trí nguồn: Appendix A.2; Figure 7.

**Bằng chứng.** Ngoài môn học và tình huống, bài báo gắn nhãn từng tiêu chí chấm theo chiều đánh giá và kỹ năng gia sư để phân tích hành vi mô hình. Vị trí nguồn: Section 2.4; Figure 4; Figure 5; Appendix A.5.

**Suy luận cho dự án.** Với Tin học THCS, nên có ít nhất ba bảng độ phủ: học liệu/chủ đề, mức nhận thức/dạng bài, và hành vi gia sư/nhiệm vụ/tiêu chí chấm.

## 3. Bài báo kiểm tra độ chính xác hoặc chất lượng dữ liệu bằng cách nào?

**Bằng chứng.** Câu hỏi và tiêu chí chấm được viết bởi chuyên gia môn học có bằng cử nhân trở lên và có kinh nghiệm gia sư hoặc chuyên môn liên quan. Mỗi mẫu có phản hồi gia sư mẫu và các tiêu chí chấm riêng. Vị trí nguồn: Introduction; Appendix A.1.

**Bằng chứng.** Để giữ bộ đánh giá đủ khó, bài báo yêu cầu 5 mô hình mạnh trả lời từng mẫu và chỉ giữ mẫu mà ít nhất 3/5 mô hình đạt dưới 50% điểm có trọng số. Vị trí nguồn: Introduction; Appendix A.1.

## 4. Bài báo kiểm tra độ khó, độ đa dạng hoặc phân tầng nhiệm vụ như thế nào?

**Bằng chứng.** TutorBench dùng thang Bloom để phân tích yêu cầu nhận thức. Ba mô hình mạnh gán nhãn Bloom; nếu ít nhất hai mô hình đồng thuận thì gán nhãn cho mẫu. Cách này phủ hơn 97% số mẫu. Kết quả cho thấy điểm của mô hình không đi theo thứ tự khó dễ tuyến tính của Bloom. Vị trí nguồn: Section 3.4; Figure 4.

**Bằng chứng.** Bài báo gắn tiêu chí chấm vào 8 kỹ năng gia sư: nhận diện khó khăn cốt lõi, nhận diện bước đúng/sai của học sinh, nhắc lại kiến thức, đưa cách giải khác, dùng ví dụ/tương tự, đặt câu hỏi gợi mở, và hướng dẫn từng bước. Vị trí nguồn: Section 3.5; Figure 5.

## 5. Bài báo có kiểm tra độ tin cậy giữa người chấm không?

**Bằng chứng.** Bài báo kiểm tra bộ chấm tự động bằng 3 lượt chấm của chuyên gia cho từng tiêu chí trên 250 mẫu, tổng 2,475 tiêu chí, từ 69 chuyên gia. Độ đồng thuận trung bình giữa người chấm là 0.75; độ khớp giữa bộ chấm tự động và người chấm là 0.78; bộ chấm tự động đạt F1 0.82 so với nhãn đa số trên các tiêu chí không trọng yếu. Vị trí nguồn: Section 3.7; Figure 6.

## 6. Bài báo có chứng minh bộ đánh giá phân biệt được mô hình/gia sư mạnh/yếu không?

**Bằng chứng.** Không mô hình nào vượt 56% tổng điểm; Gemini 2.5 Pro đạt 55.65%, GPT-5 đạt 55.33%. Các mô hình còn lại có chênh lệch rõ, đồng thời khác nhau theo từng tình huống sử dụng. Vị trí nguồn: Table 1; Figure 3; Section 3.1–3.2.

**Bằng chứng.** Study mode không được đưa vào bảng xếp hạng chính vì cách tương tác không tương đương với bộ đánh giá chấm một phản hồi cuối trong lịch sử định sẵn. Vị trí nguồn: Section 3.6.

**Suy luận cho dự án.** Dự án cần định nghĩa rất rõ: bộ đánh giá chấm một phản hồi trong bối cảnh cố định hay chấm hội thoại động. Không nên trộn hai giao thức khi báo điểm.

## 7. Bài báo dùng phản hồi mẫu như thế nào?

**Bằng chứng.** Chuyên gia viết phản hồi gia sư mẫu. Các tiêu chí chấm được xây dựa trên phản hồi này. Tuy nhiên, phản hồi của mô hình được chấm đạt/không đạt theo tiêu chí, không bị so khớp câu chữ với phản hồi mẫu. Vị trí nguồn: Appendix A.1; Section 2.3.

## 8. Tiêu chí có thể chuyển sang bộ đánh giá Tin học THCS

**Từ bằng chứng sang ứng dụng.**

- Mỗi mẫu nên có phản hồi tham chiếu hoặc phản hồi mẫu và tiêu chí quan sát được.
- Tiêu chí chấm nên tự đủ nghĩa, ít chồng chéo và bao quát những yêu cầu chính.
- Lỗi nghiêm trọng có thể dùng trọng số âm hoặc chính sách riêng, ví dụ lộ đáp án trong nhiệm vụ gợi mở.
- Bộ chấm tự động phải được kiểm tra với chuyên gia con người trước khi dùng làm bộ chấm chính.
- Mức Bloom hữu ích để phân tích yêu cầu nhận thức, nhưng không nên xem mức Bloom cao hơn là luôn khó hơn với mô hình.

## 9. Điểm chưa phù hợp hoặc cần xác nhận

**Câu hỏi mở.**

- TutorBench có 3–39 tiêu chí cho mỗi mẫu, quá nặng nếu áp dụng nguyên xi cho HNMU.
- Bộ dữ liệu thuộc STEM bậc trung học phổ thông/AP, không phải THCS Việt Nam.
- Việc kiểm tra bộ chấm tự động trong tiếng Anh/STEM không đảm bảo chuyển được ngay sang tiếng Việt/Tin học 9.
- Cần quyết định phiếu tác giả có yêu cầu tiêu chí chi tiết riêng cho từng mẫu hay chỉ lưu ghi chú để ánh xạ về bộ tiêu chí rút gọn.

## 10. Kết luận cho dự án

TutorBench cho một khung rõ để đánh giá bộ đánh giá: mẫu do chuyên gia tạo, tiêu chí chấm riêng theo mẫu, lọc mẫu để tránh bộ đánh giá quá dễ, gắn nhãn tiêu chí để phân tích độ phủ kỹ năng, và kiểm tra bộ chấm tự động bằng người chấm. Đây là bằng chứng mạnh cho việc tách `Đáp án` khỏi phản hồi gia sư mẫu trong dự án.
