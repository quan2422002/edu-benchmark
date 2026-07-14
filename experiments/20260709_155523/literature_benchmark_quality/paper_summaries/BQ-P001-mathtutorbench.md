# BQ-P001 — MathTutorBench

Bài báo: `MathTutorBench: A Benchmark for Measuring Open-ended Pedagogical Capabilities of LLM Tutors`
Tệp cục bộ: `document/paper/source_paper/2502.18940v2.pdf`
Đường dẫn ổn định: `https://arxiv.org/abs/2502.18940`
Trạng thái công bố: bản tiền công bố (`preprint`)
Vai trò trong Kế hoạch 01: bài báo lõi về cách đánh giá năng lực sư phạm của gia sư AI, tách khỏi năng lực giải bài.

## 1. Bộ đánh giá được tạo từ nguồn dữ liệu nào?

**Bằng chứng.** MathTutorBench không phải một bộ dữ liệu đơn lẻ, mà là một bộ đánh giá gồm nhiều nhiệm vụ. Bài báo dùng GSM8k cho giải bài và đặt câu hỏi kiểu Socrates; StepVerify cho kiểm tra lời giải, tìm vị trí lỗi và sửa lỗi; MathDialBridge cho sinh phản hồi giàn giáo và tuân thủ chỉ dẫn sư phạm. Table 1 nêu rõ dữ liệu đầu vào, đáp án hoặc phản hồi tham chiếu, số mẫu và số lượt trung bình của từng nhiệm vụ.

**Bằng chứng.** Mỗi nhiệm vụ trong bộ đánh giá có dữ liệu, đề dẫn, cách chấm và phản hồi tham chiếu riêng. Vị trí nguồn: Figure 2; Table 1; Section 4.1; Section 4.2.

## 2. Bài báo kiểm tra độ phủ của bộ đánh giá bằng cách nào?

**Bằng chứng.** Bài báo thể hiện độ phủ bằng cấu trúc năng lực của gia sư: năng lực chuyên môn Toán, năng lực hiểu học sinh, và năng lực sinh phản hồi của giáo viên. Ba nhóm này được cụ thể hóa thành 7 nhiệm vụ.

**Suy luận cho dự án.** Với bộ đánh giá Tin học THCS, ta không nên chỉ đo độ phủ theo chủ đề SGK. Cần thêm độ phủ theo hành vi gia sư: giải thích, chẩn đoán lỗi, phản hồi bài làm, gợi mở, và tuân thủ yêu cầu của học sinh.

## 3. Bài báo kiểm tra độ chính xác hoặc chất lượng dữ liệu bằng cách nào?

**Bằng chứng.** Với các nhiệm vụ có đáp án rõ, bài báo dùng các thước đo chuẩn như độ chính xác, F1 và micro-F1. Với phản hồi gia sư dạng mở, bài báo không dùng độ giống câu chữ. Thay vào đó, bài báo huấn luyện reward model (mô hình phần thưởng) từ dữ liệu so sánh cặp để chấm chất lượng sư phạm.

**Bằng chứng.** Dữ liệu so sánh cặp gồm các phản hồi được ưu tiên và không được ưu tiên từ GSM8k-inpainted, MathDial, MRBench và Bridge. Bridge đặc biệt quan trọng vì có phản hồi của giáo viên chuyên gia và giáo viên mới. Vị trí nguồn: Section 4.3.2; Section 4.3.3; Table 2.

## 4. Bài báo kiểm tra độ khó, độ đa dạng hoặc phân tầng nhiệm vụ như thế nào?

**Bằng chứng.** Bài báo có nhánh khó hơn cho MathDialBridge, trong đó hội thoại dài hơn. Table 1 ghi số lượt trung bình của nhánh khó là 5.78, so với 3.08 ở nhánh thường. Kết quả cho thấy việc làm gia sư khó hơn khi hội thoại dài hơn. Vị trí nguồn: Table 1; Section 6.1; Table 4.

**Suy luận cho dự án.** Độ dài hội thoại, số lượt, số bước và mức hỗ trợ giàn giáo nên là một trục độ khó riêng, bên cạnh mức nhận thức Biết/Hiểu/Vận dụng.

