# Runbook — Plan 03 / Shared benchmark promotion

Experiment: `20260806_145124`
Plan: `P03`

## Mục đích

Sinh lại `shared/benchmark/` từ các source artifact đã khóa, validate count,
checksum, join và authority mà không sửa source experiment.

## Điều kiện trước khi chạy

- Baseline Plan 03 có dòng `APPROVED`.
- Chạy từ repository root bằng đúng `benchmark_env`.
- Source experiment `20260722_000940` và `20260727_170150` còn nguyên.
- Không cần credential hoặc model API.

## Chạy promotion

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/benchmark_registry/promote_shared_benchmark.py
```

Lệnh dựng toàn bộ bundle trong staging directory rồi swap vào
`shared/benchmark/`. Chạy lại cùng source phải tạo cùng payload, manifest và
registry byte-for-byte.

## Validation

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/benchmark_registry/promote_shared_benchmark.py --validate-only
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest -q \
  tests/benchmark_registry
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/governance/validate_experiment.py experiments/20260806_145124
```

Gate bắt buộc: 18 criteria; 665 Phase-1 dialogue; 2.028 candidate và trace;
665 disposition; eligibility 1.400/628/0; 655 family trong selection; duplicate
ID bằng 0; mọi checksum manifest khớp file.

## Rollback

Không xóa source experiment. Nếu consumer shared gặp lỗi, truyền lại
`--candidate-input` cũ cho CLI grounding pool hoặc khôi phục default path theo
deprecation map trong `shared/benchmark/README.md`.

