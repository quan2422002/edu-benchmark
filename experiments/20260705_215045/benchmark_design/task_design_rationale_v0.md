# P04 — Luận giải thiết kế task v0

## 1. Mục đích

File này giải thích vì sao P04 đặt task theo **hành vi gia sư trong hội thoại** thay vì đặt task theo mức nhận thức/Bloom. Bản này phục vụ P05/P06 và nhóm HNMU khi cần hiểu benchmark đang muốn kiểm tra năng lực nào của gia sư AI.

Trạng thái chuyên môn: `needs_hnmu_review`. Đây là bản đề xuất v0, không thay thế quyết định của giáo sư/HNMU.

## 2. Căn cứ thiết kế

| Loại căn cứ | Nội dung dùng trong P04 |
|---|---|
| Bằng chứng nghiên cứu | `P03-C001` tách “giải đúng” khỏi “dạy tốt”; `P03-C004` khuyến nghị task theo hành vi gia sư; `P03-C002` nhấn mạnh chẩn đoán trạng thái/lỗi; `P03-C003` nhấn mạnh giàn giáo/gợi mở. |
| Học liệu | P02 chốt phạm vi hiện tại là SGK Tin học 9, mã `LM-SGK-TIN9-4700233123`; danh sách chủ đề/bài học v0 nằm ở `topic_taxonomy/tin9_sgk_topics_v0.csv`. |
| Quyết định dự án | `Mức độ nhận thức` là metadata riêng với 3 mức `Biết`, `Hiểu`, `Vận dụng`; không dùng mức nhận thức làm tên task. |

## 3. Vì sao không dùng mức nhận thức làm task?

Mức nhận thức trả lời câu hỏi: học sinh đang xử lý nội dung ở độ sâu nào. Nhưng benchmark gia sư LLM cần thêm câu hỏi khác: tutor phải **ứng xử như một gia sư** ra sao trước trạng thái của học sinh.

Ví dụ cùng chủ đề “Sử dụng hàm IF” trong SGK Tin học 9:

- Học sinh hỏi “Hàm IF dùng để làm gì?” → task có thể là T1, giải thích thích ứng.
- Học sinh đưa công thức sai → task có thể là T2, phản hồi bài làm.
- Học sinh nói “Em không biết bắt đầu từ đâu” → task có thể là T3, gợi ý từng bước.
- Học sinh dùng sai điều kiện logic vì hiểu nhầm quan hệ so sánh → task có thể là T4, chẩn đoán lỗi/hiểu lầm.

Bốn trường hợp này có thể cùng thuộc mức `Hiểu` hoặc `Vận dụng`, nhưng năng lực gia sư cần đo khác nhau. Vì vậy task phải dựa trên hành vi gia sư.

## 4. Task v0

| Task | Tên | Định nghĩa ngắn | Dùng khi | Không nên dùng khi |
|---|---|---|---|---|
| `T1` | Giải thích thích ứng | Tutor giải thích khái niệm/thao tác/cách làm theo mức hiểu hiện tại của học sinh. | Học sinh hỏi “là gì”, “vì sao”, “em chưa hiểu”, hoặc cần diễn giải lại nội dung SGK. | Học sinh đã đưa sản phẩm cụ thể cần nhận xét; khi đó ưu tiên T2. |
| `T2` | Phản hồi bài làm hoặc lập luận của học sinh | Tutor nhận xét phần học sinh đã làm/nói: đúng gì, sai gì, thiếu gì, nên sửa theo hướng nào. | Học sinh đưa đáp án, đoạn code, cách giải, lập luận, sản phẩm hoặc thao tác đã làm. | Học sinh chưa có nỗ lực/sản phẩm cụ thể; khi đó có thể là T1 hoặc T3. |
| `T3` | Gợi ý từng bước để học sinh tự đi tiếp | Tutor đưa gợi mở/gợi ý/hướng dẫn/làm mẫu vừa đủ để học sinh tiếp tục. | Học sinh bị kẹt và mục tiêu là hỗ trợ tự làm, không đưa lời giải quá sớm. | Khi nhiệm vụ chính là đánh giá sản phẩm đã có; khi đó ưu tiên T2. |
| `T4` | Chẩn đoán lỗi, hiểu lầm hoặc thiếu nền tảng | Tutor xác định bản chất lỗi/hiểu lầm/thiếu tiền đề trước khi hướng dẫn sửa. | Học sinh sai có hệ thống, hiểu nhầm khái niệm, lỗi code, lỗi thuật toán hoặc hỏi lệch do thiếu nền. | Khi lỗi đã quá rõ và nhiệm vụ chỉ cần phản hồi sửa bài; khi đó T2 có thể đủ. |

## 5. Quan hệ với P02 topic taxonomy

Mỗi mẫu P04/P05/P06 cần gắn với chủ đề/bài học từ `tin9_sgk_topics_v0.csv`. Khi dùng danh sách này, phải nhớ rằng bài học không đứng riêng rẽ: mỗi `bai_hoc` thuộc một `chu_de` hoặc `chu_de_con` qua `parent_id`.

Ở P04, topic/bài học là bối cảnh nội dung. Topic không thay thế task. Một task như T3 có thể xuất hiện ở nhiều chủ đề khác nhau; ngược lại một bài như “Bài 12a. Sử dụng hàm IF” có thể tạo mẫu cho T1, T2, T3 hoặc T4.

## 6. Quan hệ với mức nhận thức

P04 dùng 3 mức nhận thức từ P02:

- `Biết`: nhận ra, nêu lại, xác định khái niệm/thao tác/thông tin.
- `Hiểu`: giải thích, phân biệt, diễn giải, nêu quan hệ hoặc lý do.
- `Vận dụng`: áp dụng kiến thức/kĩ năng vào tình huống, bài tập, lỗi hoặc sản phẩm cụ thể.

Mức nhận thức là metadata của mẫu. Nó không phải task. P05 nên kiểm soát coverage theo tổ hợp: task × mức nhận thức × chủ đề/bài học × dạng dữ liệu.

## 7. Điểm cần HNMU/giáo sư xác nhận

1. Có giữ đủ 4 task T1–T4 trong pilot không?
2. T4 là task độc lập hay nhãn phụ cho T2/T3?
3. Tên tiếng Việt của task đã đủ dễ hiểu với giáo viên chuyên môn chưa?
4. Với câu hỏi lệch phạm vi hoặc thiếu nền tảng, nên ưu tiên xử lý bằng T4 hay rubric R4/R5?
