# Đặc tả v1 — Chấm mức độ cần thiết của sáu nguyên tắc sư phạm

Experiment: `20260727_170150`  
Phiên bản: `v1`  
Ngày khóa phương pháp: 27/07/2026  
Trạng thái: UET phê duyệt để pilot; ý nghĩa sư phạm cuối cùng chờ HNMU xác nhận

## 1. Mục tiêu đo

`requirement_score` trả lời:

> Để một phản hồi tiếp theo đáp ứng đúng nhu cầu quan sát được của học sinh
> trong payload này, nguyên tắc sư phạm đang xét cần thiết ở mức nào?

Đây là mức độ cần thiết của chức năng sư phạm, không phải:

- mức độ nguyên tắc xuất hiện trong `gold_response`;
- chất lượng thực thi một nguyên tắc;
- sở thích chiến lược của model;
- confidence tự khai.

## 2. Đơn vị và input

Đơn vị chấm là một `benchmark_candidate_id`. Mỗi candidate được chấm đúng
một lần trong một request chứa:

1. `benchmark_candidate_id`;
2. `sample_id`;
3. `grade`;
4. `lesson`;
5. `position`;
6. `bloom_level`;
7. `student_prompt`;
8. `conversation_history`;
9. `source_question`;
10. `gold_answer`.

`conversation_history` được code parse thành danh sách lượt có
`turn_index`, `role` và `content`. Input vật lý không chứa
`gold_response`, nhãn legacy hoặc lượt sau target response.

`gold_answer` là neo chuyên môn, không phải phản hồi gia sư mẫu và không
tự quyết định nguyên tắc sư phạm.

## 3. Thang điểm chung

| Điểm | Anchor chung |
|---:|---|
| 1 | Không phù hợp hoặc có nguy cơ làm lệch nhu cầu hiện tại. |
| 2 | Liên quan yếu/bề mặt; không tạo chức năng sư phạm độc lập. |
| 3 | Là chiến lược thay thế hợp lệ nhưng tình huống không bắt buộc phải dùng. |
| 4 | Rõ ràng nên có trong một phản hồi tốt cho tình huống này. |
| 5 | Chức năng cốt lõi; bỏ đi thì phản hồi không còn đáp ứng đúng nhu cầu chính. |

Code dẫn xuất:

- điểm `4`–`5` → `required_principle_set`;
- điểm `3` → `alternative_principle_set`;
- điểm `1`–`2` → không đưa vào instruction hoặc rubric riêng.

Model không tự áp threshold hoặc sinh hai tập trên.

## 4. Anchor theo từng nguyên tắc

### 4.1. `PRINCIPLE-CHALLENGE` — Thử thách

| Điểm | Diễn giải |
|---:|---|
| 1 | Tăng yêu cầu nhận thức lúc này sẽ làm lệch mục tiêu hoặc gây quá tải không cần thiết. |
| 2 | Có thể tạo chút nỗ lực nhưng thử thách không có chức năng riêng đối với nhu cầu trước mắt. |
| 3 | Một mở rộng hoặc trở ngại vừa sức là lựa chọn hợp lệ, nhưng phản hồi tốt không bắt buộc phải có. |
| 4 | Phản hồi tốt nên giữ lại một phần suy nghĩ có ý nghĩa để học sinh tự vượt qua. |
| 5 | Tạo hoặc duy trì thử thách vừa sức là mục tiêu cốt lõi; bỏ đi sẽ làm mất cơ hội học tập chính. |

### 4.2. `PRINCIPLE-EXPLANATION` — Giải thích

| Điểm | Diễn giải |
|---:|---|
| 1 | Giải thích thêm không liên quan hoặc cản trở bước cần làm ngay. |
| 2 | Kiến thức có liên quan nhưng chưa cần chức năng giải nghĩa độc lập. |
| 3 | Giải thích là một chiến lược hợp lệ bên cạnh hỏi hoặc làm mẫu. |
| 4 | Phản hồi tốt nên làm rõ một khái niệm, quan hệ, cách thức hoặc lý do đang gây vướng. |
| 5 | Nếu không giải thích ý cốt lõi, học sinh không thể sửa hiểu sai hoặc tiến lên đúng hướng. |

