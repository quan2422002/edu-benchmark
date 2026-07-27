# TR-P001 — MathTutorBench

Bài báo: `MathTutorBench: A Benchmark for Measuring Open-ended Pedagogical Capabilities of LLM Tutors`
Tệp cục bộ: `document/paper/source_paper/2502.18940v2.pdf`
Đường dẫn ổn định: `https://arxiv.org/abs/2502.18940`
Trạng thái công bố: bản tiền công bố (`preprint`), phiên bản v2 năm 2025
Miền nghiên cứu: gia sư Toán bậc trung học cơ sở
Vai trò trong experiment hiện tại: làm rõ sự khác nhau giữa nhiệm vụ, nguyên tắc sư phạm, thước đo theo nhiệm vụ và mô hình chấm điểm cho phản hồi gia sư mở.

## 1. Mục tiêu đọc bài báo trong experiment này

Bản tóm tắt này không nhằm mô tả toàn bộ MathTutorBench. Nó trả lời các câu hỏi phục vụ Plan 03:

1. MathTutorBench gọi đối tượng nào là “nhiệm vụ”?
2. Bốn nguyên tắc khoa học học tập có phải bốn tiêu chí chấm chung cho mọi mẫu không?
3. Một mẫu phản hồi gia sư mở được tạo và chấm như thế nào?
4. Phản hồi của giáo viên được dùng như đáp án duy nhất hay làm đối chứng?
5. Cấu trúc nào có thể chuyển sang các mẫu ứng viên Tin học THCS?

## 2. Vấn đề bài báo giải quyết

**Bằng chứng.** Bài báo cho rằng nhiều bộ đánh giá giáo dục chủ yếu đo khả năng giải bài hoặc so khớp văn bản, trong khi một gia sư còn phải hiểu trạng thái của học sinh, phát hiện lỗi, đưa hỗ trợ vừa đủ và tạo phản hồi phù hợp với diễn tiến hội thoại.

MathTutorBench vì vậy tách ba nhóm năng lực:

1. chuyên môn Toán;
2. hiểu học sinh;
3. tạo phản hồi của giáo viên/gia sư.

Vị trí nguồn: `Abstract`; `Section 1`; `Section 3.2`; `Figure 1`; `Figure 2`.

## 3. Bài báo chia nhiệm vụ như thế nào?

MathTutorBench có bảy nhiệm vụ thuộc ba nhóm năng lực:


| Nhóm năng lực        | Tên nhiệm vụ trong bài báo     | Đầu ra cần tạo hoặc dự đoán              | Thước đo                                          |
| ----------------------- | ----------------------------------- | ------------------------------------------------ | ---------------------------------------------------- |
| Chuyên môn Toán      | `Problem Solving`                   | Đáp án bài toán                             | `Accuracy`                                           |
| Chuyên môn Toán      | `Socratic Questioning`              | Câu hỏi dẫn dắt theo lối Socrates           | `BLEU`                                               |
| Hiểu học sinh         | `Student Solution Correctness`      | Nhãn đúng/sai của lời giải học sinh       | `F1`                                                 |
| Hiểu học sinh         | `Mistake Location`                  | Vị trí bước sai                              | `Micro-F1`                                           |
| Hiểu học sinh         | `Mistake Correction`                | Lời sửa cho bước/lời giải sai              | `Accuracy`                                           |
| Tạo phản hồi gia sư | `Scaffolding Generation`            | Lượt phản hồi tiếp theo của gia sư        | Tỷ lệ thắng theo mô hình chấm điểm ưu tiên |
| Tạo phản hồi gia sư | `Pedagogical Instruction Following` | Lượt phản hồi tuân thủ chỉ dẫn sư phạm | Tỷ lệ thắng theo mô hình chấm điểm ưu tiên |

**Kết luận có căn cứ.** Trong MathTutorBench, nhiệm vụ là một hợp đồng đầu vào–đầu ra có dữ liệu và thước đo riêng. Nó không phải một chiều chất lượng chung như “đúng kiến thức” hay “gợi mở tốt”.

Vị trí nguồn: `Section 4.1`; `Table 1`; `Table 4`; phần mô tả đề dẫn nhiệm vụ trong phụ lục.

## 4. Một mẫu benchmark được biểu diễn như thế nào?

### 4.1. Nhiệm vụ có đầu ra cấu trúc

Tùy nhiệm vụ, một mẫu có thể chứa:

- bài toán;
- lời giải tham chiếu;
- lời giải hoặc bước làm của học sinh;
- nhãn đúng/sai;
- vị trí lỗi;
- đáp án hoặc bản sửa tham chiếu.

Bộ chấm so đầu ra của mô hình với nhãn hoặc đáp án theo thước đo của nhiệm vụ.

### 4.2. Nhiệm vụ sinh phản hồi gia sư mở

Một mẫu điển hình chứa:

- bài toán;
- lời giải tham chiếu;
- lịch sử hội thoại;
- lượt phản hồi tiếp theo của giáo viên trong dữ liệu nguồn.

