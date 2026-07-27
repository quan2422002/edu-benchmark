# Sổ tay khám phá hệ thống nhiệm vụ — Cổng C1

Trạng thái: **chờ đại diện UET duyệt trước lô hiệu chỉnh đầu tiên**.  
Ngày cập nhật: 26/07/2026.  
Phạm vi: tám nhiệm vụ hạt giống, chưa phải hệ thống nhiệm vụ cuối và chưa được HNMU xác nhận.

## 1. Mục đích của sổ tay

Sổ tay giúp AI và đại diện UET trả lời cùng một câu hỏi: trong bối cảnh đã cho, **lượt phản hồi tiếp theo của gia sư phải thực hiện nhiệm vụ sư phạm chính nào**?

Mỗi ứng viên được mô tả bằng hợp đồng:

```text
student_state + primary_tutoring_goal + required_response_evidence
```

- `student_state`: trạng thái học sinh quan sát được từ câu hỏi và lịch sử.
- `primary_tutoring_goal`: mục tiêu sư phạm chính của lượt phản hồi tiếp theo.
- `required_response_evidence`: dấu hiệu tối thiểu phải nhìn thấy trong chính phản hồi để kết luận gia sư đã thực hiện nhiệm vụ.

`required_response_evidence` **không phải** cột `evidence_fragment_ids` của kiểm tra hội thoại thô. Cột cũ truy vết đoạn học liệu được tác nhân kiểm tra ở giai đoạn 1; trường trong Workstream C mô tả hành vi có thể quan sát ở phản hồi cần đánh giá. Hai loại bằng chứng có mục đích và đơn vị khác nhau.

## 2. Quy tắc mã hóa chung

1. Đọc `student_prompt` và toàn bộ `conversation_history`.
2. Chỉ mô tả điều có thể quan sát về học sinh; không tự suy nguyên nhân.
3. Xác định một mục tiêu chính: nếu phản hồi không đạt mục tiêu này thì cuộc học chưa thể tiến đúng hướng.
4. Viết dấu hiệu tối thiểu cần có trong phản hồi mà không sao chép câu chữ của `gold_response`.
5. Chọn một nhiệm vụ chính. Ghi các hành động khác vào `secondary_pedagogical_moves`.
6. Nếu thiếu ngữ cảnh đến mức không thể viết hợp đồng, không ép nhãn; ghi `unclassifiable_reason`.
7. Không dùng lớp, bài học, mức nhận thức, độ dài lịch sử hay hình thức câu hỏi làm nhãn nhiệm vụ.

`gold_response` là phản hồi tham chiếu và một nguồn giúp hiểu ý định của mẫu. Nó không phải cách trả lời hợp lệ duy nhất và không được ghi đè trạng thái học sinh, học liệu hoặc `gold_answer`.

## 3. Căn cứ nghiên cứu và giới hạn suy luận

| Nhiệm vụ hạt giống | Nguồn hỗ trợ | Nội dung thực sự được nguồn hỗ trợ | Giới hạn |
|---|---|---|---|
| `TASK-PROBE` | `TR-P001`, `TR-P002`, `TR-P003` | Hiểu trạng thái học sinh và đặt câu hỏi là hành vi quan trọng; nhiệm vụ benchmark cần hợp đồng đầu vào–đầu ra (`TR-C001`, `TR-C006`, `TR-C011`). | Không bài báo nào xác nhận trực tiếp “thăm dò” phải là một nhiệm vụ riêng trong dữ liệu này. |
| `TASK-EXPLAIN` | `TR-P001`, `TR-P002`, `TR-P003` | KMP-Bench có nguyên tắc giải thích; TutorBench có tình huống giải thích thích ứng; MathTutorBench tách các hợp đồng phản hồi gia sư. | Các cấu trúc nguồn không đồng nhất; tên nhiệm vụ hiện tại là giả thuyết tổng hợp. |
| `TASK-ASSESS` | `TR-P001`, `TR-P002`, `TR-P003` | KMP-Bench có nguyên tắc phản hồi; TutorBench có tình huống đánh giá và phản hồi; MathTutorBench tách nhận diện lỗi với sinh phản hồi. | Cần dữ liệu xác định “đánh giá” có tiêu chí riêng so với “củng cố”. |
| `TASK-DIAG` | `TR-P001`, `TR-P002`, `MTF-S013` | Nghiên cứu phân biệt hiểu trạng thái, phát hiện lỗi và điều chỉnh hỗ trợ; KMP-Skills có nhiệm vụ chẩn đoán cấu trúc (`TR-C010`); dàn giáo thích ứng bắt đầu bằng chẩn đoán. | `TR-C023` cảnh báo chẩn đoán trong phản hồi mở có thể chỉ là hành vi phụ. Đây là quyết định trọng yếu của UET. |
| `TASK-SCAFFOLD` | `TR-P001`, `TR-P002`, `TR-P003`, `MTF-S013` | MathTutorBench có sinh phản hồi dàn giáo; các nghiên cứu nhấn mạnh hỗ trợ thích ứng và bảo toàn phần việc của học sinh. | Phải tách “chọn cách hỗ trợ” khỏi “lượng hỗ trợ”, và không suy fading dài hạn từ một lượt. |
| `TASK-MODEL` | `TR-P001`, `TR-P002` | KMP-Bench coi làm mẫu là một nguyên tắc sư phạm; nhiệm vụ cần bằng chứng đầu ra phân biệt. | Làm mẫu có thể chỉ là chiến lược bên trong giải thích hoặc dàn giáo nếu không có hợp đồng riêng. |
| `TASK-PRACTICE` | `TR-P001`, `TR-P002` | KMP-Bench phân biệt luyện tập và thử thách; một lượt có thể cần nguyên tắc áp dụng riêng. | Chưa có bằng chứng dữ liệu rằng đây là bối cảnh đủ phổ biến trong 2.028 ứng viên. |
| `TASK-CONSOLIDATE` | `TR-P001`, `TR-P002`, `MTF-S013` | Phản hồi, chuyển giao trách nhiệm và rút hỗ trợ là thành phần của gia sư tốt. | Chỉ được chấm dấu hiệu chuyển giao trong lượt hiện tại, không suy kết quả học tập dài hạn. |

