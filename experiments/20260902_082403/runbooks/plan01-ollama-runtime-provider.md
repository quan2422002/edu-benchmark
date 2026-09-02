# Runbook — Plan 01 / Ollama runtime và provider probe

Experiment: `20260902_082403`  
Plan: `P01`

## Mục đích

Khởi động runtime Ollama cô lập bằng một launcher hợp nhất: tự ghi log, tải đúng
`qwen3.8:latest` vào cache trên `/workspace`, xác nhận model digest/Q4_K_M rồi
preload model 4K lên GPU mà không gửi prompt inference. Fixture kỹ thuật qua
`OllamaProvider` chỉ chạy sau một yêu cầu riêng của Quân. Runbook không đọc
candidate benchmark và không tạo target-response JSONL.

Quân là người duy nhất chủ động bật/tắt service vận hành. Launcher không phải
daemon hệ thống, không tự khởi động cùng máy và không được Codex dùng một server
chẩn đoán tạm thay cho service này.

## Điều kiện trước khi chạy

- Plan 01 có dòng trạng thái `APPROVED`.
- Python package đã được cài editable trong `benchmark_env`.
- GPU UUID `GPU-5e1bf88a-a431-9a0c-b462-37cd95b5e9b8` đang rảnh.
- Runtime asset tồn tại tại
  `/workspace/quannd/local_llm_runtime/ollama/v0.32.14/`.
- Port `127.0.0.1:11436` chưa có process khác sử dụng. Port `11435` thuộc một
  Docker container ngoài dự án và không được dừng hoặc tái sử dụng.
- Không chạy lệnh pull/probe bằng Ollama system ở port `11434`.

## Cấu hình và input

- Ollama: `0.32.14`.
- Release asset: `ollama-linux-amd64.tar.zst`, 1.421.191.399 byte.
- Asset SHA-256:
  `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f`.
- Model tag: `qwen3.8:latest`; quantization phải là `Q4_K_M`.
- Runtime endpoint: `http://127.0.0.1:11436`.
- Model cache: `/workspace/quannd/local_llm_cache/ollama/models`.
- Output nhỏ:
  `experiments/20260902_082403/outputs/ollama_provider_v1/`.

## Preflight

```bash
sha256sum /workspace/quannd/local_llm_runtime/ollama/v0.32.14/downloads/ollama-linux-amd64.tar.zst
df -h /workspace /
nvidia-smi --id=GPU-5e1bf88a-a431-9a0c-b462-37cd95b5e9b8
bash -n scripts/model_providers/run_ollama_server.sh
```

Hash phải khớp giá trị trên. Dừng nếu cache không nằm trên `/workspace`, GPU có
workload khác, port 11436 bận hoặc phân vùng `/workspace` còn dưới 30 GiB.

## Bật service bằng `screen`

Từ repository root:

```bash
screen -dmS ollama-qwen38 bash -lc 'exec scripts/model_providers/run_ollama_server.sh'
```

Đây là lệnh bật service canonical và do Quân chạy. Sau khi preload cùng toàn bộ
gate đạt, launcher in `READY:` rồi tiếp tục chờ trong chính session
`ollama-qwen38`; nó không tự dừng sau khi đạt `READY:`. Không coi một server tạm
do lệnh kiểm tra tạo ra là trạng thái service của dự án.

File shell tự ghi cả server output, pull progress, preflight và preload result
vào một log cố định. Kiểm session và theo dõi log:

```bash
screen -ls
tail -f experiments/20260902_082403/logs/ollama-qwen38-service.log
```

Không chạy thêm lệnh pull song song. Dòng `READY:` trong log chỉ xuất hiện sau
khi toàn bộ chuỗi sau đạt:

1. asset Ollama đúng size/SHA-256 và cache còn ít nhất 30 GiB;
2. GPU còn ít nhất 20 GiB, endpoint 11436 chưa bị chiếm;
3. server trả đúng version `0.32.14`;
4. `ollama pull qwen3.8:latest` hoàn tất hoặc resume xong;
5. metadata probe xác nhận full digest và `Q4_K_M`;
6. empty-prompt preload dùng `num_ctx=4096`, `keep_alive` là số `-1`;
7. `/api/ps` xác nhận context 4096 và ít nhất 99% model bytes trên GPU.

Nếu download bị ngắt, chạy lại đúng lệnh `screen` sau khi session cũ đã dừng;
Ollama tiếp tục các layer đã có trong cùng model store.

## Kiểm status và provider probe

Launcher tự sinh `runtime_manifest.json` trước preload. Sau khi log có `READY:`,
kiểm endpoint và model đã nạp:

```bash
curl -fsS http://127.0.0.1:11436/api/version
curl -fsS http://127.0.0.1:11436/api/ps
```

Hai lệnh status chỉ có thể thành công khi session do Quân bật vẫn đang sống.
Provider probe chỉ dùng service hiện có; nó không start hoặc stop server.

Chỉ khi Quân yêu cầu thử call, đọc full digest trong manifest rồi chạy fixture
kỹ thuật có khóa digest:

```bash
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python scripts/model_providers/probe_ollama.py --expected-digest <FULL_SHA256> --execute-model
```

Không chạy `--execute-model` nếu version, digest, Q4_K_M hoặc cache preflight
chưa đạt. Nếu API từ chối `thinking=medium`, dừng và ghi amendment; không tự đổi
thinking mode.

## Tắt và bật lại service

Quân chủ động tắt toàn bộ process tree của service bằng:

```bash
screen -r ollama-qwen38
```

Trong session vừa attach, nhấn `Ctrl+C` để interrupt launcher foreground.
Launcher nhận `SIGINT`, dừng Ollama con rồi thoát; sau đó có thể thoát khỏi
screen. Xác nhận endpoint đã tắt:

```bash
curl -fsS --max-time 3 http://127.0.0.1:11436/api/version
```

Lệnh trên phải trả lỗi kết nối sau khi service đã dừng. Muốn bật lại, chạy lại
đúng lệnh `screen -dmS ...` ở mục **Bật service bằng `screen`**. Model đã tải
được giữ trong cache nên launcher chỉ kiểm/pull manifest hiện có rồi preload,
không tải lại toàn bộ layer hợp lệ.

Theo P01-A007, launcher giữ mặc định lịch sử `OLLAMA_NUM_PARALLEL=1` nhưng cho
phép Plan 02 yêu cầu đúng mức đã duyệt là `2` bằng biến môi trường. Quy trình
parallel-2 và lệnh vận hành canonical nằm ở mục 9 của runbook Plan 02; không tự
dùng mức 3–4.

## Validation

```bash
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python -m pytest tests/model_providers -q
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python scripts/governance/validate_experiment.py experiments/20260902_082403
```

Gate live chỉ đạt khi `/api/ps` cho thấy model ở 100% GPU, response không rỗng,
usage/timing hợp lệ và `provider_probe.json` không chứa reasoning text.

## Failure và rollback

- Khi có OOM, CPU offload, NVIDIA Xid, digest khác dự kiến, root disk tăng do
  model hoặc thinking mapping sai: launcher dừng server, giữ log/manifest/layer
  đã tải và không chạy lại với cấu hình tự thay đổi.
- Để dừng, attach bằng `screen -r ollama-qwen38`, nhấn `Ctrl+C`, rồi thoát khỏi
  screen.
- Dừng runtime không sửa service/cache Ollama system. Runtime và model cache
  được giữ nguyên để điều tra hoặc resume.

## Cleanup

Plan 01 không cho phép tự động xóa runtime, archive hoặc model khoảng 18 GB.
Việc xóa cần một yêu cầu riêng, nêu đúng target và ảnh hưởng khôi phục.
