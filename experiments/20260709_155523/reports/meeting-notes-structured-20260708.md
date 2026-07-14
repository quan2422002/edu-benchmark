# Ghi chú có cấu trúc — trao đổi với HNMU ngày 08/07/2026

Ngày trao đổi: 08/07/2026
Ngày cấu trúc lại: 09/07/2026
Experiment: `20260709_155523`
Nguồn: `user_diary.md`, mục `Update plan (08-07-2026)` và mẫu `document/ideal_dialog_example.png`

## 1. Điều thay đổi quan trọng nhất

HNMU đã bắt đầu tạo dữ liệu. Sản phẩm chính mà giáo viên cung cấp là **một hội thoại kiểu mẫu giữa học sinh và gia sư AI**, kèm một số thông tin như nguồn sách, chủ đề, bài học, mức độ nhận thức, đáp án và kỹ thuật giàn giáo.

Vì vậy, luồng làm việc cần được hiểu lại như sau:

```text
HNMU tạo hội thoại thô và thông tin phụ trợ
                    ↓
UET lưu nguyên bản và tách cấu trúc tối thiểu
                    ↓
Tạo ứng viên tại từng lượt gia sư
                    ↓
Agent đề xuất nhiệm vụ; UET/HNMU duyệt
                    ↓
Tạo mẫu theo nhiệm vụ và hoàn thiện phiếu tác giả
                    ↓
Rubric được dùng để đánh giá phản hồi của mô hình trong thí nghiệm
```

Giáo viên HNMU không cần biết hoặc tự gán task. Phiếu tác giả từ giai đoạn trước trở thành **định dạng đích nội bộ của UET**, không còn là biểu mẫu mà HNMU bắt buộc phải điền trực tiếp.

## 2. Ba dòng công việc hiện tại

### 2.1. Tiếp nhận, tách cấu trúc và tạo ứng viên

Cần xây dựng một phương pháp ổn định để chuẩn bị dữ liệu thô cho agent trước khi hoàn thiện phiếu tác giả. Phương pháp này phải:

- giữ nguyên nội dung hội thoại do HNMU cung cấp;
- tách học liệu, thông tin phụ trợ và từng lượt có số thứ tự, người nói, vị trí nguồn;
- tạo ứng viên tại các lượt gia sư có giá trị đánh giá;
- lưu được cả bản gốc và bản đã ánh xạ để đối chiếu;
- chưa coi kết quả tách cấu trúc là phiếu tác giả hoàn chỉnh;
- không dùng AI để viết lại, “làm hay hơn” hoặc tự điền nội dung chưa có;
- để agent đề xuất nhiệm vụ, điểm cắt và luận giải;
- yêu cầu UET/HNMU duyệt trước khi tạo mẫu theo nhiệm vụ và ánh xạ đầy đủ vào phiếu tác giả.

### 2.2. Hoàn thiện task và rubric

Task và rubric vẫn là hai trụ cột của benchmark, nhưng chúng được UET phát triển song song với việc HNMU tạo hội thoại thô.

- Task mô tả năng lực hoặc hành vi gia sư mà mẫu dùng để đánh giá.
- Mức độ nhận thức vẫn là một trường riêng gồm `Biết`, `Hiểu`, `Vận dụng`.
- Rubric mô tả các mặt cần chấm trong phản hồi của gia sư.
- Các bản task/rubric hiện có là đầu vào v0, chưa phải bản đã được HNMU phê duyệt.

### 2.3. Thiết kế cách sử dụng benchmark

Ba bài báo đã được đọc kỹ trong P03 của experiment trước cung cấp ba cách dùng phản hồi tham chiếu đáng chú ý:


| Nghiên cứu                                                                                  | Đơn vị mô hình cần sinh                                                                                                     | Vai trò của phản hồi tham chiếu                                                                                                   | Cách chấm chính                                                                                                                                          |
| --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| *MathTutorBench: A Benchmark for Measuring Open-ended Pedagogical Capabilities of LLM Tutors* | Lượt tiếp theo của gia sư dựa trên bài toán và lịch sử hội thoại.                                                   | Phản hồi giáo viên là đối chứng trong phép xếp hạng cặp.                                                                   | Mô hình chấm chuyên biệt tính tỷ lệ phản hồi của mô hình được ưu tiên hơn phản hồi giáo viên.                                        |
| *From Solver to Tutor: Evaluating the Pedagogical Intelligence of LLMs with KMP-Bench*        | Một lượt gia sư tại vị trí hội thoại đã được cắt, với lịch sử kết thúc ở lượt học sinh ngay trước đó. | Lượt gia sư gốc bị cắt ra trở thành`reference response`.                                                                       | Mô hình giám khảo so sánh phản hồi cần chấm với phản hồi tham chiếu theo tiêu chí chung và tiêu chí sư phạm, trả về Thắng/Hòa/Thua. |
| *TutorBench: A Benchmark To Assess Tutoring Capabilities Of Large Language Models*            | Phản hồi cuối cho một hội thoại và bối cảnh đã được định sẵn.                                                    | Chuyên gia viết`golden tutoring response`; phản hồi này chủ yếu làm căn cứ để xây tiêu chí chấm riêng cho từng mẫu. | Mô hình giám khảo chấm Đạt/Không đạt trên từng tiêu chí; không phải phép so khớp văn bản với phản hồi mẫu.                          |