Các nguồn trên tạo **hạt giống có căn cứ**, không chứng minh tám nhãn là hệ thống nhiệm vụ đúng cho dữ liệu Tin học THCS. Việc giữ, gộp, tách hoặc chuyển thành hành vi phụ phải dựa thêm vào dữ liệu và quyết định của UET/HNMU.

## 4. Tám nhiệm vụ hạt giống

### 4.1. `TASK-PROBE` — Tiếp nhận và thăm dò trạng thái

**Bao gồm khi**

- thiếu một dữ kiện có thể làm thay đổi đáng kể cách hỗ trợ;
- mục tiêu chính là làm rõ ý định, mức hiểu, điều đã thử hoặc điểm vướng;
- câu hỏi tốt phải hẹp và có giá trị quyết định.

**Loại trừ khi**

- đã có lỗi cụ thể và mục tiêu là tìm nguyên nhân: xem `TASK-DIAG`;
- đã đủ dữ kiện để giải thích hoặc dàn giáo;
- chỉ hỏi xã giao “em hiểu chưa?” mà không giảm bất định liên quan.

**Ví dụ đạt**

Ứng viên `BC-HNMU-G6-R0044-STT1-AI02`: học sinh cho rằng mạng máy tính chỉ gồm các máy nối dây. Một phản hồi phù hợp cần hỏi về thiết bị không dây hoặc ví dụ mạng em đã dùng để xác định phạm vi hiểu biết trước khi sửa.

**Phản ví dụ**

Gia sư lập tức giảng toàn bộ định nghĩa mạng máy tính. Phản hồi có thể đúng chuyên môn nhưng chưa kiểm giả thuyết của học sinh và bỏ qua mục tiêu thăm dò.

### 4.2. `TASK-EXPLAIN` — Giải thích và kiến tạo hiểu biết

**Bao gồm khi**

- đích chính là hiểu khái niệm, quan hệ hoặc nguyên lý;
- phản hồi cần làm rõ “vì sao” hoặc nối biểu diễn hiện có với ý cốt lõi;
- cách trình bày phải điều chỉnh theo dấu hiệu về mức hiểu.

**Loại trừ khi**

- học sinh đang làm một sản phẩm cụ thể và chỉ cần bước tiếp theo: `TASK-SCAFFOLD`;
- cần quan sát một quy trình mẫu hoàn chỉnh: xem `TASK-MODEL`;
- học sinh đã hiểu đúng và chỉ cần làm vững: `TASK-CONSOLIDATE`.

**Ví dụ đạt**

Ứng viên `BC-HNMU-G6-R0048-STT5-AI04`: học sinh đã nghĩ tới USB nhưng chưa khái quát lợi ích dùng chung tài nguyên qua mạng. Phản hồi cần nối ví dụ máy in dùng chung với quan hệ “kết nối mạng → chia sẻ tài nguyên”.

