# Đặc tả v2 — Chấm mức độ cần thiết của sáu nguyên tắc sư phạm

Experiment: `20260727_170150`  
Phiên bản: `v2`  
Ngày cập nhật contract: 27/07/2026  
Trạng thái: UET phê duyệt để chạy lại pilot; ý nghĩa sư phạm cuối cùng chờ HNMU xác nhận

## 1. Phạm vi thay đổi từ v1

Định nghĩa `requirement_score`, sáu nguyên tắc, anchor 1–5, threshold và
ranh giới model–code của v1 được giữ nguyên. V2 sửa contract vận chuyển dữ
liệu theo hai nhận xét của UET:

1. `benchmark_candidate_id` và `sample_id` chỉ phục vụ truy vết, không có
   đóng góp ngữ nghĩa cho phép chấm. Code giữ hai trường này để điều phối,
   nhưng không gửi chúng cho model và không yêu cầu model trả lại ID.
2. System prompt giải thích rõ ý nghĩa và cách dùng của toàn bộ tám trường
   ngữ nghĩa được gửi cho model.

Code tự nối `benchmark_candidate_id` vào normalized result sau khi
response qua validation. Cách này loại model khỏi phép join xác định.

## 2. Mục tiêu đo

`requirement_score` trả lời:

> Để một phản hồi tiếp theo đáp ứng đúng nhu cầu quan sát được của học sinh
> trong payload này, nguyên tắc sư phạm đang xét cần thiết ở mức nào?

Đây là mức độ cần thiết của chức năng sư phạm, không phải mức độ nguyên tắc
xuất hiện trong `gold_response`, chất lượng thực thi nguyên tắc, sở thích
chiến lược của model hoặc confidence tự khai.

## 3. Contract dữ liệu

### 3.1. Dữ liệu điều phối chỉ dùng ở phía code

- `benchmark_candidate_id`: khóa ghép duy nhất của candidate.
- `sample_id`: khóa family hội thoại nguồn.

Hai trường này vẫn có trong grounding pool và `pilot_input.csv`, nhưng bị
loại trước khi serialize user prompt.

### 3.2. User prompt gửi model

User prompt là một JSON object có đúng tám trường, theo đúng thứ tự:

1. `grade`: lớp 6–9, dùng để hiểu mức phù hợp kiến thức và lứa tuổi;
2. `lesson`: tên bài/chủ đề, xác định miền kiến thức;
3. `position`: mục/trang học liệu nguồn, không phải vị trí lượt hội thoại;
4. `bloom_level`: mức nhận thức dự kiến của yêu cầu học tập;
5. `student_prompt`: phát biểu ban đầu mở đầu family hội thoại;
6. `conversation_history`: các lượt từ sau `student_prompt` đến ngay trước
   target response, đã parse thành danh sách `turn_index`–`role`–`content`;
7. `source_question`: câu hỏi/nhiệm vụ học tập nguồn;
8. `gold_answer`: neo chuyên môn từ dữ liệu giáo viên, không phải phản hồi
   gia sư mẫu và không tự quyết định nguyên tắc.

`gold_response`, ID truy vết, nhãn legacy và output run trước không được
đưa vào user prompt.

### 3.3. Response của model

Model chỉ trả:

```json
{
  "principle_scores": [
    {
      "principle_id": "PRINCIPLE-CHALLENGE",
      "requirement_score": 1,
      "rationale": "...",
      "evidence": "..."
    }
  ]
}
```

Response phải có đúng sáu object, đủ sáu `principle_id`, điểm nguyên 1–5
và lập luận/bằng chứng tiếng Việt. Sau validation, code tạo normalized
response bằng cách thêm `benchmark_candidate_id` của request hiện hành.

## 4. Thang điểm và tập dẫn xuất

| Điểm | Ý nghĩa |
|---:|---|
| 1 | Không phù hợp hoặc có nguy cơ làm lệch nhu cầu hiện tại. |
| 2 | Liên quan yếu/bề mặt; không tạo chức năng sư phạm độc lập. |
| 3 | Là chiến lược thay thế hợp lệ nhưng tình huống không bắt buộc phải dùng. |
| 4 | Rõ ràng nên có trong một phản hồi tốt cho tình huống này. |
| 5 | Chức năng cốt lõi; bỏ đi thì phản hồi không còn đáp ứng đúng nhu cầu chính. |

Code dẫn xuất:

- điểm `4`–`5` → `required_principle_set`;
- điểm `3` → `alternative_principle_set`;
- điểm `1`–`2` → không đưa vào instruction hoặc rubric riêng.

Anchor riêng của sáu nguyên tắc không thay đổi so với v1 và được triển khai
đầy đủ trong system prompt v2.

## 5. Lưu chính xác user prompt

Mỗi record trong `run_a.jsonl` và `run_b.jsonl` có trường `user_prompt`
chứa đúng chuỗi JSON đã truyền vào `contents` của Vertex AI. Runner chỉ
serialize một lần rồi dùng cùng chuỗi cho:

- API call;
- artifact kết quả;
- validation khi finalize.

Không tạo thêm file request riêng. Validator tái dựng user prompt từ
`pilot_input.csv` và yêu cầu khớp chính xác với trường đã lưu.

## 6. Ranh giới model–code

Model chỉ chấm sáu score và viết rationale/evidence tiếng Việt.

Code thực hiện schema validation, ID join, threshold filtering, set
derivation, review queue, run comparison, metric, hashing, retry/resume và
fail-closed publication.

## 7. Quyết định UET

| Quyết định | Disposition |
|---|---|
| Không gửi `benchmark_candidate_id` và `sample_id` cho model | approved |
| Không yêu cầu model trả lại ID | approved |
| Giải thích rõ tám trường ngữ nghĩa trong system prompt | approved |
| Lưu user prompt ngay trong mỗi record kết quả | approved |
| Giữ `pilot_v1` làm provenance; chạy contract mới tại `pilot_v2` | approved |
| Giữ model/config/threshold đã khóa của pilot v1 | approved |

V2 thay thế v1 cho mọi API call mới. Kết quả `pilot_v1` không được trộn với
`pilot_v2`.