Từ ba cách trên, hướng phù hợp nhất cho dự án hiện tại là:

1. Dùng `student_prompt` và `conversation_history` làm đầu vào.
2. Yêu cầu mô hình sinh một lượt gia sư tại vị trí đã chọn.
3. Dùng lượt gia sư tương ứng do HNMU viết làm `gold_response`/phản hồi tham chiếu.
4. Chấm bằng rubric theo task; phản hồi tham chiếu là căn cứ quan trọng nhưng không phải đáp án duy nhất về mặt câu chữ.
5. Nếu dùng mô hình giám khảo, phải kiểm tra độ phù hợp với đánh giá của HNMU trên một tập mẫu trước.

Một hội thoại HNMU có nhiều lượt gia sư có thể tạo ra nhiều mẫu benchmark bằng cách cắt tại các lượt gia sư khác nhau. Điều kiện bắt buộc là mỗi mẫu mới phải truy ngược được tới hội thoại gốc và vị trí lượt nguồn, đồng thời không sửa nội dung.

Giao thức thí nghiệm chi tiết vẫn cần xác định thêm:

- danh sách mô hình và cấu hình cần so sánh;
- số lần chạy cho mỗi mẫu khi mô hình có tính ngẫu nhiên;
- cách kết hợp điểm Likert, so sánh với phản hồi tham chiếu và đánh giá của giáo viên;
- cách báo cáo theo task, rubric, chủ đề, mức nhận thức và độ dài lịch sử;
- cách ước lượng chi phí và độ ổn định của thứ hạng mô hình.

## 3. Ánh xạ sơ bộ từ mẫu HNMU sang phiếu tác giả

Thứ tự chính thức là:

```text
Tách cấu trúc tối thiểu
→ tạo ứng viên theo lượt gia sư
→ agent đề xuất nhiệm vụ
→ UET/HNMU duyệt
→ tạo mẫu theo nhiệm vụ
→ hoàn thiện phiếu tác giả
```

Bảng dưới đây mô tả đích cuối cùng sau khi nhiệm vụ và lượt gia sư mục tiêu đã được duyệt; không phải tất cả các trường đều được điền ngay ở bước tách cấu trúc.


| Nội dung trong mẫu HNMU                         | Trường đích dự kiến                       | Cách xử lý                                                                                                                        |
| ------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Sách giáo khoa Tin học 6                       | `reference_curriculumn_list`                    | Giữ nguyên nguồn; UET bổ sung mã học liệu và định dạng trích dẫn nếu xác định được.                              |
| Chủ đề                                         | `Topic`                                         | Giữ tên gốc, đồng thời UET có thể gắn tên chủ đề chuẩn ở một lớp dữ liệu riêng.                                  |
| Tên bài và trang                               | `reference_curriculumn_list`                    | Sao chép nguyên văn; không tự suy ra mục nhỏ nếu mẫu không nêu.                                                           |
| Nội dung câu hỏi                               | Thông tin về mục tiêu/đề bài             | Không mặc định đây là lời học sinh nói. Chỉ đưa vào`student_work` hoặc trường đích khác khi quy ước cho phép. |
| Mức độ                                         | `cognitive_level`                               | Ánh xạ trực tiếp nếu thuộc ba nhãn đã chốt.                                                                                |
| Đáp án                                         | Trường mới`answer`                           | Giữ riêng như đáp án/căn cứ kiến thức của bài. Không tự động coi là`gold_response`.                                 |
| Lượt HS đầu tiên                             | `student_prompt`                                | Giữ nguyên lời học sinh; đây là tuyên bố ban đầu về vấn đề đang gặp.                                                |
| Các lượt AI/HS ở giữa                        | `conversation_history`                          | Giữ nguyên thứ tự; phần này bắt đầu bằng gia sư và kết thúc bằng học sinh theo quy ước hiện tại.                 |
| Lượt AI cuối                                   | `gold_response`                                 | Giữ nguyên câu phản hồi cuối mong muốn của gia sư.                                                                          |
| Các kỹ thuật giàn giáo                       | `Note` hoặc trường phụ trợ về giàn giáo | Giữ nguyên nhãn do HNMU cung cấp; chưa tự động dùng để chấm R3.                                                          |
| Mã task, điểm rubric, người tạo, thời gian | Các trường tương ứng                      | Không suy diễn từ hội thoại nếu nguồn không cung cấp; UET hoặc quy trình tiếp nhận bổ sung sau.                        |

