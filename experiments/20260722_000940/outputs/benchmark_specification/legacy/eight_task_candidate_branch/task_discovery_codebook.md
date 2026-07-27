# Sổ tay khám phá hệ thống nhiệm vụ — Cổng C1

Trạng thái: **chờ đại diện UET duyệt trước lô hiệu chỉnh đầu tiên**.
Ngày cập nhật: 26/07/2026.
Phạm vi: tám nhiệm vụ hạt giống, chưa phải hệ thống nhiệm vụ cuối và chưa được HNMU xác nhận.

## 1. Mục đích và hợp đồng nhiệm vụ

Sổ tay giúp AI và đại diện UET xác định nhiệm vụ sư phạm chính của lượt phản hồi tiếp theo. Mỗi ứng viên được mô tả bằng:

```text
student_state + primary_tutoring_goal + required_response_evidence
```

- `student_state`: trạng thái học sinh quan sát được từ câu hỏi và lịch sử.
- `primary_tutoring_goal`: mục tiêu sư phạm chính của lượt phản hồi tiếp theo.
- `required_response_evidence`: dấu hiệu tối thiểu phải nhìn thấy trong chính phản hồi để kết luận gia sư đã thực hiện nhiệm vụ.

`required_response_evidence` không phải `evidence_fragment_ids` của kiểm tra hội thoại thô. Cột cũ truy vết đoạn học liệu ở giai đoạn 1; trường trong Workstream C mô tả hành vi có thể quan sát ở phản hồi cần đánh giá.

## 2. Quy tắc mã hóa

1. Đọc `student_prompt` và toàn bộ `conversation_history`.
2. Chỉ mô tả điều có thể quan sát; không tự suy nguyên nhân.
3. Chọn một mục tiêu chính mà nếu không đạt thì cuộc học chưa thể tiến đúng hướng.
4. Viết dấu hiệu tối thiểu cần có mà không sao chép `gold_response`.
5. Chọn một nhiệm vụ chính; ghi hành động phụ vào `secondary_pedagogical_moves`.
6. Nếu thiếu ngữ cảnh đến mức không thể viết hợp đồng, ghi `unclassifiable_reason`.
7. Không dùng lớp, bài, mức nhận thức, độ dài lịch sử hay hình thức câu hỏi làm nhãn.

`gold_response` là phản hồi tham chiếu, không phải cách trả lời hợp lệ duy nhất.

## 3. Căn cứ và giới hạn


| Nhiệm vụ         | Căn cứ chính                                                                                          | Giới hạn cần UET kiểm                                                                 |
| ------------------ | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `TASK-PROBE`       | `TR-P001`, `TR-P002`, `TR-P003`: hiểu học sinh, đặt câu hỏi và hợp đồng nhiệm vụ             | Chưa có bằng chứng trực tiếp rằng thăm dò là nhiệm vụ riêng trong tập này. |
| `TASK-EXPLAIN`     | KMP-Bench: giải thích; TutorBench: giải thích thích ứng                                            | Tên hiện tại là tổng hợp từ các cấu trúc không đồng nhất.                   |
| `TASK-ASSESS`      | KMP-Bench: phản hồi; TutorBench: đánh giá và phản hồi                                            | Cần tách ổn định với củng cố và chẩn đoán.                                    |
| `TASK-DIAG`        | MathTutorBench/KMP-Skills: phát hiện, chẩn đoán lỗi;`MTF-S013`: chẩn đoán trước điều chỉnh | `TR-C023` cho thấy chẩn đoán có thể chỉ là hành vi phụ trong phản hồi mở.    |
| `TASK-SCAFFOLD`    | MathTutorBench: sinh dàn giáo;`MTF-S013`: hỗ trợ thích ứng                                         | Không suy việc rút hỗ trợ dài hạn từ một lượt.                                 |
| `TASK-MODEL`       | KMP-Bench: làm mẫu/mô hình hóa                                                                      | Có thể chỉ là chiến lược của giải thích hoặc dàn giáo.                       |
| `TASK-PRACTICE`    | KMP-Bench: luyện tập và thử thách                                                                   | Chưa biết độ phủ trong 2.028 ứng viên.                                             |
| `TASK-CONSOLIDATE` | Phản hồi, chuyển giao trách nhiệm và rút hỗ trợ                                                 | Chỉ chấm dấu hiệu trong lượt hiện tại.                                            |

