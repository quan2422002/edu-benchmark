# Quyết định ngưỡng C0b trước khi chạy

Trạng thái: **UET đã chốt đủ 5/5 ngưỡng trước khi chạy hai specialist**.

## Ngưỡng là gì?

Mỗi ngưỡng là tỷ lệ thống nhất tối thiểu giữa hai lần chạy độc lập A và B trên cùng 40 mẫu. Ta dùng chúng như một cổng kiểm tra xem hướng dẫn gán nhãn có đủ rõ và quy trình AI có đủ tái lập để tiếp tục hay không.

- Đây **không phải** điểm chất lượng của câu trả lời gia sư.
- Đây **không phải** tỷ lệ AI gán đúng so với ground truth.
- Đây **không phải** độ tin cậy giữa hai chuyên gia con người.
- Tất cả năm chỉ số phải đạt. Chỉ cần một chỉ số thấp hơn ngưỡng thì C0b dừng để phân tích và sửa quy trình.

## Quyết định hiện tại

| Chỉ số | Ngưỡng | Trạng thái | Ý nghĩa trên 40 mẫu |
|---|---:|---|---|
| Trùng nguyên tắc chính | **1,00** | **UET đã chốt** | A và B phải cùng nguyên tắc chính ở đủ 40/40 dòng; một bất đồng cũng làm C0b không đạt. |
| Trùng chính xác cặp chính–phụ | **0,90** | **UET đã chốt** | A và B phải cùng cả nguyên tắc chính lẫn nguyên tắc phụ ở ít nhất 36/40 dòng. |
| Jaccard trung bình của tập nhãn | **0,90** | **UET đã chốt** | Jaccard trung bình trên 40 cặp tập nhãn phải đạt ít nhất 0,90. Với các ngưỡng chính `1,00` và cặp `0,90`, đây chủ yếu là kiểm tra bổ sung. |
| Thống nhất có/không có khoảng trống | **1,00** | **UET đã chốt** | A và B phải cùng quyết định coverage gap ở đủ 40/40 dòng. |
| Thống nhất tác động của reference | **0,90** | **UET đã chốt** | Ít nhất 36/40 dòng cùng phân loại `unchanged`, `changed` hoặc `conflict`. |

## “Tác động của reference” nghĩa là gì?

Mỗi specialist gán nhãn hai lần cho cùng một mẫu:

1. Vòng 1 chỉ đọc `student_prompt` và `conversation_history`.
2. Vòng 2 mới được đọc thêm `gold_response` và `gold_answer` để đối chiếu.

Sau vòng 2, mỗi specialist tự phân loại một trong ba trạng thái:

- `unchanged`: nhãn chính, nhãn phụ và quyết định coverage gap không đổi;
- `changed`: reference khiến specialist thay đổi ít nhất một phần của quyết định nhãn;
- `conflict`: context và reference gợi ra hai cách hiểu sư phạm không tương thích, specialist không tự ép chọn mà chuyển UET review.

Chỉ số này không hỏi A và B có chọn cùng nguyên tắc hay không — việc đó đã được đo bằng hai ngưỡng đầu. Nó hỏi hai specialist có **cùng cách phản ứng khi được xem reference** hay không.

Ví dụ:

- A: vòng 1 `Explanation`, vòng 2 vẫn `Explanation` → `unchanged`.
- B: vòng 1 `Questioning`, vòng 2 đổi sang `Feedback` → `changed`.
- Hai instance không thống nhất về tác động của reference cho mẫu này.

Nếu chỉ số thấp, vấn đề có thể là hợp đồng vòng 2 chưa rõ hoặc hai specialist đang để gold ảnh hưởng nhãn theo hai cách khác nhau. Khi đó cần rà lại các dòng này trước khi scale.

## Trạng thái file máy đọc

`task_discovery/dual_run_thresholds.json` hiện có `status=uet_approved`, người duyệt và thời điểm duyệt. Cả năm giá trị đã được khóa trong file máy đọc trước khi specialist A/B chạy.

Ngưỡng là cổng chẩn đoán, không chứng minh taxonomy hợp lệ. Dù đạt ngưỡng, UET vẫn xem mọi bất đồng, mọi khoảng trống, mọi xung đột context–gold và ít nhất 8 trường hợp đồng thuận được chọn xác định.