## 4. Các nguyên tắc cần chốt trước khi viết bộ chuyển đổi

### 4.1. Hội thoại gốc là bất biến

Mỗi mẫu cần có một bản gốc chỉ đọc. Mọi thao tác tách trường phải có khả năng truy ngược về bản gốc. Nếu nội dung có lỗi chính tả hoặc ký hiệu trình bày, bộ chuyển đổi không được tự sửa; chỉ được ghi cảnh báo.

### 4.2. Tách hội thoại không đồng nghĩa với viết lại hội thoại

Ở bước tách cấu trúc, hệ thống chỉ tạo danh sách lượt có số thứ tự, người nói và vị trí nguồn. Sau khi agent đề xuất nhiệm vụ và UET/HNMU duyệt điểm cắt, mẫu benchmark mới dùng quy ước:

1. `student_prompt` là lời đầu tiên của học sinh;
2. `conversation_history` là phần trao đổi sau lời đầu tiên và trước phản hồi cuối, bắt đầu bằng gia sư và kết thúc bằng học sinh;
3. `gold_response` là phản hồi cuối mong muốn của gia sư.

Bộ chuyển đổi chỉ xác định ranh giới và sao chép nguyên văn các đoạn này. Agent không được thay đổi nội dung để làm mẫu phù hợp hơn với nhiệm vụ.

### 4.3. Dữ liệu nguồn và dữ liệu suy ra phải tách riêng

Ví dụ:

- `Mức độ: Vận dụng` do HNMU ghi là dữ liệu nguồn;
- task do UET gán là dữ liệu suy ra;
- tên chủ đề chuẩn do UET ánh xạ là dữ liệu chuẩn hóa;
- điểm rubric sinh ra sau thí nghiệm là dữ liệu đánh giá.

Không nên trộn bốn nhóm này thành một khối mà không ghi nguồn gốc.

### 4.4. Trường thiếu phải được ghi là thiếu

Không có bài làm, mã học liệu, cách trả lời khác vẫn hợp lệ hoặc thông tin tác giả thì ghi trạng thái thiếu/chờ bổ sung. Không tự tạo nội dung để làm cho mẫu “đủ trường”.

## 5. Những điểm còn mâu thuẫn hoặc cần làm rõ

### 5.1. Đơn vị được đánh giá

Quy ước gần nhất của dự án là đánh giá **phản hồi cuối của gia sư** dựa trên `student_prompt` và `conversation_history`. Trong khi đó, HNMU đang tạo **toàn bộ hội thoại kiểu mẫu** và ghi cả các kỹ thuật giàn giáo xuyên suốt.

Hai hướng này không hoàn toàn giống nhau:

- nếu chỉ chấm phản hồi cuối, các lượt gia sư trong lịch sử là ngữ cảnh cố định;
- nếu chấm cả hội thoại, mô hình phải tự tạo nhiều lượt và rubric phải đánh giá tiến trình.

Kết luận hiện tại là **giữ phương án sinh và chấm một lượt phản hồi của gia sư trên lịch sử đã định sẵn**. Cách này được hỗ trợ trực tiếp bởi cả ba nghiên cứu:

- MathTutorBench sinh lượt gia sư tiếp theo từ lịch sử;
- KMP-Bench cắt hội thoại tại một lượt gia sư và yêu cầu mô hình sinh lại lượt đó;
- TutorBench chỉ đánh giá phản hồi cuối trong hội thoại được định sẵn.

Thiết kế này chưa đánh giá khả năng mô hình tự điều khiển toàn bộ hội thoại nhiều lượt. Toàn bộ hội thoại nguồn vẫn phải được giữ để sau này có thể xây một nhánh đánh giá đa lượt riêng.

### 5.2. “Đáp án” không chắc là `gold_response`

