# P05 — Tóm tắt ma trận bao phủ tổng quát v0

## 1. Kết quả chính

Đã cập nhật ma trận bao phủ tổng quát cho benchmark gia sư AI môn Tin học 9. Ma trận không khóa vào 20 mẫu pilot, vì 20 chỉ là con số tượng trưng để bắt đầu thử nghiệm.

Ma trận hiện phủ:

- 4 task hành vi gia sư từ P04: T1–T4;
- 5 rubric R1–R5 áp dụng cho từng task thông qua P04;
- 3 mức nhận thức đã chốt tạm từ P02: Biết, Hiểu, Vận dụng;
- 8 cụm chủ đề SGK Tin học 9 từ P02;
- 6 nhóm định dạng/tình huống mẫu;
- 9 dạng bài làm/câu hỏi/sản phẩm của học sinh;
- tổng cộng 96 ô bao phủ thiết kế.

## 2. Điểm mới: tách rõ dạng bài làm của học sinh

P05 hiện có thêm ba cột:

- `primary_student_work_type`: dạng bài làm/câu hỏi/sản phẩm nên ưu tiên;
- `secondary_student_work_type`: dạng thay thế;
- `student_work_type_note`: ghi chú để P06/giáo viên hiểu nên tạo bài làm kiểu gì.

Việc này giúp tránh nhầm lẫn giữa task của tutor và vật liệu học sinh đưa vào hội thoại.

## 3. Dạng bài làm trong v0

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

## 4. Mức ưu tiên

| Mức ưu tiên | Số ô |
|---|---:|
| core | 52 |
| recommended | 27 |
| optional | 15 |
| deferred | 2 |

## 5. Gợi ý dùng cho P06

P06 nên chọn các ô `core` trước, rồi thêm `recommended` để cân bằng task, mức nhận thức, chủ đề, định dạng và dạng bài làm. Đặc biệt nên tránh hai lệch pha: toàn lý thuyết hoặc toàn code/bảng tính.
