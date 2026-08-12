# Nhật ký điều chỉnh Plan 05

Experiment: `20260806_145124`
Plan: `P05`

## P05-A001 — Chốt lát cắt chuyển đổi và đồng bộ dependency

Thời điểm: `2026-08-10T14:44:56+07:00`
Trạng thái: `RECORDED`

Quyết định triển khai:

- đường requirement scoring giữ nguyên prompt, request hash và lược đồ đầu ra,
  nhưng gọi Vertex AI thông qua hợp đồng `edu_benchmark.model_providers`;
- hai caller chấm benchmark bằng Gemini trên Vertex AI và OpenAI Responses API
  là lát cắt benchmark evaluation đầu tiên dùng cùng hợp đồng này;
- CLI công khai của requirement scoring chuyển sang
  `scripts/requirement_scoring/`; không gian tên `vertex_ai_call` chỉ tồn tại
  trong lúc chuyển mã và phải bị loại bỏ trước khi đóng plan;
- giữ `PyYAML==6.0.2` làm pin thống nhất trong `requirements.txt` và
  `pyproject.toml`. Giá trị `6.0.3` trong requirements trước đó không khớp
  metadata package và xung đột với dependency đã có trong `benchmark_env`.

Ảnh hưởng:

- không thay đổi prompt, dữ liệu benchmark, rubric hoặc kết quả khoa học;
- không gọi API thật trong kiểm chứng;
- các caller bên ngoài vẫn nhận cùng tham số và trả cùng cấu trúc dữ liệu, còn
  phần kết nối SDK được chuyển vào tầng provider độc lập.

Khả năng quay lui: dùng lát cắt Git trước Plan 05 cùng bảng ánh xạ đường dẫn
cũ–mới; không duy trì song song hai implementation provider.

## P05-A002 — Hiệu chỉnh ngôn ngữ của tài liệu dành cho con người

Thời điểm: `2026-08-11T15:38:46+07:00`
Trạng thái: `RECORDED`

Người phụ trách dự án yêu cầu sửa cách trình bày của báo cáo cuối, hướng dẫn vận
hành và tệp bàn giao Kế hoạch 05 để phần diễn giải dùng tiếng Việt nhất quán.
Tên mã, tên lớp, lệnh, đường dẫn, giá trị trạng thái và thuật ngữ kỹ thuật không
thể dịch được giữ nguyên.

Hai sản phẩm máy đọc không thuộc phạm vi dịch:

- `plans/05-status.yaml` tiếp tục dùng tiếng Anh, bao gồm cả trường diễn giải;
- `outputs/plan05/compatibility_matrix.csv` tiếp tục dùng tiếng Anh toàn bộ.

Điều chỉnh này không thay đổi mã nguồn, hợp đồng, kết quả kiểm thử, trạng thái
cổng hoặc nội dung benchmark.