Trong mẫu HNMU, “Đáp án” mô tả kiến thức cần đạt, còn câu AI cuối là một phản hồi hội thoại. Hai nội dung có vai trò khác nhau. Nếu gộp chúng, có thể làm sai ý giáo viên hoặc khiến câu trả lời chuẩn không thực sự trả lời lượt cuối.

Quyết định hiện tại:

- thêm trường `answer` — tên hiển thị tiếng Việt là **Đáp án** — vào phiên bản tiếp theo của phiếu tác giả;
- `answer` lưu kết quả hoặc kiến thức đích của bài;
- `gold_response` lưu phản hồi lý tưởng của gia sư trong đúng bối cảnh task, yêu cầu học sinh và lịch sử hội thoại;
- `gold_response` không bắt buộc phải nêu đáp án cuối;
- với task gợi mở hoặc hỗ trợ học tập chủ động, việc tiết lộ đáp án quá sớm có thể làm giảm điểm rubric dù nội dung đáp án là đúng.

Điểm này phù hợp với MathTutorBench và TutorBench: một phản hồi gia sư tốt không đồng nhất với lời giải đầy đủ; trong bối cảnh cần gợi mở, tiết lộ đáp án có thể là hành vi không mong muốn.

### 5.3. Quan hệ một-nhiều giữa hội thoại thô và mẫu benchmark

Không bắt buộc một hội thoại thô của HNMU chỉ tạo ra một mẫu benchmark.

Một hội thoại có thể tạo nhiều mẫu bằng cách:

- chọn các lượt gia sư khác nhau làm phản hồi cần dự đoán;
- cắt lịch sử ngay trước lượt đó;
- gán task phù hợp với chức năng sư phạm của lượt được chọn;
- giữ nguyên đoạn hội thoại nguồn trong mọi mẫu phát sinh.

Cách này gần với KMP-Bench, nơi các hội thoại được cắt tại lượt gia sư để tạo trường hợp đánh giá. Một hội thoại HNMU có thể chứa chẩn đoán, gợi mở và phản hồi bài làm ở các vị trí khác nhau; mỗi vị trí có thể phục vụ một task khác.

Mỗi mẫu phát sinh tối thiểu phải lưu:

- mã hội thoại nguồn;
- vị trí hoặc mã lượt gia sư nguồn;
- phạm vi các lượt được dùng làm lịch sử;
- phương pháp tạo mẫu;
- task được gán và trạng thái xác nhận;
- mã phiên bản của quy tắc ánh xạ.

Như vậy, quan hệ đúng là:

```text
1 hội thoại thô HNMU → 1 hoặc nhiều mẫu benchmark
1 mẫu benchmark → đúng 1 hội thoại nguồn và 1 lượt gia sư nguồn
```

### 5.4. Rubric đang mô tả phản hồi, chưa mô tả toàn bộ tiến trình

Ba nghiên cứu đều ủng hộ việc chấm phản hồi trong ngữ cảnh, nhưng cách quan sát khác nhau:

- MathTutorBench chấm lượt gia sư được sinh dựa trên lịch sử hội thoại;
- KMP-Bench chấm phản hồi tại một vị trí cắt, dùng tiêu chí chung và tiêu chí gắn với nguyên tắc sư phạm của lượt đó;
- TutorBench chấm phản hồi cuối bằng tiêu chí riêng cho từng mẫu.

Vì vậy, ở thiết kế hiện tại, **đối tượng trực tiếp được chấm là phản hồi do mô hình sinh**, còn `student_prompt` và `conversation_history` là bằng chứng ngữ cảnh để xác định phản hồi đó có phù hợp hay không.

R3 không chấm chất lượng của các lượt gia sư đã có trong lịch sử như thể đó là đầu ra của mô hình. Tuy nhiên, lịch sử phải được dùng để kiểm tra phản hồi mới có:

- tiếp nối đúng tiến trình giàn giáo;
- lặp lại hoặc nhảy cóc không phù hợp;
- hỗ trợ quá ít hoặc tiết lộ quá nhiều;
- thích ứng với những gì học sinh vừa thể hiện.

Nếu sau này đánh giá toàn bộ hội thoại do mô hình tự tạo, cần một giao thức và cách tổng hợp điểm khác.

### 5.5. Dữ liệu HNMU hiện có thể không đủ mọi trường

Các trường như mã task, mã học liệu, cách trả lời khác vẫn hợp lệ, điểm rubric, người kiểm tra chéo và thời gian có thể không xuất hiện trong mẫu thô. Vì thế bộ chuyển đổi phải hỗ trợ dữ liệu chưa hoàn chỉnh và sinh báo cáo thiếu trường, thay vì từ chối toàn bộ mẫu.

