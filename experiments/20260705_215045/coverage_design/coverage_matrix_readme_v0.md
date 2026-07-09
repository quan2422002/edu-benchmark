# P05 — Cách đọc ma trận bao phủ tổng quát v0

File chính của P05 là `general_coverage_matrix_v0.csv`. Đây là ma trận bao phủ thiết kế, không phải danh sách mẫu cố định.

## 1. Vì sao không khóa ở 20 mẫu?

Con số 20 mẫu chỉ phù hợp để làm pilot nhỏ. Nếu dùng 20 mẫu làm khung chính, benchmark rất dễ lệch về một vài chủ đề hoặc một vài dạng câu hỏi dễ viết. Vì vậy P05 dùng ma trận tổng quát để nhìn toàn bộ không gian cần phủ trước, sau đó P06/P07 mới chọn lát cắt phù hợp.

Ma trận hiện có:

- 4 task hành vi gia sư từ P04;
- 3 mức nhận thức: Biết, Hiểu, Vận dụng;
- 8 cụm chủ đề SGK Tin học 9 từ P02;
- 9 dạng bài làm/câu hỏi/sản phẩm của học sinh;
- tổng cộng 96 ô bao phủ.

## 2. Vì sao thêm `student_work_type`?

`format_family` chỉ nói tương đối rộng về kiểu tình huống hoặc định dạng mẫu. Nó chưa nói đủ rõ học sinh đang đưa cái gì cho gia sư xử lý. Vì vậy P05 thêm trục `student_work_type` để tách riêng dạng bài làm/câu hỏi/sản phẩm của học sinh.

Ví dụ: T2 là “phản hồi bài làm”, nhưng bài làm đó có thể là câu tự luận, đáp án trắc nghiệm, đoạn mã Python, thuật toán, bảng tính hoặc sản phẩm số.

## 3. Ý nghĩa các cột mới

| Cột | Ý nghĩa |
|---|---|
| `primary_student_work_type` | Dạng bài làm/câu hỏi/sản phẩm học sinh nên dùng trước. |
| `secondary_student_work_type` | Dạng thay thế nếu giáo viên thấy tự nhiên hơn. |
| `student_work_type_note` | Ghi chú giúp P06/giáo viên hiểu nên tạo bài làm kiểu gì. |

## 4. Dạng bài làm của học sinh trong v0

| Mã | Dạng bài làm/câu hỏi/sản phẩm | Số ô dùng làm dạng chính |
|---|---|---:|
| `SWT01` | Câu hỏi hoặc nhận định khái niệm | 10 |
| `SWT02` | Đáp án trắc nghiệm | 3 |
| `SWT03` | Câu trả lời tự luận hoặc lập luận ngắn | 18 |
| `SWT04` | Bài làm cần phản hồi hoặc sửa lỗi | 6 |
| `SWT05` | Đoạn mã Python hoặc chương trình | 6 |
| `SWT06` | Thuật toán hoặc mô tả bước giải | 5 |
| `SWT07` | Bảng tính, công thức hoặc hàm | 12 |
| `SWT08` | Thao tác công cụ hoặc sản phẩm số | 24 |
| `SWT09` | Tình huống đạo đức, pháp luật hoặc văn hoá số | 12 |

Các dạng này lấy tinh thần từ P03: khái niệm, trắc nghiệm, tự luận, sửa lỗi code, viết/hoàn thiện thuật toán hoặc chương trình; đồng thời bổ sung bảng tính, sản phẩm số và tình huống đạo đức/pháp luật vì đây là các vùng rõ trong SGK Tin học 9.

## 5. Cách dùng trong P06

P06 nên chọn trước các ô `core`, sau đó thêm một số ô `recommended` để cân bằng chủ đề, định dạng và dạng bài làm. Không cần ép đủ mọi ô ngay ở pilot đầu.

Nguyên tắc chọn lát cắt đầu tiên:

1. Mỗi task T1–T4 đều phải có mẫu.
2. Ba mức Biết, Hiểu, Vận dụng đều phải xuất hiện.
3. Không để toàn bộ mẫu rơi vào lập trình/bảng tính; cũng không để toàn bộ mẫu là câu hỏi lý thuyết.
4. Cần có nhiều dạng bài làm: khái niệm, trắc nghiệm, tự luận/lập luận, đoạn mã/chương trình, bảng tính, sản phẩm số hoặc tình huống đạo đức số.
5. Với T3, cột `note` của phiếu tác giả nên ghi nhãn hỗ trợ tiếng Việt như Gợi mở, Gợi ý, Hướng dẫn, Làm mẫu để giải thích R3.

## 6. Trạng thái

Các câu hỏi mở từ P04 được coi là tạm chốt để tiếp tục tiến độ. Ma trận này là bản v0 dùng để điều phối thiết kế, chưa thay thế xác nhận chuyên môn cuối cùng từ HNMU.
