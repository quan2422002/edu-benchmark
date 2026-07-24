# Báo cáo Plan 02 — Multi-candidate migration pilot

Experiment: `20260722_000940`  
Ngày chạy: 23/07/2026  
Decision: `D02-01-multi-candidate-each-tutor-turn`  
Kết luận gate: `PASS`

## 1. Phạm vi

Pilot chọn deterministic 20/665 raw dialogue `pass`:

- 5 mẫu lớp 6;
- 5 mẫu lớp 7;
- 5 mẫu lớp 8;
- 5 mẫu lớp 9;
- bắt buộc có `HNMU-G7-R0189-STT6` và `HNMU-G9-R0237-STT12`, là hai mẫu có correction đã được duyệt.

Selection phủ raw dialogue sinh từ 2 đến 6 candidate. Danh sách và lý do chọn nằm ở:

`outputs/benchmark_conversion/multi_candidate_migration_pilot/pilot_sample_ids.csv`

## 2. Kết quả

| Chỉ số | Kết quả |
|---|---:|
| Raw dialogue | 20 |
| Candidate family | 20 |
| Candidate | 69 |
| Lỗi blocking | 0 |
| Mẫu có correction | 2 |

Candidate theo lớp:

| Lớp | Raw dialogue | Candidate |
|---|---:|---:|
| 6 | 5 | 13 |
| 7 | 5 | 20 |
| 8 | 5 | 16 |
| 9 | 5 | 20 |

Phân bố history:

| Số lượt history | Candidate |
|---:|---:|
| 0 | 20 |
| 2 | 20 |
| 4 | 13 |
| 6 | 9 |
| 8 | 5 |
| 10 | 2 |

## 3. Kiểm tra contract bằng code/regex

Post-write validator parse toàn bộ 20 source bằng regex `HS:/AI:` và so sánh exhaustive cả 69 candidate, xác nhận:

1. mọi raw dialogue bắt đầu bằng HS và role xen kẽ;
2. mỗi lượt AI sinh đúng một candidate;
3. `student_prompt` luôn là lượt HS đầu;
4. target AI02 có history rỗng;
5. mỗi target sau đó tăng history đúng hai lượt;
6. `gold_response` trùng nguyên văn target tutor turn;
7. không source-turn index thuộc suffix được ánh xạ vào candidate;
8. candidate CSV chỉ có 10 trường nội dung/khóa đã duyệt;
9. trace có quan hệ 1:1 với candidate;
10. hai correction khớp hash, correction ID và effective turn index.

Kết quả được lưu ở `candidate_mapping_validation.json`: 20/20 source parse thành công, 69/69 candidate ánh xạ chính xác, 0 failure. Không cần đọc thủ công từng candidate deterministic.

## 4. Hash artifact

| File | SHA-256 |
|---|---|
| `benchmark_candidate_splits.csv` | `2ac92c219078d3cc445e156ae397bb3629a1f0c9eed8a4d3b6f347c592f296d3` |
| `conversion_trace.csv` | `e85759d71e6c79a184ecdcbb79baf0d59221923a78176b201637912c11bb8978` |
| `conversion_dispositions.csv` | `150f7e607f252de073537725782fd2a39150d1722c170908bd22ffea9b111b16` |
| `dialogue_split_errors.csv` | `a283d26aff5ef9222c860b121f375d452893cd1feec01afc4e5b32ea52e509b1` |
| `candidate_mapping_validation.json` | `019c2afc49574ef73ed9a8220f4fbb0b23fd177c9c99118fad0b43531dbf061d` |

## 5. Quyết định gate

Migration pilot đạt toàn bộ gate kỹ thuật của Plan 02. Được phép chạy full conversion trên đúng 665 raw dialogue `pass`.

Đây vẫn là kiểm tra conversion, không phải xác nhận task/rubric hoặc chất lượng sư phạm của 69 candidate.
