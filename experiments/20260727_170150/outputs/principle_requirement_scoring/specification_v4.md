# Đặc tả V4 — kiểm định ranh giới requirement scoring

## 1. Mục tiêu

V4 kiểm tra xem Gemini có phân biệt được trường hợp một nguyên tắc sư phạm
**bắt buộc** với trường hợp nguyên tắc đó chỉ **có thể hữu ích** hay không.
V4 không thay đổi thang điểm, ngưỡng chọn hoặc tám trường dữ liệu đầu vào
đã khóa ở V3.

Thay đổi chỉ gồm ba phần:

1. siết cổng lập luận của system prompt;
2. dùng code phát hiện mâu thuẫn có thể xác định bằng quy tắc;
3. chạy bộ calibration có positive và near-miss cho đủ sáu nguyên tắc.

## 2. Cổng lập luận trong prompt

Mọi điểm `4`–`5` phải trả lời rõ:

- `Nhu cầu độc lập:` nhu cầu nào của học sinh bắt buộc nguyên tắc này;
- `Nếu bỏ nguyên tắc này:` vì sao chiến lược khác không đáp ứng đầy đủ.

Lập luận chỉ nói “có thể hữu ích”, “nên cân nhắc” hoặc “chiến lược thay
thế” không được vượt quá điểm `3`.

### 2.1. Cổng Feedback

Điểm `4`–`5` phải có đủ:

1. đầu ra hoặc cách nghĩ cụ thể của học sinh;
2. điểm đúng, sai, thiếu hoặc chất lượng cần nhận xét;
3. hướng điều chỉnh, cải thiện hoặc bước tiếp theo.

Xác nhận đúng, khen hoặc bổ sung lời giải mà không phân tích phần học sinh
đã làm chỉ được tối đa `3`.

### 2.2. Cổng Questioning

Điểm `4`–`5` chỉ hợp lệ khi:

- câu trả lời của học sinh cung cấp thông tin còn thiếu để chọn phản hồi;
  hoặc
- việc học sinh tự trả lời/tự suy luận là mục tiêu thiết yếu của lượt.

Lập luận phải nói rõ phản hồi của gia sư phụ thuộc vào câu trả lời đó ra
sao. Câu hỏi kiểm tra thêm sau một giải thích đã đủ chỉ được tối đa `3`.

## 3. Semantic lint bằng code

Code không tự sửa điểm. Nó chỉ đưa candidate vào `review_queue.csv` khi:

- điểm `4`–`5` thiếu một trong hai nhãn lập luận bắt buộc;
- điểm `4`–`5` vẫn mô tả nguyên tắc là tùy chọn hoặc chiến lược thay thế;
- Feedback điểm cao chỉ mang tính xác nhận/khen mà không có dấu hiệu cải
  thiện;
- Questioning điểm cao được mô tả là tùy chọn nhưng không nêu sự phụ thuộc
  vào câu trả lời.

Đây là cổng phát hiện rủi ro có độ chính xác ưu tiên cao, không phải bộ
phân loại ngữ nghĩa đầy đủ. Code tuyệt đối không thay model hoặc UET/HNMU
đưa ra phán quyết sư phạm.

## 4. Bộ calibration

`calibration_cases_v1.csv` có 36 ca đối chứng:

- sáu nguyên tắc;
- mỗi nguyên tắc có ba positive với expected range `4–5`;
- mỗi nguyên tắc có ba near-miss với expected range `1–3`.

Các ca được viết có chủ đích để cô lập ranh giới định nghĩa, không nhằm
đại diện thống kê cho 2.028 candidate. Expected range hiện là giả thuyết
thiết kế tạm thời do UET review, chưa phải nhãn chuyên gia HNMU.

Calibration chạy hai lần độc lập với cùng cấu hình. Một ca đạt khi điểm
của nguyên tắc trọng tâm nằm trong expected range ở cả hai lần. Mọi ca
ngoài khoảng, mọi semantic lint và mọi bất đồng qua ngưỡng `4` đều được
đưa vào review.

## 5. Tiêu chí đọc kết quả

Các điều kiện tự động gồm:

- 36/36 ca nằm trong expected range ở cả hai lần;
- mỗi nguyên tắc có positive support ở cả hai lần;
- các ngưỡng độ ổn định đã đăng ký từ trước vẫn đạt;
- không có lỗi schema, thiếu candidate hoặc sai user prompt đã lưu.

Việc đạt cổng tự động chỉ cho phép chuyển sang UET review và pilot holdout.
Nó không chứng minh độ chính xác trên toàn bộ dữ liệu và không thay thế
review tích hợp của HNMU ở giai đoạn task/rubric hoàn chỉnh.

## 6. Artifact và quyền quyết định

- Prompt: `shared/prompts/benchmark_candidate_task_assigning/system_prompt_v4.md`
- Input: `calibration_cases_v1.csv`
- Kết quả chạy: `calibration_v1/`
- Schema: tiếp tục dùng `scoring_schema_v2.json`
- Model tạo điểm và lập luận; code kiểm schema, lưu prompt, tính chỉ số,
  áp threshold và tạo review queue.
- UET duyệt expected range và disposition của review queue.
- HNMU duyệt task/rubric và ví dụ tích hợp ở giai đoạn sau.
