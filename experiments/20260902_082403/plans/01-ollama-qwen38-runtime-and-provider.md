# Plan 01 — Ollama/Qwen3.8 runtime và model provider

Experiment: `20260902_082403`  
Trạng thái: `APPROVED BY QUÂN ON 2026-09-02 — IN PROGRESS`  
Phụ thuộc: không có plan nội bộ; chỉ đọc hiện trạng repository và server

## 1. Mục tiêu và ranh giới trách nhiệm

Thiết lập một runtime Ollama cô lập, tải và khóa đúng model
`qwen3.8:latest` Q4_K_M, rồi cài một `OllamaProvider` tuân thủ contract
`edu_benchmark.model_providers` hiện có.

Plan này chỉ trả lời hai câu hỏi:

1. Runtime/model có được quản lý an toàn và chạy ổn định trên server hiện tại
   không?
2. Ollama provider có ánh xạ chính xác request, response, usage và lỗi vào
   contract provider-neutral không?

Plan 01 **không** chuẩn bị candidate benchmark, không tạo target-response
record, không thiết kế persistence, không chạy technical smoke trên candidate
và không sinh pilot 30 mẫu. Các việc đó thuộc Plan 02.

## 2. Kết luận điều tra làm baseline

### 2.1. Model được yêu cầu

