# Gói UET review Cổng C0b

Trạng thái: **chờ đại diện UET review; Cổng C0b chưa đạt**.

## Kết quả hai specialist

Hai instance `A` và `B` đã mã hóa độc lập cùng 40 ứng viên bằng cùng model, input, manifest và tài liệu canonical. Cả hai bundle đã qua validator sau khi B sửa một lỗi nhất quán nội bộ.

| Chỉ số | Kết quả | Ngưỡng UET | Trạng thái |
|---|---:|---:|---|
| Trùng nguyên tắc chính | 0,55 | 1,00 | Không đạt |
| Trùng chính xác cặp chính–phụ | 0,55 | 0,90 | Không đạt |
| Jaccard trung bình | 0,55 | 0,90 | Không đạt |
| Trùng quyết định khoảng trống độ phủ | 1,00 | 1,00 | Đạt |
| Trùng tác động của reference | 0,70 | 0,90 | Không đạt |

Đây là tính tái lập giữa hai instance AI, không phải độ đồng thuận giữa người chấm.

## File cần review

Mở `dual_run_uet_review.csv`. Gói có 29 dòng:

- 21 dòng bắt buộc vì A/B bất đồng về nhãn hoặc tác động của reference;
- 8 dòng hai agent đồng thuận, được chọn xác định để kiểm tra tránh “cùng sai”.

Không đưa toàn bộ các dòng cùng nhãn và cùng tác động reference vào packet. Hai bundle đầy đủ vẫn được giữ tại:

- `outputs/benchmark_specification/task_discovery/dual_run/annotator_a/`
- `outputs/benchmark_specification/task_discovery/dual_run/annotator_b/`

## UET cần điền

- `uet_final_primary`: một trong sáu `PRINCIPLE-*`, hoặc để rỗng nếu kết luận là khoảng trống độ phủ;
- `uet_final_secondary`: tối đa một nguyên tắc phụ khác nguyên tắc chính;
- `uet_reference_effect_decision`: `unchanged`, `changed` hoặc `conflict`;
- `uet_decision`: `approve_a`, `approve_b`, `revise_both`, `coverage_gap` hoặc `defer`;
- `uet_note`: lý do ngắn, đặc biệt khi sửa cả hai agent hoặc cần bổ sung quy tắc biên.

Không cần gán mù và không cần đọc 11 dòng ngoài packet ở vòng review này.

## Điểm cần chú ý

- 18/40 bất đồng về nguyên tắc chính.
- Cụm lớn nhất là A chọn `Feedback` nhưng B chọn `Explanation`: 8 mẫu.
- A chọn `Modelling` nhưng B chọn `Practice`: 3 mẫu.
- Không agent nào phát hiện khoảng trống độ phủ hoặc xung đột context–gold trong lô này.
- Lô 40 hiện tại đều thuộc lớp 6 vì input được lấy theo offset đầu của tập 160 đang sắp theo lớp. Vì vậy kết quả chưa đại diện cho lớp 7–9.

Sau UET review, các quyết định sẽ được dùng để sửa ranh giới/skill nếu cần. Hai instance phải rà lại các dòng bị ảnh hưởng trước khi C0b được chạy lại; chưa được chuyển sang Workstream C1.
