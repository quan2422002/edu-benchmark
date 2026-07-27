# TR-P002 — KMP-Bench

Bài báo: `From Solver to Tutor: Evaluating the Pedagogical Intelligence of LLMs with KMP-Bench`  
Tệp cục bộ: `document/paper/source_paper/18426-AAAI26.ShiW-NLP.pdf`  
Bản có phụ lục đầy đủ: `https://arxiv.org/abs/2603.02775`  
DOI: `https://doi.org/10.1609/aaai.v40i39.40578`  
Trạng thái công bố: bài báo phản biện tại AAAI-26  
Miền nghiên cứu: gia sư Toán K–8  
Vai trò trong experiment hiện tại: tiền lệ gần nhất cho việc cắt một hội thoại thành nhiều mẫu tại từng lượt gia sư và chọn tiêu chí theo nguyên tắc sư phạm của từng lượt.

## 1. Mục tiêu đọc bài báo trong experiment này

Bản tóm tắt tập trung trả lời:

1. KMP-Bench phân biệt mô-đun, nhiệm vụ, kỹ năng và nguyên tắc sư phạm thế nào?
2. Công thức “4 tiêu chí chung + `3 × n` tiêu chí riêng” được vận hành ra sao?
3. Một lượt gia sư trở thành một mẫu benchmark như thế nào?
4. Bộ chấm tạo phán quyết gì ở cấp tiêu chí và điểm được tổng hợp ở cấp nào?
5. Cấu trúc nào phù hợp với 2.028 mẫu ứng viên hiện tại?

## 2. Vấn đề bài báo giải quyết

**Bằng chứng.** KMP-Bench cho rằng độ chính xác giải bài không đủ để đo “trí tuệ sư phạm”. Gia sư phải biết thử thách phù hợp, giải thích, mô hình hóa, tạo cơ hội luyện tập, đặt câu hỏi và phản hồi.

Bài báo vì vậy đánh giá cả:

- chất lượng phản hồi trong hội thoại gia sư;
- các kỹ năng nền tảng có đầu ra rõ hơn.

Vị trí nguồn: `Abstract`; `Introduction`; `Figure 1`.

## 3. Hai mô-đun của KMP-Bench

| Mô-đun | Đối tượng đánh giá | Cách chấm chính |
|---|---|---|
| `KMP-Dialogue` | Lượt phản hồi tiếp theo của gia sư trong hội thoại | So sánh theo cặp với phản hồi tham chiếu trên các tiêu chí áp dụng |
| `KMP-Skills` | Các kỹ năng nền tảng riêng | Thước đo thay đổi theo nhiệm vụ |

`KMP-Skills` gồm ba nhóm:

1. giải bài theo câu hỏi nối tiếp nhiều lượt;
2. phát hiện và sửa lỗi;
3. tạo bài toán.

**Kết luận có căn cứ.** Ngay trong một bài báo, hai mô-đun không dùng cùng một rubric. Hội thoại mở dùng so sánh theo tiêu chí; nhiệm vụ có đầu ra cấu trúc dùng thước đo theo nhiệm vụ.

Vị trí nguồn: `Section 3.1`; `Section 3.2`; `Table 1`; `Table 2`.

## 4. Một mẫu KMP-Dialogue được tạo thế nào?

Bài báo cắt một hội thoại trước một lượt của gia sư:

```text
lịch sử hội thoại kết thúc ở lượt học sinh
                         ↓
               mô hình sinh lượt gia sư
                         ↓
      so với lượt gia sư gốc đã bị cắt khỏi ngữ cảnh
```

Một mẫu còn có:

- vai trò/phong cách của gia sư;
- hồ sơ học sinh;
- mục tiêu học tập;
- một hoặc hai nguyên tắc sư phạm đích.

Lượt gia sư gốc trở thành phản hồi tham chiếu. Bộ chấm không yêu cầu phản hồi mô hình giống câu chữ tham chiếu; nó so sánh hai phản hồi theo từng tiêu chí.

Vị trí nguồn: `Section 3.1`; `Figure 3`; `Appendix F`.

## 5. Sáu nguyên tắc sư phạm

Mỗi lượt gia sư đích được gắn một hoặc hai nguyên tắc:

1. `Challenge` — tạo thử thách phù hợp;
2. `Explanation` — giải thích;
3. `Modelling` — làm mẫu/mô hình hóa;
4. `Practice` — tạo cơ hội luyện tập;
5. `Questioning` — đặt câu hỏi;
6. `Feedback` — phản hồi.

Các nguyên tắc vừa định hướng tạo hội thoại, vừa quyết định bộ tiêu chí áp dụng khi chấm lượt đó.

**Giới hạn diễn giải.** Đây là các hành vi sư phạm mong đợi của lượt gia sư. Chúng không mặc nhiên là sáu nhiệm vụ benchmark có hợp đồng đầu vào–đầu ra riêng.

