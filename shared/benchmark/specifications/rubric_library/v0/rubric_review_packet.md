# Gói review bộ tiêu chí hai tầng — Plan 04

Trạng thái: `provisional — awaiting UET and HNMU review`  
Đơn vị đánh giá: một lượt phản hồi tiếp theo của gia sư Tin học THCS  
Pool ví dụ ưu tiên: 1.400 candidate `eligible_without_plan03_review`

## 1. Kết quả cần review

Thư viện hiện có:

- 1 nhiệm vụ chung;
- 4 tiêu chí chung áp dụng cho mọi mẫu;
- 18 tiêu chí riêng, gồm 3 tiêu chí cho mỗi một trong 6 nguyên tắc;
- 6 mã lỗi nghiêm trọng;
- ma trận truy vết cho toàn bộ 29 mục trên.

Một mẫu có tập nguyên tắc bắt buộc gồm `n` phần tử sẽ dùng:

```text
4 tiêu chí chung + 3 × n tiêu chí riêng
```

Đây là cấu trúc học từ KMP-Bench, không phải sao chép 22 tiêu chí của bài
báo. KMP-Bench không công bố đầy đủ nội dung của 22 tiêu chí, còn dự án
phải dùng sáu năng lực và học liệu Tin học THCS để viết lại các tiêu chí
có thể quan sát trong dữ liệu hiện tại.

## 2. Ba lớp phát biểu

### Bằng chứng

- KMP-Bench dùng bốn tiêu chí chung và ba tiêu chí cho mỗi nguyên tắc được
  kích hoạt; mỗi tiêu chí tạo phán quyết `Win/Tie/Lose`.
- MathTutorBench và TutorBench cho thấy phản hồi gia sư mở cần được đánh
  giá về chất lượng sư phạm, không chỉ độ giống đáp án tham chiếu.
- Mô hình sáu năng lực đã được UET cho phép tạm dùng làm nền rubric.
- Phương pháp HNMU yêu cầu chẩn đoán, hỗ trợ thích ứng, tránh gây thất
  vọng và rút dần hỗ trợ theo diễn biến học sinh.

### Suy luận thiết kế của dự án

- Bốn tiêu chí chung lần lượt kiểm: độ đúng, bám trạng thái, mức hỗ trợ và
  giao tiếp.
- `CAP-STRAT` được quan sát chủ yếu qua tiêu chí riêng của sáu nguyên tắc;
  không cần thêm một tiêu chí chung lặp lại “chọn đúng nguyên tắc”.
- `CAP-DIAG` chỉ được chấm khi phản hồi có bằng chứng về lỗi hoặc cần phân
  biệt nguyên nhân; nó xuất hiện trong Explanation, Modelling, Feedback
  và Questioning thay vì áp dụng bắt buộc cho mọi mẫu.
- Lỗi nghiêm trọng được xử lý trước phán quyết theo tiêu chí để điểm trung
  bình không che lấp sai kiến thức, làm thay hoặc nội dung có hại.

### Quyết định cần HNMU/UET

- HNMU xác nhận nội dung, ranh giới và ví dụ môn Tin học của từng tiêu chí.
- UET xác nhận cấu trúc dữ liệu, cách kích hoạt và phép chấm so sánh.
- Hành động cuối của sáu mã lỗi chưa được khóa.
- Chưa được gọi thư viện này là rubric đã kiểm định.

## 3. Ma trận năng lực–rubric

