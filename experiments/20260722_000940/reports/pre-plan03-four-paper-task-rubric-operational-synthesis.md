# Tổng hợp cách vận hành nhiệm vụ và tiêu chí chấm của 4 bài báo trước Plan 03

Ngày rà soát: 24/07/2026
Experiment: `20260722_000940`
Phạm vi áp dụng: thiết kế nhiệm vụ và tiêu chí chấm cho 2.028 mẫu ứng viên được chuyển đổi từ 665 hội thoại thô `pass`
Trạng thái: tổng hợp nghiên cứu trước plan; chưa sửa hoặc triển khai Plan 03

## 1. Kết luận ngắn

Bốn bài báo không dùng “nhiệm vụ” và “rubric” theo cùng một nghĩa:


| Bài báo      | Nhiệm vụ vận hành ở đâu?                                                                              | Tiêu chí/thước đo của một mẫu                                                                                                                                | Vai trò của phản hồi tham chiếu/chuẩn                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| MathTutorBench | Bảy hợp đồng đầu vào–đầu ra thuộc ba nhóm năng lực                                             | Thước đo thay đổi theo nhiệm vụ; phản hồi mở dùng mô hình chấm điểm ưu tiên theo cặp, không có bảng tiêu chí hiện hữu đầy đủ theo mẫu | Phản hồi của giáo viên là đối chứng trong phép so sánh theo cặp                            |
| KMP-Bench      | Hai mô-đun; KMP-Dialogue gắn 1–2 nguyên tắc cho từng lượt gia sư, KMP-Skills có nhiệm vụ riêng | KMP-Dialogue dùng 4 tiêu chí chung +`3 × n` tiêu chí của `n` nguyên tắc; mỗi tiêu chí nhận `Win/Tie/Lose`                                               | Lượt gia sư bị cắt là phản hồi tham chiếu                                                     |
| TutorBench     | Mỗi mẫu thuộc một trong ba tình huống sử dụng gia sư                                                | Mỗi mẫu có bộ 3–39 tiêu chí riêng, chấm`Pass/Fail` và có trọng số                                                                                       | Phản hồi gia sư mẫu giúp chuyên gia viết tiêu chí; không phải đáp án câu chữ duy nhất |
| VietLegal      | 22 nhiệm vụ đầu vào–đầu ra thuộc năm tầng nhận thức                                             | Thước đo cố định theo nhiệm vụ; không có tiêu chí sư phạm riêng cho từng mẫu                                                                        | Nhãn/phản hồi chuẩn được dùng theo hợp đồng nhiệm vụ                                      |

Vì vậy, không nên chọn giữa “rubric chung” và “rubric riêng” như hai phương án loại trừ nhau. Thiết kế phù hợp hơn cho dữ liệu hiện tại là:

1. mỗi mẫu ứng viên có **một nhiệm vụ chính** mô tả hợp đồng hành vi gia sư;
2. mẫu có thể có nhiều **nhãn kỹ năng/nguyên tắc phụ**;
3. dùng một **lõi tiêu chí chung nhỏ**;
4. bổ sung **tiêu chí nguyên tử riêng theo nhiệm vụ và mẫu**;
5. tách **cổng lỗi nghiêm trọng** khỏi điểm chất lượng thông thường;
6. giữ `gold_response` và `gold_answer` làm căn cứ, không chấm exact match;
7. giữ mức nhận thức làm siêu dữ liệu độ phủ, không dùng làm nhiệm vụ.

Đây là một **suy luận thiết kế** từ bốn bài báo, chưa phải quyết định chuyên môn đã được HNMU/UET xác nhận.

## 2. Chuẩn hóa thuật ngữ trước khi so sánh

Sự không thống nhất chủ yếu do các bài báo đang nói ở năm tầng khác nhau:

1. **Mô-đun/phạm vi bộ đánh giá**: phần lớn của bộ đánh giá đang đo nhóm năng lực nào.
2. **Nhiệm vụ/tình huống sử dụng**: hợp đồng đầu vào–đầu ra mà mô hình phải thực hiện.
3. **Kỹ năng/nguyên tắc sư phạm**: hành vi sư phạm mong đợi trong phản hồi.
4. **Tiêu chí chấm**: một phát biểu nguyên tử mà bộ chấm có thể kiểm tra.
5. **Thước đo/cách tổng hợp**: cách biến các phán quyết thành điểm cấp mẫu, nhiệm vụ hoặc mô hình.

