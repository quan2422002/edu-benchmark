# Handoff

- Event ID: `EXP-20260902_082403-P01-COMPLETE-020`
- Plan ID: `P01` với các draft phụ thuộc `P02`, `P03`
- Mode: `single-agent`
- Agent: `Codex orchestrator`
- Status: `completed`
- Native thread ID/label: `not-applicable`

## Task or delegation request

Điều tra `qwen3.8:latest`, tài nguyên server và code sinh tutor response; tổ chức
một experiment có quyền phê duyệt tách biệt cho provider, pilot và full run.

## Follow-up or scope changes

Không có delegation.

Baseline ban đầu chia hai plan: Plan 01 gộp runtime, provider, target runner và
pilot; Plan 02 chạy full 1.400. Khi cả hai baseline vẫn `DRAFT`, Quân yêu cầu
tách trách nhiệm thành ba plan sau khi điều tra xác nhận persistence target
response đã tồn tại nhưng runner synchronous vẫn gắn Vertex:

1. Plan 01 chỉ gồm Ollama runtime/cache và `OllamaProvider`.
2. Plan 02 nối provider-neutral target runner, tái sử dụng persistence hiện có
   và chạy pilot 2→30.
3. Plan 03 chỉ chạy full 1.400 sau một approval riêng.

Vì chưa plan nào được phê duyệt, baseline/status/roadmap được tái tổ chức trực
tiếp và không cấp amendment ID. Coordination log giữ chronology của quyết định.

Hai yêu cầu trước vẫn được bảo toàn:

- dùng cache root canonical cho Ollama, Hugging Face, vLLM và local-LLM
  framework tương lai;
- target technical smoke/pilot dùng JSONL và contract tương thích response lịch
  sử, nhưng trách nhiệm này chuyển hoàn toàn sang Plan 02.

## Inputs read

- `README.md`, `ARCHITECTURE.md` và roadmap active của experiment.
- Candidate manifest full 1.400 và instruction bundle `v2`.
- `src/edu_benchmark/benchmark_evaluation/`.
- `src/edu_benchmark/model_providers/`.
- `scripts/benchmark_evaluation/run_vertex_smoke.py`, tests và full wrapper cũ.
- Ba target bundle lịch sử, mỗi bundle 1.400 response `completed`.
- Experiment governance templates.
- Thông tin read-only từ GPU, Ollama, systemd, RAM và filesystem.
- Ollama library/API/GPU/context/FAQ và official GitHub releases.

## Outputs created

- Roadmap ba plan và metadata đã đồng bộ.
- `plans/01-ollama-qwen38-runtime-and-provider.md` cùng status/amendment log.
- `plans/02-provider-neutral-target-runner-and-qwen38-pilot.md` cùng
  status/amendment log.
- `plans/03-qwen38-full-1400-response-generation.md` cùng status/amendment log.
- Coordination event và handoff này.

## Result summary

Ranh giới mới ngăn model provider sở hữu prompt, target-response schema hoặc
persistence nghiệp vụ. Plan 01 không tạo `run_responses.jsonl`; Plan 02 kế thừa
append/retry/resume/manifest hiện có và dùng hai response đầu làm technical smoke
của cùng pilot 30; Plan 03 không được sửa code và chỉ thực thi full run.

RTX 3090 24 GiB có khả năng chạy model khoảng 18 GB Q4_K_M với context nhỏ nhưng
phải qua runtime probe. Hai blocker vật lý vẫn là Ollama system `0.9.6` chưa hỗ
trợ Qwen3.8 và cache system nằm trên phân vùng `/` chỉ còn khoảng 19 GB. Plan 01
đề xuất runtime `0.32.14` và cache root
`/workspace/quannd/local_llm_cache/`.

## Orchestrator decision

Giữ cả ba plan ở `DRAFT`. Không sửa code, cài runtime, pull model, gọi model hoặc
sinh benchmark response trước approval tương ứng.

## Uncertainty

- Runtime probe đã xác nhận 100% GPU, nhưng peak memory/throughput trên candidate
  benchmark chỉ có thể đo ở pilot Plan 02.
- Tag `latest` mutable; các plan sau phải tiếp tục khóa full digest đã ghi trong
  runtime manifest.
- Refactor provider-neutral target runner vẫn cần regression test vì code lưu
  hiện nằm trong script Vertex-specific.

## Open questions and next human decisions

- Gate A–C đã đạt; Quân quyết định có phê duyệt riêng Plan 02 hay không.
- Quân tiếp tục sở hữu service: attach `screen -r ollama-qwen38` rồi nhấn
  `Ctrl+C` khi muốn dừng; probe không sở hữu vòng đời server.
- Plan 03 vẫn đóng.

## Cập nhật triển khai ngày 02/09/2026

Quân đã duyệt Plan 01. Codex triển khai single-agent, không gọi specialist và
không chạm `benchmark_evaluation`, candidate, `shared` hay output lịch sử.

Đã hoàn tất phần offline:

- thêm `OllamaProvider` native `/api/chat`, registry alias, kiểm runtime/cache và
  probe CLI;
- bảo toàn system/user/assistant boundary, gửi `stream=false`, ánh xạ sampling,
  usage/timing/retry và chỉ đưa `message.content` vào response text;
- runtime `0.32.14` được tải từ GitHub release chính thức, kiểm đúng
  1.421.191.399 byte và SHA-256
  `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f`,
  rồi giải nén dưới `/workspace/quannd/local_llm_runtime/ollama/v0.32.14/`;
- cache đa framework nằm dưới `/workspace/quannd/local_llm_cache/`, owner
  `quannd`, mode `0750`, không dùng phân vùng `/`;
- 28 provider/runtime/launcher tests đạt bằng
  `/workspace/quannd/miniconda3/envs/benchmark_env/bin/python`;
- ADR 0004, launcher và runbook đã được tạo.

Hiện trạng live:

- hai lần chạy ở port 11435 đã fail-closed vì port này thuộc một Docker
  container ngoài dự án; P01-A002 chuyển launcher sang port 11436;
- model đã pull đủ vào cache trên `/workspace`, resolve digest đầy đủ và xác
  nhận Q4_K_M;
- lỗi preload đầu tiên do chuỗi `keep_alive: "-1"`; P01-A003 sửa thành số `-1`;
- service canonical do Quân bật đã đạt `READY:`, context 4096 và 100% GPU;
- Gate C đã gọi fixture qua `OllamaProvider`, trả `STOP`, usage/timing hợp lệ,
  không lưu thinking text; `runtime_manifest.json` và `provider_probe.json` đều
  có trạng thái pass;
- Plan 01 đã đóng; Plan 02 chỉ được triển khai sau approval riêng của Quân.

Theo P01-A001, launcher nay tự start server, pull/resume, kiểm model, preload và
ghi log; nó vẫn không gửi prompt inference. Lệnh handoff mới để Quân chạy từ
repository root:

```bash
screen -dmS ollama-qwen38 bash -lc 'exec scripts/model_providers/run_ollama_server.sh'
```

Service tiếp tục sống trong session sau `READY:`. Quân chủ động tắt bằng:

```bash
screen -r ollama-qwen38
```

Sau khi attach, nhấn `Ctrl+C`.

Theo dõi toàn bộ tiến độ ở:

```bash
tail -f experiments/20260902_082403/logs/ollama-qwen38-service.log
```
