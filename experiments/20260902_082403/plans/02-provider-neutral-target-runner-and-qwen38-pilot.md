# Plan 02 — Provider-neutral target runner và Qwen3.8 pilot 2→30

Experiment: `20260902_082403`  
Trạng thái: `APPROVED BY QUÂN ON 2026-09-02 — IN PROGRESS`  
Phụ thuộc: `P01`

## 1. Mục tiêu và ranh giới trách nhiệm

Nối workflow sinh AI tutor response hiện có vào contract `ModelProvider`, giữ
nguyên hành vi chuẩn bị prompt và lưu target response, rồi dùng
`OllamaProvider` đã khóa ở Plan 01 để chạy hai candidate technical smoke và
resume lên pilot 30 candidate.

Plan 02 sở hữu:

- phần tích hợp `PreparedTutorRequest → ModelRequest → ModelProvider`;
- orchestration provider-neutral cho retry, resume, record và manifest;
- tương thích schema/validator với target-response record lịch sử;
- lựa chọn khóa trước 30 candidate, chạy 2→30 và đo tài nguyên/ETA.

Plan 02 không sở hữu implementation Ollama provider, không tải/nâng cấp model,
không chạy full 1.400 và không thiết kế một persistence format mới.

## 2. Baseline code phải được bảo toàn

### 2.1. Phần đã có và được tái sử dụng

| Thành phần | Chức năng hiện có |
|---|---|
| `benchmark_evaluation/smoke.py` | Join grounding, requirement set, instruction bundle và dựng `PreparedTutorRequest` kèm prompt/hash |
| `dialogue_transport.py` | Bảo toàn ranh giới multi-turn user/assistant |
| `prompt_builder.py`, `instruction_bundle.py` | Dựng system instruction từ bundle có version |
| `scripts/benchmark_evaluation/run_vertex_smoke.py` | Ghi response JSONL tăng dần, error JSONL, retry, resume, completion state, integrity và manifest |
| `benchmark_evaluation/recovery.py` | Recovery fail-closed cho target response bị thiếu/cụt |
| `model_providers/contracts.py` | Request/response/error contract dùng chung |

Ba full target bundle trước đã dùng record shape này và mỗi bundle có đúng
1.400 record cùng manifest `completed`. Vì vậy Plan 02 phải tái sử dụng và kiểm
chứng tương đương; không copy một runner riêng chỉ dành cho Ollama.

### 2.2. Khoảng cách tích hợp cần xử lý

Runner synchronous cũ vẫn:

- chứa trực tiếp `GeminiCaller`, `OpenAIMaaSCaller` và Vertex endpoint branch;
- dùng `caller.call(PreparedTutorRequest) -> dict` thay vì
  `ModelProvider.generate(ModelRequest) -> ModelResponse`;
- hard-code experiment/plan/pipeline metadata cũ;
- trộn CLI, provider, cost preflight, retry, persistence và validation trong
  một script;
- chỉ chấp nhận cost basis theo API token hoặc Vertex endpoint runtime;
- có schema sinh ra thiếu property `provider` và `usage.cost_basis`, dù record
  lịch sử thực tế chứa hai trường đó.

Plan 02 chỉ tách/generalize phần cần thiết để target generation dùng provider
boundary chung. Mọi thay đổi phải có regression test giữ nguyên input hash,
message order, finish-state classification và record fields.

## 3. Điều kiện trước approval và thực thi

- Plan 01 có trạng thái `completed`, gate `passed` và final report.
- `OllamaProvider` tests đạt và runtime probe đi thật qua full digest đã khóa.
- Runtime/model/cache còn nguyên version, digest, quantization và permission.
- Candidate manifest, requirement run và instruction bundle nguồn còn đúng hash.
- Quân duyệt riêng Plan 02 bằng dòng `APPROVED` trong file này.

Nếu một điều kiện sai, không sửa runner và không gọi model trên benchmark.

## 4. Phạm vi triển khai sau approval

### 4.1. Tách reusable target workflow

Logic nghiệp vụ đặt dưới `src/edu_benchmark/benchmark_evaluation/`; CLI chỉ đọc
argument/config, gọi package, báo progress và ánh xạ exit code.

Kiến trúc đích:

```text
candidate/input artifacts
        ↓
prepare_tutor_requests() → PreparedTutorRequest
        ↓
target-domain adapter → ModelRequest
        ↓
ModelProvider.generate() → ModelResponse / ProviderCallError
        ↓
target runner hiện có: classify → append → resume → validate → manifest
```

Thay đổi dự kiến:

- Tạo reusable target workflow, dự kiến
  `src/edu_benchmark/benchmark_evaluation/target_runner.py`.
- Dùng trực tiếp `PreparedTutorRequest` và `trace_fields()` hiện có.
- Tạo `ModelRequest` từ system instruction, conversation messages và generation
  settings; không đưa gold answer, gold response, rubric hoặc judge metadata vào
  provider.
- Nhận `ModelProvider` qua dependency injection/registry; workflow không import
  `OllamaProvider` trực tiếp.
- Tạo thin generic CLI, dự kiến
  `scripts/benchmark_evaluation/run_target_responses.py`.
- Chuyển runner Vertex cũ thành compatibility wrapper tới cùng workflow, hoặc
  giữ entry point cũ chỉ khi không còn hai bản business logic song song.
- Không sửa response/output lịch sử.

### 4.2. Persistence được kế thừa, không thiết kế lại

Target runner giữ các semantics đã có:

1. Mỗi response thành công được append ngay thành một dòng JSONL.
2. Mỗi attempt lỗi được append vào error JSONL, không chứa prompt/credential.
3. Resume đọc toàn bộ record cũ, chặn duplicate và chỉ xử lý ID chưa ghi.
4. Instruction bundle/model/candidate/config hash khác phải fail-closed và dùng
   output directory mới.
5. `MAX_TOKENS`/lý do không thành công thành `needs_review`; không giả vờ
   `completed`.
6. Response đã `needs_review` không được tự chạy lại như pending; recovery dùng
   workflow/amendment riêng.
7. Manifest được ghi atomic; JSONL là nguồn checkpoint tăng dần khi process dừng.

Schema/validator chỉ được đồng bộ với record thực tế:

- khai báo `provider` trong target response;
- khai báo `usage.cost_basis` và cho phép
  `local_runtime_no_token_api_charge` với `estimated_cost_usd=0.0`;
- giữ các field lịch sử `created_at`, `model_version`, `latency_seconds`,
  `attempt`;
- không xóa field, đổi tên field hoặc rewrite record cũ;
- thêm regression fixture lấy đúng shape của target bundle cũ.

### 4.3. Contract target response của Qwen3.8

Mỗi dòng `run_responses.jsonl` giữ contract lịch sử:

| Trường | Giá trị/nguồn cho pilot |
|---|---|
| `record_type` | `target_response` |
| `created_at` | ISO-8601 UTC |
| `experiment_id`, `plan_id` | `20260902_082403`, `plan02` |
| `pipeline_stage` | `benchmark_evaluation_target_pilot` |
| `run_id` | `target_qwen38_pilot_30_v1` |
| `benchmark_candidate_id` | ID trong selection block đã khóa |
| `provider` | `ollama` |
| `model_id` | Tag request `qwen3.8:latest` |
| `model_version` | Full resolved digest/model identity từ Plan 01 |
| `response_id` | Provider ID hoặc ID ổn định từ run/candidate/response hash |
| `response_text` | Chỉ `ModelResponse.text`, không có thinking |
| `finish_reason` | Giá trị chuẩn hóa như `STOP`, `MAX_TOKENS` |
| `response_status` | `completed` hoặc `needs_review` |
| `completion_issue` | `null` hoặc lý do chuẩn hóa |
| `system_prompt`, `user_prompt` | Exact prompt đã gửi và user message cuối |
| `conversation_messages` | Toàn bộ messages trước target |
| Các hash/bundle field | Từ `PreparedTutorRequest.trace_fields()` |
| `required_principle_ids` | Tập requirement score `>=4` đã khóa |
| `usage` | Input/output tokens, zero API token charge, local cost basis |
| `latency_seconds`, `attempt` | Wall time và attempt thành công |

`usage`:

```json
{
  "input_tokens": 0,
  "output_tokens": 0,
  "estimated_cost_usd": 0.0,
  "cost_basis": "local_runtime_no_token_api_charge"
}
```

Token count lấy từ normalized `ModelResponse.usage`. Giá trị chi phí bằng zero
chỉ có nghĩa không có phí API theo token; GPU, điện và thời gian không được diễn
giải là có chi phí kinh tế bằng zero.

