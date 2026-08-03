# Handoff — Smoke v2 phản hồi gia sư

- Delegation ID: `EXP-20260728-PLAN05-SMOKE-V2-001`
- Agent: `benchmark-specification-designer` ở chế độ single-agent
- Status: `implemented_awaiting_user_run`
- Native thread ID/label: không có

## Delegation prompt

Cài smoke v2 trên đúng 10 candidate của smoke v1, giữ giới hạn 1.024
output token, bổ sung instruction trả lời cô đọng và dừng đóng khi
provider báo phản hồi bị cắt.

## Follow-up or steer messages

UET yêu cầu xem đủ ba lưu ý: Llama có thể dùng lại adapter MaaS hiện tại;
SocraticLM cần endpoint tự triển khai; smoke v2 trước mắt chỉ chạy Gemini
trên cùng mẫu với v1.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260727_170150/roadmap.md`
- `experiments/20260727_170150/plans/05-benchmark-evaluation-configuration.md`
- `experiments/20260727_170150/outputs/benchmark_evaluation/smoke_gemini35_instruction_v1/run_manifest.json`
- `shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v1.yaml`
- `src/edu_benchmark/benchmark_evaluation/`
- `scripts/benchmark_evaluation/run_vertex_smoke.py`

## Outputs created

- `shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v2.yaml`
- Cập nhật runner, schema, model registry, test và tài liệu Plan 05.

## Result summary

Bundle `v2` giữ nguyên sáu instruction nguyên tắc và chỉ siết phong cách:
trả lời cô đọng, không lặp lại toàn bộ hội thoại, không mở rộng quá bước
cần thiết và kết thúc trọn câu. CLI nhận manifest v1 để khóa chính xác 10
candidate. Gemini và API OpenAI-compatible đều chuẩn hóa
`finish_reason`; `MAX_TOKENS`/`length` được ghi `needs_review`, khiến
manifest không thể báo `completed`. `max_output_tokens` vẫn là 1.024.

Model ID trong OpenAPI request của Llama là
`meta/llama-4-maverick-17b-128e-instruct-maas`: tên model cơ sở do Google
liệt kê không có tiền tố, nhưng trường `model` gửi tới endpoint phải có
dạng `publisher/model`. Runner có cổng kiểm tra cấu trúc này trước khi
gọi API. Không cần adapter hội thoại mới cho Llama. SocraticLM có thể
dùng lại cấu trúc message
OpenAI-compatible nhưng vẫn cần caller cho Vertex Raw Predict và quy
trình dựng–gỡ endpoint riêng.

Sau lần retry nhận HTTP 404 cho toàn bộ 10 mẫu, runner được bổ sung log
lỗi tức thời. Mỗi exception hiện được in ra terminal và ghi crash-safe
vào `run_errors.jsonl` với candidate, attempt, traceback, HTTP status và
response body. Prompt và credential không được ghi vào file lỗi. HTTP
400/403/404 được coi là lỗi cấu hình/quyền không thể hồi phục nên không
gọi lại cùng request; 408/409/425/429 và 5xx vẫn có thể retry.

## Orchestrator decision

Không gọi API trong bước cài đặt. UET chạy smoke v2 bằng lệnh được bàn
giao, sau đó so sánh response v1–v2 trên cùng ID.

## Uncertainty

Giới hạn 1.024 token được giữ theo quyết định UET. Nếu bundle `v2` vẫn tạo
response bị cắt, kết quả phải ở review; không được tự tăng giới hạn hoặc
coi đó là response hợp lệ.

## Open questions and next human decisions

- UET chạy và review smoke v2.
- Sau smoke v2, quyết định có khóa bundle `v2` cho pilot 240 mẫu hay không.
- Chấp nhận EULA Llama trước smoke model mở.
- Chọn cấu hình máy và giới hạn chi phí trước khi triển khai SocraticLM.

## Cập nhật SocraticLM ngày 28/07

Llama Maverick đã hoàn thành 10/10 mẫu, không có lỗi hoặc mẫu review.
SocraticLM đã được nối thành provider `vertex-endpoint` cô lập: cùng
runner, prompt, native history, retry và output contract, nhưng dùng
Vertex `rawPredict` tới custom vLLM endpoint. Công cụ vòng đời mới build
image, upload model, dựng endpoint một L4, ghi manifest có `delete_by`,
hiển thị chi phí theo giờ và dọn đúng tài nguyên sau smoke. Cleanup không
được ghi thành công nếu gcloud trả lỗi chưa được xác định.

UET vẫn phải tự xem điều khoản model card mang nhãn giấy phép `other`,
chạy deployment với cờ xác nhận, chạy smoke 10 mẫu rồi cleanup ngay.
SocraticLM vẫn là ứng viên chuyên biệt chờ kiểm tiếng Việt/Tin học, không
phải model đã được chấp nhận vào panel chính.

Deployment đầu tiên build image thành công nhưng Model Registry upload
dừng trước khi tạo model/endpoint: Vertex AI Service Agent thiếu quyền
đọc Artifact Registry repository. Manager đã được sửa để cấp
`roles/artifactregistry.reader` ở phạm vi repository, tái sử dụng image
đã build và lưu stderr gcloud vào lifecycle manifest nếu lỗi lặp lại.
Smoke error `status!='deployed'` chỉ là hệ quả đúng của lỗi deployment.

Lần chạy tiếp theo đã cấp IAM thành công và upload Model Registry resource
`models/4142239083587960832`, nhưng gcloud không in resource name dù
operation hoàn tất. Manager đã chuyển sang truy vấn registry bằng đúng
display name + image URI, phục hồi resource duy nhất và áp dụng cùng cơ
chế cho endpoint. Lần chạy tiếp theo không upload model trùng.