Vị trí nguồn: `Section 2.3`; `Section 3.1`; `Figure 2`; `Figure 3`.

## 6. Bộ 22 tiêu chí được vận hành thế nào?

Thư viện tiêu chí của `KMP-Dialogue` gồm:

- 4 tiêu chí chung cho mọi lượt;
- 3 tiêu chí riêng cho mỗi một trong 6 nguyên tắc.

Tổng thư viện là:

```text
4 + 3 × 6 = 22 tiêu chí
```

Nhưng mỗi mẫu chỉ dùng:

```text
4 + 3 × n
```

trong đó `n` là số nguyên tắc được gắn với lượt gia sư:

- một nguyên tắc → 7 tiêu chí;
- hai nguyên tắc → 10 tiêu chí.

Ngoài 7 hoặc 10 phán quyết theo tiêu chí, bộ chấm còn tạo một phán quyết tổng thể riêng.

**Điểm cần thận trọng.** Bài báo chỉ công bố tên minh họa của một phần trong 22 tiêu chí, chẳng hạn:

- `Contextual Coherence and Relevance`;
- `Adherence to Defined Persona/Teaching Style`;
- `Relevance/Alignment` của nguyên tắc luyện tập;
- `Difficulty Appropriateness`.

Không đủ căn cứ để tự đặt tên cho toàn bộ tiêu chí còn lại.

Vị trí nguồn: `Section 3.1`; `Figure 3`; `Appendix F`.

## 7. Bộ chấm tạo đầu ra gì?

Với mỗi tiêu chí áp dụng, bộ chấm so candidate với phản hồi tham chiếu và xuất:

- `Win` — candidate tốt hơn;
- `Tie` — hai phản hồi tương đương;
- `Lose` — candidate kém hơn;
- lý do.

Bộ chấm còn đưa ra một `Overall Judgement` độc lập.

**Kết luận có căn cứ.** Phán quyết theo tiêu chí và phán quyết tổng thể là hai đầu ra khác nhau. Không nên thay thế một loại bằng loại còn lại.

Vị trí nguồn: `Section 3.1`; `Appendix F`.

## 8. Điểm được tổng hợp như thế nào?

Ở cấp mô hình:

1. `General-Level Acc` là trung bình tỷ lệ thắng của bốn tiêu chí chung.
2. Điểm mỗi nguyên tắc là trung bình tỷ lệ thắng của ba tiêu chí thuộc nguyên tắc đó.
3. `Overall Acc` là trung bình của:
   - điểm chung;
   - trung bình điểm của sáu nguyên tắc.
4. `Overall Judgement Acc` từ phán quyết tổng thể được báo riêng.

**Giới hạn diễn giải.** Đây là phép tổng hợp ở cấp mô hình trên toàn bộ tập đánh giá. Nó không chứng minh rằng một mẫu phải có điểm tổng bằng trung bình đơn giản của 7 hoặc 10 tiêu chí.

Vị trí nguồn: `Section 4.1`; `Table 1`.

## 9. KMP-Skills dùng thước đo nào?

| Nhóm nhiệm vụ | Đầu ra | Thước đo |
|---|---|---|
| Giải bài nối tiếp nhiều lượt | Đáp án ở từng lượt | Độ chính xác theo lượt |
| Phát hiện và sửa lỗi | Nhận diện lỗi và bản sửa | `F1`, độ chính xác sửa lỗi, `MR-Score` |
| Tạo bài toán | Bài toán và lời giải | Đạt/không đạt trên các chiều chất lượng |

Các chiều cho bài toán được tạo gồm:

- cấu tạo bài toán;
- tính đúng của lời giải;
- chất lượng lời giải;
- với bài tương tự, độ phù hợp về mức tương tự.

Quy tắc có tính “đóng”: nếu không đáp ứng một chiều cốt lõi, mẫu bị đánh giá không đạt.

Vị trí nguồn: `Section 3.2`; bảng và phụ lục của `KMP-Skills`.

## 10. Vai trò con người và bằng chứng kiểm định

**Bằng chứng.**

- Năm nghiên cứu sinh Tiến sĩ ngành Khoa học máy tính kiểm tra thủ công 5.910 luồng hội thoại.
- 451 luồng, tương đương khoảng `7,6%`, bị loại.
- 300 trường hợp được người chấm gán nhãn để kiểm bộ chấm tự động.
- Độ khớp trung bình giữa bộ chấm tự động và nhãn con người khoảng `89,8%`.

**Giới hạn.** Con số `89,8%` là độ khớp giữa bộ chấm và người chấm trên tập kiểm định, không phải độ đồng thuận giữa nhiều chuyên gia độc lập. Người kiểm tra là nghiên cứu sinh kỹ thuật, không phải giáo viên Toán phổ thông.

Vị trí nguồn: `Figure 1`; phần tạo và xác minh luồng hội thoại; `Table 3`; `Appendix I`.