Metadata chi tiết như Ollama version, full digest, quantization, template,
parameter hash, cache root, `num_ctx`, `num_predict`, thinking, sampling,
provider timing và resource snapshots nằm trong `run_manifest.json`, không tạo
response shape riêng cho Ollama.

### 4.4. Khóa pilot 30 trước model call

Nguồn benchmark:

- Candidate manifest:
  `experiments/20260727_170150/outputs/benchmark_evaluation/full_1400_v1/candidate_manifest.json`.
- Instruction bundle:
  `shared/prompts/benchmark_tutor_response_generation/instruction_bundle_v2.yaml`.
- Candidate manifest SHA-256:
  `44555b481f63d29f77df651bc68e83c37c2529a56a213d6a560f01302d03e5bd`.
- Candidate-ID hash:
  `4d4687d2f70235aff569f7b74121f5d2964558d9c57661139f28a3b410bb1fbb`.
- Instruction bundle SHA-256:
  `711256237b0d23923e516b974e498ff51dbd3251666512c6acfc3889b8329510`.

Selection 30 được khóa trong immutable section của `run_manifest.json` trước
model call:

- giữ đúng 10 candidate của smoke `instruction_v2` cũ để so sánh cùng input;
- thêm 20 candidate cân bằng lớp, độ dài input, một/hai/ba principle, có/không
  history và nội dung code;
- không quá một target request cho cùng candidate;
- hai technical-smoke ID nằm trong 30 ID: một input ngắn và một input dài nhất;
- lưu danh sách ID, selection method/version và SHA-256 trước khi gọi provider.

Không chọn/thay candidate sau khi xem output, trừ khi Quân duyệt amendment với
lý do lỗi input độc lập với model.

### 4.5. Cấu hình pilot ứng viên

Cấu hình chỉ được khóa cuối sau khi đọc final report Plan 01:

| Trường | Baseline đề xuất |
|---|---|
| Runtime/API | Ollama `0.32.14`, native `/api/chat`, loopback `11435` |
| Model | `qwen3.8:latest`, full digest/Q4_K_M đã khóa |
| `num_ctx` | 4096 |
| `num_predict` | 2048 |
| Thinking | `medium` nếu Plan 01 xác nhận hỗ trợ |
| Seed | `20260902` |
| Sampling | Không override ngoài giá trị đã duyệt; lưu model defaults |
| Parallel/inflight | 1 |
| `keep_alive` | `-1` trong pilot; unload có kiểm soát cuối run |
| Timeout | 600 giây/request |
| Retry | Tối đa 2 cho lỗi provider được phân loại retryable |

Mọi khác biệt so với baseline phải được ghi trong baseline trước approval hoặc
amendment sau approval; không đổi cấu hình sau khi nhìn response cùng run ID.

## 5. Chuỗi kiểm tra và model call

### Gate A — Offline equivalence

- Fake provider test chứng minh request mapping đúng system/messages/settings.
- Test response/error mapping, retry, resume, duplicate rejection và hash drift.
- Regression test với target-record shape lịch sử.
- Test local cost basis, truncated response và no-thinking persistence.
- Test compatibility entry point không duy trì logic song song.
- Preflight dựng đủ 30 request và manifest selection nhưng không gọi model.

### Gate B — Technical smoke trong cùng pilot bundle

- Gọi đúng hai ID đã khóa và ghi hai dòng đầu vào `run_responses.jsonl`.
- Yêu cầu 2/2 `STOP`, response không rỗng, prompt/hash khớp, model digest đúng và
  không có thinking leakage.
- Ghi phase `technical_smoke_completed` vào manifest nhưng giữ cùng run ID và
  cùng configuration.
- Quân hoặc orchestrator xác nhận Gate B trước khi resume 28 ID.

Nếu một response `needs_review`, empty, sai digest, OOM/Xid hoặc role mapping
khả nghi, dừng. Không thay nó bằng candidate khác và không tiếp tục pilot.

### Gate C — Resume lên pilot 30

- Runner đọc lại hai record, xác nhận hash/config và chỉ gửi 28 pending ID.
- Kết thúc với đúng 30 candidate ID duy nhất; không ghi lại hai smoke response.
- Quân review thủ công tối thiểu 10/30 response về tiếng Việt, độ liên quan, kết
  thúc trọn câu, không lặp system prompt và không để lộ reasoning.