Ví dụ, `Questioning` trong KMP-Bench là một nguyên tắc sư phạm của lượt gia sư; `Adaptive Explanation Generation` trong TutorBench là một tình huống sử dụng; còn `F1` trong MathTutorBench là thước đo của một nhiệm vụ có đầu ra cấu trúc. Chúng không phải ba đối tượng cùng cấp.

Đối với dự án hiện tại:

- `T1–T4` chỉ nên được gọi là task nếu mỗi mục có input, output và hành vi đích phân biệt được;
- các hành vi như chẩn đoán hiểu sai, đặt câu hỏi gợi mở, đưa ví dụ hoặc không tiết lộ đáp án có thể là kỹ năng/nguyên tắc hoặc tiêu chí;
- `Biết`, `Hiểu`, `Vận dụng` nên là siêu dữ liệu nhận thức/độ phủ;
- lỗi nghiêm trọng nên có chính sách chặn điểm hoặc loại riêng, không nên được trộn vào một thang điểm trung bình thông thường.

## 3. MathTutorBench

### 3.1. Bộ đánh giá chia nhiệm vụ như thế nào?

MathTutorBench tổ chức benchmark quanh ba nhóm năng lực:

1. chuyên môn Toán (`Math Expertise`);
2. hiểu học sinh (`Student Understanding`);
3. tạo phản hồi gia sư (`Teacher Response Generation/Pedagogy`).

Bên dưới là bảy task có hợp đồng khác nhau:


| Nhóm năng lực        | Tên nhiệm vụ trong bài báo     | Đầu ra đích                            | Thước đo chính                                   |
| ----------------------- | ----------------------------------- | ------------------------------------------ | ---------------------------------------------------- |
| Math expertise          | Problem solving                     | Đáp án bài toán                       | Accuracy                                             |
| Math expertise          | Socratic questioning                | Câu hỏi theo hướng Socratic            | BLEU                                                 |
| Student understanding   | Student-solution correctness        | Nhãn đúng/sai của lời giải học sinh | F1                                                   |
| Student understanding   | Mistake location                    | Vị trí bước sai                        | Micro-F1                                             |
| Student understanding   | Mistake correction                  | Sửa lỗi trong lời giải                 | Accuracy                                             |
| Tạo phản hồi gia sư | `Scaffolding Generation`            | Phản hồi tiếp theo của gia sư         | Tỷ lệ thắng theo mô hình chấm điểm ưu tiên |
| Tạo phản hồi gia sư | `Pedagogical Instruction Following` | Phản hồi tuân thủ yêu cầu sư phạm  | Tỷ lệ thắng theo mô hình chấm điểm ưu tiên |

Như vậy, “nhiệm vụ” ở đây không phải các chiều chất lượng chung. Mỗi nhiệm vụ có đầu vào, đầu ra, nhãn/phản hồi chuẩn và thước đo riêng.

### 3.2. Bốn learning-science principles có phải bốn rubric chung không?

Không. Bài báo nêu bốn nguyên tắc:

- bảo đảm tính đúng đắn;
- scaffold thay vì đưa thẳng đáp án;
- khuyến khích học sinh tự sửa;
- tránh làm học sinh quá tải.

Chúng mô tả định hướng xây dựng và đánh giá chất lượng gia sư, nhưng bộ chấm cuối cho phản hồi mở là một mô hình chấm điểm ưu tiên đã học. Bài báo không gắn bốn dòng tiêu chí hiện ra cho từng mẫu rồi cộng điểm bốn dòng đó.

Trong quá trình thử bộ chấm, bài báo có dùng nguồn MRBench với tám loại tiêu chí: chất lượng hướng dẫn, khả năng hành động được, tiết lộ đáp án, nhận diện/vị trí lỗi, tính mạch lạc, giọng điệu và tính tự nhiên giống người. Tuy nhiên, đây không phải bằng chứng rằng bộ đánh giá cuối vận hành bằng tám tiêu chí đó cho mọi mẫu.

### 3.3. Một mẫu phản hồi mở được vận hành thế nào?

Luồng khái quát:

```text
bài toán + lời giải tham chiếu + lịch sử hội thoại
                       ↓
             mô hình sinh lượt gia sư
                       ↓
mô hình chấm điểm ưu tiên chấm phản hồi mô hình và phản hồi giáo viên
                       ↓
phản hồi mô hình thắng phản hồi giáo viên? → tỷ lệ thắng
```