Nguồn tạo hạt giống, không chứng minh tám nhãn là hệ thống nhiệm vụ cuối.

## 4. Định nghĩa, điều kiện và ví dụ

### `TASK-PROBE` — Tiếp nhận và thăm dò trạng thái

- Bao gồm: thiếu dữ kiện có thể làm thay đổi cách hỗ trợ; cần hỏi hẹp về ý định, mức hiểu, điều đã thử hoặc điểm vướng.
- Loại trừ: đã có lỗi cụ thể cần tìm nguyên nhân (`DIAG`); đã đủ dữ kiện để giải thích/dàn giáo.
- Ví dụ đạt: `BC-HNMU-G6-R0044-STT1-AI02` — hỏi về thiết bị không dây hoặc mạng học sinh đã dùng để kiểm phạm vi quan niệm “mạng chỉ gồm máy nối dây”.
- Phản ví dụ: giảng toàn bộ định nghĩa mạng ngay, không kiểm giả thuyết của học sinh.

### `TASK-EXPLAIN` — Giải thích và kiến tạo hiểu biết

- Bao gồm: đích chính là hiểu một khái niệm, quan hệ hoặc nguyên lý.
- Loại trừ: cần bước tiếp theo của sản phẩm (`SCAFFOLD`); cần quan sát quy trình mẫu (`MODEL`); chỉ cần làm vững điều đã đúng (`CONSOLIDATE`).
- Ví dụ đạt: `BC-HNMU-G6-R0048-STT5-AI04` — nối ví dụ máy in dùng chung với quan hệ “kết nối mạng → chia sẻ tài nguyên”.
- Phản ví dụ: chỉ đọc lại định nghĩa mạng, không xử lý biểu diễn hiện có của học sinh.

### `TASK-ASSESS` — Đánh giá bài làm và phản hồi

- Bao gồm: đã có câu trả lời/sản phẩm; cần phán đoán phần đúng, chưa đúng hoặc mức đạt bằng căn cứ.
- Loại trừ: cần tìm nguyên nhân gốc (`DIAG`); cần khái quát điều đã đúng (`CONSOLIDATE`).
- Ví dụ đạt: `BC-HNMU-G6-R0173-STT4-AI06` — xác nhận đúng chi tiết `Replace All` thay tất cả kết quả cùng lúc.
- Phản ví dụ: “Tuyệt vời, em giỏi lắm!” mà không chỉ ra phần đúng.

### `TASK-DIAG` — Chẩn đoán hiểu sai hoặc thiếu nền tảng

- Bao gồm: có lỗi/bế tắc cụ thể; phản hồi phải phân biệt hoặc kiểm tra nguyên nhân trước khi sửa.
- Loại trừ: chỉ thiếu trạng thái chung (`PROBE`); chỉ cần phán đoán sản phẩm (`ASSESS`); nguyên nhân đã rõ và cần bước tự sửa (`SCAFFOLD`).
- Ví dụ đạt: vòng lặp chạy mãi dù có điều kiện dừng; gia sư kiểm tra biến điều khiển có được cập nhật sau mỗi lượt.
- Phản ví dụ: “Em hãy thêm điều kiện dừng” mà chưa xác định vì sao điều kiện hiện tại không hoạt động.
- Câu hỏi UET: giữ nhiệm vụ riêng, hay coi chẩn đoán là hành vi phụ trong phản hồi mở?

### `TASK-SCAFFOLD` — Dàn giáo giải quyết vấn đề

- Bao gồm: đang làm nhiệm vụ cụ thể; cần bước tiếp theo vừa đủ và giữ phần việc có ý nghĩa cho học sinh.
- Loại trừ: đích hiểu khái niệm (`EXPLAIN`); cần mẫu hoàn chỉnh (`MODEL`); làm thay toàn bộ.
- Ví dụ đạt: `BC-HNMU-G6-R0181-STT12-AI02` — hướng dẫn mở `Replace`, rồi hỏi chuỗi sai nhập vào ô nào.
- Phản ví dụ: liệt kê trọn quy trình và điền sẵn tất cả thông tin.

### `TASK-MODEL` — Làm mẫu hoặc minh họa quy trình

