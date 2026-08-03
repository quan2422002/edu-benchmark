# Báo cáo Plan 03 — Phân tích full run requirement-scoring

Trạng thái: `AWAITING_UET_DISPOSITION`

## 1. Evidence — bằng chứng trực tiếp

- Bundle có 2028 candidate thuộc
  665 family.
- Có 12168 score; mọi ID, join, request hash và
  `user_prompt` đều qua validator.
- Failure hiện hành: 0; lỗi lịch sử được
  giữ riêng: 1.
- Đây là một run duy nhất của `gemini-3.5-flash`; các score là đề xuất
  của model, không phải ground truth.

### 1.1. Phân bố theo nguyên tắc

| Nguyên tắc | Số bắt buộc | Candidate-macro | Family-macro | Số thay thế | Trung vị |
| --- | --- | --- | --- | --- | --- |
| PRINCIPLE-CHALLENGE | 17 | 0.008 | 0.006 | 62 | 2.0 |
| PRINCIPLE-EXPLANATION | 1115 | 0.550 | 0.594 | 612 | 4.0 |
| PRINCIPLE-MODELLING | 107 | 0.053 | 0.050 | 620 | 2.0 |
| PRINCIPLE-PRACTICE | 60 | 0.030 | 0.025 | 428 | 2.0 |
| PRINCIPLE-FEEDBACK | 1412 | 0.696 | 0.670 | 95 | 5.0 |
| PRINCIPLE-QUESTIONING | 976 | 0.481 | 0.462 | 1036 | 3.0 |

### 1.2. Toàn bộ tập nguyên tắc bắt buộc quan sát được

`rare_required_set` nghĩa là dưới 5 candidate
hoặc dưới 3 family.

| Tập nguyên tắc | Candidate | Tỷ lệ | Family | Family-macro | Hiếm |
| --- | --- | --- | --- | --- | --- |
| PRINCIPLE-FEEDBACK\|PRINCIPLE-QUESTIONING | 584 | 0.288 | 379 | 0.265 |  |
| PRINCIPLE-EXPLANATION\|PRINCIPLE-FEEDBACK | 512 | 0.252 | 356 | 0.266 |  |
| PRINCIPLE-EXPLANATION | 290 | 0.143 | 279 | 0.164 |  |
| PRINCIPLE-EXPLANATION\|PRINCIPLE-QUESTIONING | 144 | 0.071 | 138 | 0.077 |  |
| PRINCIPLE-FEEDBACK | 120 | 0.059 | 105 | 0.048 |  |
| PRINCIPLE-EXPLANATION\|PRINCIPLE-FEEDBACK\|PRINCIPLE-QUESTIONING | 97 | 0.048 | 91 | 0.050 |  |
| PRINCIPLE-QUESTIONING | 92 | 0.045 | 85 | 0.046 |  |
| PRINCIPLE-EXPLANATION\|PRINCIPLE-MODELLING | 44 | 0.022 | 43 | 0.023 |  |
| PRINCIPLE-PRACTICE\|PRINCIPLE-FEEDBACK | 26 | 0.013 | 25 | 0.011 |  |
| PRINCIPLE-MODELLING\|PRINCIPLE-QUESTIONING | 16 | 0.008 | 16 | 0.007 |  |
| PRINCIPLE-PRACTICE\|PRINCIPLE-FEEDBACK\|PRINCIPLE-QUESTIONING | 14 | 0.007 | 13 | 0.006 |  |
| PRINCIPLE-MODELLING\|PRINCIPLE-FEEDBACK | 12 | 0.006 | 10 | 0.005 |  |
| PRINCIPLE-EXPLANATION\|PRINCIPLE-MODELLING\|PRINCIPLE-FEEDBACK | 10 | 0.005 | 10 | 0.006 |  |
| PRINCIPLE-MODELLING\|PRINCIPLE-FEEDBACK\|PRINCIPLE-QUESTIONING | 10 | 0.005 | 7 | 0.004 |  |
| PRINCIPLE-CHALLENGE\|PRINCIPLE-FEEDBACK\|PRINCIPLE-QUESTIONING | 9 | 0.004 | 9 | 0.004 |  |
| PRINCIPLE-CHALLENGE\|PRINCIPLE-FEEDBACK | 8 | 0.004 | 8 | 0.003 |  |
| PRINCIPLE-EXPLANATION\|PRINCIPLE-PRACTICE\|PRINCIPLE-FEEDBACK | 8 | 0.004 | 8 | 0.003 |  |
| __EMPTY__ | 8 | 0.004 | 8 | 0.005 |  |
| PRINCIPLE-MODELLING | 7 | 0.003 | 7 | 0.002 |  |
| PRINCIPLE-EXPLANATION\|PRINCIPLE-MODELLING\|PRINCIPLE-QUESTIONING | 5 | 0.002 | 5 | 0.002 |  |
| PRINCIPLE-PRACTICE\|PRINCIPLE-QUESTIONING | 5 | 0.002 | 5 | 0.002 |  |
| PRINCIPLE-EXPLANATION\|PRINCIPLE-PRACTICE | 3 | 0.001 | 3 | 0.001 | có |
| PRINCIPLE-EXPLANATION\|PRINCIPLE-MODELLING\|PRINCIPLE-PRACTICE | 1 | 0.000 | 1 | 0.001 | có |
| PRINCIPLE-EXPLANATION\|PRINCIPLE-MODELLING\|PRINCIPLE-PRACTICE\|PRINCIPLE-FEEDBACK | 1 | 0.000 | 1 | 0.001 | có |
| PRINCIPLE-MODELLING\|PRINCIPLE-PRACTICE\|PRINCIPLE-FEEDBACK | 1 | 0.000 | 1 | 0.000 | có |
| PRINCIPLE-PRACTICE | 1 | 0.000 | 1 | 0.000 | có |