Phản hồi giáo viên là một đối chứng chất lượng cao, không phải chuỗi duy nhất được chấp nhận. Mô hình có thể tạo phản hồi khác câu chữ nhưng vẫn được ưu tiên.

### 3.4. Điểm mạnh và giới hạn khi chuyển sang dự án

Điểm dùng được:

- nhiệm vụ khác nhau có thể cần thước đo khác nhau;
- phản hồi gia sư mở không nên bị so khớp chính xác với phản hồi tham chiếu;
- năng lực giải bài và năng lực dạy học phải được tách.

Giới hạn:

- mô hình chấm điểm ưu tiên cho một điểm ẩn, khó truy nguyên tiêu chí nào gây lỗi;
- bài báo thuộc miền Toán;
- phép kiểm bộ chấm tốt nhất được báo cáo khoảng `0,84` trên phân biệt chuyên gia với giáo viên mới, không phải một nghiên cứu đầy đủ về độ đồng thuận ở mọi tiêu chí;
- bài báo không đo kết quả học tập thật của học sinh.

## 4. KMP-Bench

### 4.1. Hai module khác nhau

KMP-Bench gồm:

- `KMP-Dialogue`: đánh giá phản hồi gia sư tiếp theo trong hội thoại;
- `KMP-Skills`: đánh giá các kỹ năng/tác vụ riêng gồm giải bài theo câu hỏi nối tiếp nhiều lượt, phát hiện và sửa lỗi, và tạo bài toán.

`KMP-Dialogue` gần nhất với cấu trúc dữ liệu của dự án hiện tại. Bài báo cắt hội thoại ngay trước một lượt gia sư:

```text
lịch sử trước lượt gia sư
        ↓ mô hình sinh phản hồi
phản hồi ứng viên ↔ lượt gia sư gốc/phản hồi tham chiếu
        ↓ bộ chấm so sánh theo cặp trên từng tiêu chí
Win / Tie / Lose + lý do
```

Điều này tương ứng trực tiếp với việc Plan 02 tạo một mẫu ứng viên cho mỗi lượt gia sư.

### 4.2. Nhiệm vụ, nguyên tắc và tiêu chí chấm có quan hệ thế nào?

Mỗi lượt gia sư đích được gắn một hoặc hai trong sáu nguyên tắc sư phạm:

1. Challenge;
2. Explanation;
3. Modelling;
4. Practice;
5. Questioning;
6. Feedback.

KMP-Dialogue có một thư viện 22 tiêu chí:

- 4 universal criteria;
- 3 criteria cho mỗi một trong 6 principles.

Nhưng một mẫu **không được chấm cả 22 tiêu chí**. Nếu mẫu có `n` nguyên tắc:

```text
số tiêu chí áp dụng = 4 + 3 × n
```

Do `n` bằng 1 hoặc 2, mỗi mẫu có 7 hoặc 10 phán quyết theo tiêu chí, cộng thêm một phán quyết tổng thể `Win/Tie/Lose` riêng.

Bài báo chỉ minh họa tên của một phần tiêu chí, ví dụ `Contextual Coherence and Relevance`, `Adherence to Defined Persona/Teaching Style`, `Relevance/Alignment` của hoạt động luyện tập và `Difficulty Appropriateness`. Không có đủ căn cứ để tự dựng tên đầy đủ của cả 22 tiêu chí.

### 4.3. Bộ chấm và cách tổng hợp

Bộ chấm so sánh phản hồi ứng viên với phản hồi tham chiếu trên từng tiêu chí:

- `Win`;
- `Tie`;
- `Lose`;
- rationale.

Bài báo còn sinh một phán quyết tổng thể riêng. Hai đầu ra này không nên nhập làm một.

Ở cấp model:

- `General-Level Acc` là trung bình tỷ lệ thắng của bốn tiêu chí chung;
- điểm mỗi nguyên tắc là trung bình tỷ lệ thắng của ba tiêu chí thuộc nguyên tắc đó;
- `Overall Acc` là trung bình của điểm chung và trung bình điểm sáu nguyên tắc;
- `Overall Judgement Acc` từ phán quyết tổng thể được báo riêng.

Đây là cách tổng hợp ở cấp mô hình, không phải bằng chứng cho việc cộng có trọng số 7/10 tiêu chí thành một điểm mẫu duy nhất.