## 5. Bài báo có kiểm tra độ tin cậy giữa người chấm không?

**Bằng chứng.** Bài báo không báo cáo độ đồng thuận giữa nhiều người chấm cho toàn bộ bộ đánh giá. Thay vào đó, bài báo kiểm tra mô hình phần thưởng bằng khả năng phân biệt phản hồi của giáo viên chuyên gia và giáo viên mới. Mô hình phần thưởng đạt độ chính xác tốt nhất 0.84 trong thiết lập này. Vị trí nguồn: Abstract; Figure 3; Table 3; Section 6.2.

**Giới hạn.** Đây là kiểm tra độ tin cậy của bộ chấm tự động, không phải kiểm tra độ đồng thuận giữa các giáo viên trên từng mẫu.

## 6. Bài báo có chứng minh bộ đánh giá phân biệt được mô hình/gia sư mạnh/yếu không?

**Bằng chứng.** Table 4 cho thấy nhiều mô hình giải bài tốt nhưng phản hồi giàn giáo kém. Ví dụ GPT-4o và Qwen2.5-Math-7B-Instruct mạnh ở giải bài nhưng không nhất thiết mạnh ở năng lực gợi mở. LearnLM cân bằng tốt hơn ở một số trục. Vị trí nguồn: Table 4; Section 6.1.

**Kết luận từ bằng chứng.** Bộ đánh giá có khả năng phân biệt “mô hình giải bài tốt” và “gia sư tốt”. Đây là điểm rất quan trọng cho dự án, vì gia sư AI không chỉ cần đúng đáp án.

## 7. Bài báo dùng phản hồi tham chiếu như thế nào?

**Bằng chứng.** Với nhiệm vụ sinh phản hồi gia sư, phản hồi tham chiếu là lượt nói của giáo viên. Mô hình phần thưởng chấm chất lượng sư phạm của phản hồi sinh ra, thay vì so khớp câu chữ với phản hồi tham chiếu. Vị trí nguồn: Table 1; Figure 2; Section 4.3.

**Suy luận cho dự án.** Với dữ liệu HNMU, lượt gia sư trong hội thoại mẫu có thể dùng làm phản hồi tham chiếu. Tuy nhiên, không nên coi đó là “đáp án câu chữ duy nhất”. Nó nên là căn cứ để viết tiêu chí chấm hoặc để so sánh chất lượng phản hồi.

## 8. Tiêu chí có thể chuyển sang bộ đánh giá Tin học THCS

**Từ bằng chứng sang ứng dụng.**

- Cần tách năng lực trả lời đúng khỏi năng lực dạy tốt.
- Cần nhóm nhiệm vụ về hiểu học sinh: nhận diện đúng/sai, tìm vị trí lỗi, sửa hoặc giải thích lỗi.
- Với nhiệm vụ gợi mở, việc không đưa đáp án ngay là tiêu chí sư phạm quan trọng.
- Hội thoại dài hơn có thể làm nhiệm vụ gia sư khó hơn.

## 9. Điểm chưa phù hợp hoặc cần xác nhận

**Câu hỏi mở.**

- Bài báo thuộc Toán; lỗi trong Scratch/Python/Tin học có cấu trúc khác lỗi giải toán.
- Việc huấn luyện mô hình phần thưởng riêng có thể vượt quá phạm vi hiện tại.
- Bài báo không đo kết quả học tập của học sinh, nên không thể suy ra rằng điểm bộ đánh giá cao đồng nghĩa học sinh học tốt hơn.
- Cần HNMU xác nhận khi nào gia sư nên gợi mở, khi nào nên đưa hướng dẫn đầy đủ.

## 10. Kết luận cho dự án

MathTutorBench không đưa ra một bảng kiểm riêng tên là “chất lượng của bộ đánh giá”. Tuy vậy, bài báo chứng minh bộ đánh giá đáng tin qua bốn điểm: độ phủ theo năng lực gia sư, nhiệm vụ có đáp án hoặc phản hồi tham chiếu rõ, bộ chấm tự động được kiểm tra bằng phản hồi chuyên gia–người mới, và kết quả cho thấy bộ đánh giá phân biệt được người giải bài tốt với gia sư tốt.
