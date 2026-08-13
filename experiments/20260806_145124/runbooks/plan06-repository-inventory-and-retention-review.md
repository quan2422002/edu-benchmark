# Hướng dẫn vận hành — Kiểm kê kho mã nguồn và duyệt chính sách lưu giữ

Experiment: `20260806_145124`
Plan: `P06`

## Mục đích

Tạo lại bảng kiểm kê tệp, phát hiện nội dung trùng lặp từ 1 MiB trở lên và tổng
hợp đề xuất lưu giữ mà không xóa, di chuyển, ghi đè hoặc chuyển dữ liệu nguồn ra
ngoài kho mã nguồn.

## Điều kiện trước khi chạy

- Plan 06 có dòng trạng thái `APPROVED`.
- Repository đã được cài ở chế độ editable trong `benchmark_env`.
- Kiểm tra `git status --short` để phân biệt thay đổi của người dùng với đầu ra
  do công cụ tạo.
- Không cung cấp thông tin xác thực hoặc thêm tệp `.env` vào cấu hình quét.

## Cấu hình và đầu vào

- Cấu hình:
  `experiments/20260806_145124/configs/repository-hygiene-v1.yaml`.
- Phạm vi quét: toàn bộ thư mục làm việc, trừ `.git`, bộ nhớ đệm Python, thông
  tin xác thực,
  `document/`, Google Cloud SDK cục bộ và experiment quản trị
  `20260806_145124` đang ghi kết quả quét. Việc loại trừ phần quản trị của chính
  lượt quét giúp đầu ra ổn định khi tệp trạng thái, bàn giao và nhật ký điều phối
  được cập nhật sau đó.
- Công cụ chỉ đọc nội dung để tính SHA-256. Việc tìm nơi tham chiếu chỉ đọc các
  tệp văn bản UTF-8 được Git theo dõi và có dung lượng không quá 5 MiB.
- Tệp chưa được Git theo dõi và không thuộc nhóm lưu giữ đã cấu hình không được
  ghi đường dẫn hoặc SHA-256 vào đầu ra. Tệp kê khai chỉ ghi tổng số lượng và
  dung lượng của nhóm ngoài phạm vi này.
- Ba đầu ra:
  `repository_inventory.csv`, `duplicate_groups.csv` và
  `retention_manifest.json`.

## Kiểm tra trước khi chạy

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/repository_hygiene/inventory_repository.py --help
git status --short
```

## Chạy kiểm kê

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/repository_hygiene/inventory_repository.py \
  --config experiments/20260806_145124/configs/repository-hygiene-v1.yaml
```

Công cụ ghi từng đầu ra qua tệp tạm rồi thay thế nguyên tử. Thứ tự hàng và ID
nhóm trùng lặp là xác định đối với cùng một trạng thái thư mục làm việc.

## Tiếp tục sau khi gián đoạn

Không có trạng thái chạy cần tiếp tục. Chạy lại cùng lệnh sau khi xử lý nguyên
nhân lỗi. Công cụ không sửa tệp nguồn nên việc chạy lại không cần thao tác phục
hồi dữ liệu.

## Kiểm chứng

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest \
  tests/repository_hygiene/test_inventory.py
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/governance/validate_experiment.py experiments/20260806_145124
git diff --check
```

Trong `retention_manifest.json`, các điều kiện tối thiểu của lượt kiểm kê là:

- `mode` bằng `non_destructive_inventory`;
- `source_mutation_count` bằng `0`;
- `tracked_over_github_100mb_count` bằng `0`;
- `reachable_head_blobs.over_github_100mb_count` bằng `0`;
- `destructive_actions_executed` là danh sách rỗng.

## Khi có lỗi và cách quay lui

Nếu quá trình quét bị gián đoạn, tệp nguồn vẫn nguyên vẹn. Tệp tạm có hậu tố
`.tmp` trong `outputs/plan06/` không có giá trị nghiệm thu; có thể chạy lại công
cụ để xuất bộ kết quả hoàn chỉnh. Không dùng kết quả nếu checksum hoặc trạng
thái Git thay đổi trong lúc quét.

## Chính sách lưu giữ đã duyệt

Theo `P06-A001`, hướng dẫn này không có bước xóa hoặc di chuyển:

- 45 JSONL của experiment `20260727_170150` được giữ tại đúng đường dẫn hiện tại
  và bị Git bỏ qua bằng hai quy tắc giới hạn theo họ đầu ra;
- đầu ra OCR lịch sử, bản sao ảnh học liệu và SQLite tiếp tục được giữ cục bộ;
- sáu bản chụp lịch sử, 16 tệp trung gian/bản sao lưu và `main.xdv` tiếp tục
  được Git theo dõi;
- một DOCX và ba PDF cục bộ được bảo toàn như thay đổi của người dùng ngoài phạm
  vi; thông tin mô tả riêng lẻ của chúng không xuất hiện trong sản phẩm kiểm kê;
- không dùng Git LFS, không tạo `shared/local_archives/` và không viết lại lịch
  sử Git.

Nếu chính sách này thay đổi trong tương lai, cần một amendment mới và phê duyệt
đích cụ thể trước khi thêm bất kỳ lệnh xóa, di chuyển hoặc bỏ theo dõi nào.