Mô hình nhận ngữ cảnh và sinh lượt gia sư tiếp theo. Phản hồi vừa sinh không được so khớp câu chữ với phản hồi giáo viên. Hai phản hồi được đưa qua mô hình chấm điểm ưu tiên để xác định phản hồi nào có chất lượng sư phạm tốt hơn.

Luồng vận hành:

```text
bài toán + lời giải tham chiếu + lịch sử hội thoại
                         ↓
                mô hình sinh phản hồi
                         ↓
chấm phản hồi mô hình và phản hồi giáo viên bằng cùng bộ chấm
                         ↓
     phản hồi mô hình có điểm cao hơn? → một lượt thắng
```

Vị trí nguồn: `Figure 2`; `Section 4.3`; `Table 4`.

## 5. Bốn nguyên tắc sư phạm có phải rubric chung không?

**Bằng chứng.** Bài báo nhấn mạnh bốn nguyên tắc:

1. bảo đảm tính đúng đắn;
2. hỗ trợ từng bước thay vì đưa ngay đáp án;
3. khuyến khích học sinh tự sửa lỗi;
4. tránh làm học sinh quá tải.

**Kết luận có căn cứ.** Đây là các nguyên tắc định hướng xây dựng và đánh giá năng lực gia sư. Bài báo không thể hiện chúng như bốn dòng tiêu chí chấm được gắn vào mọi mẫu rồi cộng điểm.

Đối với hai nhiệm vụ sinh phản hồi mở, bộ đánh giá cuối sử dụng một mô hình chấm điểm ưu tiên đã học từ dữ liệu so sánh. Vì vậy, phán quyết về các nguyên tắc nằm ẩn trong điểm của mô hình chấm, thay vì được xuất ra thành bốn kết quả riêng.

Vị trí nguồn: `Section 3.2`; `Section 4.3.1–4.3.3`; `Figure 6`; `Figure 7`.

## 6. Bộ tiêu chí nào được dùng để phát triển mô hình chấm?

**Bằng chứng.** Một phần dữ liệu huấn luyện bộ chấm đến từ MRBench, nơi các phản hồi được so sánh theo tám loại tiêu chí:

- chất lượng hướng dẫn;
- khả năng hành động được;
- có tiết lộ đáp án hay không;
- nhận diện lỗi;
- xác định vị trí lỗi;
- tính mạch lạc;
- giọng điệu;
- tính tự nhiên giống người.

Các nguồn khác gồm MathDial, Bridge và dữ liệu về câu hỏi gợi mở.

**Giới hạn diễn giải.** Tám loại tiêu chí này thuộc nguồn dữ liệu phát triển bộ chấm; chúng không trở thành một bảng tám tiêu chí hiện hữu bắt buộc cho mọi mẫu MathTutorBench.

Vị trí nguồn: `Section 4.2`; `Table 2`; `Section 4.3.1–4.3.3`.

## 7. Phản hồi tham chiếu được dùng như thế nào?

**Bằng chứng.** Với nhiệm vụ sinh phản hồi mở, phản hồi của giáo viên là đối chứng trong phép so sánh. Điểm được báo cáo dưới dạng tỷ lệ phản hồi của mô hình được bộ chấm ưu tiên hơn phản hồi giáo viên.

Điều này có hai hệ quả:

- phản hồi tham chiếu không phải cách diễn đạt hợp lệ duy nhất;
- chất lượng của phép chấm phụ thuộc vào cả phản hồi tham chiếu và độ tin cậy của mô hình chấm.

Vị trí nguồn: `Figure 2`; `Section 4.3`; `Table 4`.

## 8. Cách tổng hợp điểm

Các nhiệm vụ có đầu ra cấu trúc được báo điểm bằng thước đo riêng. Hai nhiệm vụ sinh phản hồi mở được báo bằng tỷ lệ thắng của phản hồi mô hình so với phản hồi giáo viên.

MathTutorBench không lấy một bộ tiêu chí chung rồi tính thành một điểm duy nhất cho tất cả bảy nhiệm vụ. Kết quả được giữ riêng theo nhiệm vụ và nhóm năng lực, qua đó chỉ ra rằng mô hình giỏi giải bài chưa chắc giỏi làm gia sư.

Vị trí nguồn: `Table 3`; `Table 4`; `Section 6.1`.

## 9. Vai trò con người và bằng chứng kiểm định

Các nguồn dữ liệu có vai trò của con người gồm:

- MathDial có hội thoại giữa giáo viên và học sinh mô phỏng;
- Bridge có phản hồi của giáo viên mới và bản sửa của giáo viên chuyên gia;
- các tập so sánh có nhãn ưu tiên của con người.

Mô hình chấm tốt nhất đạt khoảng `0,84` độ chính xác khi phân biệt phản hồi chuyên gia với phản hồi giáo viên mới trong phép thử Bridge.

**Giới hạn.** Đây không phải nghiên cứu đầy đủ về độ đồng thuận giữa nhiều người chấm trên toàn bộ các nhiệm vụ và tiêu chí.

