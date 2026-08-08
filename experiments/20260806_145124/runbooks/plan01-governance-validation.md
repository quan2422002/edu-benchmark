# Runbook — Plan 01 / Kiểm tra quản trị experiment

Experiment: `20260806_145124`
Plan: `P01`

## Mục đích

Kiểm tra template và một experiment dùng governance v1 mà không gọi API hoặc
thay đổi artifact benchmark.

## Điều kiện trước khi chạy

- Baseline Plan 01 có dòng trạng thái `APPROVED`.
- Chạy từ repository root.
- Dùng đúng Python của `benchmark_env`; không dùng Conda base/system Python.

## Cấu hình và input

- Schema/template: `experiments/_templates/`
- Experiment: `experiments/20260806_145124/`
- Expected output: thông báo validation passed; không tạo file output.

## Preflight

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -c \
  "import sys; print(sys.executable)"
```

Kết quả phải là
`/home/quannda/miniconda3/envs/benchmark_env/bin/python`.

## Chạy chính

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/governance/validate_experiment.py experiments/20260806_145124
```

## Resume

Validator không ghi state nên không cần resume. Sửa lỗi được báo rồi chạy lại
cùng command.

## Validation

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest \
  tests/governance/test_experiment_governance.py \
  tests/agents/test_coordination_contract.py \
  tests/agents/test_documentation.py -q
```

## Failure và rollback

Exit code khác 0 là fail-closed. Không đổi lifecycle sang `completed` cho đến
khi validator và test liên quan đều đạt. Nếu contract gây thêm paperwork hoặc
không phân biệt được approval thật, rollback template/code của Plan 01 và giữ
roadmap + baseline + handoff hiện hành.

## Cleanup

Không có cleanup và không có lệnh xóa trong runbook này.

