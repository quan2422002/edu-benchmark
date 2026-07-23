# Báo cáo Plan 01 — Pilot chuyển raw dialogue thành benchmark candidate

Ngày hoàn thành: 23/07/2026
Phạm vi: Tin học THCS lớp 6–9
Trạng thái: Plan 01 hoàn thành; chưa khuyến nghị chạy Plan 02 trên toàn bộ 665 mẫu cho đến khi chốt split policy.

## 1. Kết quả chính

Pipeline deterministic đã:

1. join hai snapshot audit lớp 6–7 và lớp 8–9;
2. tạo `conversion_input_pass_samples.csv` gồm đúng 665 `sample_id` duy nhất;
3. giữ riêng evidence chặn cấp mẫu và toàn bộ evidence cấp tiêu chí của phase 1;
4. chọn pilot 40 mẫu, đúng 10 mẫu mỗi lớp;
5. tạo 40 benchmark candidate hợp lệ theo `final_tutor_response`;
6. ghi toàn bộ hội thoại không tương thích vào `dialogue_split_errors.csv`.


| Gate                                       | Kết quả |
| ------------------------------------------ | --------: |
| Raw sample`pass` sau join                  |       665 |
| ID duy nhất                               |       665 |
| Input validation error blocking            |         0 |
| Blocking evidence bằng`[]`                |   665/665 |
| All-evidence khác rỗng                   |   665/665 |
| Pilot raw samples                          |        40 |
| Candidate hợp lệ                         |        40 |
| Candidate mỗi lớp                        |        10 |
| Lỗi split trong chính 40 mẫu đã chọn |         0 |

Phân bố input theo lớp là: lớp 6 có 106 mẫu, lớp 7 có 132 mẫu, lớp 8 có 209 mẫu và lớp 9 có 218 mẫu.

## 2. Contract đã triển khai

- Nhãn chất lượng canonical: `pass`, `need_human_review`, `failed`.
- `gold_answer` lấy nguyên văn từ `answer_sgv`.
- `student_prompt` là lượt `HS` đầu tiên.
- `conversation_history` là JSON-list các lượt sau prompt ban đầu và trước phản hồi mục tiêu; mỗi phần tử có `turn_index`, `role`, `content`.
- `gold_response` là lượt `AI` cuối và, trong strategy hiện tại, phải đồng thời là lượt cuối của raw dialogue.
- `benchmark_candidate_id` có dạng `BC-<sample_id>-FINAL`.
- `raw_dialogue` được giữ nguyên để truy vết.
- Nếu có correction do người phụ trách duyệt, `conversion_dialogue` chứa bản hiệu lực để parse và `dialogue_correction_ids` trỏ tới overlay có hash; snapshot và `raw_dialogue` không đổi.
- Plan 01 không tạo evidence cấp candidate hoặc `candidate_quality_decision`.

Hai trường raw-audit evidence:

- `raw_audit_blocking_evidence_fragment_ids`: chuẩn hóa từ cột cấp mẫu của phase 1; cả 665 mẫu `pass` đều là `[]`.
- `raw_audit_all_evidence_fragment_ids`: union có sắp xếp và loại trùng từ checklist chi tiết. Một số cell lịch sử chứa nhiều ID phân cách bằng dấu `;`; pipeline tách các cell này thành từng fragment ID trước khi union. Số fragment mỗi mẫu: 457 mẫu có 1, 73 mẫu có 2, 124 mẫu có 3, 9 mẫu có 4 và 2 mẫu có 5.

Trong thống kê pilot, `single evidence` nghĩa là `raw_audit_all_evidence_fragment_ids` có đúng một fragment ID duy nhất; `multiple evidence` nghĩa là có từ hai ID trở lên. Đây vẫn là evidence raw audit phase 1, không phải blocking evidence hoặc evidence cấp benchmark candidate.

## 3. Pilot và khả năng tái lập

