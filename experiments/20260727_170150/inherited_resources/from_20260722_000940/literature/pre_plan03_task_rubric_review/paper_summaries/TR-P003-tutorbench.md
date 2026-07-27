# TR-P003 — TutorBench

Bài báo: `TutorBench: A Benchmark To Assess Tutoring Capabilities Of Large Language Models`  
Tệp cục bộ: `document/paper/source_paper/2510.02663v1.pdf`  
Đường dẫn ổn định: `https://arxiv.org/abs/2510.02663`  
Tập mẫu công khai: `https://huggingface.co/datasets/tutorbench/tutorbench`  
Trạng thái công bố: bản tiền công bố (`preprint`) năm 2025  
Miền nghiên cứu: gia sư STEM bậc trung học phổ thông và AP  
Vai trò trong experiment hiện tại: bằng chứng trực tiếp nhất cho tiêu chí chấm riêng ở cấp mẫu, trọng số tiêu chí và cách dùng phản hồi mẫu để viết tiêu chí.

## 1. Mục tiêu đọc bài báo trong experiment này

Bản tóm tắt trả lời:

1. Ba tình huống sử dụng của TutorBench được định nghĩa bằng đầu vào–đầu ra thế nào?
2. Có hay không một bộ tiêu chí chung cho mọi mẫu?
3. Vì sao mỗi mẫu có 3–39 tiêu chí?
4. Trọng số `+5`, `+1`, `-5` được vận hành như thế nào?
5. Phản hồi mẫu được dùng để chấm trực tiếp hay để xây dựng tiêu chí?
6. Phần nào có thể chuyển sang các mẫu Tin học THCS hiện tại?

## 2. Vấn đề bài báo giải quyết

**Bằng chứng.** TutorBench cho rằng các bộ đánh giá hiện có chưa phản ánh đầy đủ năng lực gia sư trong những tình huống thực tế, đồng thời nhiều phép chấm dùng tiêu chí chung quá rộng hoặc thước đo bề mặt.

Bài báo xây dựng 1.490 mẫu do chuyên gia tạo, phủ sáu môn STEM và ba tình huống sử dụng gia sư. Mỗi mẫu có phản hồi gia sư mẫu và một tập tiêu chí riêng.

Vị trí nguồn: `Abstract`; `Introduction`; `Section 2`; `Appendix A.1`.

## 3. Ba tình huống sử dụng

### 3.1. `Adaptive Explanation Generation`

Mẫu thường chứa:

- câu hỏi ban đầu của học sinh;
- phần giải thích trước đó của gia sư;
- câu hỏi hoặc biểu hiện chưa hiểu tiếp theo của học sinh.

Mô hình phải tạo giải thích mới phù hợp với nhu cầu vừa bộc lộ, thay vì lặp lại giải thích cũ.

### 3.2. `Assessment and Feedback`

Mẫu thường chứa:

- bài toán hoặc câu hỏi;
- lời giải/bài làm của học sinh.

Mô hình phải đánh giá phần đúng và sai, nhận diện lỗi, giải thích và đưa phản hồi giúp học sinh sửa.

### 3.3. `Active Learning Support`

Mẫu thường chứa:

- bài toán;
- bài làm chưa hoàn chỉnh hoặc sai;
- trạng thái học sinh đang cần hỗ trợ.

Mô hình phải đưa gợi ý hoặc bước tiếp theo có ích nhưng không làm thay toàn bộ.

**Kết luận có căn cứ.** Mỗi mẫu thuộc một trong ba tình huống sử dụng. Các tình huống này là hợp đồng hành vi gia sư, không phải các chiều chấm điểm.

Vị trí nguồn: `Section 2.1`; `Figure 2`.

## 4. Một mẫu benchmark được xây dựng như thế nào?

Quy trình chuyên gia:

1. xây dựng câu hỏi và bối cảnh theo một tình huống sử dụng;
2. viết phản hồi gia sư mẫu;
3. dựa vào yêu cầu của mẫu và phản hồi mẫu để viết các tiêu chí chấm;
4. gắn thuộc tính cho từng tiêu chí;
5. dùng phản hồi của các mô hình mạnh để lọc, giữ các mẫu đủ khó.

