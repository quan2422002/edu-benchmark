# BQ-P004 — VietLegal / V-Legal

Bài báo: `Benchmarking Vietnamese Legal Knowledge of Large Language Models`
Tệp cục bộ: `document/paper/source_paper/2512.14554v5.pdf`
Đường dẫn ổn định: `https://arxiv.org/abs/2512.14554`
Trạng thái công bố: bản tiền công bố (`preprint`) trong kho mã cục bộ
Vai trò trong Kế hoạch 01: bài báo ngoài miền gia sư, nhưng rất hữu ích về kiểm soát chất lượng của bộ đánh giá tiếng Việt, phân tầng nhận thức, chuyên gia gán nhãn, hệ thống truy xuất nguồn và độ đồng thuận.

## 1. Bộ đánh giá được tạo từ nguồn dữ liệu nào?

**Bằng chứng.** VietLegal thu thập văn bản pháp luật từ nguồn chính thức của nhà nước, xử lý khoảng 55,000 văn bản bằng HTML parsing và OCR, rồi lưu vào cơ sở dữ liệu văn bản pháp luật và cơ sở dữ liệu đồ thị tri thức. Vị trí nguồn: Section 3.2; Figure 1.

**Bằng chứng.** Bộ dữ liệu cuối gồm 10,450 mẫu được chuyên gia xác thực, mỗi mẫu được gắn với nguồn pháp luật có thẩm quyền. Vị trí nguồn: Abstract; Section 3.2; Appendix E.

## 2. Bài báo kiểm tra độ phủ của bộ đánh giá bằng cách nào?

**Bằng chứng.** VietLegal dùng khung 5 mức nhận thức lấy cảm hứng từ Bloom, từ nhận diện/nhớ lại đến đánh giá/tuân thủ, gồm 22 nhiệm vụ. Table 1 ghi mục tiêu, dạng bài, thước đo và số mẫu kiểm tra của từng nhiệm vụ. Vị trí nguồn: Section 3.1; Table 1; Figure 3.

**Bằng chứng.** Bộ đánh giá có số lượng mục tiêu theo từng nhiệm vụ và từng mức nhận thức; quy trình gán nhãn được thiết kế bám theo 22 nhiệm vụ này. Vị trí nguồn: Appendix E; Table 1.

**Suy luận cho dự án.** Với Tin học THCS, cần bảng mục tiêu độ phủ theo khối lớp, chủ đề, bài học, mức nhận thức và dạng bài. Không nên chỉ nhìn tổng số mẫu.

## 3. Bài báo kiểm tra độ chính xác hoặc chất lượng dữ liệu bằng cách nào?

**Bằng chứng.** VietLegal dùng quy trình chuyên gia nhiều tầng. Chuyên gia cao cấp định nghĩa chủ đề và nguồn; hai chuyên gia trẻ độc lập tạo tình huống và đáp án theo từng đợt dữ liệu; sau mỗi 100 mẫu, hai người đổi đợt dữ liệu và kiểm tra chéo trong chế độ mù. Mẫu bất đồng được thảo luận, nếu vẫn chưa thống nhất thì chuyển lên chuyên gia cao cấp phân xử. Vị trí nguồn: Appendix E, Labelling Process; Verifying Process.

**Bằng chứng.** Người gán nhãn phải qua 2 ngày huấn luyện, làm thử 50 mẫu cho mỗi nhiệm vụ, hiệu chỉnh qua các ca biên và đạt ít nhất 85% khớp với nhãn chuẩn trước khi làm dữ liệu chính. Vị trí nguồn: Appendix E, Recruitment/Training.

**Bằng chứng.** Bài báo kiểm tra nguy cơ rò rỉ/trùng dữ liệu bằng 1,000 mẫu phân tầng, dùng Google search, Common Crawl, n-gram và so khớp mờ. Tỷ lệ chồng lặp tiềm năng là 1.8% và chủ yếu đến từ văn bản pháp luật/khuôn mẫu bắt buộc. Vị trí nguồn: data contamination analysis; Figure 3; Appendix.

## 4. Bài báo kiểm tra độ khó, độ đa dạng hoặc phân tầng nhiệm vụ như thế nào?

**Bằng chứng.** VietLegal có 5 mức nhận thức, 22 nhiệm vụ và nhiều dạng đầu ra: trắc nghiệm, nhiều lựa chọn, nhận diện thực thể, sinh văn bản, phân loại nhị phân và cấu trúc đồ thị tri thức. Vị trí nguồn: Table 1; Figure 3.