Bộ chọn dùng thứ tự `sample_id` và greedy scoring cố định để phủ mức nhận thức, nhóm số lượt, số lượng evidence và bài học. Kết quả có đủ `Biết`, `Hiểu`, `Vận dụng` ở từng lớp. “Tương thích” ở đây chỉ có nghĩa là thỏa shape của `final_tutor_response`, không phải đã được duyệt chất lượng benchmark. Lớp 6 không có mẫu tương thích thuộc nhóm `>=10` lượt. Trong toàn bộ tập tương thích, lớp 8 và 9 chỉ có single raw-audit evidence nên pilot không thể chọn multiple evidence. Các fallback được ghi trong `pilot_selection_summary.json`.

Hai lần chạy cùng input tạo cùng candidate output. SHA-256 của lần chạy hoàn thành:

- `conversion_input_pass_samples.csv`: `d3f156dc80ce5815d79c07d23f75cc856de34241cf89155479daa25a17a95b57`
- `pilot_v0/benchmark_candidate_splits.csv`: `404c293de5149b0f78758acfdfd658ca68eccf1767b0dc90b9703203cbfc6ace`
- `pilot_v0/pilot_sample_ids.csv`: `47acabd9b0c3abe4b501221ebe9d0cb533adb45e63c3ad3c41330195a7f5701e`

## 4. Blocker phát hiện trước Plan 02

Có 297/665 mẫu `pass` (44,66%) còn không tương thích với contract strict hiện tại sau hai correction được duyệt:


| Lớp      | Tổng pass | Tương thích | Không tương thích |
| --------- | ---------: | -------------: | --------------------: |
| 6         |        106 |             65 |                    41 |
| 7         |        132 |             75 |                    57 |
| 8         |        209 |            101 |                   108 |
| 9         |        218 |            127 |                    91 |
| **Tổng** |    **665** |        **368** |               **297** |

297 mẫu còn lại đều có lượt cuối là `HS`, không phải `AI`. Hai lỗi `non_alternating_roles` đã được sửa qua `dialogue_corrections.csv` theo quyết định của người phụ trách dự án:

- `HNMU-G7-R0189-STT6`: gộp lượt AI 4–5;
- `HNMU-G9-R0237-STT12`: đổi nhãn lượt 8 từ `HS` thành `AI`.

Đây không phải lỗi raw-audit decision: các mẫu có thể đạt tiêu chí chất lượng phase 1 nhưng không đáp ứng shape của một split strategy được định nghĩa ở phase 2.

## 5. Khuyến nghị cho Plan 02

Chưa nên chạy mục tiêu “full conversion 665 mẫu” bằng nguyên contract `final_tutor_response`. Cần người phụ trách dự án chốt một trong các hướng:

1. giữ strict contract và chỉ conversion 368 mẫu tương thích;
2. thêm strategy riêng cho hội thoại kết thúc bằng `HS`, lấy lượt AI gần cuối làm response mục tiêu và giữ lượt HS sau đó như outcome/provenance, không đưa nó ngược vào context;
3. chuyển 297 mẫu sang hàng chờ HNMU/UET xác nhận điểm cắt trước conversion.

Điều tra bổ sung cho 297 lượt cuối nằm trong `reports/plan01-last-student-turn-investigation.md` và `outputs/benchmark_conversion/last_student_turn_analysis.csv`. Sau khi có quyết định split policy, cần cập nhật/duyệt Plan 02 và test contract tương ứng trước khi chạy full-scale.

## 6. Validation

Đã chạy bằng:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Kết quả:

- `tests/benchmark_conversion`: 23 passed;
- toàn bộ test repository: 83 passed;
- build input: 665 rows, 665 unique IDs, 0 blocking errors;
- pilot: 40 selected, 40 candidates, 10 per grade, 0 selected-split errors;
- candidate row contract violations: 0.

Kết quả agent-assisted audit và candidate pilot vẫn là dữ liệu nghiên cứu tạm thời, chưa thay thế phê duyệt chuyên môn/sư phạm của HNMU/UET.