### 4.4. KMP-Skills dùng cơ chế chấm khác KMP-Dialogue

Các nhiệm vụ trong KMP-Skills dùng thước đo theo nhiệm vụ:

- giải bài theo câu hỏi nối tiếp: độ chính xác theo lượt;
- phát hiện/sửa lỗi: `F1`, độ chính xác sửa lỗi và `MR-Score`;
- tạo bài toán: đánh giá `Pass/Fail` theo các chiều `Problem Construction`, `Solution Correctness`, `Solution Quality`; với bài tương tự có thêm `Similarity Appropriateness`.

Vì vậy, ngay trong một bài báo cũng không có một bộ tiêu chí thống nhất cho mọi mô-đun.

### 4.5. Điểm mạnh và giới hạn khi chuyển sang dự án

Điểm dùng được:

- nhiệm vụ/nguyên tắc phải gắn ở cấp lượt ứng viên, không gắn một nhãn duy nhất cho cả hội thoại thô;
- có thể có lõi tiêu chí chung và tiêu chí được chọn theo nguyên tắc;
- phán quyết theo tiêu chí và phán quyết tổng thể nên được lưu riêng;
- phản hồi tham chiếu có thể dùng trong phép so sánh theo cặp.

Giới hạn:

- phản hồi tham chiếu của KMP-Dialogue phần lớn đến từ quy trình sinh/kiểm dữ liệu riêng của bài báo;
- điểm so sánh theo cặp phụ thuộc mạnh vào chất lượng phản hồi tham chiếu;
- bài báo không công bố đầy đủ tên của cả 22 tiêu chí;
- các nguyên tắc là hành vi sư phạm, không tự động tương đương với mã nhiệm vụ.

## 5. TutorBench

### 5.1. Ba tình huống sử dụng

TutorBench có ba tình huống sử dụng:

1. `Adaptive Explanation Generation`;
2. `Assessment and Feedback`;
3. `Active Learning Support`.

Mỗi mẫu thuộc một tình huống sử dụng. Cấu trúc điển hình:


| Tình huống            | Ngữ cảnh chính                                                        | Mô hình cần sinh                          |
| ----------------------- | ------------------------------------------------------------------------ | -------------------------------------------- |
| Adaptive explanation    | Câu hỏi ban đầu, giải thích trước đó, follow-up của học sinh | Giải thích thích ứng với nhu cầu mới  |
| Assessment and feedback | Bài toán và lời giải của học sinh                                 | Đánh giá, chỉ lỗi và feedback          |
| Active learning support | Bài làm sai/dở dang hoặc trạng thái bế tắc                       | Hint/next step có ích mà không làm thay |

Ba tình huống này gần với T1–T3 hiện tại hơn cách chia nguyên tắc của KMP-Bench.

### 5.2. Rubric được tạo ở cấp nào?

Tiêu chí chấm được xây ở cấp mẫu. Chuyên gia:

1. viết nội dung mẫu/tình huống;
2. viết phản hồi gia sư mẫu;
3. dựa trên phản hồi và yêu cầu của mẫu để viết bộ tiêu chí riêng.

Mỗi mẫu có từ 3 đến 39 tiêu chí; toàn bộ bộ đánh giá có 15.220 tiêu chí cho 1.490 mẫu. Tiêu chí được thiết kế để:

- self-contained;
- mutually exclusive;
- collectively comprehensive;
- verifiable.

Các nhãn chung như tính đúng, tính liên quan, điều chỉnh theo học sinh, nhận diện hiểu sai, câu hỏi gợi mở, yêu cầu rõ/ngầm hoặc khách quan/chủ quan là siêu dữ liệu phân tích của tiêu chí. Chúng không phải một bộ tiêu chí chung bắt buộc cho mọi mẫu.

### 5.3. Cách chấm

Mỗi tiêu chí được bộ chấm LLM chấm độc lập:

- `Pass`;
- `Fail`.

Trọng số tiêu chí:

- `+5`: critical positive;
- `+1`: noncritical positive;
- `-5`: undesirable/critical negative.

Bài báo tính trung bình nhị phân có trọng số `ARR_w`. Có một câu hỏi mở: mô tả nói điểm được chuẩn hóa về `[0,1]`, nhưng công thức in chưa diễn giải đầy đủ cách xử lý nếu tổng tử số âm do tiêu chí `-5`. Dự án không nên tự suy ra một phép chặn điểm rồi gán cho bài báo.