- Báo p50/p95 input/output tokens, latency, prompt/decode throughput, VRAM,
  nhiệt độ, retry và ETA full có tối thiểu 20% dự phòng.

Manual review là quality gate vận hành, không phải human ground truth hay kết
luận chất lượng model.

## 6. Output dự kiến

Toàn bộ machine output:

`experiments/20260902_082403/outputs/qwen38_pilot_30_v1/`

| File | Format | Vai trò |
|---|---|---|
| `run_responses.jsonl` | UTF-8 JSONL, một object/dòng | Tăng từ 2 lên 30 record, cùng run/config |
| `run_errors.jsonl` | UTF-8 JSONL, một attempt lỗi/dòng | Retry/audit, không chứa prompt/reasoning/secret |
| `run_manifest.json` | Một JSON object ghi atomic | Selection/config hash, phase history 2→30, resume, integrity và resource summary |

Plan còn có tối đa một runbook, final report và handoff. Không ghi output vào
`shared/` hoặc experiment nguồn.

## 7. Nghiệm thu Plan 02

- Target workflow gọi provider qua `ModelProvider`, không qua branch Ollama đặc
  thù trong runner.
- Persistence/retry/resume/validation có regression test tương đương hành vi cũ.
- Existing Vertex/OpenAI provider consumers và test liên quan không regression.
- Technical smoke đạt 2/2 và resume không gọi lại hai ID.
- Pilot đạt 30/30 ID duy nhất, zero missing/duplicate/empty/truncation/thinking
  leakage và zero invalid provenance.
- Full digest/config/input hash nhất quán trong toàn bundle.
- Quân review tối thiểu 10 response và chấp nhận hoặc từ chối gate.
- ETA full và tài nguyên được báo; nếu ETA vượt 24 giờ, Plan 03 vẫn đóng cho tới
  khi Quân chấp nhận rõ ràng.
- Tất cả test/validator đạt bằng exact `benchmark_env` Python.
- `ARCHITECTURE.md`, README và governance artifact phản ánh component thực tế.

## 8. Phạm vi ghi sau approval

- `src/edu_benchmark/benchmark_evaluation/`
- `scripts/benchmark_evaluation/`
- `tests/benchmark_evaluation/`
- `README.md`
- `ARCHITECTURE.md`
- `src/edu_benchmark/README.md`
- `experiments/20260902_082403/`

Plan 02 chỉ đọc `src/edu_benchmark/model_providers/` đã hoàn tất ở Plan 01. Nếu
phát hiện provider bug, dừng và xin amendment/plan sửa đúng owner; không lén mở
rộng phạm vi. Không ghi `shared/`, runtime/cache, system service hoặc output cũ.

## 9. Rủi ro và rollback

| Rủi ro | Dấu hiệu | Xử lý |
|---|---|---|
| Refactor làm đổi prompt/hash | Regression fixture khác baseline | Dừng; compatibility entry point cũ tiếp tục là rollback |
| Hai runner song song | Cùng logic persistence ở script và package | Không nghiệm thu; gom về một implementation |
| Resume ghi trùng | Candidate đã có xuất hiện lần hai | Dừng, giữ artifact để điều tra; không tự sửa JSONL |
| Schema drift | Record cũ không validate hoặc field bị đổi | Dừng; mở rộng tương thích, không rewrite lịch sử |
| Model/runtime bất ổn | OOM, Xid, CPU offload, digest drift | Dừng pilot; quay về gate Plan 01 |
| Thinking/truncation | Reasoning trong answer hoặc `MAX_TOKENS` | Dừng; không đổi cap/mode cùng run |

Rollback code dùng compatibility wrapper/implementation đã kiểm chứng trước refactor.
Rollback run giữ JSONL/manifest và dừng foreground runtime; không xóa artifact.

## 10. Quyết định cần Quân duyệt

Sau khi Plan 01 pass, Quân duyệt riêng:

1. Cho phép tách target workflow provider-neutral nhưng giữ nguyên persistence
   semantics và record shape lịch sử.
2. Cho phép khóa selection 30, trong đó hai ID đầu là technical smoke.
3. Cho phép cấu hình pilot chính xác sau khi đối chiếu final report Plan 01.
4. Cho phép resume 2→30 chỉ sau Gate B.
5. Xác nhận hoàn tất Plan 02 không tự động mở full run Plan 03.
