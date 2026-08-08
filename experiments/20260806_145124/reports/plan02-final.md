# Báo cáo cuối — Plan 02

Experiment: `20260806_145124`
Baseline: `plans/02-python-packaging-and-clean-environment-validation.md`
Trạng thái kết luận: `completed`

## 1. Kết quả

Plan 02 đã hoàn tất src-layout packaging, dependency groups, Conda
specification, import migration và hai lane CI offline. Package cài editable và
wheel đều import được ngoài repository mà không cần `sys.path` injection.

Clean-trackable drill dùng đúng tập file Git có thể theo dõi, do đó không đưa
prototype OCR local vào wheel hoặc test evidence. Wheel từ snapshot này import
được `edu_benchmark` và compatibility package `vertex_ai_call`; 188 test
self-contained trong snapshot đạt. Governance artifact Plan 01–02 hiện đều có
thể được Git theo dõi.

## 2. So với baseline

| Tiêu chí | Kết quả | Bằng chứng |
|---|---|---|
| Editable install và import ngoài repo | `pass` | Import bằng exact `benchmark_env` trỏ đúng package dưới `src/` |
| Wheel từ Git-trackable snapshot | `pass` | Isolated target import đạt; không chứa prototype OCR bị ignore |
| Không còn production/test import `src.*` | `pass` | Static scan toàn bộ `src/`, `scripts/`, `tests/` |
| Không còn `sys.path` injection | `pass` | `tests/conftest.py` đã bỏ; packaging contract đạt |
| Core không bắt buộc provider | `pass` | 127 test đạt khi chủ động chặn Google/OpenAI/dotenv/tqdm imports |
| CI offline không đọc secret/gọi API | `pass` | Hai lane trong `.github/workflows/offline-tests.yml` và contract test |
| Dependency consistency | `pass` | `pip check`: no broken requirements |
| Conda specification | `pass` | `conda env create --dry-run` giải được Python 3.12 specification |
| Governance và tracking | `pass` | Validator đạt; artifact governance không còn bị ignore |

## 3. Amendment đã áp dụng

- `P02-A001`: chọn setuptools, Python 3.12, environment specification và Ubuntu CI.
- `P02-A002`: ghim PyYAML 6.0.2 để tương thích PaddleX hiện có.
- `P02-A003`: loại prototype OCR local khỏi repository contract và tách CI thành
  core không provider cùng self-contained offline suite.

## 4. Validation

- Exact interpreter:
  `/home/quannda/miniconda3/envs/benchmark_env/bin/python`
- Kết quả closeout:
  - governance validation passed;
  - packaging contract: `7 passed`;
  - core/provider-independent với provider imports bị chặn: `127 passed`;
  - self-contained working-tree suite: `206 passed`;
  - Git-trackable snapshot suite, không tính packaging subprocess test:
    `188 passed`;
  - toàn bộ local suite có data/prototype local: `270 passed`;
  - `pip check`: no broken requirements;
  - isolated wheel import và forbidden import/path scan: passed.

## 5. Artifact chính

- `pyproject.toml`
- `environment.yml`
- `requirements.txt`
- `.github/workflows/offline-tests.yml`
- Import migration trong `src/`, `scripts/`, `tests/`
- `tests/packaging/test_packaging_contract.py`
- `runbooks/plan02-packaging-and-offline-validation.md`

## 6. Giới hạn và backlog

- `environment.yml` là direct-input specification, không phải transitive hoặc
  bit-for-bit lock.
- CI ban đầu chỉ có Ubuntu/Python 3.12; Windows chưa phải gate Plan 02.
- `vertex_ai_call` còn là top-level compatibility package đến Plan 05.
- Test tích hợp cần raw XLSX hoặc experiment JSONL bị ignore chỉ chạy trên local
  workspace có dữ liệu; chúng không được trình bày là clean-clone CI evidence.
- PaddleOCR/VietOCR/MinerU code và environment local là prototype thất bại,
  không thuộc package hoặc clean-clone contract.
- Workflow GitHub Actions đã được kiểm hợp đồng và mô phỏng local; trạng thái run
  trên GitHub chỉ có sau khi branch được push hoặc mở pull request.

## 7. Gate tiếp theo

Plan 02 hoàn tất. Plan 03 có thể được project lead đọc và quyết định duyệt nhưng
vẫn là `DRAFT`; closeout này không tự động cấp quyền triển khai Plan 03.