Vị trí nguồn: `Section 4.2`; `Table 2`; `Section 6.2`.

## 10. Kết quả liên quan trực tiếp tới Plan 03

**Bằng chứng.**

- Năng lực giải đúng bài không bảo đảm năng lực dạy học tốt.
- Có thể tách nhiệm vụ hiểu học sinh khỏi nhiệm vụ tạo phản hồi.
- Hội thoại dài hơn tạo khó khăn riêng cho mô hình.
- Phản hồi gia sư mở cần cách chấm chấp nhận nhiều cách diễn đạt hợp lệ.

Vị trí nguồn: `Section 6.1`; `Section 6.2`; `Table 3`; `Table 4`.

## 11. Khả năng chuyển sang Tin học THCS

### Bằng chứng có thể sử dụng

- Cần phân biệt “đưa ra đáp án đúng” và “hỗ trợ học sinh học”.
- Nhiệm vụ chẩn đoán đúng/sai hoặc vị trí lỗi có thể có đầu ra cấu trúc và thước đo khách quan.
- Nhiệm vụ sinh phản hồi gia sư mở không nên dùng so khớp câu chữ.
- Độ dài lịch sử hội thoại là một biến cần báo cáo.

### Suy luận cho dự án

- `gold_answer` có thể làm neo sự thật cho tính đúng chuyên môn.
- `gold_response` có thể làm phản hồi tham chiếu, ví dụ tốt hoặc căn cứ viết tiêu chí.
- Không nên dùng bốn nguyên tắc của bài báo làm bằng chứng duy nhất cho bốn tiêu chí chung của mọi mẫu.
- Nếu dùng mô hình chấm điểm ưu tiên, dự án vẫn cần tiêu chí hiện hữu để truy nguyên lỗi và kiểm định bằng chuyên gia.

## 12. Giới hạn khi chuyển miền

- Bài báo thuộc Toán, không phải Tin học THCS Việt Nam.
- Lỗi trong mã lệnh, thuật toán, bảng tính hoặc sản phẩm số có cấu trúc khác lỗi giải toán.
- Mô hình chấm đưa ra điểm tổng hợp khó truy nguyên.
- Bài báo không đo kết quả học tập thật của học sinh.
- Bằng chứng tiếng Anh không bảo đảm bộ chấm hoạt động tương đương bằng tiếng Việt.

## 13. Phát biểu đưa vào ma trận bằng chứng


| Phát biểu                                                                                                   | Nhãn        | Vị trí nguồn                         |
| ------------------------------------------------------------------------------------------------------------- | ------------ | --------------------------------------- |
| MathTutorBench có ba nhóm năng lực và bảy nhiệm vụ với đầu ra, dữ liệu và thước đo riêng.   | Bằng chứng | `Section 3.2`; `Section 4.1`; `Table 1` |
| Bốn nguyên tắc khoa học học tập không phải bốn tiêu chí hiện hữu gắn với mọi mẫu.            | Bằng chứng | `Section 3.2`; `Section 4.3.1–4.3.3`   |
| Phản hồi mở được chấm bằng ưu tiên so với phản hồi giáo viên, không bằng so khớp câu chữ. | Bằng chứng | `Figure 2`; `Section 4.3`; `Table 4`    |
| Dự án nên dùng phản hồi tham chiếu làm căn cứ, không phải đáp án câu chữ duy nhất.          | Suy luận    | Tổng hợp từ các bằng chứng trên  |

## 14. Câu hỏi mở cho HNMU/UET

1. Những nhiệm vụ Tin học nào có thể chấm bằng đầu ra cấu trúc, và những nhiệm vụ nào phải chấm phản hồi mở?
2. `gold_response` hiện tại có đủ chất lượng để dùng làm đối chứng hay chỉ nên dùng để viết tiêu chí?
3. Dự án có cần một phép so sánh theo cặp phụ bên cạnh phép chấm từng tiêu chí không?
4. Tiêu chí nào phải hiện hữu để khắc phục nhược điểm khó truy nguyên của mô hình chấm điểm ưu tiên?

## 15. Kết luận có mục tiêu

Đóng góp quan trọng nhất của MathTutorBench cho Plan 03 không phải một bộ rubric chung. Bài báo cung cấp bằng chứng rằng:

- nhiệm vụ phải được định nghĩa bằng đầu vào–đầu ra và thước đo;
- năng lực hiểu học sinh, giải bài và tạo phản hồi sư phạm là các năng lực khác nhau;
- phản hồi gia sư mở phải chấp nhận nhiều cách trả lời hợp lệ;
- phản hồi của giáo viên có thể là đối chứng, nhưng không phải đáp án câu chữ duy nhất.

Do mô hình chấm của bài báo không xuất tiêu chí chi tiết ở cấp mẫu, MathTutorBench nên được kết hợp với một phương pháp có tiêu chí hiện hữu như TutorBench hoặc KMP-Bench, thay vì sao chép độc lập.
