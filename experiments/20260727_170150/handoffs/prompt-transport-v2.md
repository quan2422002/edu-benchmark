# Handoff — Contract prompt v2

- Delegation ID: không có; thay đổi được orchestrator triển khai trực tiếp
- Agent: orchestrator
- Status: implemented_without_api_call
- Native thread ID/label: không có

## Delegation prompt

Không có specialist delegation. UET yêu cầu loại hai ID truy vết khỏi
input model, giải thích rõ tám trường ngữ nghĩa trong system prompt và lưu
chính xác user prompt trong output.

## Follow-up or steer messages

Project lead yêu cầu đường dẫn thư mục output được truyền tường minh trong
câu lệnh chạy.

## Inputs read

- Plan 01, Plan 02 và roadmap của experiment `20260727_170150`;
- system prompt, schema, runner và test v1;
- `pilot_input.csv` và bundle `pilot_v1` đã chạy.

## Outputs created

- đặc tả, schema, manifest và system prompt v2;
- code transport/validation v2 và test tương ứng;
- tài liệu trạng thái, kiến trúc và plan được đồng bộ.

## Result summary

User prompt gửi model chỉ còn tám trường ngữ nghĩa. ID candidate/sample
được code giữ để điều phối và nối vào normalized response. Mỗi record
`run_a.jsonl`/`run_b.jsonl` lưu đúng chuỗi `user_prompt` đã truyền vào
Vertex. Pilot v1 được giữ nguyên; mọi lần chạy mới dùng `pilot_v2`.

## Orchestrator decision

Không tạo file request riêng vì sẽ nhân bản dữ liệu. `user_prompt` nằm
ngay trong từng run record. Lệnh bàn giao phải có `--output-root` tuyệt
đối; runner ghi bundle mới vào thư mục con `pilot_v2`.

## Uncertainty

Chưa gọi Vertex AI bằng contract v2. Chất lượng score cần UET review sau
khi project lead chạy lại pilot.

## Open questions and next human decisions

- Project lead chạy `pilot_v2`.
- UET review user prompt, score, evidence và metric A/B của v2.