Tập công khai cho thấy các trường về:

- nhiệm vụ/tình huống sử dụng;
- đề dẫn và ngữ cảnh theo tình huống;
- phản hồi mẫu;
- danh sách tiêu chí cùng thuộc tính;
- mức Bloom.

Vị trí nguồn: `Appendix A.1`; thẻ dữ liệu và cấu trúc tập mẫu công khai.

## 5. Rubric có phải một bộ chung không?

Không. Mỗi mẫu có bộ từ 3 đến 39 tiêu chí riêng. Toàn bộ 1.490 mẫu có 15.220 tiêu chí.

Tiêu chí được yêu cầu:

- tự đủ nghĩa;
- ít chồng chéo;
- cùng nhau bao quát các yêu cầu quan trọng;
- có thể kiểm chứng từ phản hồi.

**Kết luận có căn cứ.** TutorBench không công bố một bộ tiêu chí bắt buộc dùng cho mọi mẫu. Các nhãn chiều đánh giá và kỹ năng gia sư là siêu dữ liệu để nhóm/phân tích tiêu chí, không phải tiêu chí chung.

Vị trí nguồn: `Section 2.3`; `Section 2.4`.

## 6. Thuộc tính của tiêu chí

Mỗi tiêu chí có các thuộc tính phục vụ phân tích, gồm:

### 6.1. Chiều đánh giá

Ví dụ:

- tuân thủ chỉ dẫn;
- phong cách và giọng điệu;
- tính đúng;
- tính liên quan;
- điều chỉnh theo trình độ học sinh;
- xử lý cảm xúc;
- xử lý thành phần trực quan.

### 6.2. Kỹ năng gia sư

Ví dụ:

- nhận diện hiểu sai;
- nhận diện bước đúng/sai;
- nhắc lại kiến thức cần thiết;
- đưa ví dụ hoặc phép tương tự;
- đưa cách giải khác;
- đặt câu hỏi gợi mở;
- hỗ trợ theo từng bước.

### 6.3. Loại yêu cầu

- yêu cầu được nói rõ hoặc ngầm định;
- tiêu chí khách quan hoặc có phần chủ quan.

**Giới hạn diễn giải.** Các thuộc tính này giúp phân tích độ phủ và lỗi của mô hình. Chúng không thay thế nội dung tiêu chí cụ thể của từng mẫu.

Vị trí nguồn: `Section 2.4`; `Figure 4`; `Figure 5`; `Appendix A.5`.

## 7. Cách chấm từng tiêu chí

Bộ chấm đọc:

- đề dẫn và bối cảnh;
- phản hồi của mô hình;
- nội dung một tiêu chí.

Sau đó đưa phán quyết:

- `Pass` — phản hồi đáp ứng tiêu chí;
- `Fail` — phản hồi không đáp ứng tiêu chí.

Các tiêu chí được chấm độc lập. Cách làm này cho phép truy nguyên phản hồi đạt hoặc không đạt yêu cầu nào.

Vị trí nguồn: `Section 2.3`.

## 8. Trọng số được dùng thế nào?

Ba loại trọng số:

- `+5`: yêu cầu tích cực trọng yếu;
- `+1`: yêu cầu tích cực không trọng yếu;
- `-5`: hành vi không mong muốn hoặc lỗi nghiêm trọng.

Điểm mẫu được tính bằng trung bình nhị phân có trọng số, được bài báo ký hiệu `ARR_w`.

**Điểm chưa rõ trong nguồn.** Bài báo mô tả điểm được chuẩn hóa về `[0,1]`, nhưng công thức in chưa giải thích đầy đủ cách xử lý khi các tiêu chí trọng số âm làm tử số âm. Không nên tự thêm quy tắc chặn điểm rồi nói đó là quy tắc của bài báo.

Vị trí nguồn: `Section 2.3`; `Equation 1`.

