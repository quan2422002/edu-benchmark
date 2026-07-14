# BQ-P002 — KMP-Bench

Bài báo: `From Solver to Tutor: Evaluating the Pedagogical Intelligence of LLMs with KMP-Bench`
Tệp cục bộ: `document/paper/source_paper/18426-AAAI26.ShiW-NLP.pdf`
Đường dẫn ổn định: `https://arxiv.org/abs/2603.02775`
Trạng thái công bố: AAAI-26; có bản trên arXiv
Vai trò trong Kế hoạch 01: bài báo lõi về đánh giá hội thoại gia sư nhiều lượt, độ phủ theo nguyên tắc sư phạm và kiểm soát chất lượng dữ liệu có dùng AI để sinh.

## 1. Bộ đánh giá được tạo từ nguồn dữ liệu nào?

**Bằng chứng.** KMP-Bench bắt đầu từ bài toán K-8 lấy từ 9 nguồn. Sau đó bài báo lọc và thẩm định thành 8K bài toán đã xác thực. Các bài toán này phủ 11 miền Toán học và 9 cấp học từ mẫu giáo đến lớp 8. Vị trí nguồn: Figure 1; Seed Problem Foundation; Dataset Statistics.

**Bằng chứng.** Từ các bài toán gốc, bài báo tạo 4 loại thành phần sư phạm: câu hỏi mở rộng, phân tích và sửa lỗi, bài luyện tập tương tự, và giải thích điểm học sinh còn bối rối. Các thành phần này được ghép thành luồng hội thoại và mở rộng thành 4.6K hội thoại gia sư. Vị trí nguồn: Figure 1; Tutoring Dialogue Curation.

## 2. Bài báo kiểm tra độ phủ của bộ đánh giá bằng cách nào?

**Bằng chứng.** KMP-Bench thể hiện độ phủ ở nhiều lớp:

- nguồn dữ liệu: 9 nền tảng giáo dục;
- miền kiến thức: 11 miền Toán;
- cấp học: 9 cấp học K-8;
- nguyên tắc sư phạm: thử thách phù hợp, giải thích, làm mẫu, luyện tập, đặt câu hỏi, phản hồi;
- loại năng lực: hội thoại tổng thể và kỹ năng gia sư nền tảng.

Vị trí nguồn: Dataset Statistics; Figure 2; Evaluation Framework.

**Suy luận cho dự án.** Đây là bài báo gần nhất với nhu cầu hiện tại: bộ đánh giá cần vừa phủ học liệu, vừa phủ hành vi gia sư. Chỉ một trong hai là chưa đủ.

## 3. Bài báo kiểm tra độ chính xác hoặc chất lượng dữ liệu bằng cách nào?

**Bằng chứng.** KMP-Bench có nhiều lớp kiểm soát chất lượng: nhiều mô hình cùng kiểm tra bài toán gốc; ví dụ vài mẫu do con người viết để hướng dẫn sinh dữ liệu; bước tự kiểm tra bằng mô hình; và kiểm tra thủ công luồng hội thoại. Người rà soát loại các luồng có học liệu bị bịa, trình tự sư phạm không hợp lý hoặc lượt hội thoại không có giá trị sư phạm. Kết quả loại 451 luồng, tương đương 7.6%. Vị trí nguồn: Figure 1; Dialogue Flow Generation and Verification.

**Bằng chứng.** Với bài luyện tập tương tự, bài báo tạo ba mức độ: dễ, trung bình, khó; đồng thời có bước tránh các biến thể quá tầm thường của bài gốc. Vị trí nguồn: Crafting Pedagogical Interaction Components.

## 4. Bài báo kiểm tra độ khó, độ đa dạng hoặc phân tầng nhiệm vụ như thế nào?

**Bằng chứng.** KMP-Bench dùng ba mức độ cho bài luyện tập tương tự, đồng thời thống kê số lượt trao đổi và độ dài lượt nói. Figure 2 báo trung bình 9.3 lượt trao đổi và 40 từ mỗi lượt. Vị trí nguồn: Figure 2; Dataset Statistics.

**Bằng chứng.** KMP-Dialogue đánh giá 6 nguyên tắc sư phạm. Mỗi phản hồi được chấm bằng tiêu chí chung và tiêu chí riêng theo nguyên tắc sư phạm. KMP-Skills đánh giá giải bài nhiều lượt, phát hiện/sửa lỗi và tạo bài toán. Vị trí nguồn: Evaluation Framework; Table 1; Table 2.

