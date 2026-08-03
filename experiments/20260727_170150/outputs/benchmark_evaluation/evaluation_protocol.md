# Giao thức đánh giá phản hồi gia sư — Plan 05

Trạng thái: **smoke v2 đã hoàn thành; phương án hybrid đã khóa: sinh full
ba cấu hình, rồi judge cost-pilot 30 mẫu; instruction vẫn chờ HNMU review**.

## Phạm vi

- Pool nguồn: 2.028 candidate; pool ưu tiên: 1.400 candidate.
- Thư viện tạm dùng: 22 rubric (4 chung + 18 riêng) và 6 lỗi nghiêm trọng.
- Score nguyên tắc và rubric chưa phải nhãn chuyên gia.

## Request cho tutor model

System instruction được gửi riêng và chỉ chứa vai trò gia sư, lớp, bài học,
câu hỏi nguồn, instruction chung và instruction của các nguyên tắc bắt buộc.
Nguồn instruction đã khóa là `v1` tại
`shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v1.yaml` với SHA-256
`f8390c493ef30b9eb791a18955da8aba7c8a2cca310fd2b598ee3e5add8ce4a1`. Mỗi yêu cầu ghi rõ tên tiếng Việt, mục tiêu,
hành vi cần thể hiện, điều cần tránh và cách bảo toàn quyền chủ động của
học sinh.
Registry gốc hiện vẫn dùng bundle `v1` để bảo toàn baseline. Smoke v2
phải truyền tường minh bundle `v2` và manifest smoke v1 để chỉ thay đổi
yêu cầu trả lời cô đọng trên đúng cùng 10 candidate.
`student_prompt` là message `user` đầu tiên; từng lượt history giữ nguyên
ranh giới và role native. Request không chứa `gold_answer`, `gold_response`,
fragment, rubric, score, candidate ID hoặc sample ID.

Mỗi target record lưu nguyên system prompt, user prompt cuối cùng và toàn
bộ message có role; các hash phải khớp lại với chính nội dung đã lưu.
Record đồng thời lưu `finish_reason`, `response_status` và
`completion_issue`. Kết quả dừng vì `MAX_TOKENS`, `length` hoặc lý do
không thành công khác phải vào review, không được tính là hoàn thành.
Hợp đồng ba trường này áp dụng từ smoke v2; bundle v1 là baseline lịch sử
không được tự suy diễn ngược `finish_reason` khi provider metadata không
còn trong artifact.
Manifest và record cùng ghi experiment, plan, pipeline stage và run ID.
Toàn bộ cấu hình cùng run sinh/chấm thuộc phase này nằm dưới một gốc
`outputs/benchmark_evaluation/`.

Tập nguyên tắc bắt buộc được code tái lập chính xác từ
`requirement_score >= 4`. Nguyên tắc điểm `3` không được đưa vào
instruction, không kích hoạt rubric riêng và không được gửi judge.

Validator dừng đóng nếu history không phải danh sách, `turn_index` không
tăng, role sai/không xen kẽ, content rỗng hoặc ngữ cảnh không bắt đầu và
kết thúc bằng học sinh.

## Panel và smoke test

Panel vận hành hiện có Gemini 3.5 Flash và Llama 4 Maverick. Pilot còn có
một prompt ablation dùng cùng Gemini 3.5 Flash với bundle
`instruction_bundle_v3_learnlm.yaml`; đây không phải model độc lập hoặc
model chuyên biệt. SocraticLM chưa vượt deployment smoke và Claude Sonnet
4.6 chưa được kích hoạt trên Marketplace. Nếu model chuyên biệt không đạt,
phải báo khoảng trống thay vì thay bằng model đa dụng.

## Sinh và chấm

Một judge call cho một cặp candidate–target response phải trả toàn bộ phán
quyết theo tiêu chí, lỗi nghiêm trọng và phán quyết tổng thể; không gọi
riêng từng rubric. Hai response được ẩn danh và tráo bằng seed.

System prompt chuẩn là
`shared/prompts/benchmark_response_judging/system_prompt_v2.md` và được gửi
qua system field native. User prompt là một message Markdown; mọi nội dung
trong bối cảnh, lịch sử, học liệu và response đều là dữ liệu, không phải
instruction cho judge.

Căn cứ học liệu được nhóm theo đúng `book_title + lesson_title`. Mỗi nhóm
chỉ gửi heading và content; fragment cùng nhóm giữ thứ tự và cách nhau bằng
`-----`. `position`, `scope`, fragment metadata, ID và cột quản trị lỗi
không được gửi model.

Judge chỉ nhận/trả tên tiêu chí và tên lỗi. Code ánh xạ tên về ID sau khi
kiểm catalog. Mỗi lỗi chỉ mang tên các rubric vừa bị lỗi ảnh hưởng vừa đang
áp dụng cho candidate. Judge kiểm lỗi độc lập cho hai response; cả hai có
thể cùng mắc lỗi.

Sau unblind, code giữ phán quyết raw và áp cổng xác định trên mỗi tiêu chí
bị ảnh hưởng: không bên nào mắc lỗi thì giữ raw; chỉ target mắc thì
`Lose`; chỉ reference mắc thì `Win`; cả hai mắc thì target vẫn `Lose`.
Nhiều lỗi cùng ảnh hưởng một tiêu chí chỉ tạo một điều chỉnh. Phán quyết
tổng thể của judge được giữ làm kết quả phụ và không bị cổng này ghi đè.