## 9. Phản hồi gia sư mẫu được dùng như thế nào?

**Bằng chứng.** Chuyên gia viết phản hồi mẫu trước hoặc trong quá trình xây dựng tiêu chí. Phản hồi này giúp xác định những thành phần mà một câu trả lời tốt cần có.

Khi đánh giá mô hình, bộ chấm xét phản hồi theo từng tiêu chí. Bài báo không yêu cầu so khớp câu chữ với phản hồi mẫu và cũng không thiết lập phép so sánh theo cặp với phản hồi mẫu như cơ chế chính.

**Kết luận có căn cứ.** Phản hồi mẫu chủ yếu là bằng chứng hỗ trợ biên soạn tiêu chí và một ví dụ chất lượng cao, không phải đáp án câu chữ duy nhất.

Vị trí nguồn: `Appendix A.1`; `Section 2.3`.

## 10. Lọc mẫu theo độ khó

**Bằng chứng.** Năm mô hình mạnh được cho trả lời từng mẫu. Bài báo chỉ giữ mẫu nếu ít nhất ba trong năm mô hình đạt dưới 50% điểm có trọng số.

Mục đích là loại các mẫu quá dễ đối với nhóm mô hình mạnh ở thời điểm xây dựng.

**Giới hạn.** Quy tắc này phụ thuộc vào tập mô hình và bộ chấm dùng lúc lọc. Nó không bảo đảm độ khó ổn định theo thời gian hoặc với mô hình thuộc ngôn ngữ khác.

Vị trí nguồn: `Introduction`; `Appendix A.1`.

## 11. Mức Bloom được dùng thế nào?

Ba mô hình gán mức Bloom; mẫu được nhận nhãn khi ít nhất hai mô hình đồng thuận. Quy trình phủ hơn 97% số mẫu.

Mức Bloom được gắn sau khi xây dựng mẫu để phân tích yêu cầu nhận thức. Kết quả của mô hình không giảm đều khi mức Bloom tăng.

**Kết luận có căn cứ.** Trong TutorBench, Bloom là siêu dữ liệu phân tích, không phải một tình huống gia sư và không quyết định bộ tiêu chí.

Vị trí nguồn: `Section 3.4`; `Figure 4`.

## 12. Vai trò chuyên gia và kiểm định bộ chấm

**Bằng chứng.**

- 69 chuyên gia tham gia kiểm định;
- 250 mẫu với 2.475 tiêu chí;
- mỗi tiêu chí có ba lượt chấm của con người;
- độ đồng thuận trung bình giữa người chấm là `0,75`;
- độ khớp trung bình giữa bộ chấm tự động và người chấm là `0,78`;
- `F1 = 0,82` so với nhãn đa số trên 1.900 tiêu chí không trọng yếu.

**Giới hạn quan trọng.** Các tiêu chí trọng yếu trọng số `+5/-5` không nằm trong phép tính F1 nói trên. Vì vậy `0,82` không xác nhận toàn bộ cơ chế chấm có trọng số.

Vị trí nguồn: `Section 3.7`; `Figure 6`.

## 13. Kết quả liên quan trực tiếp tới Plan 03

**Bằng chứng.**

- Không mô hình nào đạt quá khoảng 56% điểm tổng.
- Mô hình có điểm khác nhau theo từng tình huống sử dụng và nhóm kỹ năng.
- Mức Bloom cao hơn không đồng nghĩa mẫu luôn khó hơn đối với mô hình.
- Chấm theo tiêu chí riêng cho phép phân tích lỗi chi tiết hơn điểm tổng.

Vị trí nguồn: `Table 1`; `Figure 3`; `Section 3.1–3.5`.

## 14. Khả năng chuyển sang Tin học THCS

### Bằng chứng có thể sử dụng

