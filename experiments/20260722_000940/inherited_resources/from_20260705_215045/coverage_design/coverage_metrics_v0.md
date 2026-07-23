# P05 — Chỉ số kiểm soát độ bao phủ v0

Các chỉ số dưới đây dùng để kiểm soát một tập mẫu pilot bất kỳ được chọn từ `general_coverage_matrix_v0.csv`. Chúng không bắt buộc pilot phải có đúng 20 mẫu.

## 1. Các trục cần kiểm soát

Một lát cắt pilot nên báo cáo tối thiểu các trục sau:

- task: T1–T4;
- mức nhận thức: Biết, Hiểu, Vận dụng;
- chủ đề SGK Tin học 9;
- định dạng/tình huống mẫu qua `format_family`;
- dạng bài làm/câu hỏi/sản phẩm học sinh qua `student_work_type`;
- mức ưu tiên qua `coverage_priority`.

## 2. Độ phủ dạng bài làm của học sinh

`student_work_type` là trục mới được tách khỏi `format_family` để nhìn rõ học sinh đang đưa vật liệu gì vào hội thoại.

Các dạng nên có trong lát cắt đầu tiên nếu đủ thời gian:

- câu hỏi hoặc nhận định khái niệm;
- đáp án trắc nghiệm;
- câu trả lời tự luận hoặc lập luận ngắn;
- bài làm cần phản hồi hoặc sửa lỗi;
- đoạn mã Python/chương trình;
- thuật toán hoặc mô tả bước giải;
- bảng tính/công thức/hàm;
- thao tác công cụ hoặc sản phẩm số;
- tình huống đạo đức, pháp luật hoặc văn hoá số.

Nếu pilot quá nhỏ, có thể chưa cần đủ mọi dạng, nhưng không nên chỉ có câu hỏi khái niệm hoặc chỉ có code.

## 3. Diễn giải nhanh bản v0

Ma trận hiện có 96 ô. Phân bố theo mức ưu tiên:

| Mức ưu tiên | Số ô |
|---|---:|
| core | 52 |
| recommended | 27 |
| optional | 15 |
| deferred | 2 |

Phân bố dạng bài làm chính:

| Mã | Dạng bài làm/câu hỏi/sản phẩm | Số ô |
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

Khi P06 viết ví dụ, chỉ cần chọn lát cắt đại diện, không cố phủ hết mọi ô.
