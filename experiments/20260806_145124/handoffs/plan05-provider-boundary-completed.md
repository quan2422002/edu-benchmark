# Bàn giao — Kế hoạch 05 / Ranh giới nhà cung cấp mô hình và nghiệp vụ chấm mức độ bắt buộc

- Mã sự kiện: `EXP-20260806-P05-WORKFLOW-COMPLETED-040`
- Mã kế hoạch: `P05`
- Chế độ: `single-agent`
- Tác nhân: `orchestrator`
- Trạng thái: `completed`
- Mã/nhãn luồng chuyên biệt: `not-applicable`

## Yêu cầu thực hiện

Tách rõ `src/` và `scripts/`, xây tầng nhà cung cấp mô hình độc lập, chuyển các
thành phần sử dụng đại diện và loại bỏ không gian tên `vertex_ai_call` trước khi
đóng plan 05.

## Quyết định phát sinh

P05-A001 chọn nghiệp vụ chấm mức độ bắt buộc cùng hai thành phần gọi bộ chấm
đồng bộ bằng Gemini và OpenAI làm lát cắt đại diện, đặt ba giao diện dòng lệnh
của nghiệp vụ này tại `scripts/` và đồng bộ PyYAML về `6.0.2`. Không gọi API
trả phí hoặc sửa nội dung bộ benchmark.

P05-A002 hiệu chỉnh báo cáo cuối, hướng dẫn vận hành và tệp bàn giao sang tiếng
Việt nhất quán. Tệp trạng thái cùng bảng tương thích là sản phẩm máy đọc nên
được giữ nguyên tiếng Anh theo chỉ dẫn của người phụ trách dự án.

P05-A003 chuyển các giá trị requirement scoring riêng của experiment sang YAML
config bắt buộc tại CLI, thống nhất `include_thoughts=true` trên các đường
Gemini hiện hành và dùng phân loại `retryable` để tránh lặp lại lỗi provider
không thể khắc phục. Không có API thật hoặc output lịch sử nào bị thay đổi.

## Đầu ra chính

- `src/edu_benchmark/model_providers/`
- `src/edu_benchmark/requirement_scoring/`
- `scripts/requirement_scoring/`
- `experiments/20260806_145124/configs/requirement-scoring-20260727-v1.yaml`
- phần cải tổ `gemini_judge.py`, `openai_judge.py` và hàm chuẩn hóa lý do kết
  thúc dùng chung cho quy trình chấm theo lô;
- ba đầu ra máy đọc của plan 05, hướng dẫn vận hành, báo cáo, phép kiểm thử
  và tài liệu kiến trúc.

## Kết quả

Tầng nhà cung cấp không nhập quy trình nghiệp vụ; nghiệp vụ chấm mức độ bắt
buộc và hai thành phần gọi bộ chấm dùng cùng hợp đồng trung gian trong phép kiểm
thử ngoại tuyến. Giao diện dòng lệnh, việc đóng gói và đường nhập mới đều đạt; không gian
tên cũ đã bị loại bỏ. Toàn bộ `302` phép kiểm thử, bộ kiểm tra quản trị,
`pip check` và phép kiểm tra sai khác định dạng đều đạt bằng `benchmark_env`.

## Quyết định của tác nhân điều phối

Đóng Kế hoạch 05 ở trạng thái `completed`. Đưa Kế hoạch 06 về trạng thái chờ
người phụ trách dự án duyệt; chưa có quyền xóa hoặc khử trùng lặp đầu ra trước
khi được phê duyệt.

## Câu hỏi mở

- Kế hoạch 06 cần xác định chính sách lưu giữ và thao tác xóa/di chuyển nào được
  phép.
- Kaggle, Ollama, vLLM và hợp đồng gọi nhà cung cấp theo lô vẫn là phần mở rộng
  tương lai, chỉ triển khai khi có thành phần sử dụng cùng yêu cầu cụ thể.