### 5.4. Phản hồi mẫu có phải chuỗi đích để so khớp chính xác không?

Không. Phản hồi gia sư mẫu là căn cứ giúp chuyên gia mô tả phản hồi tốt và viết tiêu chí. Bài báo không nói rằng phản hồi mô hình phải giống câu chữ phản hồi mẫu, cũng không thiết lập phản hồi mẫu là đối chứng bắt buộc trong mọi phép so sánh theo cặp.

### 5.5. Việc kiểm định bộ chấm nói được gì?

Bài báo báo cáo:

- 250 samples;
- 2.475 criteria;
- ba lượt chấm của con người cho mỗi tiêu chí;
- 69 chuyên gia tham gia;
- mean human agreement `0,75`;
- độ khớp giữa bộ chấm và con người `0,78`;
- F1 `0,82` so với majority vote trên 1.900 noncritical criteria.

Điểm cần thận trọng: các critical criteria trọng số `+5/-5` bị loại khỏi phép tính F1 nêu trên. Do đó `0,82` không xác nhận toàn bộ weighted scheme.

### 5.6. Điểm mạnh và giới hạn khi chuyển sang dự án

Điểm dùng được:

- một nhiệm vụ/tình huống chung có thể đi kèm tiêu chí riêng ở cấp mẫu;
- tiêu chí nguyên tử, quan sát được giúp rà soát dễ hơn;
- phản hồi mẫu là bằng chứng hỗ trợ biên soạn, không phải chuỗi đích duy nhất;
- nội dung tiêu chí nên tách khỏi các nhãn phân tích.

Giới hạn:

- 3–39 tiêu chí mỗi mẫu rất tốn chi phí biên soạn/rà soát;
- dữ liệu thuộc STEM tiếng Anh bậc high school/AP;
- độ tin cậy của bộ chấm tiếng Việt trong miền Tin học THCS chưa được kiểm;
- trọng số `+5/+1/-5` không nên chuyển nguyên xi nếu chưa calibration.

## 6. VietLegal/VLegal-Bench

### 6.1. Vì sao bài báo pháp luật vẫn hữu ích?

Đây không phải bộ đánh giá gia sư. Giá trị chính của bài báo là:

- taxonomy task có cấu trúc;
- task-specific metrics;
- provenance tới nguồn có thẩm quyền;
- quy trình kiểm tra chéo và phân xử;
- phân biệt cognitive taxonomy với task.

### 6.2. Cách chia task

Bài báo có 22 nhiệm vụ thuộc năm tầng lấy cảm hứng từ Bloom:


| Tầng                         | Số task | Ví dụ chức năng                                                                                                       |
| ----------------------------- | -------: | ------------------------------------------------------------------------------------------------------------------------- |
| Recognition and Recall        |        5 | NER, topic/concept/article/schema recall                                                                                  |
| Understanding and Structuring |        5 | relation extraction, element recognition, graph structuring, judgment verification, intent                                |
| Suy luận                     |        5 | dự đoán điều/khoản, quyết định của tòa, suy luận nhiều điều, xung đột, chế tài/biện pháp khắc phục |
| Interpretation and Generation |        3 | summarization, judicial reasoning, objective opinion                                                                      |
| Ethics, Fairness and Bias     |        4 | bias, privacy, ethical consistency, unfair contracts                                                                      |

Một mẫu thuộc một nhiệm vụ, nhận chỉ dẫn và nhãn/phản hồi chuẩn theo nhiệm vụ đó. Mức nhận thức là tầng tổ chức taxonomy, không thay thế nhiệm vụ.

### 6.3. Tiêu chí và thước đo

Các nhiệm vụ dùng thước đo riêng như:

- Accuracy;
- F1/Macro-F1;
- ROUGE-L;
- Node-F1/Edge-F1.

Ba generation tasks còn được human audit trên một subset với hai chiều chung, thang 1–5:

- Legal Accuracy;
- Completeness.

Đây là một lớp kiểm định bổ sung, không phải tiêu chí riêng theo mẫu được dùng làm thước đo chính cho toàn bộ 10.450 mẫu.

### 6.4. Điểm mạnh và giới hạn khi chuyển sang dự án

Điểm dùng được:

- mức nhận thức nên là trục độ phủ;
- thước đo có thể thay đổi theo hợp đồng nhiệm vụ;
- provenance và adjudication phải hiện trong dữ liệu;
- automatic evaluation có thể được kiểm bằng một human rubric nhỏ trên subset.