**Phản ví dụ**

“Mạng máy tính là các máy tính kết nối với nhau.” Câu này nêu định nghĩa nhưng không xử lý biểu diễn hiện có của học sinh và chưa làm rõ lợi ích đang được hỏi.

### 4.3. `TASK-ASSESS` — Đánh giá bài làm và phản hồi

**Bao gồm khi**

- đầu vào đã có câu trả lời, mã lệnh, thao tác hoặc sản phẩm;
- mục tiêu chính là cho biết phần đúng, chưa đúng hoặc mức đạt;
- phán đoán phải gắn với chi tiết quan sát được.

**Loại trừ khi**

- mục tiêu là tìm nguyên nhân gốc của lỗi: xem `TASK-DIAG`;
- phần làm đã đúng và mục tiêu chính là yêu cầu khái quát hoặc áp dụng gần: `TASK-CONSOLIDATE`;
- phản hồi chỉ có lời khen.

**Ví dụ đạt**

Ứng viên `BC-HNMU-G6-R0173-STT4-AI06`: học sinh suy ra `Replace All` thay tất cả kết quả cùng lúc. Phản hồi cần xác nhận chính chi tiết đó và, nếu cần, nhắc điều kiện kiểm tra trước khi thay hàng loạt.

**Phản ví dụ**

“Tuyệt vời, em giỏi lắm!” Không có căn cứ nào cho biết phần nào đúng hoặc học sinh nên giữ chú ý ở đâu.

### 4.4. `TASK-DIAG` — Chẩn đoán hiểu sai hoặc thiếu nền tảng

**Bao gồm khi**

- có lỗi hoặc bế tắc cụ thể;
- nguyên nhân chưa rõ;
- phản hồi tốt phải phân biệt hoặc kiểm tra nguyên nhân trước khi sửa.

**Loại trừ khi**

- chỉ thiếu thông tin chung về nhu cầu: `TASK-PROBE`;
- chỉ cần nhận xét sản phẩm đúng/sai: `TASK-ASSESS`;
- nguyên nhân đã rõ và mục tiêu là đưa bước tự sửa: `TASK-SCAFFOLD`.

**Ví dụ đạt**

Học sinh nói vòng lặp chạy mãi dù đã đặt điều kiện dừng. Phản hồi hỏi biến điều khiển có được cập nhật trong thân vòng lặp không, hoặc yêu cầu đối chiếu giá trị biến trước và sau một lượt. Câu hỏi này phân biệt được nguyên nhân thay vì đoán.

**Phản ví dụ**

“Em hãy thêm điều kiện dừng.” Phản hồi sửa bề mặt nhưng chưa xác định vì sao điều kiện hiện có không hoạt động.

**Câu hỏi bắt buộc cho UET**

Trường hợp này có đủ hợp đồng và tiêu chí riêng để giữ `TASK-DIAG`, hay “chẩn đoán” nên là hành vi phụ trong `TASK-ASSESS`/`TASK-SCAFFOLD` đối với phản hồi mở?

### 4.5. `TASK-SCAFFOLD` — Dàn giáo giải quyết vấn đề

**Bao gồm khi**

- học sinh đang làm một nhiệm vụ cụ thể;
- có thể xác định bước tiếp theo vừa đủ;
- phản hồi phải giữ lại phần việc có ý nghĩa cho học sinh.

**Loại trừ khi**

- đích chính là hiểu khái niệm: `TASK-EXPLAIN`;
- quan sát mẫu hoàn chỉnh là bắt buộc: `TASK-MODEL`;
- phản hồi làm thay toàn bộ.

**Ví dụ đạt**

Ứng viên `BC-HNMU-G6-R0181-STT12-AI02`: học sinh cần sửa “Sapa” thành “Sa Pa” trong cả bài. Phản hồi chỉ dẫn mở `Replace`, rồi hỏi em sẽ nhập chuỗi sai vào ô nào; các bước sau vẫn để học sinh thực hiện.

**Phản ví dụ**

Gia sư liệt kê trọn quy trình, điền sẵn cả hai ô và yêu cầu bấm `Replace All`. Phản hồi giải quyết việc trước mắt nhưng lấy mất phần suy nghĩ/thao tác cần đánh giá.

### 4.6. `TASK-MODEL` — Làm mẫu hoặc minh họa quy trình

**Bao gồm khi**

- học sinh chưa có mô hình thực hiện;
- việc quan sát một mẫu là phương tiện chính để tiến lên;
- phản hồi phải làm lộ bước hoặc quyết định cốt lõi rồi chuyển giao.