| Năng lực | Rubric quan sát chính | Điều không được suy ra |
|---|---|---|
| `CAP-ACC` | `RUB-GEN-ACC`; các tiêu chí nội dung của Explanation, Modelling, Practice, Feedback, Questioning | Học sinh đã hiểu hoặc sẽ làm đúng |
| `CAP-STATE` | `RUB-GEN-ALIGN`; `CHA-CALIB`; `EXP-ADAPT`; `PRA-ALIGN`; `FBK-GROUND`; `QUE-QUALITY/DEPEND` | Nguyên nhân sâu xa khi input không đủ bằng chứng |
| `CAP-STRAT` | Ba tiêu chí riêng của mỗi nguyên tắc; một phần `RUB-GEN-SCAFF` | Mức hỗ trợ đã vừa đủ chỉ vì tên chiến lược phù hợp |
| `CAP-SCAFF` | `RUB-GEN-SCAFF`; `CHA-AGENCY`; `EXP-ADAPT`; `MOD-TRANSFER`; `PRA-CONSOL`; `FBK-ACTION`; `QUE-DEPEND` | Rút dần hỗ trợ dài hạn nếu không có lịch sử |
| `CAP-DIAG` | `EXP-CORE`; `MOD-THINK`; `FBK-GROUND/DISC`; `QUE-PURPOSE` | Mọi câu trả lời sai đều có nguyên nhân chẩn đoán được |
| `CAP-CARE` | `RUB-GEN-COMM`; một phần `EXP-ADAPT` và `QUE-QUALITY` | Động lực, cảm xúc hoặc tiến bộ thật của học sinh |

Không có năng lực nào bị bỏ trống. Tuy nhiên, đây mới là kiểm độ phủ nội
dung, chưa phải bằng chứng rằng người chấm phân biệt được mọi tiêu chí.

## 4. Ranh giới quan trọng

### Explanation và Modelling

- Explanation làm rõ **điều gì hoặc vì sao**.
- Modelling biểu diễn **làm như thế nào**, gồm quy trình và điểm quyết
  định có thể quan sát.
- Một ví dụ chỉ thuộc Modelling khi nó thực sự trình diễn cách áp dụng;
  một danh sách bước không tự động là mẫu tốt.

### Practice và Challenge

- Practice nhằm củng cố khả năng áp dụng và làm độc lập.
- Challenge tạo nỗ lực nhận thức vượt lên mức thực hiện hiện tại.
- Một hoạt động có thể kích hoạt cả hai nếu vừa củng cố kỹ năng vừa yêu
  cầu suy luận mới; hai bộ tiêu chí vẫn chấm hai chức năng khác nhau.

### Feedback và Explanation

- Feedback bắt đầu từ chi tiết học sinh đã thể hiện và dẫn hướng cải thiện.
- Explanation có thể làm rõ kiến thức ngay cả khi học sinh chưa đưa bài
  làm.
- “Đúng rồi”, lời khen hoặc đưa đáp án thay thế không đủ là Feedback.

### Questioning và Challenge

- Questioning yêu cầu câu trả lời có chức năng sư phạm rõ.
- Challenge yêu cầu nỗ lực nhận thức đáng kể và vừa sức.
- Một câu hỏi chẩn đoán đơn giản có thể là Questioning nhưng không phải
  Challenge.

### `CAP-STATE` và `CAP-DIAG`

- STATE: học sinh đang ở đâu, đã làm gì và cần gì.
- DIAG: vì sao có lỗi, hiểu lầm hoặc bế tắc.

### `CAP-STRAT` và `CAP-SCAFF`

- STRAT: chọn phương tiện nào — hỏi, giải thích, làm mẫu, luyện tập hay
  phản hồi.
- SCAFF: điều tiết phương tiện đó ở mức nào, vào lúc nào và còn giữ phần
  việc nào cho học sinh.

## 5. Sáu ca biên để kiểm khả năng phân biệt

Các ca dưới đây dùng context thật trong pool 1.400, nhưng phản hồi đạt,
gần đạt và kém là anchor có kiểm soát. Chúng chưa phải nhãn chuyên gia.

### Challenge — `BC-HNMU-G6-R0181-STT12-AI08`

Học sinh vừa dùng `Replace All` sửa thành công 10 chỗ.