Theo [Ollama library](https://ollama.com/library/qwen3.8) và trang tag
[`qwen3.8:latest`](https://ollama.com/library/qwen3.8:latest), tag được quan sát
ngày 02/09/2026 trỏ đến Qwen3.8-27B:

| Thuộc tính | Giá trị đã quan sát | Ý nghĩa cho Plan 01 |
|---|---|---|
| Parameter | 27,3B dense | Tương đối lớn cho một GPU 24 GiB |
| Format/quantization | GGUF `Q4_K_M` | Đúng biến thể Quân yêu cầu |
| Dung lượng model | Khoảng 18 GB | Có khả năng vừa VRAM nhưng headroom không lớn |
| Context công bố | 256K | Không cấp context này trên RTX 3090 trong probe |
| Input | Text và image | Provider Plan 01 chỉ cần chứng minh text path |
| Projector | CLIP 461M BF16 | Phải tính vào kiểm tra load thực tế dù không gửi ảnh |
| Thinking | Bật mặc định, có điều khiển | Phải tách thinking khỏi `ModelResponse.text` |
| License | Apache-2.0 | Lưu license/model metadata trong runtime manifest |
| Tag alias | `latest` và `27b` cùng digest rút gọn `22130167c4c2` khi khảo sát | Tag mutable; phải khóa full digest sau pull |

Ollama chỉ thêm hỗ trợ Qwen3.8-27B từ
[`v0.32.12`](https://github.com/ollama/ollama/releases/tag/v0.32.12), bổ sung
xử lý developer instruction ở
[`v0.32.13`](https://github.com/ollama/ollama/releases/tag/v0.32.13), và bản
stable mới nhất quan sát được là
[`v0.32.14`](https://github.com/ollama/ollama/releases/tag/v0.32.14). Binary
system `0.9.6` hiện có không đủ điều kiện cho model này.

### 2.2. Tài nguyên server đã đo

| Thành phần | Trạng thái ngày 02/09/2026 | Đánh giá |
|---|---|---|
| GPU | 1 × RTX 3090, compute capability 8.6 | Được Ollama/NVIDIA hỗ trợ |
| VRAM | 24.576 MiB; 23.890 MiB rảnh khi đo | Phải probe context nhỏ mới kết luận |
| Driver/CUDA | 575.57.08 / CUDA 12.9 | Vượt yêu cầu driver hiện hành của Ollama |
| GPU workload | Không có compute process; khoảng 233 MiB cho desktop | Gần như rảnh tại thời điểm đo |
| CPU | Xeon Silver 4114, 10 core/20 thread | Không chọn CPU offload làm cấu hình chính |
| RAM | 62 GiB; khoảng 36 GiB available | Đủ hỗ trợ runtime nhưng không thay VRAM gate |
| Swap | 0 | OOM phải fail-closed |
| Phân vùng `/` | 439 GB, chỉ còn 19 GB | Không pull model vào cache system |
| Phân vùng workspace | Khoảng 1,2 TB còn trống | Dùng cho runtime/cache cô lập |
| Ollama system | Service active, client/server `0.9.6` | Không sửa hoặc nâng cấp trong plan này |
| Cache system | 6,5 GB tại `/usr/share/ollama/.ophuollama/models` | Không xóa, di chuyển hoặc ghi thêm |

Nhu cầu bộ nhớ phụ thuộc context và số request song song. Runtime probe phải dùng
`ollama ps` để kiểm tỷ lệ GPU; xem [FAQ](https://docs.ollama.com/faq),
[context length](https://docs.ollama.com/context-length) và
[GPU support](https://docs.ollama.com/gpu).

### 2.3. Ranh giới code hiện có

| Thành phần | Trạng thái | Quyết định Plan 01 |
|---|---|---|
| `model_providers/contracts.py` | Có `ModelRequest`, `ModelResponse`, `TokenUsage`, `ProviderCallError`, `ModelProvider` | Tuân thủ, chỉ mở rộng khi Ollama có dữ liệu thật sự không biểu diễn được |
| `model_providers/registry.py` | Registry lazy cho Vertex AI/OpenAI | Đăng ký backend `ollama` |
| `benchmark_evaluation/smoke.py` | Chuẩn bị `PreparedTutorRequest` | Không sửa, không gọi |
| `scripts/benchmark_evaluation/run_vertex_smoke.py` | Có persistence nhưng gắn Vertex | Không sửa trong Plan 01 |
| Target response JSONL/schema | Artifact nghiệp vụ benchmark | Không thuộc Plan 01 |

Provider dùng native `POST /api/chat`, không dùng `/v1/chat/completions`, vì
native API trả `done_reason`, token count và timing trực tiếp. Contract tham
chiếu: [Generate a chat message](https://docs.ollama.com/api/chat) và
[Show model details](https://docs.ollama.com/api-reference/show-model-details).

## 3. Phạm vi triển khai sau approval

### 3.1. Runtime cô lập

- Binary Ollama `v0.32.14` đặt tại
  `/workspace/quannd/local_llm_runtime/ollama/v0.32.14/`.
- Bind duy nhất `127.0.0.1:11435`, không đụng service `11434` hiện có.
- Chạy `ollama serve` foreground trong terminal/session quan sát được; không tạo
  daemon hoặc systemd unit mới.
- Không sửa `/usr/local/bin/ollama`, `/etc/systemd/system/ollama.service` hoặc
  `/usr/share/ollama/`.
- Chỉ cho phép GPU UUID
  `GPU-5e1bf88a-a431-9a0c-b462-37cd95b5e9b8`.
- `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1`,
  `OLLAMA_FLASH_ATTENTION=1`; KV cache bắt đầu bằng `f16`.
- Binary/asset lấy từ release chính thức và kiểm SHA-256 trước giải nén.
- Chỉ pull model sau khi preflight xác nhận model store thật nằm trên
  `/workspace` và phân vùng đủ dung lượng.

### 3.2. Quy ước cache local-LLM dùng chung

Storage root canonical:

`/workspace/quannd/local_llm_cache/`

```text
/workspace/quannd/local_llm_cache/
├── ollama/models/
├── huggingface/hub/
├── huggingface/datasets/
├── huggingface/assets/
├── huggingface/xet/
├── vllm/
├── torch/
├── triton/
└── tmp/
```

Ánh xạ environment:

| Framework | Biến | Giá trị |
|---|---|---|
| Quy ước dự án | `LOCAL_LLM_CACHE_ROOT` | `/workspace/quannd/local_llm_cache` |
| Ollama | `OLLAMA_MODELS` | `$LOCAL_LLM_CACHE_ROOT/ollama/models` |
| Hugging Face Hub | `HF_HUB_CACHE` | `$LOCAL_LLM_CACHE_ROOT/huggingface/hub` |
| Hugging Face Datasets | `HF_DATASETS_CACHE` | `$LOCAL_LLM_CACHE_ROOT/huggingface/datasets` |
| Hugging Face assets | `HF_ASSETS_CACHE` | `$LOCAL_LLM_CACHE_ROOT/huggingface/assets` |
| Hugging Face Xet | `HF_XET_CACHE` | `$LOCAL_LLM_CACHE_ROOT/huggingface/xet` |
| vLLM | `VLLM_CACHE_ROOT` | `$LOCAL_LLM_CACHE_ROOT/vllm` |
| Torch, khi dùng | `TORCH_HOME` | `$LOCAL_LLM_CACHE_ROOT/torch` |
| Triton, khi dùng | `TRITON_CACHE_DIR` | `$LOCAL_LLM_CACHE_ROOT/triton` |

Hugging Face/vLLM weights dùng chung `HF_HUB_CACHE`; không tải lặp snapshot vào
`vllm/`. Không đặt global `XDG_CACHE_HOME`. Không lưu token/credential trong
cache. Root và thư mục con phải thuộc `quannd`, không world-writable; preflight
kiểm owner, permission, filesystem và dung lượng trống.

Quy ước dựa trên `OLLAMA_MODELS` trong [Ollama FAQ](https://docs.ollama.com/faq),
các biến cache của
[Hugging Face Hub](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables),
[Hugging Face Datasets](https://huggingface.co/docs/datasets/main/cache) và
[vLLM](https://docs.vllm.ai/en/stable/configuration/env_vars/). Khi được triển
khai, quy ước cross-framework này được ghi thành ADR dưới `docs/decisions/`.

### 3.3. Ollama provider

Code reusable phải nằm trong package; CLI probe chỉ parse argument, gọi package
và ánh xạ exit code:

- Tạo `src/edu_benchmark/model_providers/ollama/provider.py` và `__init__.py`.
- Đăng ký `ollama` trong `model_providers/registry.py`.
- Bổ sung export cần thiết trong `model_providers/__init__.py`.
- Tạo thin operational probe dưới `scripts/model_providers/` nếu cần.
- Bổ sung fake-HTTP tests trong `tests/model_providers/`.
- Không thêm Ollama Python SDK nếu standard-library HTTP đáp ứng contract.

Provider phải:

1. Nhận `ModelRequest` và gửi system instruction thành system message riêng.
2. Giữ nguyên mọi ranh giới `user`/`assistant` theo thứ tự.
3. Ánh xạ `GenerationSettings` dùng chung và chỉ dùng `provider_options` cho
   trường thực sự đặc thù Ollama.
4. Gửi `stream=false`; không tự đổi context, thinking hoặc sampling.
5. Chỉ trả `message.content` trong `ModelResponse.text`; không ghép
   `message.thinking` và không lưu reasoning trace.
6. Chuẩn hóa `done_reason=stop` thành `STOP`; reason hết giới hạn thành
   `MAX_TOKENS`; reason khác giữ dạng chuẩn hóa có thể audit.
7. Ánh xạ `prompt_eval_count`, `eval_count` vào `TokenUsage`; giữ timing và
   provider metadata trong `TokenUsage.metadata`.
8. Gắn model tag, full digest đã resolve, Ollama version và response ID ổn định.
9. Phân loại timeout/connection/HTTP 5xx là retryable; HTTP 4xx cấu hình sai là
   non-retryable; cắt response body và không đưa prompt/secret vào lỗi.
10. Từ chối empty content và malformed JSON.

Nếu dữ liệu thinking/timing cần metadata mới, ưu tiên `TokenUsage.metadata` hoặc
provider-specific runtime manifest; không đưa khái niệm benchmark vào provider.

### 3.4. Offline tests và runtime provider probe

#### Gate A — Offline

Fake-HTTP tests phải phủ:

- system + single-turn và system + multi-turn mapping;
- `stream=false`, model, timeout, token cap, seed và provider options;
- thinking được tách khỏi answer;
- token/timing metadata và finish-reason normalization;
- empty response, malformed JSON, connection error, timeout, HTTP 4xx/5xx;
- registry lazy-load và `close()` idempotent;
- zero network access trong unit tests.

#### Gate B — Runtime/model

- `/api/version` trả đúng `0.32.14`.
- `/api/show` xác nhận Qwen3.8-27B, `Q4_K_M`, full digest, license, template và
  parameters.
- Cache path thật nằm trên `/workspace`; phân vùng `/` không tăng theo model.
- Model load được với `num_ctx=4096`, parallel 1; `ollama ps` báo `100% GPU`.
- Ghi VRAM/RAM trước và sau load; không có OOM, Xid hoặc CPU offload ngoài dự
  kiến.

#### Gate C — Provider probe

Gọi `OllamaProvider.generate()` với một fixture kỹ thuật cố định, không lấy từ
benchmark và không dùng instruction bundle. Fixture gồm system instruction ngắn
và một hội thoại user/assistant/user để kiểm role mapping.

Cấu hình probe ban đầu:

| Trường | Giá trị |
|---|---|
| API | Native `POST /api/chat` |
| Model | `qwen3.8:latest`, resolve sang full digest đã khóa |
| `num_ctx` | 4096 |
| `max_output_tokens`/`num_predict` | 256 |
| Thinking probe | `medium`, nếu API xác nhận hỗ trợ |
| Seed | `20260902` |
| Parallel | 1 |
| Timeout | 600 giây |

Probe đạt khi response không rỗng, finish reason và token/timing hợp lệ, không
rò thinking vào `ModelResponse.text`, model/digest đúng, và provider đóng kết
nối sạch. Nếu `thinking=medium` không được API chấp nhận, dừng để Quân quyết
định bằng amendment; không tự chuyển sang `true` hoặc `false`.

## 4. Output dự kiến

Plan 01 không tạo `run_responses.jsonl`.

Các artifact chính dưới
`experiments/20260902_082403/outputs/ollama_provider_v1/`:

| File | Vai trò |
|---|---|
| `runtime_manifest.json` | Binary/model digest, cache path, env, GPU/RAM/disk snapshot, model metadata |
| `provider_probe.json` | Fixture hash, normalized response metadata, timing, usage và gate result; không lưu reasoning |

Ngoài ra có tối đa một runbook, final report và handoff cho Plan 01. Runtime và
model cache lớn nằm ngoài repository.

## 5. Nghiệm thu Plan 01

- Tất cả provider tests đạt bằng
  `/workspace/quannd/miniconda3/envs/benchmark_env/bin/python`.
- Ollama `0.32.14` và full model digest/Q4_K_M được xác minh.
- Model nằm đúng cache root trên `/workspace` và không sửa system service/cache.
- Model load 100% GPU ở context 4K, hoặc Plan 01 dừng với bằng chứng rõ ràng.
- Provider probe đi thật qua `ModelProvider.generate()` và đạt toàn bộ Gate C.
- Provider không import `benchmark_evaluation`, không đọc benchmark artifact và
  không sở hữu persistence/output schema nghiệp vụ.
- README/ARCHITECTURE/ADR chỉ cập nhật theo component thực tế đã cài.
- Governance validator đạt.

Hoàn tất Plan 01 chỉ chứng minh provider/runtime sẵn sàng; không chứng minh
target runner hoặc Qwen3.8 pilot đạt.

## 6. Phạm vi ghi sau approval

- `src/edu_benchmark/model_providers/ollama/`
- `src/edu_benchmark/model_providers/__init__.py`
- `src/edu_benchmark/model_providers/registry.py`
- `scripts/model_providers/`
- `tests/model_providers/`
- `README.md`
- `ARCHITECTURE.md`
- `src/edu_benchmark/README.md`
- `docs/decisions/`
- `experiments/20260902_082403/`
- `/workspace/quannd/local_llm_runtime/ollama/v0.32.14/`
- `/workspace/quannd/local_llm_cache/`

Không được sửa `src/edu_benchmark/benchmark_evaluation/`,
`scripts/benchmark_evaluation/`, `tests/benchmark_evaluation/`, `shared/`, input/
output cũ của experiment `20260727_170150`, system Ollama service hoặc cache
system.

## 7. Rủi ro và rollback

| Rủi ro | Dấu hiệu | Xử lý |
|---|---|---|
| Model không vừa VRAM | CPU/GPU split, OOM, headroom quá thấp | Dừng; không tự đổi quant/context |
| Root disk đầy | Model xuất hiện dưới `/usr/share/ollama` | Dừng pull; không xóa cache cũ |
| Tag `latest` thay đổi | Digest khác baseline đã duyệt | Dừng; khóa lại qua amendment |
| Runtime regression | Hang, empty content, CPU bất thường | Timeout, giữ log tinh gọn, dừng runtime |
| Thinking mapping sai | Answer chứa reasoning hoặc API từ chối mode | Dừng; không tự đổi mode |
| Workload khác xuất hiện | GPU process/VRAM thay đổi | Không load model; chờ GPU rảnh |

Rollback là dừng foreground runtime và giữ runtime/cache cô lập để Quân quyết
định. Không tự động xóa model khoảng 18 GB; xóa là destructive action cần yêu
cầu riêng.

## 8. Quyết định cần Quân duyệt

1. Cho phép runtime cô lập trên `127.0.0.1:11435` và không nâng cấp system
   service.
2. Cho phép canonical cache root `/workspace/quannd/local_llm_cache/` và các
   path ngoài repository nêu ở Mục 6.
3. Cho phép pull đúng `qwen3.8:latest` rồi khóa full digest/Q4_K_M.
4. Cho phép một provider probe kỹ thuật không dùng benchmark candidate.
5. Xác nhận Plan 02 vẫn đóng sau khi Plan 01 hoàn tất cho tới khi được duyệt
   riêng.
