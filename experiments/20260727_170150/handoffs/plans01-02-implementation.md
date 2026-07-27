# Handoff triển khai Plan 01–02

- Delegation ID ban đầu: `EXP-20260727-IMPLEMENT-001`
- Delegation ID cập nhật runtime:
  `EXP-20260727-ADC-CONCURRENCY-001`
- Agent: orchestrator chạy single-agent với skill
  `benchmark-specification-designer`
- Trạng thái: `source_updated_without_execution`
- Native thread ID/label: không có

## Delegation prompt

Triển khai hai plan đã được project lead duyệt, nhưng không chạy pilot hoặc
gửi bất kỳ request nào đến Vertex AI. Sau khi cài code, bàn giao lệnh để
project lead tự chạy.

## Follow-up or steer messages

- Project lead xác nhận đã thiết lập Vertex AI cục bộ cho project
  `edu-benchmark` và yêu cầu bỏ API key.
- Project lead yêu cầu đa luồng, ghi output tăng dần và chỉ retry các mẫu
  lỗi sau khi chạy hết lượt tổng thể.
- Project lead yêu cầu không chạy code; chỉ bàn giao câu lệnh.

## Inputs read

- hai plan và roadmap của experiment `20260727_170150`;
- grounding pool 2.028 candidate và bảng sáu nguyên tắc kế thừa;
- đặc tả sáu năng lực và căn cứ nghiên cứu kế thừa;
- tài liệu chính thức của Google Gen AI SDK về Vertex AI chuẩn, ADC và
  structured output.

## Outputs created

- prompt tiếng Việt:
  `shared/prompts/benchmark_candidate_task_assigning/system_prompt_v1.md`;
- ba artifact tinh gọn của Plan 01 dưới
  `outputs/principle_requirement_scoring/`;
- runner, Vertex client và logic validation/metric dưới
  `src/vertex_ai_call/`;
- kiểm thử offline dưới `tests/vertex_ai_call/`;
- dependency được khóa trong `requirements.txt`.

## Result summary

Plan 01 đã khóa đặc tả v1, schema, prompt và manifest hash. Plan 02 đã cài
pipeline chọn pilot 40 candidate theo lớp/family, chạy lặp A/B có resume,
validate đủ sáu score, dẫn xuất tập nguyên tắc bằng code và tính metric/review
queue. Runtime active dùng ADC với project `edu-benchmark`, location
`global`; không đọc API key hoặc `.env`.

Mỗi run dùng tối đa 8 worker mặc định. Worker không ghi file; thread điều
phối append từng response hợp lệ vào JSONL rồi `flush`/`fsync`. Sau khi
toàn bộ lượt quét kết thúc, runner chỉ gửi lại các candidate lỗi, tối đa
`max_retries` lần mỗi candidate và luôn tuân theo trần tổng request.

Không có API call hoặc output pilot thật nào được tạo trong lần triển khai
này.

## Validation

Đã dùng:

`/home/quannda/miniconda3/envs/benchmark_env/bin/python`

Kết quả trước lần cập nhật ADC/đa luồng:

- `tests/vertex_ai_call/`: 10 test đạt;
- toàn bộ repository: 144 test đạt;
- kiểm tra biên dịch Python đạt;
- test xác nhận hash của 41 file snapshot và specification manifest,
  schema, pilot selection, metric, fake SDK client và API execution guard.

Code ADC/đa luồng/retry, progress bar và cấu hình model đã được kiểm bằng
client giả, không gọi Vertex AI. Toàn bộ `tests/` của dự án đạt 147 test bằng
`/home/quannda/miniconda3/envs/benchmark_env/bin/python`. Test xác nhận
việc ghi 40 kết quả tăng dần, chỉ retry candidate lỗi sau lượt quét đầu và
gửi `thinking_budget=0`; test progress xác nhận đủ số xử lý, số hoàn
thành, số lỗi và số request.

## Orchestrator decision

Plan 01 được đánh dấu hoàn thành. Plan 02 được đánh dấu đã cài đặt nhưng
chờ project lead chủ động chạy API và review output; chưa được coi là hoàn
thành pilot.

## Lệnh project lead chạy

Chạy từ repository root:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  src/vertex_ai_call/run_requirement_scoring.py pilot \
  --project edu-benchmark \
  --location global \
  --model gemini-2.5-flash \
  --temperature 0 \
  --top-p 1 \
  --max-output-tokens 4096 \
  --seed 20260727 \
  --thinking-budget 0 \
  --concurrency 8 \
  --max-retries 3 \
  --max-requests 120 \
  --execute-api
```

Lệnh này chuẩn bị pilot, chạy hai lần lặp A/B trên cùng 40 candidate rồi
hoàn tất bundle. Runner dùng ADC, hỗ trợ resume bằng request hash nếu quá
trình bị ngắt, và chỉ retry các candidate chưa có output hợp lệ.

Cấu hình model đã được project lead khóa để ưu tiên tính ổn định:
`gemini-2.5-flash`, không thinking, `temperature=0`, `top_p=1`,
`max_output_tokens=4096` và `seed=20260727`.

Progress bar mặc định được bật và hiển thị riêng cho lượt quét đầu cùng
từng lượt retry của run A/B. Mỗi thanh báo tiến độ lượt quét, tổng số mẫu
đã hoàn thành trên 40, số lỗi tạm thời và số request đã dùng trên trần
120. Có thể thêm `--no-progress` nếu cần tắt hiển thị; tùy chọn này không
tham gia request hash và không đổi kết quả model.

## Uncertainty

Đặc tả và score vẫn là provisional cho đến khi UET review kết quả pilot và
HNMU review gói nguyên tắc–năng lực–rubric tích hợp. Chưa có bằng chứng thực
nghiệm về độ ổn định vì API chưa chạy. Runner sẽ dừng trước khi tạo worker
nếu ADC không khả dụng.

## Open questions and next human decisions

- Project lead chạy lệnh pilot và kiểm chi phí/quota Vertex AI.
- UET review các score bất đồng, review queue và metric A/B.
- Sau khi pilot đạt, quyết định có khóa cấu hình để chạy đủ 2.028 candidate
  hay quay lại hiệu chỉnh prompt/anchor.
