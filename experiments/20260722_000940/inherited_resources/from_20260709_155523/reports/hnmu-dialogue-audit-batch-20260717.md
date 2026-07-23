# Báo cáo kiểm toán tổng thể dữ liệu hội thoại HNMU lớp 6–7

Trạng thái: `draft_audit_repaired_strict_synced` — đã có kiểm toán cơ học v0, checklist chi tiết sau repair tiêu chí và bảng tổng hợp agent-level đã strict-sync từ checklist; chưa thay thế HNMU/UET review.

Ngày tạo báo cáo v0: 17/07/2026
Ngày cập nhật repair: 19/07/2026, dựa trên repair shard ngày 18/07/2026  
Ngày cập nhật strict-sync: 20/07/2026

## 1. Phạm vi

- Lớp xử lý trong vòng này: 6, 7.
- File raw nhìn thấy trong thư mục:
  - `shared/raw_data/HNMU-teacher_dialog_samples/Lớp 6.xlsx`
  - `shared/raw_data/HNMU-teacher_dialog_samples/Lớp 7.xlsx`
  - `shared/raw_data/HNMU-teacher_dialog_samples/Lớp 8.xlsx`
  - `shared/raw_data/HNMU-teacher_dialog_samples/Lớp 9.xlsx`
- File đã xử lý trong vòng audit này:
  - `shared/raw_data/HNMU-teacher_dialog_samples/Lớp 6.xlsx`
  - `shared/raw_data/HNMU-teacher_dialog_samples/Lớp 7.xlsx`

Các file lớp 8–9 được xử lý trong vòng audit riêng tại `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/`, không ghi đè kết quả lớp 6–7.

## 2. Kết quả cơ học v0

Kết quả cơ học/truy xuất sơ bộ ban đầu vẫn được giữ nguyên để truy vết:

- Số dòng hội thoại được đọc: 462.
- Số issue thiếu trường/định dạng: 2.
- Số cặp trùng/gần trùng ứng viên: 0.
- Số mẫu trong hàng đợi review v0: 2.
- Phân bố quyết định chất lượng v0: `pass`: 460, `fail`: 2.
- Các trục coverage đã xuất: `bloom_band`, `grade`, `lesson_by_grade`, `source_file`, `topic`.

Lưu ý: `quality_check_results.csv` và `hnmu_review_queue.csv` ở root output vẫn là kết quả tổng hợp cơ học/truy xuất v0. File chính ở cấp mẫu sau agent audit là `agent_shard_audit/merged/quality_check_suggestions.csv`; file này đã dùng schema canonical với cột `quality_decision` và nên được ưu tiên khi cần xem kết quả ngữ nghĩa/sư phạm theo checklist.

## 3. Cập nhật sau repair checklist chi tiết

Sau khi phát hiện shard 01 và shard 03 thiếu hai tiêu chí bắt buộc, đã bổ sung:

- `RAW-CON-06` — Không bịa học liệu.
- `RAW-CON-07` — Nhất quán metadata.