- Mỗi mẫu có thể có tiêu chí riêng mà vẫn thuộc một nhiệm vụ chung.
- Tiêu chí phải nguyên tử, tự đủ nghĩa và kiểm chứng được.
- Phản hồi mẫu có thể hỗ trợ viết tiêu chí mà không trở thành đáp án duy nhất.
- Có thể gắn thuộc tính cho tiêu chí để đo độ phủ kỹ năng.
- Bộ chấm tự động phải được kiểm bằng nhiều lượt chấm của chuyên gia.

### Suy luận cho dự án

- T1–T3 hiện tại gần với ba tình huống sử dụng của TutorBench.
- Nên tạo bảng `candidate_rubric_criteria.csv` ngoài bảng ứng viên chính.
- Không nên áp dụng nguyên xi 3–39 tiêu chí; cần thí điểm để chọn ngân sách tiêu chí khả thi.
- Lỗi nghiêm trọng nên được tách thành cổng hoặc chính sách riêng thay vì sao chép trực tiếp trọng số `-5`.
- Trong giai đoạn đầu, có thể chấm `pass`, `failed`, `need_human_review` ở cấp tiêu chí.

## 15. Giới hạn khi chuyển miền

- Dữ liệu thuộc STEM tiếng Anh bậc trung học phổ thông/AP.
- Tin học THCS Việt Nam có yêu cầu riêng về chương trình, học liệu, ngôn ngữ và sản phẩm số.
- Việc viết 3–39 tiêu chí cho 2.028 mẫu rất tốn nguồn lực.
- Độ tin cậy của bộ chấm tiếng Việt chưa được biết.
- Cơ chế trọng số chưa được kiểm định đầy đủ trên tiêu chí trọng yếu.

## 16. Phát biểu đưa vào ma trận bằng chứng

| Phát biểu | Nhãn | Vị trí nguồn |
|---|---|---|
| Mỗi mẫu thuộc một trong ba tình huống sử dụng gia sư. | Bằng chứng | `Section 2.1` |
| Mỗi mẫu có 3–39 tiêu chí riêng; không có bộ tiêu chí chung bắt buộc được công bố. | Bằng chứng | `Section 2.3` |
| Bộ chấm đưa ra `Pass/Fail` độc lập cho từng tiêu chí. | Bằng chứng | `Section 2.3` |
| Tiêu chí có trọng số `+5`, `+1`, `-5`. | Bằng chứng | `Section 2.3`; `Equation 1` |
| Phản hồi mẫu được dùng để hỗ trợ xây dựng tiêu chí, không phải để so khớp câu chữ. | Bằng chứng | `Appendix A.1`; `Section 2.3` |
| Dự án nên dùng tiêu chí riêng ở cấp mẫu nhưng giới hạn số lượng qua thí điểm. | Suy luận | Tổng hợp từ các bằng chứng trên |

## 17. Câu hỏi mở cho HNMU/UET

1. HNMU có thể viết hoặc duyệt bao nhiêu tiêu chí cho mỗi mẫu trong thí điểm?
2. Tiêu chí chung là những dòng chấm giống hệt nhau, hay chỉ là khuôn để cụ thể hóa theo mẫu?
3. Lỗi trọng yếu nào phải dẫn đến loại mẫu hoặc chặn điểm?
4. Bộ chấm tiếng Việt cần đạt ngưỡng đồng thuận nào?
5. Có cần trọng số trong phiên bản đầu hay chỉ báo riêng tỷ lệ đạt từng nhóm tiêu chí?

## 18. Kết luận có mục tiêu

TutorBench cung cấp bằng chứng mạnh nhất cho cấu trúc:

```text
một nhiệm vụ chung
→ một mẫu cụ thể
→ phản hồi mẫu do chuyên gia viết
→ bộ tiêu chí riêng của mẫu
→ chấm đạt/không đạt từng tiêu chí
→ tổng hợp thành điểm mẫu
```

Điểm nên học là tiêu chí nguyên tử và riêng theo mẫu. Điểm không nên sao chép ngay là số lượng 3–39 và trọng số `+5/+1/-5`, vì chi phí xây dựng lớn và độ tin cậy của phần trọng yếu chưa được chứng minh đầy đủ cho tiếng Việt/Tin học THCS.