Có thể dùng specialist agent để **đề xuất** các trường còn thiếu, đặc biệt là task. Tuy nhiên, không nên xây một agent mới ngay nếu specialist `benchmark-specification-designer` hiện có đã phù hợp. Hướng an toàn hơn là:

1. dùng quy tắc cố định để điền các trường có thể suy ra chắc chắn;
2. dùng `benchmark-specification-designer` để đề xuất task và giải thích căn cứ;
3. dùng `learning-resource-curator` khi cần đề xuất mã học liệu;
4. lưu nhãn `model_suggested`, độ tin cậy, phiên bản agent/model và căn cứ nguồn;
5. chuyển trường không chắc chắn sang UET/HNMU xác nhận;
6. không để agent viết thêm hoặc sửa hội thoại, `answer` hay `gold_response`.

Chỉ nên tạo specialist mới nếu chạy thử cho thấy hai specialist hiện có không đáp ứng được hợp đồng đầu ra hoặc cần một quy trình gán nhãn hoàn toàn riêng.

### 5.6. Lượt gia sư HNMU làm phản hồi tham chiếu

Nhận định của người phụ trách dự án về KMP-Bench là đúng. KMP-Bench:

1. cắt hội thoại tại một lượt gia sư;
2. giữ lịch sử tới lượt học sinh ngay trước đó;
3. yêu cầu mô hình sinh phản hồi gia sư tiếp theo;
4. dùng lượt gia sư gốc đã bị cắt làm phản hồi tham chiếu;
5. so sánh phản hồi mô hình với phản hồi tham chiếu theo từng tiêu chí và kết luận Thắng/Hòa/Thua.

MathTutorBench cũng dùng phản hồi giáo viên làm đối chứng khi tính tỷ lệ thắng. TutorBench dùng phản hồi gia sư lý tưởng để hình thành rubric riêng cho từng mẫu, rồi chấm phản hồi mô hình theo rubric.

Do đó, các lượt gia sư trong hội thoại HNMU có thể được dùng làm phản hồi tham chiếu. Tuy nhiên:

- phản hồi tham chiếu không phải chuỗi văn bản duy nhất được coi là đúng;
- không dùng độ giống từ vựng làm thước đo chính;
- một phản hồi khác vẫn có thể tốt hơn hoặc tương đương nếu đáp ứng task và rubric;
- phản hồi tham chiếu cũng cần được kiểm tra chất lượng trước khi dùng;
- cần tách rõ `answer` với `gold_response`.

## 6. Việc nên làm tiếp theo

1. Chốt hợp đồng tiếp nhận dữ liệu thô: trường nguồn, cách ghi hội thoại, trường bắt buộc và quy tắc không sửa nội dung.
2. Viết đặc tả tách cấu trúc tối thiểu và quy tắc tạo ứng viên tại từng lượt gia sư.
3. Thiết kế hợp đồng đầu ra để agent đề xuất nhiệm vụ, điểm cắt, luận giải, bằng chứng và độ tin cậy.
4. Chạy hiệu chỉnh trên một nhóm mẫu thật và để UET/HNMU duyệt đề xuất.
5. Viết đặc tả ánh xạ đầy đủ vào phiếu tác giả sau khi nhiệm vụ được duyệt.
6. Thêm trường `answer` vào đặc tả phiên bản mới của phiếu tác giả, không sửa ngược bản đã chốt mà không có version.
7. Hoàn thiện nhiệm vụ và tiêu chí chấm, đặc biệt là cửa sổ quan sát của từng tiêu chí.
8. Xây bộ chuyển đổi, kiểm tra truy vết và đối chiếu từng ký tự với nguồn.
9. Viết giao thức thí nghiệm dựa trên ba nghiên cứu: mô hình, chỉ dẫn, phản hồi tham chiếu, số lần chạy, cách chấm, chỉ số tổng hợp và kiểm tra độ ổn định.

## 7. Kết luận vận hành

Điểm xoay lần này là hợp lý: HNMU tập trung vào chuyên môn và hội thoại sư phạm; UET chịu trách nhiệm kỹ thuật hóa dữ liệu và thiết kế benchmark. Tuy nhiên, cần giữ một ranh giới rất cứng: **chuyển đổi cấu trúc không được biến thành chỉnh sửa nội dung**. Bản gốc, bản ánh xạ, nhãn UET bổ sung và kết quả đánh giá phải là các lớp dữ liệu tách biệt và truy vết được.