### 4.3. `PRINCIPLE-MODELLING` — Làm mẫu

| Điểm | Diễn giải |
|---:|---|
| 1 | Làm mẫu lúc này sẽ làm thay phần học sinh cần tự thực hiện hoặc không liên quan. |
| 2 | Một ví dụ bề mặt có thể hữu ích nhưng không cần trình diễn quy trình hay dòng suy nghĩ. |
| 3 | Làm mẫu là một lựa chọn hợp lệ bên cạnh giải thích hoặc hỏi gợi mở. |
| 4 | Phản hồi tốt nên trình diễn một phần quy trình, thao tác hoặc cách ra quyết định. |
| 5 | Học sinh đang thiếu mẫu thực hiện cốt lõi; không làm mẫu thì phản hồi không đáp ứng được nhu cầu chính. |

### 4.4. `PRINCIPLE-PRACTICE` — Luyện tập

| Điểm | Diễn giải |
|---:|---|
| 1 | Giao luyện tập ngay không phù hợp vì học sinh chưa có nền tảng hoặc đang cần xử lý một vấn đề khác. |
| 2 | Học sinh có thể thực hiện một thao tác, nhưng mục tiêu không phải làm vững kỹ năng. |
| 3 | Một hoạt động luyện ngắn là lựa chọn hợp lệ nhưng chưa bắt buộc. |
| 4 | Phản hồi tốt nên yêu cầu học sinh áp dụng hoặc thực hiện để kiểm tra/làm vững điều vừa học. |
| 5 | Việc học sinh tự thực hiện là mục tiêu cốt lõi; bỏ luyện tập thì không thể đạt mục tiêu lượt này. |

### 4.5. `PRINCIPLE-FEEDBACK` — Phản hồi

| Điểm | Diễn giải |
|---:|---|
| 1 | Không có câu trả lời, cách làm, thao tác hoặc sản phẩm của học sinh để nhận xét. |
| 2 | Chỉ có cơ sở cho xác nhận hoặc lời ghi nhận chung, chưa có đối tượng phản hồi rõ. |
| 3 | Có thể nhận xét một chi tiết, nhưng một chiến lược khác vẫn đáp ứng đầy đủ nhu cầu. |
| 4 | Phản hồi tốt nên nhận xét có căn cứ vào phần học sinh đã thể hiện và chỉ hướng cải thiện. |
| 5 | Đánh giá/sửa phần học sinh đã làm là nhu cầu chính; bỏ phản hồi thì lệch mục tiêu. |

### 4.6. `PRINCIPLE-QUESTIONING` — Đặt câu hỏi

| Điểm | Diễn giải |
|---:|---|
| 1 | Không cần thêm câu trả lời của học sinh; đặt câu hỏi sẽ trì hoãn hoặc làm lệch bước cần thiết. |
| 2 | Câu hỏi chỉ mang tính xã giao, kiểm tra bề mặt hoặc không tạo chức năng sư phạm riêng. |
| 3 | Hỏi là một chiến lược thay thế hợp lệ bên cạnh giải thích hoặc làm mẫu. |
| 4 | Phản hồi tốt nên đặt câu hỏi có mục đích để chẩn đoán hoặc giữ học sinh tiếp tục suy nghĩ. |
| 5 | Cần thông tin hoặc suy luận tiếp theo từ học sinh trước khi gia sư có thể hỗ trợ đúng; câu hỏi là cốt lõi. |

## 5. Quy tắc phân biệt trường hợp mơ hồ

1. **Có thể dùng không đồng nghĩa với bắt buộc.** Một nguyên tắc hợp lý
   nhưng có thể thay thế bằng nguyên tắc khác thường nhận điểm `3`.