- Đạt: ghi nhận kết quả rồi yêu cầu dự đoán rủi ro khi từ cần thay là một
  phần của từ dài hơn và đề xuất cách kiểm tra trước khi thay toàn bộ.
- Gần đạt: chỉ giao thêm một từ khác để thay, không tạo suy luận mới.
- Kém: chỉ nói “Giỏi lắm!” hoặc giao một bài khó không liên quan.

Ca này cho thấy gold_response hiện tại có thể thua một response khác trên
tiêu chí Challenge; gold_response không phải đáp án duy nhất.

### Explanation — `BC-HNMU-G6-R0030-STT1-AI02`

Học sinh hỏi đơn vị nhỏ nhất để đo thông tin.

- Đạt: nêu `bit`, giải thích bit biểu diễn một trong hai trạng thái `0/1`
  và liên hệ trực tiếp tới cách máy tính biểu diễn thông tin.
- Gần đạt: chỉ trả lời “Bit”.
- Kém: trả lời sai đơn vị hoặc giải thích lẫn bit với byte.

### Modelling — `BC-HNMU-G7-R0166-STT11-AI02`

Học sinh biết chèn ảnh trong Word nhưng chưa tìm được thao tác ở
PowerPoint.

- Đạt: làm mẫu một đường thao tác cụ thể trên một slide, nêu điểm quyết
  định chọn nguồn ảnh, rồi để học sinh chèn ảnh tiếp theo.
- Gần đạt: liệt kê tên các nút nhưng không biểu diễn cách dùng trên một
  trường hợp.
- Kém: bảo học sinh “mò ở thẻ Insert” hoặc làm toàn bộ mà không chuyển
  giao.

### Practice — `BC-HNMU-G6-R0099-STT14-AI02`

Học sinh muốn tìm địa chỉ và số điện thoại của một bảo tàng Tin học.

- Đạt: yêu cầu học sinh tự tạo và thử một cụm từ khóa có cả hai mục tiêu,
  sau đó báo lại kết quả.
- Gần đạt: yêu cầu “em tìm thử đi” nhưng không nêu kỹ năng hoặc sản phẩm
  cần luyện.
- Kém: cung cấp luôn địa chỉ và số điện thoại nên học sinh không thực
  hành tìm kiếm.

### Feedback — `BC-HNMU-G6-R0145-STT4-AI04`

Học sinh nêu Google Docs là phần mềm soạn thảo ngoài Microsoft Word.

- Đạt: xác nhận Google Docs đúng là ví dụ, chỉ ra đặc điểm làm căn cứ và
  dẫn học sinh so sánh một điểm chung với LibreOffice.
- Gần đạt: chỉ nói “Đúng rồi!”.
- Kém: phủ nhận đáp án đúng hoặc khen nhưng chuyển sang nội dung khác.

### Questioning — `BC-HNMU-G6-R0057-STT14-AI02`

Máy in báo `Printer Offline`.

- Đạt: hỏi một dấu hiệu cụ thể như nguồn máy in hoặc trạng thái cáp, chờ
  câu trả lời rồi mới quyết định bước kiểm tra tiếp.
- Gần đạt: hỏi “em đã kiểm tra máy in chưa?” mà không nêu cần quan sát gì.
- Kém: đặt câu hỏi rồi tự trả lời và đưa luôn toàn bộ quy trình.

## 6. Cách chấm dự kiến

Plan 04 chỉ khóa nội dung tiêu chí, chưa khóa judge prompt. Hướng dự kiến
cho Plan 05:

1. công khai instruction và tập nguyên tắc bắt buộc cho tutor;
2. tạo response mô hình mà không cung cấp gold_response;
3. evaluator nhận cùng context, grounding, rubric và hai response;
4. áp cổng lỗi nghiêm trọng;
5. với từng rubric đang hoạt động, kết luận `Win`, `Tie` hoặc `Lose` và
   nêu bằng chứng;
