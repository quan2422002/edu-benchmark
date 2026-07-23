# Điều tra 297 hội thoại kết thúc bằng lượt học sinh

Ngày: 23/07/2026  
Phạm vi: 297 raw sample `pass` còn kết thúc bằng `HS` sau hai correction do người phụ trách dự án duyệt  
Phương pháp: phân tích deterministic bằng rule minh bạch; không phải phán quyết chuyên môn của HNMU/UET

## 1. Hai lỗi vai trò đã được sửa

Không sửa snapshot kế thừa hoặc raw Excel. Quyết định được lưu trong:

`outputs/benchmark_conversion/dialogue_corrections.csv`

Pipeline kiểm SHA-256 của dialogue gốc trước khi áp dụng:

| Sample | Quyết định |
|---|---|
| `HNMU-G7-R0189-STT6` | Gộp lượt AI 4 và 5 thành một lượt AI; giữ nguyên hai đoạn nội dung. |
| `HNMU-G9-R0237-STT12` | Đổi nhãn lượt 8 từ `HS` thành `AI`; nội dung không đổi. |

`conversion_input_pass_samples.csv` giữ:

- `raw_dialogue`: bản snapshot nguyên gốc;
- `conversion_dialogue`: bản hiệu lực sau correction;
- `dialogue_correction_ids`: ID quyết định được áp dụng.

Sau correction, số mẫu strict-compatible tăng từ 366 lên 368 và không còn lỗi `non_alternating_roles`.

## 2. Câu hỏi điều tra

Giả thuyết ban đầu là lượt `HS` cuối chủ yếu chỉ xác nhận. Phân tích cần phân biệt:

1. có từ lịch sự/xác nhận như “dạ”, “vâng”, “em hiểu rồi”;
2. toàn bộ lượt chỉ là lời xác nhận không có nội dung khác;
3. lượt là câu trả lời cho câu hỏi/gợi ý của gia sư;
4. lượt báo đã thực hiện thao tác hoặc cam kết bước tiếp theo;
5. lượt đặt câu hỏi xác nhận/follow-up.

Không được coi từ “dạ” là bằng chứng rằng cả lượt không có giá trị.

## 3. Kết quả định lượng

### Độ dài

| Số từ ở lượt `HS` cuối | Số mẫu |
|---|---:|
| `<=5` | 9 |
| `6–10` | 57 |
| `11–20` | 204 |
| `>20` | 27 |

Có 231/297 lượt dài từ 11 từ trở lên. Vì vậy phần lớn không phải câu xác nhận cực ngắn.

### Dấu hiệu ngôn ngữ

Các nhóm có thể chồng lấn:

| Dấu hiệu | Số mẫu |
|---|---:|
| Lịch sự/đồng thuận như “dạ”, “vâng”, “đúng rồi” | 191 |
| Hiểu/nhớ/nhận ra | 66 |
| Cảm ơn | 30 |
| Thực hiện/cam kết hành động theo rule hẹp | 49 |
| Kết thúc bằng câu hỏi | 6 |

191 mẫu có dấu hiệu lịch sự hoặc đồng thuận, nhưng điều đó không đồng nghĩa với 191 lượt chỉ có xác nhận.

### Phân loại heuristic loại trừ lẫn nhau

| Nhóm | Số mẫu | Cách hiểu |
|---|---:|---|
| `answer_or_explanation_to_tutor_prompt` | 206 | Trả lời câu hỏi/gợi ý ở lượt AI ngay trước. |
| `action_commitment_or_completion` | 49 | Báo đã làm xong hoặc sẽ thực hiện bước tiếp theo. |
| `reflection_or_other_closing` | 35 | Phản ánh kết quả, nhận xét hoặc kết thúc khác. |
| `student_followup_or_confirmation_question` | 6 | Học sinh hỏi lại/xác nhận; nên review trước khi dùng strategy mới. |
| `pure_acknowledgement_or_thanks` | 1 | Khớp rule hẹp cho lời xác nhận/cảm ơn thuần túy. |

Kết luận: nhận xét “chủ yếu có sắc thái xác nhận/kết thúc” đúng ở mức chức năng diễn ngôn, nhưng không đúng nếu hiểu rằng các lượt đó hầu hết là filler có thể bỏ. Ít nhất 206 lượt là câu trả lời cho prompt của gia sư; nhiều lượt còn cho thấy học sinh đã thao tác hoặc hiểu bài.

## 4. Ý nghĩa với split policy

Với 291/297 mẫu không kết thúc bằng câu hỏi, lượt `HS` cuối có thể được giữ như `post_response_student_outcome` nếu Plan 02 chọn strategy trailing outcome:

- không đưa outcome ngược vào model input;
- lấy lượt AI ngay trước làm `gold_response`;
- giữ outcome để truy vết phản ứng học sinh và hỗ trợ audit chất lượng response;
- không gọi outcome là evidence chuyên môn cấp candidate trước Plan 04.

Sáu mẫu kết thúc bằng câu hỏi nên được review riêng trước khi migration pilot, vì chúng có thể báo hiệu phản hồi AI trước đó còn tạo ra một điểm chưa được giải quyết.

Đây là khuyến nghị kỹ thuật từ phân tích heuristic, không thay thế quyết định split policy của người phụ trách dự án hoặc đánh giá sư phạm của HNMU/UET.

## 5. Artifact

- `outputs/benchmark_conversion/last_student_turn_analysis.csv`: 297 dòng, có lượt AI trước, lượt HS cuối, flag, category, rationale và treatment đề xuất.
- `outputs/benchmark_conversion/last_student_turn_analysis_summary.json`: thống kê tổng hợp.
- `outputs/benchmark_conversion/dialogue_corrections.csv`: hai quyết định correction có hash.
- `outputs/benchmark_conversion/pilot_v0/dialogue_split_errors.csv`: hiện còn 297 dòng `last_turn_not_tutor`.