File checklist chi tiết đã sửa đầy đủ là:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/raw_dialogue_checklist_results.repaired.csv
```

Kết quả sau repair:


| Mục                                      | Kết quả |
| ----------------------------------------- | --------: |
| Số mẫu                                  |       462 |
| Số tiêu chí bắt buộc trên mỗi mẫu |        18 |
| Tổng số dòng checklist chi tiết       |      8316 |
| Số dòng`pass`                           |      7923 |
| Số dòng`uncertain`                      |       382 |
| Số dòng`fail`                           |         8 |
| Số dòng`not_applicable`                 |         3 |

Phân bố riêng cho hai tiêu chí vừa repair:


| Tiêu chí                             | `pass` | `uncertain` | `fail` |
| -------------------------------------- | -----: | ----------: | -----: |
| `RAW-CON-06` — Không bịa học liệu |    451 |          11 |      0 |
| `RAW-CON-07` — Nhất quán metadata   |    408 |          53 |      1 |

Ý nghĩa diễn giải trước khi strict-sync:

- Tuy nhiên, từ thời điểm này, nếu cần xem checklist chi tiết theo từng tiêu chí, nên dùng file repaired thay vì file merged cũ.
- Các dòng `uncertain`/`fail` trong checklist repaired là căn cứ để tạo hàng đợi review mới trước khi chuyển sang Plan 06.

## 4. Strict-sync từ checklist chi tiết sang kết quả tổng hợp

Ngày 20/07/2026, bảng tổng hợp agent-level đã được đồng bộ lại từ checklist chi tiết theo rule strict:

- có ít nhất một tiêu chí `fail` → mẫu tổng thể là `failed`;
- không có `fail` nhưng có ít nhất một tiêu chí `uncertain` → mẫu tổng thể là `need_human_review`;
- toàn bộ tiêu chí là `pass` hoặc `not_applicable` → mẫu tổng thể là `pass`.

`confidence_score` tổng thể là độ tin cậy của quyết định tổng thể:

- `failed`: confidence thấp nhất trong các tiêu chí `fail`;
- `need_human_review`: confidence thấp nhất trong các tiêu chí `uncertain`;
- `pass`: confidence thấp nhất trong toàn bộ tiêu chí của mẫu.

Kết quả tổng hợp sau strict-sync:

| Quyết định tổng thể | Số mẫu | Diễn giải |
| --- | ---: | --- |
| `pass` | 238 | Không còn tiêu chí `fail` hoặc `uncertain`; có thể xem xét chuyển đổi thử, nhưng vẫn chưa thay thế phán quyết chuyên môn. |
| `need_human_review` | 222 | Có ít nhất một tiêu chí `uncertain`; cần HNMU/UET xem lại điểm chưa chắc trước khi dùng làm đầu vào chính thức cho Plan 06. |
| `failed` | 2 | Có lỗi rõ ở ít nhất một tiêu chí; không nên chuyển đổi trong batch hiện tại nếu chưa sửa/xác nhận lại. |

Hàng đợi HNMU/UET xem lại sau strict-sync có 224 mẫu, gồm 222 mẫu `need_human_review` và 2 mẫu `failed`.

File kiểm tra consistency xác nhận không còn mâu thuẫn giữa checklist chi tiết và bảng tổng hợp:

```text
experiments/20260709_155523/reports/quality-suggestion-consistency-audit-lop6-7-20260720.md
```

## 5. Diễn giải coverage theo SGK/SGV

Coverage theo chủ đề được ánh xạ qua:

```text
shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv
```

Tức là coverage theo mục lục SGK/SGV đã chuẩn hóa, không lấy dữ liệu thô HNMU làm nguồn chuẩn. Dữ liệu HNMU chỉ cung cấp mẫu cần kiểm toán; trường `Bài` trong dữ liệu thô được dùng để đối chiếu sang registry SGK/SGV.

Phân bố theo chủ đề trong batch lớp 6–7:

- Ứng dụng tin học: 182 mẫu (39.39%); mã chủ đề: `TIN6-CD05;TIN7-CD04`; trạng thái registry: `needs_hnmu_review`.
- Máy tính và cộng đồng: 84 mẫu (18.18%); mã chủ đề: `TIN6-CD01;TIN7-CD01`; trạng thái registry: `needs_hnmu_review`.
- Giải quyết vấn đề với sự trợ giúp của máy tính: 84 mẫu (18.18%); mã chủ đề: `TIN6-CD06;TIN7-CD05`; trạng thái registry: `needs_hnmu_review`.
- Tổ chức lưu trữ, tìm kiếm và trao đổi thông tin: 56 mẫu (12.12%); mã chủ đề: `TIN6-CD03;TIN7-CD02`; trạng thái registry: `needs_hnmu_review`.
- Mạng máy tính và Internet: 28 mẫu (6.06%); mã chủ đề: `TIN6-CD02`; trạng thái registry: `needs_hnmu_review`.
- Đạo đức, pháp luật và văn hoá trong môi trường số: 28 mẫu (6.06%); mã chủ đề: `TIN6-CD04;TIN7-CD03`; trạng thái registry: `needs_hnmu_review`.

Coverage theo bài học được ghi ở trục `lesson_by_grade`, vì bài học phụ thuộc vào từng lớp. Do đó các dòng bài học trong `coverage_summary.csv` luôn kèm `grade`, `grade_label`, `topic_id`, `topic_label`, `lesson_id` và `lesson_label`.

## 6. Output chính

Các bảng audit cơ học nằm trong:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit
```

Các file quan trọng:

- `checklists/`: snapshot checklist và registry tiêu chí dùng cho lượt audit này.
- `coverage_summary.csv`: xem độ phủ theo lớp, chủ đề, bài học, mức nhận thức, nguồn file.
- `missing_field_report.csv`: xem lỗi thiếu trường/định dạng.
- `duplicate_candidates.csv`: xem cặp trùng/gần trùng ứng viên.
- `quality_check_results.csv`: kết luận chất lượng cơ học/truy xuất v0 theo mẫu.
- `hnmu_review_queue.csv`: hàng đợi review v0 từ kiểm toán cơ học/truy xuất.

Các bảng specialist/shard nằm trong:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit
```

File quan trọng nhất sau repair:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/raw_dialogue_checklist_results.repaired.csv
```

Các file agent-level tổng hợp sau strict-sync:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/quality_check_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/hnmu_review_queue_suggestions.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/merge_validation_summary.json
```

Report repair riêng:

```text
experiments/20260709_155523/reports/hnmu-dialogue-auditor-shard-repair-20260718.md
```

## 7. Validation

Đã chạy validator có kiểm registry trên:

- `shard_01/raw_dialogue_checklist_results.repaired.csv` — OK.
- `shard_03/raw_dialogue_checklist_results.repaired.csv` — OK.
- `merged/raw_dialogue_checklist_results.repaired.csv` — OK.

Đã chạy test agent:

```text
pytest tests/agents -q → 32 passed
```

Python executable dùng để chạy validation:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

## 8. Lưu ý diễn giải

- `pass` trong bản v0 chỉ có nghĩa là mẫu qua các kiểm tra cơ học và truy xuất sơ bộ; chưa phải xác nhận chuyên môn cuối cùng.
- Checklist repaired giúp bảo đảm mỗi mẫu có đủ 18 tiêu chí bắt buộc; bảng tổng hợp agent-level đã được strict-sync từ checklist này.
- Evidence học liệu hiện vẫn cần hiểu là nguồn phục vụ kiểm toán, không thay thế quyết định chuyên môn của HNMU/UET.
- Các mẫu có `need_human_review` hoặc `failed` trong `quality_check_suggestions.csv` cần được đưa vào review queue trước khi chuyển đổi thành mẫu benchmark.