### 1.3. Trạng thái đủ điều kiện đi tiếp

| Trạng thái | Số lượng | Tỷ lệ |
| --- | --- | --- |
| eligible_without_plan03_review | 1400 | 0.690 |
| needs_uet_review | 628 | 0.310 |
| blocked | 0 | 0.000 |

### 1.4. Lý do cần review hoặc bị chặn

| Lý do | Số candidate |
| --- | --- |
| feedback_confirmation_only | 592 |
| questioning_without_answer_dependency | 10 |
| no_required_principle | 8 |
| high_score_modal_conflict:PRINCIPLE-EXPLANATION | 7 |
| high_score_modal_conflict:PRINCIPLE-FEEDBACK | 7 |
| rare_required_set | 7 |
| high_score_missing_counterfactual:PRINCIPLE-QUESTIONING | 4 |
| high_score_missing_counterfactual:PRINCIPLE-EXPLANATION | 2 |
| high_score_missing_counterfactual:PRINCIPLE-FEEDBACK | 2 |
| high_score_missing_counterfactual:PRINCIPLE-MODELLING | 1 |
| high_score_modal_conflict:PRINCIPLE-MODELLING | 1 |
| high_score_modal_conflict:PRINCIPLE-QUESTIONING | 1 |
| more_than_three_required | 1 |

## 2. Inference — diễn giải tạm thời

- Phân bố trên mô tả hành vi của một lần chấm bằng model; không phải ước
  lượng accuracy hoặc độ ổn định.
- `eligible_without_plan03_review` chỉ có nghĩa không bị cờ ở Plan 03.
  Nhóm này vẫn phải qua audit `gold_response`, grounding và review tích hợp
  ở các plan sau.
- Khác biệt giữa lớp, bài học hoặc vị trí lượt chỉ được báo mô tả. Plan 03
  không dùng chúng để kết luận một candidate có lỗi.

## 3. Teacher decision needed — phần UET/HNMU cần quyết định

1. UET xem các dòng ưu tiên cao trong `full_run_review_queue.csv`, trước
   hết là lỗi evidence/cấu trúc, tập rỗng hoặc trên ba nguyên tắc.
2. UET quyết định disposition theo nhóm lý do; không sửa trực tiếp
   `run_full.jsonl`.
3. HNMU xác nhận ranh giới sư phạm của sáu nguyên tắc trong gói tích hợp
   rubric–instruction–ví dụ ở plan sau.

## 4. Giới hạn

- Không có run B trên full pool nên không báo agreement, Jaccard hoặc F1.
- Không có nhãn chuyên gia cấp candidate nên không báo accuracy.
- Lint dùng regex chỉ tạo cờ review và không tự sửa score.
- Tổ hợp hiếm là quy tắc vận hành để lấy mẫu review, không phải bằng chứng
  rằng tổ hợp đó sai về mặt sư phạm.