**Loại trừ khi**

- một gợi ý đơn lẻ đủ để học sinh tiếp tục: `TASK-SCAFFOLD`;
- ví dụ chỉ minh họa một khái niệm: thường là `TASK-EXPLAIN`;
- mẫu không có cơ hội để học sinh tự làm tiếp.

**Ví dụ đạt**

Học sinh đề nghị xem một lần cách tính trung bình của ba số trong Scratch. Gia sư làm mẫu với ba biến khác, giải thích vì sao phải cộng trước rồi chia cho 3, sau đó yêu cầu học sinh tự thay bằng dữ liệu của bài.

**Phản ví dụ**

“Em tạo ba biến rồi thử tiếp nhé.” Đây là gợi ý dàn giáo, chưa phải một quy trình mẫu.

### 4.7. `TASK-PRACTICE` — Tạo luyện tập hoặc thử thách

**Bao gồm khi**

- học sinh đã có nền tảng ban đầu;
- mục tiêu là luyện, kiểm tra chuyển giao hoặc tăng độ khó;
- phản hồi tạo một nhiệm vụ mới, không phải bước còn thiếu của nhiệm vụ hiện tại.

**Loại trừ khi**

- câu hỏi chỉ giúp hoàn thành bài đang làm: `TASK-SCAFFOLD`;
- áp dụng rất gần chỉ nhằm làm vững ý vừa học: `TASK-CONSOLIDATE`;
- nhiệm vụ mới không bám mục tiêu hoặc quá khó.

**Ví dụ đạt**

Sau khi học sinh đã viết được điều kiện kiểm tra số dương, gia sư giao bài mới: phân loại một số là âm, bằng 0 hay dương mà chưa đưa lời giải, đồng thời nêu rõ đầu ra cần in.

**Phản ví dụ**

Trong lúc học sinh còn chưa hoàn thành điều kiện đầu tiên, gia sư giao thêm một chương trình phức tạp hơn. Đây là tăng tải, không phải luyện tập thích ứng.

### 4.8. `TASK-CONSOLIDATE` — Củng cố và chuyển giao

**Bao gồm khi**

- học sinh vừa thể hiện hiểu đúng hoặc hoàn thành một bước;
- mục tiêu là ổn định, khái quát hoặc yêu cầu áp dụng rất gần;
- phản hồi chuyển việc diễn đạt/thực hiện trở lại cho học sinh.

**Loại trừ khi**

- chỉ cần phán đoán chất lượng bài làm: `TASK-ASSESS`;
- tạo một bài mới đáng kể: `TASK-PRACTICE`;
- chỉ khen hoặc kết thúc xã giao.

**Ví dụ đạt**

Ứng viên `BC-HNMU-G7-R0186-STT3-AI08`: sau khi học sinh đã nhận ra hai điều kiện dừng của tìm kiếm tuần tự, phản hồi yêu cầu em tự tóm tắt lại cả hai điều kiện bằng lời của mình.

**Phản ví dụ**

“Đúng rồi, tốt lắm!” Không có hành động làm vững hoặc chuyển giao nào có thể quan sát.

## 5. Quy tắc ranh giới dễ nhầm

| Cặp | Câu hỏi quyết định | Nhãn thứ nhất khi | Nhãn thứ hai khi |
|---|---|---|---|
| `PROBE–DIAG` | Đang thiếu dữ kiện về trạng thái, hay đang kiểm nguyên nhân của một lỗi cụ thể? | `PROBE`: chưa đủ dữ kiện để chọn hỗ trợ. | `DIAG`: có lỗi cụ thể và cần phép kiểm nguyên nhân. |
| `EXPLAIN–SCAFFOLD` | Đích chính là hiểu quan hệ hay hoàn thành bước tiếp theo? | `EXPLAIN`: nếu bỏ phần giải nghĩa thì mục tiêu thất bại. | `SCAFFOLD`: nếu không có bước vừa đủ thì học sinh không đi tiếp nhiệm vụ. |
| `EXPLAIN–MODEL` | Ví dụ dùng để soi sáng khái niệm hay quan sát một quy trình? | `EXPLAIN`: ví dụ có thể thay bằng cách giải thích tương đương. | `MODEL`: quy trình/sản phẩm mẫu là bằng chứng bắt buộc. |
| `ASSESS–DIAG` | Cần biết bài làm đang đúng ở đâu hay vì sao lỗi xảy ra? | `ASSESS`: phán đoán chất lượng là mục tiêu trung tâm. | `DIAG`: phân biệt nguyên nhân là mục tiêu trung tâm. |
| `ASSESS–CONSOLIDATE` | Cần phán đoán hay làm vững điều vừa đúng? | `ASSESS`: học sinh cần biết chất lượng hiện tại. | `CONSOLIDATE`: phần đúng đã rõ và cần khái quát/chuyển giao. |
| `SCAFFOLD–MODEL` | Một gợi ý có đủ không, hay học sinh cần quan sát mẫu? | `SCAFFOLD`: giữ lại phần việc chính cho học sinh. | `MODEL`: trình diễn mẫu là phương tiện chính, sau đó mới chuyển giao. |
| `PRACTICE–CONSOLIDATE` | Đang mở nhiệm vụ mới hay áp dụng rất gần để làm vững? | `PRACTICE`: nhiệm vụ mới có mục tiêu luyện/chuyển giao. | `CONSOLIDATE`: bước ngắn nối trực tiếp với điều vừa hình thành. |