Giới hạn:

- không đo tutoring behavior;
- `ROUGE-L` không đủ cho phản hồi gia sư mở;
- Bloom của miền luật không chuyển trực tiếp sang Tin học THCS;
- bài báo có một bất nhất nội bộ: bảng mô tả ba chuyên gia cao cấp trong đánh giá con người, phụ lục lại mô tả hai chuyên gia trẻ. Không nên dùng số người đánh giá này làm tiền lệ cứng.

## 7. So sánh trực tiếp ba cơ chế chấm phản hồi mở


| Cơ chế               | MathTutorBench                           | KMP-Dialogue                                                          | TutorBench                                                        |
| ---------------------- | ---------------------------------------- | --------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Đơn vị chấm        | Cặp phản hồi                          | Cặp phản hồi × tiêu chí                                         | Phản hồi ứng viên × tiêu chí                               |
| Phản hồi tham chiếu | Phản hồi giáo viên                   | Lượt gia sư gốc bị cắt                                          | Phản hồi mẫu chủ yếu hỗ trợ biên soạn                    |
| Tiêu chí hiện ra    | Không có trong bộ chấm cuối         | 4 tiêu chí chung + tiêu chí theo nguyên tắc                     | Tiêu chí riêng của mẫu                                       |
| Đầu ra bộ chấm     | Điểm ưu tiên                         | `Win/Tie/Lose` + lý do                                               | `Pass/Fail`                                                       |
| Cách tổng hợp       | Tỷ lệ thắng so với giáo viên       | Tỷ lệ thắng theo nhóm chung/nguyên tắc/mô hình                | Trung bình có trọng số ở cấp mẫu                           |
| Ưu điểm             | Gọn, chấp nhận nhiều cách trả lời | Truy được theo hành vi và so được với phản hồi tham chiếu | Rất cụ thể, rà soát được yêu cầu của từng mẫu        |
| Rủi ro                | Điểm tổng khó truy nguyên           | Phụ thuộc phản hồi tham chiếu                                    | Chi phí biên soạn/rà soát lớn, trọng số cần hiệu chỉnh |

Không bài báo nào cung cấp trực tiếp một phương án hoàn chỉnh cho dữ liệu hiện tại. Thiết kế tốt nhất phải kết hợp ưu điểm và giảm các rủi ro trên.

## 8. Đề xuất cho 2.028 mẫu ứng viên hiện tại

### 8.1. Nhiệm vụ ở cấp mẫu ứng viên

Mỗi mẫu ứng viên nên có:

- một mã nhiệm vụ chính `primary_task_id`;
- không hoặc nhiều mã kỹ năng phụ `secondary_skill_ids`;
- độ tin cậy, lý do và trạng thái rà soát.

Không gán nhiệm vụ duy nhất cho toàn hội thoại thô, vì các lượt gia sư khác nhau trong cùng hội thoại có thể thực hiện hành vi khác nhau.

T1–T3 có ánh xạ gần với TutorBench:

- T1: adaptive explanation;
- T2: assessment and feedback;
- T3: active-learning scaffolding/hint.

Đối với T4:

- **suy luận đề xuất**: dùng chẩn đoán làm kỹ năng phụ mặc định trong các mẫu phản hồi mở, vì chẩn đoán thường nằm bên trong phản hồi, giải thích hoặc hỗ trợ từng bước;
- chỉ dùng T4 làm nhiệm vụ chính nếu định nghĩa một hợp đồng đầu ra chẩn đoán có cấu trúc và phân biệt được.

Điểm này phải được kiểm trên phân bố thật của 2.028 candidates và do HNMU/UET chốt.

### 8.2. Cấu trúc tiêu chí kết hợp

Đề xuất ba lớp:

#### A. Lõi tiêu chí chung nhỏ

Ví dụ ba chiều đánh giá cần thí điểm:

1. đúng kiến thức và phù hợp learning-resource grounding;
2. nhất quán với ngữ cảnh và trạng thái hiểu của học sinh;
3. rõ ràng, liên quan và phù hợp lứa tuổi.

Đây là chiều/khuôn tiêu chí, chưa phải nội dung tiêu chí cuối cho mọi mẫu.

#### B. Tiêu chí riêng theo nhiệm vụ và mẫu

