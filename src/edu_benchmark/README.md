# `edu_benchmark`

Package này chứa code dùng chung cho dự án benchmark gia sư AI môn Tin học.

## Nguyên tắc

1. Code dùng chung đặt trong `src/edu_benchmark/`, không đặt rải trong từng experiment.
2. Code không sửa dữ liệu gốc; mọi kết quả xử lý phải là bản dẫn xuất có truy vết.
3. Các script/validator phải chạy bằng môi trường Conda `benchmark_env`.
4. Các module trong package này chỉ là khung ở Plan 02; logic thật sẽ được thêm trong các plan sau.

## Cấu trúc

- `data_io`: đọc Excel/CSV và chuẩn hóa bảng trung gian.
- `dialogue_audit`: kiểm thiếu trường, độ phủ, nhất quán, trùng/gần trùng và chất lượng hội thoại.
- `benchmark_conversion`: chuyển dữ liệu thô đã qua kiểm toán thành mẫu benchmark.
- `learning_resources`: xử lý học liệu, chủ đề, bài học, OCR, fragment và registry.
- `benchmark_quality`: kiểm tra khả năng áp dụng/phân biệt của benchmark sau chuyển đổi.