## 5. Bài báo có kiểm tra độ tin cậy giữa người chấm không?

**Bằng chứng.** Bài báo dùng Gemini-2.0-Flash làm bộ chấm tự động và kiểm tra bằng 300 mẫu do chuyên gia con người gán nhãn. Table 3 báo tỷ lệ khớp 89.7%, 87.1% và 92.5% ở ba nhóm mô hình, trung bình khoảng 89.8%. Vị trí nguồn: Table 3; Analysis of the Accuracy of KMP-Dialogue Evaluator.

**Giới hạn.** Đây là độ khớp giữa bộ chấm tự động và nhãn của chuyên gia, không phải độ đồng thuận giữa nhiều chuyên gia độc lập.

## 6. Bài báo có chứng minh bộ đánh giá phân biệt được mô hình/gia sư mạnh/yếu không?

**Bằng chứng.** Table 1 cho thấy mô hình đa dụng và mô hình chuyên Toán khác nhau mạnh theo điểm hội thoại sư phạm. Qwen2.5-Math-72B-Instruct kém Qwen2.5-72B-Instruct ở KMP-Dialogue, cho thấy chuyên Toán không tự động thành giỏi làm gia sư. Vị trí nguồn: Table 1; Main Results.

**Bằng chứng.** KMP-LM-7B sau khi huấn luyện thêm trên KMP-Pile cải thiện rõ so với Qwen2.5-Math-7B-Instruct, gồm +13.4 điểm overall accuracy ở KMP-Dialogue và tăng mạnh ở KMP-Skills. Vị trí nguồn: Table 1; Table 2; Main Results.

## 7. Bài báo dùng phản hồi tham chiếu như thế nào?

**Bằng chứng.** KMP-Dialogue cắt hội thoại tại một lượt gia sư. Lượt gia sư gốc trở thành phản hồi tham chiếu. Bộ chấm so sánh phản hồi của mô hình với phản hồi tham chiếu theo ba mức thắng/hòa/thua trên các tiêu chí chung và tiêu chí theo nguyên tắc sư phạm. Vị trí nguồn: Evaluation Framework; Table 1.

**Suy luận cho dự án.** Cách này rất phù hợp với dữ liệu HNMU: một hội thoại thô có thể tạo nhiều ứng viên bằng cách cắt ở từng lượt gia sư. Lượt gia sư gốc là phản hồi tham chiếu, còn nhiệm vụ và tiêu chí chấm quyết định cách đánh giá.

## 8. Tiêu chí có thể chuyển sang bộ đánh giá Tin học THCS

**Từ bằng chứng sang ứng dụng.**

- Phải kiểm tra tính hợp lý và trình tự sư phạm của hội thoại, không chỉ kiểm tra đáp án.
- Nên có bảng độ phủ theo học liệu, mức nhận thức, dạng bài và hành vi gia sư.
- Dữ liệu có dùng AI để sinh phải được lọc lỗi; KMP-Bench loại 7.6% luồng sau kiểm tra thủ công.
- Có thể dùng phản hồi tham chiếu từ hội thoại mẫu để chấm theo tiêu chí, nhưng không chấm bằng độ giống câu chữ.

## 9. Điểm chưa phù hợp hoặc cần xác nhận

**Câu hỏi mở.**

- KMP-Bench dùng nhiều tiêu chí hơn phạm vi hiện tại; cần rút gọn cho HNMU.
- Bài báo thuộc Toán K-8; cần HNMU xác nhận cách chuyển sang Tin học, Scratch và Python.
- Bộ chấm tự động chưa thể thay người rà soát trong giai đoạn đầu tiếng Việt.

## 10. Kết luận cho dự án

KMP-Bench là bằng chứng mạnh nhất cho quy trình dữ liệu hội thoại: dữ liệu có dùng AI để sinh phải qua xác thực, kiểm tra thủ công, lọc biến thể tầm thường và kiểm tra độ khớp giữa bộ chấm tự động với chuyên gia. Bài báo cũng củng cố quy trình “hội thoại thô → cắt tại lượt gia sư → phản hồi tham chiếu → chấm theo nhiệm vụ và tiêu chí”.
