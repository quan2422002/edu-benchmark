# Tổng hợp nền tảng đo lường cho Plan 03

## 1. Kết luận chính

Các nguồn phương pháp ủng hộ chuỗi thiết kế sau:

1. xác định năng lực gia sư cần đo;
2. mô tả nhiệm vụ như một hợp đồng đầu vào–đầu ra;
3. quy định bằng chứng quan sát được;
4. kiểm hiệu lực nội dung bằng quy trình chuyên gia có cấu trúc;
5. kiểm độ nhất quán giữa người chấm trước khi dùng nhãn con người làm chuẩn tham chiếu;
6. kiểm độ khó, khả năng phân biệt và hiệu ứng sàn/trần để tránh bộ mẫu dồn vào một đầu của phổ;
7. nếu dùng LLM chấm điểm, kiểm thiên lệch vị trí và độ nhạy của giao thức;
8. với phản hồi mở, không giả định một `gold_response` là cách trả lời hợp lệ duy nhất.

## 2. Các nhóm bằng chứng

### 2.1. Năng lực, nhiệm vụ và bằng chứng

Thiết kế lấy bằng chứng làm trung tâm xem đánh giá là quá trình suy luận từ kết quả thực hiện nhiệm vụ tới năng lực tiềm ẩn qua mô hình năng lực, nhiệm vụ và bằng chứng (`MTF-S001`). Vì vậy Plan 03 không nên bắt đầu bằng việc tái sử dụng hệ tiêu chí cũ rồi gắn ngược năng lực vào sau.

### 2.2. Hiệu lực đo lường

Nguồn về hiệu lực (`MTF-S002`) nhấn mạnh rằng hiệu lực là một lập luận dựa trên nhiều nhóm bằng chứng. Rà soát nội dung của chuyên gia là cần thiết nhưng chưa đủ; dự án còn phải xét quá trình chấm, cấu trúc điểm, quan hệ với các biến khác và hệ quả sử dụng.

### 2.3. Độ nhất quán giữa người chấm

Các nguồn `MTF-S003` và `MTF-S004` yêu cầu phân biệt tỷ lệ đồng thuận với chỉ số có hiệu chỉnh ngẫu nhiên, đồng thời chọn chỉ số theo kiểu dữ liệu và thiết kế chấm. Dự án phải báo rõ ai chấm, chấm dữ liệu nào, dùng thang gì và xử lý bất đồng ra sao.

### 2.4. Phân tích mẫu đánh giá

Các nguồn `MTF-S005` và `MTF-S006` cho thấy số lượng mẫu lớn chưa bảo đảm khả năng đo tốt. Bộ mẫu cần phủ dải chất lượng, tránh hiệu ứng sàn/trần và được kiểm tra khả năng phân biệt sau thí điểm.

### 2.5. LLM chấm điểm

Các nguồn `MTF-S007` và `MTF-S008` chỉ ra thiên lệch vị trí cùng độ nhạy của so sánh theo cặp. Nếu dùng LLM chấm điểm, dự án phải đảo hoặc cân bằng thứ tự, kiểm độ nhạy giao thức và không coi kết quả mô hình là quyết định chuyên gia cuối cùng.

### 2.6. Phản hồi tham chiếu không duy nhất

Các nguồn `MTF-S009`–`MTF-S012` cho thấy phản hồi mở có thể có nhiều cách trả lời đúng, nhiều mức chi tiết và ít trùng từ. Vì vậy:

- `gold_response` là một mốc hoặc ví dụ tốt, không phải câu trả lời duy nhất;
- ưu tiên theo cặp không nên mặc định là điểm chính;
- nếu dựa trên phản hồi tham chiếu, cần cân nhắc nhiều cách trả lời hợp lệ hoặc tập mốc chẩn đoán.

### 2.7. Ranh giới giữa lựa chọn chiến lược và dàn giáo

Van de Pol và cộng sự (2010, `MTF-S013`) phân biệt các **phương tiện hỗ trợ** như hỏi, giải thích, làm mẫu, phản hồi, hướng dẫn và gợi ý với những đặc trưng khiến hỗ trợ trở thành dàn giáo thích ứng: điều chỉnh theo năng lực hiện tại, rút dần hỗ trợ và chuyển giao trách nhiệm. Do đó:

- `CAP-STRAT` đo gia sư chọn phương tiện hoặc chức năng sư phạm nào cho mục tiêu trước mắt;
- `CAP-SCAFF` đo gia sư điều tiết phương tiện đó bao nhiêu, vào thời điểm nào và giữ lại bao nhiêu quyền chủ động cho học sinh.

Tương tự, `CAP-STATE` mô tả học sinh đang ở đâu và cần gì, còn `CAP-DIAG` giải thích nguyên nhân của lỗi, hiểu lầm hoặc bế tắc. Chẩn đoán là công cụ để đạt tính thích ứng, không phải đồng nghĩa với việc đọc trạng thái. Với ứng viên một lượt, chỉ nên đánh giá điều tiết cục bộ; rút dần và chuyển giao dài hạn cần bằng chứng nhiều lượt. Hai cặp này phải được kiểm định bằng ví dụ đối chứng trước khi cân nhắc gộp.

## 3. Hàm ý cho các Workstream tiếp theo

- Workstream B giữ mô hình năng lực tách khỏi hệ thống nhiệm vụ và tiêu chí.
- Các cặp `STATE–DIAG` và `STRAT–SCAFF` được giữ tạm như cặp cần kiểm định ranh giới, không coi là ứng viên gộp.
- Gói HNMU phải hỏi riêng về mức phù hợp, đầy đủ, rõ ràng và chồng lấn của từng năng lực.
- Hiệu chỉnh người chấm phải phân biệt bất đồng do cách diễn đạt tiêu chí, cách hiểu và ranh giới nhiệm vụ.
- Thí điểm LLM chấm điểm chỉ là công cụ kiểm tra hỗ trợ và phải đối chiếu với người chấm.
- Phản hồi tham chiếu nên được quản trị như một tập cách trả lời hợp lệ hoặc tập mốc chẩn đoán khi dữ liệu cho thấy cần thiết.

## 4. Câu hỏi còn mở

1. Ngưỡng đồng thuận phù hợp cho người chấm phản hồi gia sư Tin học THCS tiếng Việt là bao nhiêu?
2. So sánh theo cặp có đủ ổn định để làm điểm chính trong miền này hay không?
3. Mỗi nhóm nhiệm vụ cần bao nhiêu cách trả lời hợp lệ thay thế cho `gold_response`?
4. Phân bố độ khó và khả năng phân biệt của 2.028 mẫu ứng viên hiện tại ra sao?

## 5. Kết luận vận hành

Nguyên tắc trung tâm là:

> Xác định năng lực trước, xây nhiệm vụ sau, rồi mới định nghĩa bằng chứng và cách chấm.

`gold_response` được dùng thận trọng như mốc tham chiếu, ví dụ hoặc nguồn biên soạn tiêu chí; không mặc định là đáp án duy nhất cho mọi phản hồi mở.