**Bằng chứng.** Bài báo dùng thước đo khác nhau theo nhiệm vụ: Accuracy, F1, Macro-F1, ROUGE-L, Node-F1, Edge-F1, Binary F1 và thang Likert 1–5 do con người chấm cho nhiệm vụ sinh văn bản. Vị trí nguồn: Table 1; Section 4; Appendix F.

## 5. Bài báo có kiểm tra độ tin cậy giữa người chấm không?

**Bằng chứng.** Trên 10,450 mẫu, độ đồng thuận ban đầu là 92.39% và Cohen’s Kappa là 0.89 trước khi thảo luận. 7.61% mẫu bất đồng được xử lý qua đồng thuận và phân xử bởi chuyên gia cao cấp. Vị trí nguồn: Appendix E, Verifying Process.

**Bằng chứng.** Với nhiệm vụ sinh văn bản, bài báo dùng đánh giá mù đôi; Cohen’s Kappa trung bình là 0.92 trên các chiều được chấm. Vị trí nguồn: Appendix F.1; Table 4.

## 6. Bài báo có chứng minh bộ đánh giá phân biệt được mô hình mạnh/yếu không?

**Bằng chứng.** VietLegal đánh giá 23 mô hình trên nhiều nhiệm vụ và cho thấy khác biệt theo họ mô hình, mức thích nghi miền, cách đề dẫn và truy xuất nguồn. Ở nhiệm vụ sinh văn bản, phản hồi do con người viết cao hơn phản hồi của mô hình khoảng 1.2–1.5 điểm trên thang 1–5. Vị trí nguồn: Table 2; Table 3; Table 4; Appendix F.

**Bằng chứng.** Phương pháp truy xuất nguồn theo kiểu tác tử cải thiện một số nhiệm vụ suy luận nhưng không đồng đều; bài báo nhấn mạnh cần chiến lược truy xuất theo nhiệm vụ. Vị trí nguồn: Table 11; Agentic RAG.

## 7. Bài báo dùng đáp án hoặc phản hồi mẫu như thế nào?

**Bằng chứng.** VietLegal có đáp án hoặc phản hồi chuẩn do chuyên gia xác thực theo từng nhiệm vụ. Với nhiệm vụ sinh văn bản, phản hồi do con người viết được so sánh với phản hồi của mô hình trong đánh giá mù đôi, không chỉ dùng ROUGE-L. Vị trí nguồn: Table 4; Appendix F.1.

## 8. Tiêu chí có thể chuyển sang bộ đánh giá Tin học THCS

**Từ bằng chứng sang ứng dụng.**

- Cần hệ thống học liệu/nguồn chính thức trước khi tạo và chấm bộ đánh giá.
- Giáo viên hoặc người rà soát cần công cụ truy xuất học liệu để tìm nguồn khi tạo và xác minh mẫu.
- Cần kiểm tra chéo, đo độ đồng thuận và có cơ chế phân xử cho dữ liệu quan trọng.
- Cần kiểm tra rò rỉ/trùng lặp khi dữ liệu có dùng AI để sinh hoặc lấy từ nguồn phổ biến.
- Mỗi mức nhận thức hoặc dạng nhiệm vụ cần thước đo phù hợp; không nên dùng một thước đo cho tất cả.

## 9. Điểm chưa phù hợp hoặc cần xác nhận

**Câu hỏi mở.**

- VietLegal thuộc lĩnh vực luật, không phải giáo dục/gia sư; không thể chuyển trực tiếp nhiệm vụ.
- Khung 5 mức nhận thức của VietLegal khác với 3 mức HNMU đang dùng: Biết, Hiểu, Vận dụng.
- Nguồn luật có tính chính thức và cấu trúc rõ hơn ảnh SGK/OCR hiện tại của dự án; vì vậy cần kế hoạch học liệu riêng.
- Chiến lược truy xuất học liệu chỉ nên thiết kế sau khi cơ sở dữ liệu học liệu đủ tin cậy.

## 10. Kết luận cho dự án

VietLegal là bằng chứng rất mạnh cho lớp “chất lượng của bộ đánh giá” ở dữ liệu tiếng Việt: cần nguồn chính thức, hệ thống truy xuất cho người tạo dữ liệu, quy trình chuyên gia gán nhãn, kiểm tra chéo, đo độ đồng thuận, kiểm tra trùng/rò rỉ và đánh giá theo mức nhận thức. Đây là bài báo nên dùng làm khuôn cho phần học liệu và kiểm định dữ liệu thô HNMU, dù không phải bài báo về gia sư.
