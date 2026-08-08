# Runbook — Plan 02 / Packaging và offline validation

Experiment: `20260806_145124`
Plan: `P02`

## Mục đích

Cài repository theo src-layout, kiểm import ngoài repo và chạy toàn bộ validation
offline mà không cấp credential hoặc gọi model provider.

## Điều kiện trước khi chạy

- Baseline Plan 02 có dòng trạng thái `APPROVED`.
- Chạy lệnh cài đặt bằng đúng Python của `benchmark_env`.
- Không đặt API key hoặc ADC chỉ để chạy test.

## Cấu hình và input

- Package metadata: `pyproject.toml`
- Direct dependencies: `requirements.txt`
- Conda specification: `environment.yml`
- CI reference: `.github/workflows/offline-tests.yml`
- Expected output: editable package, import portability và test report; không
  tạo benchmark/model output.

## Preflight

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -c \
  "import sys; print(sys.executable); print(sys.version)"
```

## Chạy chính

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip install \
  -r requirements.txt
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip install \
  --no-deps -e .
```

## Kiểm import ngoài repository

```bash
cd /tmp
/home/quannda/miniconda3/envs/benchmark_env/bin/python -I -c \
  "import edu_benchmark, vertex_ai_call; print(edu_benchmark.__file__); print(vertex_ai_call.__file__)"
```

Hai path phải trỏ về `src/edu_benchmark/` và `src/vertex_ai_call/` thông qua
editable install, không nhờ current working directory hoặc `PYTHONPATH`.

## Validation

Từ repository root:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip check
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/governance/validate_experiment.py experiments/20260806_145124
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest -q
```

GitHub Actions chạy hai lane không credential:

- `core-without-providers` cài `.[dev]` và chạy các test provider-independent;
- `self-contained-offline` cài full `requirements.txt` nhưng chỉ chạy test có
  fixture được track trong Git.

Test cần raw XLSX hoặc experiment JSONL bị ignore là local integration test,
không phải clean-clone CI gate. Khi kiểm local trước closeout, dựng wheel từ danh
sách `git ls-files -co --exclude-standard`, bỏ path đã xóa khỏi working tree, rồi
cài wheel vào target tạm ngoài repository. Wheel phải import được cả hai package
và không chứa prototype OCR local bị ignore.

## Resume

Các bước là idempotent; chạy lại cùng command sau khi sửa lỗi. Không có API run
hoặc output record cần resume.

## Failure và rollback

- `pip check` khác 0: khôi phục pin tương thích, không gỡ package OCR/provider
  theo suy đoán.
- Import ngoài repo thất bại: giữ package chưa đóng gate và kiểm package discovery.
- Test thất bại: không mở Plan 03.
- Có thể rollback import migration theo commit; không cần sửa dữ liệu/output.

## Cleanup

Không commit `build/`, `dist/` hoặc `*.egg-info`. Nếu một wheel probe tạo các
thư mục này, chỉ xóa đúng artifact do probe đó sinh sau khi đã kiểm target.