Hình thức bề mặt không quyết định nhãn. Một câu hỏi có thể phục vụ thăm dò, chẩn đoán, giải thích, dàn giáo hoặc củng cố; phải xét trạng thái, mục tiêu và bằng chứng đáp ứng.

## 6. Trường hợp chưa phân loại

Chỉ để `unclassifiable` khi không thể viết hợp đồng có căn cứ, chẳng hạn:

- nội dung đa phương thức bị thiếu nên không biết học sinh muốn đánh giá sản phẩm nào;
- câu hỏi và lịch sử mâu thuẫn đến mức không xác định được nhiệm vụ tiếp theo;
- xuất hiện một bối cảnh có mục tiêu và bằng chứng riêng nhưng chưa có nhãn phù hợp.

**Ví dụ**

`student_prompt`: “Thầy xem hình em gửi và chỉ chỗ sai giúp em.” Không có hình, lịch sử hoặc mô tả sản phẩm. Không ép vào `TASK-PROBE` hay `TASK-ASSESS`; ghi thiếu đầu vào cần thiết. Nếu ảnh được bổ sung, ứng viên có thể trở thành `TASK-ASSESS` hoặc `TASK-DIAG` tùy mục tiêu.

Không dùng `unclassifiable` chỉ vì người mã hóa phân vân giữa hai nhãn. Khi đó phải áp dụng bảng ranh giới, ghi cả hai giả thuyết và chuyển vào hàng đợi UET.

## 7. Quyền chủ động và các hành vi phụ

Quyền chủ động hiện là yêu cầu xuyên suốt, đặc biệt trong `TASK-SCAFFOLD`, `TASK-MODEL`, `TASK-PRACTICE` và `TASK-CONSOLIDATE`; chưa phải một nhiệm vụ riêng. Các hành vi như hỏi gợi mở, giải thích ngắn, xác nhận, khích lệ hoặc đưa ví dụ được ghi là `secondary_pedagogical_moves` khi chúng không phải mục tiêu chính.

Workstream D sẽ quyết định yêu cầu nào trở thành tiêu chí chung và yêu cầu nào là tiêu chí theo nhiệm vụ. Workstream C không chấm chất lượng phản hồi.

## 8. Trạng thái dữ liệu và điều kiện mở lô đầu

- Thống kê 2.028 ứng viên và mẫu khám phá 160 ứng viên đã được tạo xác định.
- Hai mươi nhãn cũ trong `specialist_draft/task_discovery/task_discovery_annotations.csv` là bản thử trước cổng C1. Chúng không được tính là mã hóa chính thức, không được dùng để báo độ phủ và không được đưa vào kết quả hiệu chỉnh.
- Số ứng viên đã mã hóa chính thức tại cổng này: **0**.
- Chỉ sau khi đại diện UET duyệt hoặc yêu cầu sửa xong sổ tay, AI mới được mã hóa lô 40 đầu tiên với `coder_id = AI-CODER-01`.

## 9. Quyết định cần đại diện UET đưa ra

1. Từng nhiệm vụ hạt giống có đủ rõ để dùng trong lô 40 đầu tiên không?
2. `TASK-DIAG`, `TASK-MODEL` và `TASK-PRACTICE` nên được giữ như nhiệm vụ hạt giống riêng hay chuyển thành hành vi phụ cho tới khi có bằng chứng dữ liệu?
3. Bảy quy tắc ranh giới có cho phép chọn một mục tiêu chính mà không dựa vào `gold_response` không?
4. Ví dụ và phản ví dụ có đúng ý nghĩa Tin học THCS không?
5. Có cho phép mở Bước C2 và mã hóa chính thức lô 40 đầu tiên không?
