# Báo cáo Plan 02 — Full multi-candidate conversion

Experiment: `20260722_000940`  
Ngày hoàn thành: 23/07/2026; hardening sau hậu kiểm: 24/07/2026  
Trạng thái: `COMPLETED`  
Decision: `D02-01-multi-candidate-each-tutor-turn`

## 1. Kết quả chính

Plan 02 đã chuyển toàn bộ 665 raw dialogue `pass` thành pool 2.028 benchmark candidate sơ bộ, mỗi lượt AI tạo một candidate.

| Chỉ số | Kết quả |
|---|---:|
| Raw dialogue đầu vào | 665 |
| Candidate family | 665 |
| Candidate | 2.028 |
| Candidate ID duy nhất | 2.028 |
| Trace khớp candidate | 2.028 |
| Conversion disposition `converted` | 665 |
| Lỗi blocking | 0 |
| Correction được áp dụng | 2 mẫu |

Đây là pool trước task/rubric assignment và quality audit, chưa phải benchmark chính thức.

## 2. Phân bố

### Theo lớp

| Lớp | Raw dialogue | Candidate |
|---|---:|---:|
| 6 | 106 | 279 |
| 7 | 132 | 438 |
| 8 | 209 | 557 |
| 9 | 218 | 754 |
| **Tổng** | **665** | **2.028** |

### Candidate trên mỗi raw dialogue

| Candidate/raw dialogue | Raw dialogue |
|---:|---:|
| 2 | 292 |
| 3 | 167 |
| 4 | 105 |
| 5 | 85 |
| 6 | 14 |
| 7 | 2 |

### Độ dài history

| Số lượt history | Candidate |
|---:|---:|
| 0 | 665 |
| 2 | 665 |
| 4 | 373 |
| 6 | 206 |
| 8 | 101 |
| 10 | 16 |
| 12 | 2 |

## 3. Contract đã triển khai

- `student_prompt`: lượt HS đầu tiên, cố định trong một candidate family;
- `conversation_history`: đúng prefix từ lượt 2 đến trước target AI;
- `gold_response`: nguyên văn target AI;
- `gold_answer`: lấy từ `answer_sgv`;
- suffix sau target không được ánh xạ vào candidate;
- 297 raw dialogue kết thúc bằng HS vẫn conversion bình thường; source turn HS cuối không được dùng trong candidate;
- candidate ID: `BC-<sample_id>-AI<effective_turn_index_2_digits>`;
- candidate cùng `sample_id` là một family.

Parser chung chấp nhận hội thoại kết thúc bằng HS hoặc AI. Splitter legacy `final_tutor_response` của Plan 01 vẫn giữ riêng precondition lượt cuối là AI và đã qua regression test.

## 4. Schema và output

Candidate file có đúng 10 cột:

1. `benchmark_candidate_id`
2. `sample_id`
3. `grade`
4. `lesson`
5. `position`
6. `bloom_level`
7. `student_prompt`
8. `conversation_history`
9. `gold_response`
10. `gold_answer`

Provenance kỹ thuật nằm trong `conversion_trace.csv`; raw/correction/evidence không bị nhồi vào candidate CSV.

Full output:

`outputs/benchmark_conversion/full_v0/`

- `benchmark_candidate_splits.csv`
- `conversion_trace.csv`
- `conversion_dispositions.csv`
- `dialogue_split_errors.csv`
- `candidate_mapping_validation.json`
- `conversion_summary.json`
- `run_status.json`

## 5. Validation và reproducibility

- migration pilot: 20 raw dialogue → 69 candidate, 0 lỗi;
- full conversion được chạy hai lần liên tiếp;
- bốn CSV giữ nguyên SHA-256;
- candidate/trace ID khớp 1:1;
- 665/665 source bắt đầu bằng HS và parse role xen kẽ;
- xác nhận đúng 297 source kết thúc bằng HS;
- regex/structural validator xác nhận 2.028/2.028 mapping chính xác;
- output được publish nguyên bundle qua staging; `run_status.json` chỉ chuyển sang `complete` sau mọi gate;
- 89 test toàn repository pass.

Python executable:

`/home/quannda/miniconda3/envs/benchmark_env/bin/python`

SHA-256 full output:

| File | SHA-256 |
|---|---|
| `benchmark_candidate_splits.csv` | `6648569d5afe006acdd6e4129ee04ab2b27dfea89439c507a3b8f3b23c5eb63e` |
| `conversion_trace.csv` | `776ff800fb9e56ef93242094acff2584aefd983af90fdb532c8b3b52a602421d` |
| `conversion_dispositions.csv` | `3dc6f369e88a1e64f7cb510f991b6959184686d4b6b561a3806346d83d79846e` |
| `dialogue_split_errors.csv` | `a283d26aff5ef9222c860b121f375d452893cd1feec01afc4e5b32ea52e509b1` |
| `candidate_mapping_validation.json` | `6c246c548b4d9898df58a43133d1e1d33c818eca1af30f02ec99c2a0f29b3d8e` |

## 6. Hạn chế và handoff sang Plan 03

- 2.028 candidate chưa được gán task/rubric.
- Candidate sớm trong một dialogue có thể quá chung chung hoặc không phù hợp task.
- Hội thoại dài tạo nhiều candidate hơn, nên downstream phải báo cả candidate-macro và family-macro/weighting tương đương.
- Mọi candidate cùng `sample_id` phải nằm cùng split để tránh leakage.
- Candidate không khớp task/rubric phải có disposition rõ, không bị xóa âm thầm.
- Plan 03/04 dùng thống nhất `conversion_dispositions.csv`; Plan 03 chỉ nhận các family có `conversion_disposition = converted`.

Quyết định task/rubric, chất lượng sư phạm và giữ/loại cuối cùng vẫn thuộc các plan sau và thẩm quyền HNMU/UET.