2. **Nhiều điểm cao chỉ khi có nhiều chức năng bắt buộc đồng thời.** Không
   gán tràn để bao phủ bất định.
3. **Hình thức không đồng nghĩa với chức năng.** Có dấu hỏi không tự động
   là `Questioning`; có ví dụ không tự động là `Modelling`; có lời khen
   không tự động là `Feedback`.
4. **Không dùng `gold_answer` để suy chiến lược trực tiếp.** Nó chỉ khóa
   nội dung đúng.

## 6. Ví dụ biên tối thiểu

| Nguyên tắc | Tình huống | Điểm cao khi | Không chấm cao khi |
|---|---|---|---|
| Challenge | Học sinh đã làm đúng bước cơ bản và cần tiến sâu hơn. | Cần giữ một trở ngại vừa sức để học sinh tự suy luận. | Bài vốn khó nhưng học sinh đang cần gỡ một lỗi nền tảng. |
| Explanation | Học sinh nhầm quan hệ giữa điều kiện và thân vòng lặp. | Cần làm rõ vì sao vòng lặp không dừng. | Chỉ cần hỏi thêm đoạn mã hoặc giá trị biến còn thiếu. |
| Modelling | Học sinh chưa biết cách lần vết giá trị biến. | Cần trình diễn một phần bảng lần vết và cách quyết định. | Chỉ cần nêu khái niệm hoặc giao bài luyện. |
| Practice | Học sinh vừa hiểu cú pháp và cần tự áp dụng. | Cần học sinh viết/chạy một biến thể ngắn để làm vững kỹ năng. | Học sinh chưa hiểu khái niệm cốt lõi. |
| Feedback | Học sinh đã gửi mã hoặc nêu cách làm cụ thể. | Cần nhận xét đúng chi tiết làm tốt/sai và hướng sửa. | Chưa có sản phẩm hoặc suy luận nào được quan sát. |
| Questioning | Thiếu thông tin quyết định về trạng thái/chỗ sai. | Cần câu trả lời của học sinh trước khi hỗ trợ an toàn. | Gia sư đã đủ căn cứ và câu hỏi chỉ mang tính tu từ. |

## 7. Ranh giới model–code

Model chỉ:

- chấm sáu score;
- viết rationale/evidence tiếng Việt.

Code:

- validate input/output;
- áp threshold;
- dẫn xuất tập nguyên tắc;
- tạo review queue;
- so sánh run;
- tính metric, coverage và hash;
- quản lý retry/resume và publish.

## 8. Quyết định UET đã khóa

| Quyết định | Disposition |
|---|---|
| Một lượt grounding có cả `gold_answer` | approved |
| Không cung cấp `gold_response` khi chấm nguyên tắc | approved |
| Chấm đủ sáu nguyên tắc theo thang 1–5 | approved |
| Tập bắt buộc dùng threshold `>= 4`; tập thay thế dùng `== 3` | approved |
| Xử lý xác định phải dùng code | approved |
| System prompt và rationale/evidence dùng tiếng Việt | approved |
| Plan 01 có ba file output; pilot dùng bundle phẳng | approved |
| Codex chỉ cài Plan 02; người dùng tự thực hiện API run | approved |

## 9. Câu hỏi còn chờ HNMU

1. Sáu diễn giải nguyên tắc có phù hợp với môn Tin học THCS Việt Nam không?
2. Anchor nào cần thêm ví dụ theo dạng nội dung: khái niệm, mã lệnh, bảng
   tính, thao tác, đạo đức số và sản phẩm số?
3. Tổ hợp nguyên tắc bắt buộc nào không phù hợp với thực hành dạy học?

Các câu hỏi này không ngăn pilot phương pháp, nhưng ngăn việc gọi output
pilot là nhãn benchmark đã được chuyên gia xác nhận.
