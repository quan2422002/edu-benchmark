# Tóm tắt pilot chấm requirement

Trạng thái tự động: **ĐẠT các ngưỡng đăng ký**

## Chỉ số chính

- Candidate: 40
- Tỷ lệ trùng điểm chính xác: 1.000
- Tỷ lệ chênh không quá một mức: 1.000
- Exact agreement của tập bắt buộc: 1.000
- Jaccard trung bình của tập bắt buộc: 1.000
- Tỷ lệ candidate không crossing ngưỡng 4: 1.000
- Số dòng trong review queue: 4

## F1 theo nguyên tắc tại ngưỡng 4

- `PRINCIPLE-CHALLENGE`: 1.000
- `PRINCIPLE-EXPLANATION`: 1.000
- `PRINCIPLE-MODELLING`: 1.000
- `PRINCIPLE-PRACTICE`: 1.000
- `PRINCIPLE-FEEDBACK`: 1.000
- `PRINCIPLE-QUESTIONING`: 1.000

## Kết quả gate

- `within_one_rate`: đạt
- `required_exact_agreement`: đạt
- `required_jaccard_mean`: đạt
- `principle_f1`: đạt
- `no_threshold_crossing_rate`: đạt

Kết quả tự động không thay thế UET/HNMU review. Chỉ các dòng trong
`review_queue.csv` cần được người phụ trách dự án phân xử trực tiếp.
