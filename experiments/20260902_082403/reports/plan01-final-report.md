# Báo cáo cuối — Plan 01

Experiment: `20260902_082403`  
Baseline: `plans/01-ollama-qwen38-runtime-and-provider.md`  
Trạng thái kết luận: `completed`

## 1. Kết quả

Plan 01 đạt toàn bộ Gate A–C. Runtime Ollama `0.32.14` và model
`qwen3.8:latest` Q4_K_M được cài cô lập trên `/workspace`; service do Quân chủ
động bật/tắt trong `screen` đang phục vụ tại `127.0.0.1:11436`. Provider native
`/api/chat` đã đi qua fixture kỹ thuật thật, trả response hợp lệ và không lưu
nội dung thinking vào answer hoặc artifact.

## 2. So với baseline

| Tiêu chí | Kết quả | Bằng chứng |
|---|---|---|
| Provider và launcher offline tests | `pass` | `28 passed` trong `tests/model_providers` |
| Ollama đúng version và asset | `pass` | `runtime_manifest.json`; asset size/SHA-256 đều đúng |
| Model đúng tag/digest/Q4_K_M | `pass` | Digest `22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643` |
| Cache không nằm trên phân vùng `/` | `pass` | `/workspace/quannd/local_llm_cache/ollama/models` |
| Context 4096 và 100% GPU | `pass` | `/api/ps`: `size_vram == size == 17278099782`, context 4096 |
| Provider fixture thật | `pass` | `provider_probe.json`: `passed=true`, HTTP 200, `finish_reason=STOP` |
| Usage/timing hợp lệ | `pass` | 82 input, 52 output, 134 total token; total duration khoảng 2,89 giây |
| Không lưu reasoning text | `pass` | Không có trường `thinking`; chỉ giữ cờ/độ dài metadata |
| Vòng đời do Quân quản lý | `pass` | `screen` foreground; attach và `Ctrl+C` để dừng |

## 3. Amendment đã áp dụng

- `P01-A001`: launcher hợp nhất pull, preload và log.
- `P01-A002`: chuyển endpoint sang port 11436.
- `P01-A003`: sửa `keep_alive` thành số `-1` và khóa operator lifecycle.
- `P01-A004`: dừng bằng `Ctrl+C` trong session.
- `P01-A005`: tương thích curl 7.68.
- `P01-A006`: Gate C chấp nhận model đã preload thay cho yêu cầu 20 GiB VRAM
  còn trống trước một load mới.

## 4. Validation

- Exact interpreter:
  `/workspace/quannd/miniconda3/envs/benchmark_env/bin/python`
- Commands:
  - `python -m pytest tests/model_providers -q`
  - `bash -n scripts/model_providers/run_ollama_server.sh`
  - `python scripts/model_providers/probe_ollama.py --expected-digest <digest> --execute-model`
  - `python scripts/governance/validate_experiment.py experiments/20260902_082403`
  - scoped `git diff --check`
- Result: `28 passed`; live probe và governance đều pass.

## 5. Artifact chính

- `outputs/ollama_provider_v1/runtime_manifest.json`
  - SHA-256: `69c40d9837ff9932061c45417217f0ed941ec184e3f7a9db38f1f25a6cc6b21f`
- `outputs/ollama_provider_v1/provider_probe.json`
  - SHA-256: `0e9387134a92289e346af337f2f6e3c5df12d16a8695edb5bbd8f6619e35816c`
- `logs/ollama-qwen38-service.log`

## 6. Giới hạn và backlog

- Fixture Plan 01 chỉ chứng minh provider/runtime, không đánh giá chất lượng gia
  sư trên benchmark.
- Model preload lần đầu mất khoảng 2 phút 26 giây; sau load còn khoảng 5,8 GiB
  VRAM. Plan 02 phải giữ parallel bằng 1 và đo peak/ETA trên pilot.
- Ollama có thể refresh metadata công khai từ `ollama.com`; service vẫn bind
  loopback và request fixture dùng model local đã khóa digest. Chế độ hoàn toàn
  offline (`OLLAMA_NO_CLOUD`) chưa phải acceptance criterion của Plan 01.
- Service hiện do Quân giữ trong `screen`; Plan 01 không tạo systemd/daemon.

## 7. Gate tiếp theo

Plan 02 có thể được đưa ra cho Quân duyệt. Việc đóng Plan 01 không tự động phê
duyệt hoặc triển khai Plan 02.
