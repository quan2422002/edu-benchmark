# D02-01 — Multi-candidate conversion tại mỗi lượt gia sư

Experiment: `20260722_000940`  
Trạng thái: `APPROVED`  
Người quyết định: người phụ trách dự án  
Ngày quyết định: 23/07/2026  
Plan áp dụng: Plan 02

## Quyết định

1. Chỉ dùng 665 raw dialogue có quality decision `pass` từ phase 1.
2. Dùng `split_strategy = each_tutor_turn`.
3. Mỗi lượt AI trong `conversion_dialogue` tạo đúng một benchmark candidate.
4. `student_prompt` luôn là lượt HS đầu tiên.
5. Với target AI ở effective turn `k`, `conversation_history` gồm đúng các lượt từ 2 đến `k - 1`; `gold_response` là nội dung lượt `k`.
6. Mọi lượt sau target không được đưa vào candidate đó.
7. Lượt HS cuối của hội thoại không được dùng ở bất kỳ đâu trong candidate; không thêm `post_response_student_outcome`.
8. `gold_answer` lấy từ `answer_sgv`.
9. Candidate content nằm trong `benchmark_candidate_splits.csv`; provenance kỹ thuật và correction nằm trong `conversion_trace.csv`.
10. Candidate cùng `sample_id` là một family và phải nằm cùng downstream split.
11. Candidate không khớp task/rubric ở Plan 03 phải có disposition rõ ràng trước khi bị loại khỏi benchmark cuối.

## Candidate ID và effective turn

Candidate ID có dạng:

`BC-<sample_id>-AI<effective_turn_index_2_digits>`

Effective turn index được tính sau khi áp dụng correction overlay đã duyệt. ID và trace phải deterministic khi input, correction table và policy version không đổi.

## Correction kế thừa

Plan 02 chỉ kế thừa hai correction đã được duyệt:

- `HNMU-G7-R0189-STT6`: gộp hai lượt AI liên tiếp;
- `HNMU-G9-R0237-STT12`: đổi nhãn lượt giữa từ HS thành AI.

Correction phải tiếp tục được bảo vệ bằng SHA-256 của raw dialogue nguồn. Không được tự tạo correction mới trong conversion.

## Versioning và rollback

- Không ghi đè output `pilot_v0/` của Plan 01.
- Migration pilot ghi vào `multi_candidate_migration_pilot/`.
- Full run Plan 02 ghi vào `full_v0/`.
- Nếu contract target/history/ID thay đổi, phải tạo decision/version mới; không đổi semantics âm thầm trong `full_v0`.
- Có thể rollback bằng cách bỏ output Plan 02 và tiếp tục dùng artifact Plan 01; raw dialogue và inherited snapshot không bị sửa.

## Phạm vi thẩm quyền

Quyết định này chỉ chốt conversion kỹ thuật. Nó không xác nhận task/rubric suitability, chất lượng sư phạm hoặc tư cách benchmark chính thức của candidate. Các quyết định đó thuộc Plan 03–05 và review HNMU/UET.
