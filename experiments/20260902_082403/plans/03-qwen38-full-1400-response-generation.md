# Plan 03 — Sinh full 1.400 phản hồi Qwen3.8

Experiment: `20260902_082403`  
Trạng thái: `DRAFT — AWAITING PLAN 02 GATE AND PROJECT-LEAD APPROVAL`  
Phụ thuộc: `P02`

## 1. Mục tiêu và ranh giới trách nhiệm

Sau khi Ollama provider, provider-neutral target runner và pilot đều đạt, chạy
đúng một target configuration Qwen3.8 trên toàn bộ 1.400 candidate, tạo response
bundle có thể resume và kiểm toán được.

Plan 03 chỉ sở hữu preflight và execution full run. Nó không sửa provider,
runner, schema, prompt, pilot selection hoặc model configuration sau khi đã nhìn
full output.

## 2. Điều kiện trước approval và thực thi

- Plan 01 và Plan 02 đều có trạng thái `completed`, gate `passed` và final
  report.
- Quân đã chấp nhận full model digest, cấu hình thinking/context/output,
  manual-review pilot, ETA và cửa sổ GPU.
- Pilot có đúng 30/30 target response hợp lệ và chứng minh resume 2→30.
- GPU không có compute process khác và đủ VRAM/headroom như pilot.
- Candidate manifest, instruction bundle, provider code, runner code và toàn bộ
  hash input/config vẫn đúng.
- Test/validator của Plan 01–02 vẫn đạt trong `benchmark_env`.
- Plan 03 được Quân duyệt riêng bằng dòng `APPROVED` trong file này.

Nếu bất kỳ điều kiện nào sai, full run không được bắt đầu.

## 3. Cấu hình được kế thừa

Plan 03 không tự đặt lại model configuration. Nó đọc cấu hình đã khóa trong
final report và manifest Plan 02. Baseline trước đo đạc là:

- Ollama native `/api/chat` tại loopback `127.0.0.1:11435`.
- Ollama `0.32.14` và cache/model path đã khóa ở Plan 01.
- `qwen3.8:latest`, full digest đã xác minh, 27,3B `Q4_K_M`.
- Instruction bundle `v2`, SHA-256
  `711256237b0d23923e516b974e498ff51dbd3251666512c6acfc3889b8329510`.
- Candidate manifest SHA-256
  `44555b481f63d29f77df651bc68e83c37c2529a56a213d6a560f01302d03e5bd`.
- Candidate-ID hash
  `4d4687d2f70235aff569f7b74121f5d2964558d9c57661139f28a3b410bb1fbb`.
- `num_ctx=4096`, `num_predict=2048`, thinking mode đã xác nhận ở pilot, seed
  `20260902`, một request tại một thời điểm và sampling contract từ Plan 02.

Mọi khác biệt so với pilot phải được ghi bằng amendment trước model call. Không
trộn hai configuration vào cùng run ID hoặc output directory.

## 4. Các bước triển khai dự kiến

### 4.1. Freeze và preflight

1. Ghi snapshot SHA-256 của provider code, runner code, input, instruction bundle
   và pilot manifest.
2. Kiểm `/api/version`, `/api/show`, full model digest, quantization, template,
   parameters và runtime env.
3. Kiểm GPU process/VRAM, RAM, disk/cache path; dừng nếu khác ngưỡng pilot.
4. Dựng lại đủ 1.400 `PreparedTutorRequest`; xác nhận tập ID và request hash
   khớp nguồn, không chứa gold/rubric/evaluator-only fields.
5. Chạy offline validation và fake-provider regression tests.
6. Tạo `run_manifest.json` trạng thái `prepared`, khóa toàn bộ selection/config/
   input/code hash trước response đầu tiên.

### 4.2. Chạy chính

- Xử lý deterministic theo danh sách candidate ID đã khóa.
- Một inflight request; model giữ trong VRAM giữa các request.
- Dùng đúng provider-neutral target runner đã nghiệm thu ở Plan 02.
- Append từng response thành công vào `run_responses.jsonl`.
- Mỗi attempt lỗi ghi vào `run_errors.jsonl` nhưng không lặp prompt/reasoning.
- Manifest checkpoint atomic ở các mốc vận hành được runbook khóa; JSONL là
  nguồn trạng thái tăng dần.
- Retry tối đa hai lần chỉ với `ProviderCallError.retryable=true`.
- HTTP 4xx cấu hình sai, digest mismatch, OOM/Xid, empty response, malformed
  response hoặc thinking leakage dừng fail-closed.
- `MAX_TOKENS` được ghi `needs_review`; không tự tăng cap trong primary run.
- Ghi resource snapshot định kỳ đủ để phát hiện VRAM/temperature drift nhưng
  không tạo thêm payload lớn ngoài artifact budget.

### 4.3. Resume

Resume phải:

1. Đọc và validate toàn bộ response đã có.
2. Dừng nếu provider/model/runtime/input/config/code hash khác.
3. Không gửi lại ID có response đã được ghi hợp lệ.
4. Chỉ chạy pending ID chưa có record.
5. Giữ attempt, resume history, timing và integrity; không ghi đè lịch sử.

Nếu có response `needs_review`, recovery là quyết định riêng bằng amendment,
khóa đúng danh sách ID và cap/config mới. Không sửa response đã hoàn tất hoặc
gọi full primary bundle là `completed` trước recovery hợp lệ.

### 4.4. Validation cuối

- Có đúng 1.400 JSONL record và 1.400 candidate ID duy nhất.
- Tập ID bằng chính xác candidate manifest; không thiếu/thừa.
- Mọi record có `response_status=completed`, finish reason thành công và
  `response_text` không rỗng.
- System prompt, conversation, request hash, bundle version/hash và required
  principle IDs được validator dựng lại và đối chiếu từ input nguồn.
- Provider/model/runtime/digest/config nhất quán với Plan 02.
- Không có raw thinking trong `response_text` hoặc artifact chính.
- Mỗi dòng giữ đúng target-response contract đã nghiệm thu ở Plan 02; metadata
  Ollama chi tiết nằm trong manifest, không tạo response shape mới.
- Manifest chỉ chuyển `completed` sau khi tất cả kiểm tra đạt.

## 5. Output và phạm vi ghi

Output chính:

`experiments/20260902_082403/outputs/qwen38_full_1400_v1/`

Ba machine output:

- `run_responses.jsonl`
- `run_errors.jsonl`
- `run_manifest.json`

Ngoài ra có tối đa một runbook, final report và handoff của Plan 03. Không ghi
vào `shared/` hoặc experiment nguồn.

Runtime/model cache chỉ được đọc từ path đã nghiệm thu ở Plan 01. Plan 03 không
được nâng cấp Ollama, pull lại tag, sửa provider hoặc sửa runner.

## 6. Nghiệm thu

- 1.400/1.400 candidate hoàn tất với zero duplicate/missing/extra.
- Zero empty, zero truncation và zero thinking leakage trong final bundle.
- Full model digest, Ollama version, config hash và input/code hashes khớp Plan
  01–02.
- Không có response ID nào của pilot bị trộn vào full run; full run dựng response
  mới cho đúng 1.400 ID dưới run ID riêng.
- Báo cáo tổng token, p50/p95 latency, prompt/decode throughput, wall time,
  retry, peak VRAM, temperature và trạng thái GPU offload.
- Validation và governance validator đạt bằng exact `benchmark_env` Python.
- Báo cáo chỉ gọi đây là target-response generation; không đưa ra kết luận chất
  lượng hoặc xếp hạng trước judge/human validation.

## 7. Phạm vi ghi sau approval

- `experiments/20260902_082403/outputs/qwen38_full_1400_v1/`
- runbook, final report, handoff, status, amendment và coordination artifact trực
  tiếp của Plan 03 dưới `experiments/20260902_082403/`

Plan 03 không được ghi vào `src/`, `scripts/`, `tests/`, `shared/`, runtime/cache
hoặc experiment nguồn. Nếu preflight phát hiện cần sửa code/config contract,
dừng Plan 03 và quay lại owner plan phù hợp; không hot-fix trong full run.

## 8. Rủi ro và rollback

| Rủi ro | Dấu hiệu | Xử lý |
|---|---|---|
| Process chết | JSONL dừng giữa batch | Giữ output và resume đúng pending ID |
| Hash/model drift | Runtime/model/code khác manifest | Đóng gate; không merge hai configuration |
| OOM/thermal/Xid | GPU lỗi hoặc vượt ngưỡng pilot | Dừng model, giữ checkpoint, chờ Quân quyết định |
| Truncation | Một hoặc nhiều `MAX_TOKENS` | Bundle `blocked_pending_recovery`; amendment riêng |
| Sai role/prompt hàng loạt | Response cho thấy system/history mapping bất thường | Dừng; quay về Plan 02, không sửa prompt cùng run |
| ETA thay đổi lớn | Throughput giảm ngoài dải pilot | Dừng ở checkpoint vận hành và xin quyết định |

Rollback chỉ dừng foreground runtime và giữ response/checkpoint. Xóa model hoặc
output là destructive action cần yêu cầu riêng.

## 9. Quyết định cần duyệt

Sau khi Plan 02 pass, Quân duyệt riêng:

1. Configuration chính xác được kế thừa từ pilot.
2. ETA, cửa sổ chạy và quyền sử dụng độc quyền GPU.
3. Cho phép model call đủ 1.400 candidate.
4. Stop rules và nguyên tắc recovery phải qua amendment.
5. Xác nhận output vẫn experiment-scoped, chưa promote vào `shared`.

Plan này hiện là `DRAFT`; chưa cho phép full run.
