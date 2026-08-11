# Runbook — Plan 04 / Phân tích Section V bằng cấu hình khả chuyển

Experiment: `20260806_145124`
Plan: `P04`

## Mục đích

Tái lập phân tích Section V trên 1.400 mẫu từ ba đầu vào đã khóa mà không gọi API
mô hình. Cùng một tệp cấu hình phải được xác định giống nhau khi chạy từ thư mục
gốc của kho mã nguồn hoặc từ một thư mục làm việc khác.

## Điều kiện trước khi chạy

- Plan 04 có dòng trạng thái `APPROVED`.
- Gói Python đã được cài ở chế độ `editable` trong môi trường Conda
  `benchmark_env`.
- Ba đầu vào lịch sử trong mục dưới đây còn tồn tại và khớp mã băm.
- Không cần thông tin xác thực, biến môi trường bí mật hoặc quyền gọi nhà cung
  cấp mô hình.

Xác nhận đúng trình thông dịch sau khi kích hoạt môi trường:

```bash
conda activate benchmark_env
python -c "import sys; assert sys.prefix.endswith('/benchmark_env'); print(sys.executable)"
```

## Cấu hình và đầu vào

- Cấu hình:
  [`section-v-ablation-v1.yaml`](../configs/section-v-ablation-v1.yaml)
- Phiên bản: `v1`
- SHA-256 cấu hình:
  `fe70465bed7b1e8898eeb75e77511bc3ee5a06591b825ff42221bfb48d8918a2`
- Tập ứng viên: 1.400 dòng, SHA-256
  `7dec13c3cc3a53337bc6c5fdf800e6c89856f49a3b6b0626dca885e59cb0fed9`
- Phán quyết Gemini: 4.200 dòng, SHA-256
  `4c2e7f5b9ffd68a1dad5f6999700864683536386df6331ec16a0c6e279902936`
- Phán quyết GPT: 4.200 dòng, SHA-256
  `ebfc8bd0276b105ef3348c2ec0227571ce7267b186d60490fc2107633a104ab9`
- Kết quả dự kiến:
  `outputs/plan04/section_v_results.json`
- Manifest lần chạy:
  `outputs/plan04/section_v_run_manifest.json`

Mọi đường dẫn trong cấu hình và `manifest` đều tính từ thư mục gốc của kho mã
nguồn; cấu hình không chứa đường dẫn tuyệt đối của máy người phát triển.

## Kiểm tra trước khi chạy (`preflight`)

Từ thư mục gốc của kho mã nguồn:

```bash
python -m edu_benchmark.experiment_runtime preflight \
  --config experiments/20260806_145124/configs/section-v-ablation-v1.yaml
```

Từ một thư mục làm việc khác, dùng nguyên tham số cấu hình tương đối:

```bash
cd /tmp
python -m edu_benchmark.experiment_runtime preflight \
  --config experiments/20260806_145124/configs/section-v-ablation-v1.yaml
```

Hai lệnh phải in cùng `config_sha256` và `preflight_fingerprint`. Bước kiểm tra
dừng trước khi ghi kết quả nếu đầu vào thiếu, sai mã băm, sai số dòng, đường dẫn
thoát khỏi kho mã nguồn hoặc cấu hình chứa trường thông tin xác thực bị cấm.
Nếu run manifest hiện có đã ở trạng thái `completed`, preflight phải in
`completed_manifest_preserved: true` và không thay đổi nội dung hoặc mã băm của
manifest đó. Trường `completed_manifest_matches_preflight` phải là `true` và
`checks.completed_manifest` phải là `matched_preserved` nếu manifest khớp
fingerprint hiện tại. Giá trị `false` cùng `stale_preserved` nghĩa là preflight
của môi trường hiện tại đạt nhưng kết quả cũ phải được chạy lại trước khi
`validate` có thể đạt.

Preflight chỉ trả `preflight_passed` sau khi pipeline, runner, đúng ba input
role/format, output schema, resume policy, parameter và provenance offline đều
hợp lệ. Khi một điều kiện không đạt, CLI trả exit code `2` và JSON lỗi có
`status: preflight_failed`; không ghi manifest preflight mới.

## Chạy chính

Lệnh này có thể chạy từ mọi thư mục làm việc sau khi gói Python đã được cài:

```bash
python -m edu_benchmark.experiment_runtime run \
  --config experiments/20260806_145124/configs/section-v-ablation-v1.yaml
```

Điểm vào tương thích dưới `scripts/` chỉ dùng khi đang ở thư mục gốc của kho mã
nguồn:

```bash
python scripts/benchmark_evaluation/analyze_section_v_ablation.py \
  --config experiments/20260806_145124/configs/section-v-ablation-v1.yaml
```

## Tiếp tục lần chạy (`resume`)

Quy trình này không hỗ trợ tiếp tục ở cấp mẫu vì nó là phép dựng lại ngoại tuyến,
xác định và chạy xong trong một lượt ngắn. Kết quả chỉ được thay thế nguyên tử
sau khi đủ 1.400 mẫu, mỗi bộ phán quyết đủ 4.200 dòng và kết quả tương đương mốc
đối chiếu. `Manifest` ghi rõ `resume.policy: unsupported` và không giả lập trạng
thái chờ xử lý.

Các trình chạy sinh/chấm trả phí được giữ ở trạng thái `compatibility` và tiếp
tục dùng cơ chế chỉ chạy ID chưa hoàn tất của chính chúng; Plan 04 không chạy lại
chúng.

## Kiểm tra kết quả

```bash
python -m edu_benchmark.experiment_runtime validate \
  --config experiments/20260806_145124/configs/section-v-ablation-v1.yaml
```

Lệnh kiểm tra phải xác nhận:

- preflight fingerprint hiện tại khớp fingerprint đã lưu, bao gồm cấu hình, đầu
  vào và mã băm các tệp code đã đăng ký;
- các bản ghi config, input, output, provenance, resume, equivalence và secret
  scan trong manifest khớp hợp đồng hiện tại;
- mã băm tệp và mã băm ngữ nghĩa của output khớp manifest;
- các anchor Section V đều `passed`;
- SHA-256 ngữ nghĩa của kết quả mới bằng mốc đối chiếu sau khi chỉ chuẩn hóa
  đường dẫn tuyệt đối của kho mã nguồn thành đường dẫn tương đối;
- không có thông tin xác thực được ghi vào tệp.

## Lỗi và cách quay lui

- Nếu đầu vào hoặc cấu hình sai, bước kiểm tra dừng đóng và không chạy phân tích.
- Nếu kết quả khác mốc đối chiếu ngoài phần đường dẫn truy xuất nguồn, trình chạy
  dừng trước khi công bố kết quả mới.
- Mốc đối chiếu tại experiment `20260727_170150` luôn chỉ đọc và không bị ghi đè.
- Tệp bọc lệnh trả phí cũ không bị sửa hoặc xóa; chúng vẫn là đường quay lui cho
  vòng đời lịch sử đến Plan 07.

## Dọn dẹp

Không có bước dọn dẹp tự động. Hai đầu ra Plan 04 đều nhỏ, được đăng ký làm bằng
chứng tái lập và phải được giữ lại để duyệt.
