# Amendments — Plan 02

Experiment: `20260806_145124`
Baseline: `plans/02-python-packaging-and-clean-environment-validation.md`

## P02-A001 — Chốt mặc định packaging, environment và CI ban đầu

- Thời điểm: `2026-08-07T11:59:59+07:00`
- Người quyết định: orchestrator, trong phạm vi Plan 02 đã được project lead duyệt
- Quyết định:
  - dùng `pyproject.toml` với setuptools và src-layout;
  - package tạm thời cả `edu_benchmark` và `vertex_ai_call`; việc hợp nhất
    `vertex_ai_call` thuộc Plan 05;
  - dùng `environment.yml` làm specification đa nền tảng ở mức direct input;
  - giữ `requirements.txt` là môi trường đầy đủ cho runner hiện hành, còn
    `pyproject.toml` tách dependency `dev` và `providers` thành optional groups;
  - CI ban đầu chỉ chạy Ubuntu, Python 3.12, offline test sau bước cài dependency;
  - không thêm một lockfile giả: direct dependencies được pin, transitive
    dependency chưa được khóa hoàn toàn và phải được báo rõ.
- Lý do: đây là lựa chọn nhỏ nhất tương thích `benchmark_env` hiện tại, không
  kéo packaging sang refactor runtime của Plan 05 và không tuyên bố mức tái lập
  cao hơn bằng chứng.
- Ảnh hưởng: import chuẩn chuyển sang `edu_benchmark`/`vertex_ai_call`; test và
  active Python scripts không còn dựa vào `sys.path` injection sau editable install.
- Không thay đổi: logic nghiệp vụ, model configuration, dữ liệu benchmark,
  output lịch sử và shell wrapper experiment-specific.

## P02-A002 — Đồng bộ PyYAML với OCR dependency hiện có

- Thời điểm: `2026-08-07T12:05:22+07:00`
- Người quyết định: orchestrator, trong phạm vi Plan 02 đã được project lead duyệt
- Quyết định: dùng `PyYAML==6.0.2` trong cả `requirements.txt` và
  `pyproject.toml` thay cho pin `6.0.3` trước Plan 02.
- Lý do: dependency sync cho thấy `paddlex 3.7.2` đã có trong `benchmark_env`
  yêu cầu chính xác PyYAML 6.0.2. Giữ 6.0.3 làm `pip check` báo xung đột; toàn bộ
  test dự án trước migration vốn đã chạy thành công với 6.0.2.
- Ảnh hưởng: environment trở lại trạng thái dependency-consistent; không thay
  schema YAML hay logic đọc/ghi hiện hành.
- Không thay đổi: phiên bản PaddleX, OCR environment policy, dữ liệu và output.

## P02-A003 — Tách clean-clone gate khỏi prototype và dữ liệu local

- Thời điểm: `2026-08-07T15:22:28+07:00`
- Người quyết định: project lead xác nhận phạm vi; orchestrator triển khai trong
  Plan 02 đã duyệt
- Quyết định:
  - giữ các prototype PaddleOCR, VietOCR và MinerU thất bại trong local workspace
    theo `.gitignore`; không coi chúng là package hoặc artifact chính thức;
  - build wheel kiểm chứng từ snapshot chỉ gồm file Git có thể theo dõi;
  - chia CI thành lane `core-without-providers` và `self-contained-offline`;
  - không dùng test cần raw XLSX hoặc experiment JSONL bị ignore làm clean-clone
    CI gate; chúng vẫn là local integration tests.
- Lý do: working tree đầy đủ đã làm bằng chứng package/test bao gồm cả file local
  không xuất hiện trong clean clone. CI phải đo đúng repository contract được
  publish, đồng thời vẫn chứng minh core package không cần provider dependency.
- Ảnh hưởng: README và architecture không còn quảng bá OCR prototype local như
  workflow được hỗ trợ; CI không cần secret hoặc provider API.
- Không thay đổi: `.gitignore`, code/dữ liệu OCR local, logic benchmark, output
  lịch sử và các test tích hợp cần dữ liệu local.