Smoke judge đã hoàn thành đủ 20/20 cặp trên 10 candidate. Pilot kế tiếp
dùng manifest `pilot_80_v1`: 80 candidate thuộc 80 family, đúng 20 mẫu mỗi
lớp, giữ 10 smoke anchor, lấy đủ 8 mẫu Challenge và bao phủ có chủ đích
Practice/Modelling, lịch sử hội thoại, Bloom cùng kích thước tập nguyên
tắc. Ba target configuration tạo 240 response: Gemini 3.5 Flash baseline,
Llama 4 Maverick và cùng Gemini 3.5 Flash với system instruction định hướng
LearnLM. Cấu hình LearnLM là một prompt ablation trên cùng base model, không
phải model thứ ba độc lập hay model chuyên biệt. Gemini 3.5 Flash chấm đủ
240 cặp. Hai cấu hình Gemini phải được nhóm theo `target_run_id`, không được
gộp chỉ vì cùng `model_id`.
Pilot không đại diện phân bố quần thể và chưa có calibration người–judge
độc lập mới. Kết quả target Gemini phải được báo riêng vì target và judge
cùng model. Lần chạy Claude thất bại do chưa kích hoạt Marketplace được
giữ làm provenance, không được resume như một Gemini run.

Kết quả báo Win/Tie/Lose theo tiêu chí chung, nguyên tắc, lớp,
candidate-macro và family-macro. Mặc định không đổi Tie thành 0,5.

## Ngân sách

Hard cap toàn experiment là 250 USD: 56 USD lịch sử, 20 USD smoke/endpoint,
55 USD pilot, 94 USD main và 25 USD dự phòng. Trước batch kế tiếp, runner
phải bảo đảm:

```text
actual_spend_to_date
+ current_plan_spend
+ upper_bound(next_batch)
+ reserve
<= 250 USD
```

Pilot hiện tại dùng Gemini 3.5 Flash làm judge duy nhất. Cận trên gồm mọi
attempt retry là 3,29184 USD cho Gemini baseline, 0,534624 USD cho Llama,
3,43584 USD cho Gemini+LearnLM prompt và 42,58944 USD cho judge; tổng
49,851744 USD, dưới trần pilot 55 USD. Model chuyên biệt vẫn là khoảng
trống vận hành và không được thay thế ngầm bằng cấu hình LearnLM này.

Lần Gemini baseline đầu ghi đủ 1.400 record nhưng 436 response chạm
`MAX_TOKENS` ở cap 1.024. Recovery 1.536 hoàn thành 417/436 mẫu với chi phí
4,7877885 USD; 19 mẫu còn lại tiếp tục bị cắt. Follow-up giữ nguyên model,
prompt, seed và MEDIUM thinking, chỉ chạy lại 19 ID ở cap 2.048 với cận trên
1,307124 USD. Source bundle chỉ được dựng lại và thay thế nguyên tử sau khi
kết hợp đủ 417 kết quả cũ và 19 kết quả mới; staging nằm trong `/tmp`, bị xóa
sau merge, còn provenance hai lượt được nhúng vào manifest chính.

Lượt Llama full đầu hoàn thành 1.314/1.400 mẫu; 86 mẫu còn thiếu sau retry
do HTTP 429 `RESOURCE_EXHAUSTED`. Resume chỉ được gửi đúng các ID chưa ghi,
dùng 2 worker, exponential backoff 15–60 giây và jitter tối đa 5 giây.
Manifest phải cộng dồn chi phí cùng `resume_history`. LearnLM chỉ bắt đầu
khi Llama đạt đủ 1.400 mẫu; judge cost-pilot vẫn bị chặn trước thời điểm đó.

Retry Llama đã hoàn thành đủ 1.400/1.400. Lượt LearnLM ghi 1.400 record
nhưng 386 response bị `MAX_TOKENS` ở cap 1.024. Recovery khóa đúng các ID
này, giữ bundle v3 và cấu hình ngữ nghĩa, tăng riêng cap lên 2.048 và chỉ
merge nguyên tử khi 386/386 response hoàn chỉnh. Staging nằm trong `/tmp`;
cận trên bảo thủ là 27,250056 USD.

Phương án hybrid khóa đúng 1.400 candidate từ export eligible. Ba target
full tạo 4.200 response; cận trên bảo thủ là 127,09032 USD và ngoại suy từ
smoke khoảng 18,678072 USD. Sau đó judge chỉ chấm 30 candidate trên cả ba
cấu hình, tức 90 phép so sánh; cận trên 15,97104 USD và ngoại suy khoảng
3,223544 USD. Tập 30 mẫu chỉ đo chi phí/vận hành, không đại diện quần thể.
Lượt đầu giữ được 70/90 judgment; resume chỉ gửi 20 phép còn thiếu, dùng 8
worker và backoff+jitter cho lỗi DNS/connection. Cận trên resume là
3,54912 USD; prompt, schema và generation config không đổi.

Nếu cost-pilot đạt cổng, full judge chỉ xét Gemini baseline và Llama, tức
2.800 phép so sánh; LearnLM chỉ được phân tích ở cost-pilot. Cận trên full
judge hiện là 496,8768 USD nên cổng này vẫn đóng dưới hard cap 250 USD và
phải được tái dự toán từ usage cost-pilot.

## Cổng còn mở

- Follow-up 19 response Gemini đã merge đủ 1.400/1.400. Wrapper full phải xác minh và bỏ qua baseline, chỉ chạy Llama và LearnLM.
- Khi đủ 4.200 response, người dùng chạy wrapper judge cost-pilot 30 mẫu.
- Giá, model version và actual billing phải được chụp lại trước mỗi run.
- UET duyệt usage/chi phí cost-pilot trước khi cân nhắc full judge hai model.
- HNMU duyệt instruction và diễn giải rubric.