- Bao gồm: quan sát mẫu là phương tiện chính; mẫu làm lộ bước/điểm quyết định rồi chuyển giao.
- Loại trừ: một gợi ý đủ để đi tiếp (`SCAFFOLD`); ví dụ chỉ soi sáng khái niệm (`EXPLAIN`).
- Ví dụ đạt: làm mẫu tính trung bình ba số khác trong Scratch, giải thích thứ tự phép tính, rồi yêu cầu học sinh tự thay dữ liệu.
- Phản ví dụ: “Em tạo ba biến rồi thử tiếp nhé”; đây là gợi ý, chưa phải quy trình mẫu.

### `TASK-PRACTICE` — Tạo luyện tập hoặc thử thách

- Bao gồm: học sinh có nền tảng; phản hồi tạo nhiệm vụ mới để luyện, kiểm tra chuyển giao hoặc tăng độ khó.
- Loại trừ: câu hỏi chỉ giúp bài hiện tại (`SCAFFOLD`); áp dụng rất gần để làm vững (`CONSOLIDATE`).
- Ví dụ đạt: sau bài kiểm tra số dương, giao bài mới phân loại số âm, 0 hoặc dương mà không đưa lời giải.
- Phản ví dụ: khi học sinh chưa xong điều kiện đầu tiên, giao ngay chương trình phức tạp hơn.

### `TASK-CONSOLIDATE` — Củng cố và chuyển giao

- Bao gồm: học sinh vừa hiểu/hoàn thành đúng; cần xác nhận có căn cứ, khái quát, nêu lại hoặc áp dụng gần.
- Loại trừ: chỉ cần phán đoán (`ASSESS`); mở bài mới đáng kể (`PRACTICE`); chỉ khen.
- Ví dụ đạt: `BC-HNMU-G7-R0186-STT3-AI08` — yêu cầu học sinh tự tóm tắt hai điều kiện dừng vừa xác định.
- Phản ví dụ: “Đúng rồi, tốt lắm!” mà không có hành động làm vững hoặc chuyển giao.

## 5. Quy tắc ranh giới


| Cặp                    | Câu hỏi quyết định                                                              |
| ----------------------- | ------------------------------------------------------------------------------------ |
| `PROBE–DIAG`           | Thiếu dữ kiện về trạng thái, hay đang kiểm nguyên nhân của lỗi cụ thể? |
| `EXPLAIN–SCAFFOLD`     | Đích chính là hiểu quan hệ, hay hoàn thành bước tiếp theo?                |
| `EXPLAIN–MODEL`        | Ví dụ chỉ soi sáng khái niệm, hay quy trình mẫu là bắt buộc?              |
| `ASSESS–DIAG`          | Cần biết bài làm đúng ở đâu, hay vì sao lỗi xảy ra?                      |
| `ASSESS–CONSOLIDATE`   | Cần phán đoán chất lượng, hay làm vững điều vừa đúng?                  |
| `SCAFFOLD–MODEL`       | Một gợi ý có đủ, hay học sinh cần quan sát mẫu?                            |
| `PRACTICE–CONSOLIDATE` | Đang mở nhiệm vụ mới, hay áp dụng rất gần để làm vững?                  |

Hình thức bề mặt không quyết định nhãn. Một câu hỏi có thể phục vụ nhiều mục tiêu; phải xét đủ trạng thái, mục tiêu và bằng chứng.

## 6. Trường hợp chưa phân loại

Chỉ dùng `unclassifiable` khi thiếu đầu vào quyết định, dữ liệu mâu thuẫn, hoặc xuất hiện hợp đồng mới chưa có nhãn.

Ví dụ: “Thầy xem hình em gửi và chỉ chỗ sai giúp em” nhưng không có hình hoặc mô tả sản phẩm. Không ép vào `PROBE` hay `ASSESS`; ghi thiếu đầu vào.

Không dùng `unclassifiable` chỉ vì phân vân giữa hai nhãn; chuyển trường hợp đó vào hàng đợi UET.

## 7. Trạng thái và cổng tiếp theo

- Census 2.028 ứng viên và mẫu khám phá 160 ứng viên đã sẵn sàng.
- Hai mươi nhãn cũ trong `specialist_draft/` là bản thử trước cổng, không được tính là kết quả chính thức.
- Số ứng viên mã hóa chính thức: **0**.
- Sau khi UET duyệt sổ tay, AI mới mã hóa lô 40 đầu tiên bằng `AI-CODER-01`.

UET cần quyết định: mức rõ của từng nhiệm vụ; cách xử lý `DIAG`, `MODEL`, `PRACTICE`; bảy ranh giới; và có cho phép mở Bước C2 hay không.