6. giữ phán quyết từng tiêu chí riêng với phán quyết tổng thể.

Evaluator phải được phép kết luận response mô hình tốt hơn
gold_response. Thứ tự hai response phải được đảo hoặc kiểm soát ở thí
điểm để phát hiện thiên lệch vị trí.

UET đã khóa contract chống tính trùng:

- bốn rubric chung chỉ đo điều kiện nền của toàn bộ response;
- rubric riêng chỉ đo giá trị tăng thêm khi thực hiện nguyên tắc tương
  ứng, không chấm lại toàn bộ điều kiện nền;
- serious error là cổng quyết định, không phải rubric và không tạo điểm
  cộng/trừ riêng;
- mỗi error chỉ thực hiện đúng một `suggested_action`;
- `affected_rubric_ids` cho biết phạm vi cần xem và giải thích, nhưng
  không tự động làm tất cả rubric đó thành `Lose`;
- nếu `suggested_action` chỉ định rõ một rubric bị ép `Lose` hoặc giới hạn
  tổng thể, evaluator mới áp hành động đó;
- nếu một response thỏa hai error khác loại, ghi riêng hai error và áp
  action của từng loại một lần; không nhân số lần phạt theo số rubric bị
  ảnh hưởng.

## 7. Kết quả desk check ban đầu

Kiểm thủ công sáu context trên cho thấy:

- các anchor đạt/gần đạt/kém có thể được viết khác nhau trên cả sáu
  nguyên tắc;
- các ranh giới Explanation–Modelling, Practice–Challenge và
  Feedback–Questioning tạo phán quyết khác nhau thay vì chỉ đổi tên;
- một số gold_response trong pool eligible chỉ khen hoặc hỏi, nên không
  thể dùng eligibility Plan 03 làm bảo đảm chất lượng gold;
- Challenge và Practice ít mẫu nhưng vẫn có context để tạo pilot.

Đây chỉ là `inference` từ desk check, không phải bằng chứng về độ tin cậy,
khả năng phân biệt giữa mô hình hoặc mức chồng lấn thực nghiệm. Do hạn
thời gian, Plan 04 không chạy pilot. Plan 07 phải dùng response tốt,
trung bình và kém từ nhiều mô hình hoặc biến đổi có kiểm soát, rồi kiểm
việc các cặp rubric có dùng cùng bằng chứng và gần như luôn cho cùng
phán quyết hay không.

## 8. Câu hỏi UET cần quyết định

1. Có giữ đúng 4 tiêu chí chung và 3 tiêu chí cho mỗi nguyên tắc hay cần
   gộp tiêu chí nào trước khi gửi HNMU?
2. Thang vận hành chính có phải `Win/Tie/Lose` theo KMP-Bench không?
3. `ERR-NONRESPONSIVE` có phải lỗi nghiêm trọng hay chỉ là một lần Lose ở
   `RUB-GEN-ALIGN`?
4. HNMU sẽ review toàn bộ 22 tiêu chí hay review theo sáu nhóm nguyên tắc
   cùng các ca biên đại diện?

## 9. Câu hỏi HNMU cần xác nhận

1. Mỗi tiêu chí có đúng với hành vi gia sư Tin học THCS và đủ dễ hiểu cho
   giáo viên không?
2. Ví dụ nào còn sai hoặc thiếu sắc thái chuyên môn, thao tác phần mềm,
   mã lệnh hay đạo đức số?
3. Mức nào của sai chuyên môn, làm thay hoặc xác nhận hiểu lầm phải giới
   hạn phán quyết tổng thể?
4. Ranh giới Feedback với lời khen/xác nhận và Practice với một bước đang
   làm đã đủ rõ chưa?
5. Có tiêu chí quan trọng nào của gia sư Tin học bị thiếu nhưng không thể
   biểu diễn bằng 4 tiêu chí chung hoặc 18 tiêu chí riêng hiện tại không?