## 11. Kết quả liên quan trực tiếp tới Plan 03

**Bằng chứng.**

- Mô hình chuyên giải Toán có thể kém mô hình đa dụng ở chất lượng gia sư.
- Mô hình mạnh/yếu khác nhau theo từng nguyên tắc sư phạm.
- Lỗi thường gặp gồm hỗ trợ từng bước sai, né giải quyết yêu cầu bằng cách thay thế và đặt câu hỏi mơ hồ.
- Việc huấn luyện trên dữ liệu hội thoại sư phạm cải thiện cả điểm hội thoại và một số kỹ năng nền tảng.

Vị trí nguồn: `Table 1`; `Table 2`; `Main Results`; phần phân tích lỗi.

## 12. Khả năng chuyển sang Tin học THCS

### Bằng chứng có thể sử dụng

- Một hội thoại có thể tạo nhiều mẫu bằng cách cắt trước từng lượt gia sư.
- Nhãn sư phạm cần được gắn ở cấp lượt, không phải cấp hội thoại thô.
- Có thể dùng lõi tiêu chí chung và chọn tiêu chí riêng theo hành vi mục tiêu.
- Phản hồi tham chiếu không phải đáp án câu chữ duy nhất.
- Cần giữ kết quả theo tiêu chí để truy nguyên.

### Suy luận cho dự án

- 2.028 mẫu ứng viên hiện tại có cấu trúc gần `KMP-Dialogue`.
- Mỗi mẫu nên có một nhiệm vụ chính và có thể có nhiều kỹ năng/nguyên tắc phụ.
- Không nên sao chép 22 tiêu chí; dự án cần một thư viện nhỏ hơn, được HNMU hiệu chỉnh.
- Phép so sánh theo cặp chỉ nên là phép chấm phụ cho đến khi chất lượng `gold_response` được xác nhận.

## 13. Giới hạn khi chuyển miền

- Bài báo thuộc Toán K–8, không phải Tin học THCS Việt Nam.
- Nhiều hội thoại được mô hình sinh rồi con người lọc, khác nguồn dữ liệu HNMU.
- Chất lượng so sánh theo cặp phụ thuộc phản hồi tham chiếu.
- Tên đầy đủ của 22 tiêu chí không được công bố.
- Độ tin cậy của bộ chấm tiếng Việt chưa được biết.

## 14. Phát biểu đưa vào ma trận bằng chứng

| Phát biểu | Nhãn | Vị trí nguồn |
|---|---|---|
| KMP-Dialogue cắt hội thoại trước lượt gia sư và dùng lượt bị cắt làm phản hồi tham chiếu. | Bằng chứng | `Section 3.1`; `Figure 3` |
| Mỗi lượt đích có một hoặc hai trong sáu nguyên tắc sư phạm. | Bằng chứng | `Section 2.3`; `Section 3.1` |
| Mỗi mẫu dùng 4 tiêu chí chung + 3 tiêu chí cho mỗi nguyên tắc được gắn. | Bằng chứng | `Section 3.1`; `Figure 3`; `Appendix F` |
| Mẫu có một nguyên tắc được chấm 7 tiêu chí; hai nguyên tắc được chấm 10 tiêu chí. | Bằng chứng | Suy ra trực tiếp từ công thức của bài báo |
| Các nguyên tắc nên là kỹ năng/nhãn phụ, không mặc nhiên là nhiệm vụ. | Suy luận | Đối chiếu cấu trúc `KMP-Dialogue` và `KMP-Skills` |

## 15. Câu hỏi mở cho HNMU/UET

1. Những nguyên tắc nào phù hợp với gia sư Tin học THCS?
2. Mỗi mẫu cần tối đa bao nhiêu kỹ năng phụ?
3. Lõi tiêu chí chung nên có bao nhiêu tiêu chí?
4. Khi nào phản hồi tham chiếu đủ tin cậy để so sánh theo cặp?
5. Có cần giữ một phán quyết tổng thể ngoài các phán quyết theo tiêu chí không?

## 16. Kết luận có mục tiêu

KMP-Bench là tiền lệ trực tiếp nhất cho cấu trúc dữ liệu hiện tại:

```text
một hội thoại thô
→ nhiều điểm cắt trước lượt gia sư
→ nhiều mẫu ứng viên
→ mỗi mẫu có nguyên tắc sư phạm riêng
→ chọn bộ tiêu chí phù hợp
→ so candidate với phản hồi tham chiếu
```

Điểm cần học là cấu trúc chọn tiêu chí theo lượt, không phải con số 22. Plan 03 nên phân biệt rõ nhiệm vụ, kỹ năng/nguyên tắc, tiêu chí chung và tiêu chí riêng; đồng thời chưa nên phụ thuộc hoàn toàn vào so sánh theo cặp khi `gold_response` chưa được chuyên gia xác nhận.
