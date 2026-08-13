# Hướng dẫn vận hành — Kiểm chứng và hoàn tất quá trình cải tổ

Thử nghiệm: `20260806_145124`
Kế hoạch: `P07`

## Mục đích

Kiểm chứng toàn bộ hợp đồng cải tổ từ một bản chụp chỉ chứa trạng thái Git dự
kiến, không phụ thuộc tệp cục bộ bị bỏ qua và không gọi API nhà cung cấp.

## Điều kiện trước khi chạy

- Kế hoạch 07 có dòng trạng thái `APPROVED`.
- Dùng đúng trình thông dịch:
  `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.
- Cài `requirements.txt`, sau đó cài kho mã nguồn ở chế độ editable bằng
  `python -m pip install --no-deps -e .`.
- Kiểm tra `git status --short` và không đưa thay đổi ngoài phạm vi vào snapshot.

## Kiểm chứng trong thư mục làm việc

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/governance/validate_experiment.py experiments/20260806_145124
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/benchmark_registry/promote_shared_benchmark.py --validate-only
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip check
git diff --check
```

Kiểm tra bước chuẩn bị chạy khả chuyển từ ngoài kho mã nguồn:

```bash
cd /tmp
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  -m edu_benchmark.experiment_runtime preflight \
  --config /home/quannda/Kaggle/edu-benchmark/experiments/20260806_145124/configs/section-v-ablation-v1.yaml
```

## Kiểm chứng bản chụp Git sạch

1. Chỉ đưa các tệp thuộc Plan 07 vào chỉ mục Git; không đưa tệp bản thảo hoặc tệp
   người dùng ngoài phạm vi vào.
2. Tạo cây Git tạm bằng `git write-tree` và xuất bằng `git archive` vào thư mục tạm
   dưới `/tmp`.
3. Dựng gói wheel từ bản chụp với:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip wheel \
  --no-deps --no-build-isolation . --wheel-dir <thu_muc_wheel_tam>
```

4. Cài gói wheel vào `benchmark_env`, kiểm tra nhập mô-đun từ `/tmp`, rồi chạy đúng hai
   phạm vi ngoại tuyến của `.github/workflows/offline-tests.yml`.
5. Chạy công cụ kiểm tra quản trị và benchmark dùng chung trong bản chụp.
6. Khôi phục bản cài editable của kho mã nguồn làm việc sau phép thử.

Bản chụp này không chứa `.git`, dữ liệu JSONL bị bỏ qua, tệp OCR cục bộ hoặc thay
đổi bản thảo của người dùng. Vì Plan 06 không chuyển dữ liệu ra kho ngoài, phép
thử phục hồi dữ liệu ngoài không áp dụng.

## Kiểm tra tài liệu và an toàn

- Kiểm tra liên kết cục bộ trong `README.md`, `ARCHITECTURE.md`, `AGENTS.md`,
  `shared/benchmark/README.md`, lộ trình và các kế hoạch hiện hành.
- Kiểm tra chuỗi điều hướng `README.md` → `shared/benchmark/README.md` → tệp kê khai
  của 18/665/2.028/1.400.
- Quét tệp Git theo dõi để tìm mẫu khóa riêng tư và khóa API thực tế. Chuỗi mẫu
  cấm dùng trong công cụ kiểm tra không phải thông tin xác thực và phải được phân loại
  là dương tính giả.
- Dùng kiểm kê Plan 06 để xác nhận không có tệp được theo dõi hoặc blob trong
  `HEAD` vượt 100 MiB.

## Khi có lỗi

- Lỗi nhập mô-đun từ gói wheel hoặc đường dẫn trỏ vào thư mục Conda thay vì kho mã nguồn:
  sửa ranh giới cấu hình/package, không thêm `sys.path`.
- Lỗi bản chụp nhưng thư mục làm việc đạt: coi là lỗi tái lập thật; không đóng plan
  chỉ dựa trên kết quả cục bộ.
- Lỗi liên kết hoặc số lượng sản phẩm chuẩn: dừng việc đóng thử nghiệm cho đến
  khi nguồn chuẩn và tài liệu thống nhất.
- Không tự động chạy lại model, xóa dữ liệu hoặc viết lại lịch sử Git.
