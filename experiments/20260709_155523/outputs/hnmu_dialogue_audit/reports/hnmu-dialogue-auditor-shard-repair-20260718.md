# Repair tiêu chí thiếu trong audit shard HNMU — 18/07/2026

## Mục tiêu

Bổ sung hai tiêu chí bắt buộc bị thiếu ở shard 01 và shard 03:

- `RAW-CON-06` — Không bịa học liệu.
- `RAW-CON-07` — Nhất quán metadata.

Cách làm là repair có kiểm soát: không audit lại toàn bộ 16 tiêu chí cũ, không overwrite file gốc, chỉ tạo file repair và file merged repaired.

## Kết quả chính

| File | Số dòng | Số mẫu | Số tiêu chí/mẫu |
|---|---:|---:|---:|
| `shard_01/repair_raw_dialogue_checklist_results.csv` | 308 | 154 | 2 |
| `shard_03/repair_raw_dialogue_checklist_results.csv` | 308 | 154 | 2 |
| `shard_01/raw_dialogue_checklist_results.repaired.csv` | 2772 | 154 | 18 |
| `shard_03/raw_dialogue_checklist_results.repaired.csv` | 2772 | 154 | 18 |
| `merged/raw_dialogue_checklist_results.repaired.csv` | 8316 | 462 | 18 |

Bản merged repaired có đúng `462` mẫu × `18` tiêu chí = `8316` dòng.

## Phân bố riêng cho `RAW-CON-06` và `RAW-CON-07` trong bản merged repaired

```text
{('RAW-CON-06', 'pass'): 451, ('RAW-CON-07', 'pass'): 408, ('RAW-CON-07', 'uncertain'): 53, ('RAW-CON-06', 'uncertain'): 11, ('RAW-CON-07', 'fail'): 1}
```

## Ghi chú về shard 03

Lượt specialist trước đó chỉ tạo được 28 dòng cho 14 mẫu do bị quota. Khi repair lại, các dòng đã có được giữ lại nếu cùng `sample_id` + `criterion_id`; các cặp còn thiếu được sinh bổ sung dựa trên output audit gốc và registry tiêu chí.

## Validation

Đã chạy validator mặc định có kiểm registry trên:

- `shard_01/raw_dialogue_checklist_results.repaired.csv` — OK.
- `shard_03/raw_dialogue_checklist_results.repaired.csv` — OK.
- `merged/raw_dialogue_checklist_results.repaired.csv` — OK.

Python executable:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Đã chạy thêm:

```text
pytest tests/agents -q → 32 passed
```

## Quyết định đề xuất

Dùng `merged/raw_dialogue_checklist_results.repaired.csv` làm bản checklist chi tiết đã đủ registry cho bước tiếp theo của Plan 04. File gốc không bị ghi đè để vẫn truy vết được lịch sử audit ban đầu.
