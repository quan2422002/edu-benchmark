# Tóm tắt calibration requirement-scoring

Trạng thái tự động: **CHƯA ĐẠT expected range tạm thời**

## Chỉ số chính

- Calibration case: 36
- Cả hai run nằm trong expected range: 32/36 (0.889)
- Candidate bị semantic lint: 13
- Số dòng trong review queue: 20
- Expected range còn tạm thời, chờ UET review: có

## Kết quả theo nguyên tắc

- `PRINCIPLE-CHALLENGE`: positive 3/3; near-miss 3/3
- `PRINCIPLE-EXPLANATION`: positive 3/3; near-miss 2/3
- `PRINCIPLE-MODELLING`: positive 3/3; near-miss 3/3
- `PRINCIPLE-PRACTICE`: positive 3/3; near-miss 2/3
- `PRINCIPLE-FEEDBACK`: positive 3/3; near-miss 2/3
- `PRINCIPLE-QUESTIONING`: positive 3/3; near-miss 2/3

Calibration là bộ kiểm tra ranh giới có chủ đích, không phải ước lượng
accuracy đại diện cho toàn bộ 2.028 candidate. `review_queue.csv` chứa
case ngoài expected range, semantic lint, bất đồng A/B và spot check; nó
không thay thế UET/HNMU review.