Mỗi mẫu nhận một số tiêu chí nguyên tử, ví dụ:

- T1: nhận đúng chỗ học sinh chưa hiểu; giải thích thích ứng; dùng ví dụ/biểu diễn phù hợp khi cần;
- T2: phân biệt phần đúng/sai; giải thích nguyên nhân; đưa hướng sửa có thể hành động;
- T3: đưa bước tiếp theo hữu ích; mức hỗ trợ vừa đủ; không tiết lộ đáp án quá sớm.

Số tiêu chí không nên chốt theo mức `3–39` của TutorBench hoặc `7/10` của KMP-Bench trước thí điểm. Mục tiêu là đủ bao phủ yêu cầu nhưng khả thi cho biên soạn/rà soát.

#### C. Cổng lỗi nghiêm trọng

Tách riêng:

- sai kiến thức nghiêm trọng;
- bịa nguồn;
- nội dung không an toàn;
- tiết lộ đáp án làm hỏng task scaffolding;
- các lỗi nghiêm trọng khác do HNMU/UET xác nhận.

Không nên biến lỗi nghiêm trọng thành một R5 rồi cho phép điểm tốt ở R1–R4 “bù” lại. Chính sách có thể là rà soát, chặn điểm hoặc loại.

### 8.3. Các trường chuẩn/tham chiếu

- `gold_response`: phản hồi tham chiếu của tác giả; dùng để hiểu ý đồ, viết tiêu chí, tạo ví dụ và có thể làm đối chứng phụ sau khi chất lượng được HNMU xác nhận.
- `gold_answer`: neo sự thật/đáp án chuyên môn của bài; giúp bộ chấm kiểm tính đúng, không phải phản hồi gia sư đích.

Không dùng so khớp chính xác cho hai trường này.

### 8.4. Phán quyết và điểm

Khởi đầu nên chấm ở cấp tiêu chí:

- `pass`;
- `failed`;
- `need_human_review` khi bằng chứng hoặc phán quyết không đủ chắc.

Nên báo riêng:

- kết quả trên lõi tiêu chí chung;
- kết quả theo nhiệm vụ;
- tỷ lệ lỗi nghiêm trọng;
- độ phủ và tỷ lệ cần rà soát.

Chưa nên đặt trọng số tùy ý hoặc tạo một điểm tổng duy nhất trước khi có thí điểm HNMU, phân tích độ đồng thuận giữa người chấm và hiệu chỉnh bộ chấm.

### 8.5. Cấu trúc quan hệ thay vì tăng cột mẫu ứng viên

Giữ `benchmark_candidate_splits.csv` gọn. Tạo các bảng ngoài:

- `benchmark_tasks.csv`;
- `secondary_skills.csv`;
- `rubric_dimensions.csv`;
- `task_rubric_templates.csv`;
- `candidate_rubric_criteria.csv`;
- `serious_errors.csv`;
- `candidate_task_assignments.csv`.

`candidate_rubric_criteria.csv` tối thiểu cần các trường:

```text
benchmark_candidate_id
criterion_id
criterion_type
dimension_id
criterion_text
polarity
criticality
research_ids
learning_material_ids
authoring_source
status
```

Cách này cho phép một mẫu có tiêu chí riêng mà không làm phình tệp ứng viên chính.

## 9. Tác động tới draft Plan 03 hiện tại

### 9.1. Những phần nên giữ

- gợi ý nhiệm vụ chính/phụ;
- mức nhận thức không được dùng làm nhiệm vụ;
- lỗi nghiêm trọng ở danh mục riêng;
- ma trận truy vết;
- hàng chờ rà soát và độ tin cậy;
- không để agent tự đánh dấu `confirmed`;
- độ phủ quan sát được, không tuyên bố bao phủ chương trình.

### 9.2. Những phần cần sửa trước khi duyệt

1. `rubrics.csv` hiện đang giữ R1–R5 lặp theo mỗi nhiệm vụ. Cấu trúc này chỉ biểu diễn tiêu chí cố định cấp nhiệm vụ, không biểu diễn được:
   - cách KMP-Bench chọn tiêu chí theo nguyên tắc;
   - tiêu chí riêng cho từng mẫu như TutorBench.
2. `suggested_rubric_ids` chỉ trỏ tới tiêu chí có sẵn; cần tách:
   - mã chiều/khuôn tiêu chí;
   - các tiêu chí cụ thể của từng mẫu.
3. Nhiệm vụ, kỹ năng phụ và chiều tiêu chí cần thành ba registry khác nhau.
4. T4 cần quyết định là nhiệm vụ hay kỹ năng phụ.
5. Cần thêm thí điểm biên soạn/kiểm định tiêu chí trước khi gán cho toàn bộ 2.028 mẫu.
6. Cần định nghĩa đầu ra của bộ chấm ở cấp tiêu chí và chính sách cho `need_human_review`.
7. Cần tránh gộp trọng số tùy ý thành một điểm trước khi hiệu chỉnh.

Không sửa Plan 03 trong đợt nghiên cứu này để project lead có thể xem kết luận trước.

## 10. Bằng chứng, suy luận và câu hỏi mở

### Bằng chứng trực tiếp từ bài báo

- MathTutorBench dùng thước đo khác nhau theo nhiệm vụ và mô hình chấm điểm ưu tiên cho phản hồi mở.
- KMP-Dialogue áp dụng 4 tiêu chí chung + `3 × n` tiêu chí theo nguyên tắc cho từng lượt gia sư đích.
- TutorBench dùng 3–39 tiêu chí riêng cho mỗi mẫu với phán quyết `Pass/Fail` và trọng số.
- VietLegal dùng taxonomy nhiệm vụ và thước đo theo nhiệm vụ; mức nhận thức tổ chức độ phủ/taxonomy.

### Suy luận cho dự án

- dùng một nhiệm vụ chính và nhiều kỹ năng phụ ở cấp mẫu;
- dùng lõi tiêu chí chung nhỏ kết hợp với tiêu chí riêng theo mẫu;
- để chẩn đoán là kỹ năng phụ mặc định;
- chấm tuyệt đối ở cấp tiêu chí trước khi thử so sánh theo cặp hoặc tính điểm tổng có trọng số;
- lưu các tiêu chí cụ thể trong bảng quan hệ ngoài tệp ứng viên.

### Open questions cần HNMU/UET quyết định

1. T4 có hợp đồng đầu ra riêng đủ rõ để là nhiệm vụ chính không?
2. Lõi tiêu chí chung nên có những chiều nào và có tiêu chí chung thật sự hay chỉ là khuôn?
3. Số tiêu chí trên mỗi mẫu nào vừa đủ cho thí điểm?
4. Lỗi nghiêm trọng nào dẫn tới `score_cap`, `exclusion` hoặc chỉ `review`?
5. `gold_response` trong 665 hội thoại thô có đủ chất lượng để dùng trong phép so sánh theo cặp không?
6. Bộ chấm tiếng Việt cần đạt ngưỡng đồng thuận nào trước khi chạy toàn bộ?
7. Có dùng trọng số sau hiệu chỉnh không, và nếu có thì trọng số phục vụ cấp tiêu chí hay cấp chiều đánh giá?

## 11. Nguồn và vị trí kiểm chứng

Nguồn chính:

- MathTutorBench: `document/paper/source_paper/2502.18940v2.pdf`; Sections 3.2, 4.1–4.3; Tables 1–4; Figures 2, 5–7; `https://arxiv.org/html/2502.18940v2`.
- KMP-Bench: `document/paper/source_paper/18426-AAAI26.ShiW-NLP.pdf`; Sections 2.3, 3.1–3.2; Figure 3; Tables 1–3; Appendices F, I trên `https://arxiv.org/html/2603.02775v1`; publication record `https://doi.org/10.1609/aaai.v40i39.40578`.
- TutorBench: `document/paper/source_paper/2510.02663v1.pdf`; Sections 2.1–2.4, 3.1–3.7; Equation 1; Appendix A.1; `https://arxiv.org/html/2510.02663v1`; public subset `https://huggingface.co/datasets/tutorbench/tutorbench`.
- VietLegal/VLegal-Bench: `document/paper/source_paper/2512.14554v5.pdf`; Section 3.1; Table 1; Sections 3.2, 4.1; Appendices E–G; Table 4; `https://arxiv.org/html/2512.14554v5`.

Các tệp truy vết:

- `literature_notes/pre_plan03_task_rubric_review/review_protocol.md`;
- `literature_notes/pre_plan03_task_rubric_review/search_log.csv`;
- `literature_notes/pre_plan03_task_rubric_review/evidence_matrix.csv`;
- `literature_notes/pre_plan03_task_rubric_review/operational_claim_matrix.csv`.
