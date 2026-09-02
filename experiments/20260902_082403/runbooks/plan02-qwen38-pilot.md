# Runbook — Plan 02 Qwen3.8 pilot 30 mẫu

Experiment: `20260902_082403`  
Plan: `P02`  
Người có quyền gọi model: Quân (operator)

## 1. Ranh giới vận hành

Code/agent không tự bật, tắt hoặc gọi model. Quân tự giữ Ollama trong một
session `screen` theo runbook Plan 01, rồi tự chạy các lệnh inference bên dưới.
Runner chỉ gọi endpoint đã tồn tại ở `127.0.0.1:11436` và không tạo daemon hay
fallback service.

Mọi lệnh Python dùng đúng interpreter và chạy từ repository root:

```bash
cd /workspace/quannd/kaggle-backup/edu-benchmark
PYTHON=/workspace/quannd/miniconda3/envs/benchmark_env/bin/python
CONFIG=experiments/20260902_082403/configs/qwen38-pilot-30-v1.json
LOG=experiments/20260902_082403/logs/qwen38-pilot-30-v1.log
set -o pipefail
```

## 2. Kiểm tra service do Quân đang giữ

```bash
curl -fsS http://127.0.0.1:11436/api/version
curl -fsS http://127.0.0.1:11436/api/ps
```

Kết quả phải cho thấy Ollama `0.32.14`, model `qwen3.8:latest`, context `4096`
và model nằm trên GPU. Nếu hai lệnh lỗi thì dừng; runner không tự start service.

## 3. Preflight không gọi model

```bash
$PYTHON scripts/benchmark_evaluation/run_target_responses.py \
  --config "$CONFIG"
```

Lệnh này kiểm hash năm input nguồn, dựng đúng 30 `PreparedTutorRequest`, kiểm
config/selection hash, đối chiếu JSONL checkpoint và cập nhật manifest. Không
có `--execute-api`, vì vậy không gửi request tới model.

## 4. Technical smoke cho một run mới hoàn toàn

Chỉ dùng lệnh này khi `run_responses.jsonl` chưa tồn tại hoặc có đúng 0 dòng:

```bash
$PYTHON scripts/benchmark_evaluation/run_target_responses.py \
  --config "$CONFIG" \
  --execute-api \
  --max-new-records 2 2>&1 | tee -a "$LOG"
```

Sau đó kiểm:

```bash
wc -l experiments/20260902_082403/outputs/qwen38_pilot_30_v1/run_responses.jsonl
$PYTHON -c 'import json; p="experiments/20260902_082403/outputs/qwen38_pilot_30_v1/run_manifest.json"; d=json.load(open(p)); print(d["phase"], d["integrity"], d["failed_candidate_ids"], d["needs_review_candidate_ids"])'
```

Technical smoke đạt khi hai record đều `STOP`, response không rỗng, không có
duplicate, failure, review state hoặc thẻ `<think>`.

## 5. Metric GPU được ghi

Config bật sampling mỗi 0,2 giây trên đúng GPU UUID của Plan 01. Với mỗi
candidate, manifest ghi:

- VRAM baseline, peak, after và peak delta;
- minimum free VRAM;
- GPU utilization trung bình/peak;
- nhiệt độ peak;
- power trung bình/peak và số snapshot.

Metric dung lượng được lưu bằng GiB (`1 GiB = 1024 MiB`) với hậu tố `_gib`, ví
dụ `memory_used_peak_gib` và `memory_free_min_gib`. Metric nằm ở
`provider_observations[].resource_usage`; tổng hợp cross-candidate nằm ở
`resource_summary`. Manifest được checkpoint atomic ngay sau từng response để
`Ctrl+C` không làm mất metric của response đã ghi. Monitor lỗi trước hoặc trong
request thì run dừng đóng; không tiếp tục với candidate thiếu metric.

Theo `P02-A003`, hai artifact chứa 4 response cũ đã bị xóa theo yêu cầu của
Quân. Run tuần tự mới đã hoàn tất 30/30 checkpoint có GPU metric.

## 6. Resume run tuần tự — chỉ dùng nếu checkpoint chưa đủ 30

```bash
$PYTHON scripts/benchmark_evaluation/run_target_responses.py \
  --config "$CONFIG" \
  --execute-api 2>&1 | tee -a "$LOG"
```

Runner đọc JSONL checkpoint, xác nhận request/config/source hash và chỉ gọi các
ID còn lại. Có thể nhấn `Ctrl+C` để
dừng runner; các dòng và metric đã append/checkpoint vẫn được giữ. Chạy lại
preflight rồi cùng lệnh resume để tiếp tục.

Trong terminal, `tqdm` hiển thị `đã xử lý/tổng`, phần trăm, thời gian đã chạy,
ETA và tốc độ. Postfix cho biết candidate vừa xong, số `ok/review/failed`, thời
gian và tổng token của candidate, cùng VRAM peak/free theo GiB. Retry và lỗi
được in thành dòng riêng. Kết thúc lệnh chỉ in summary ngắn; provenance đầy đủ
vẫn nằm trong manifest. `tee -a` vừa hiển thị vừa nối cùng nội dung vào
`$LOG`; `set -o pipefail` giúp shell vẫn trả mã lỗi của Python nếu runner lỗi.

## 7. Kiểm tra sau pilot

```bash
wc -l experiments/20260902_082403/outputs/qwen38_pilot_30_v1/run_responses.jsonl
$PYTHON -c 'import json; p="experiments/20260902_082403/outputs/qwen38_pilot_30_v1/run_manifest.json"; d=json.load(open(p)); print(d["status"], d["phase"], d["integrity"], d["failed_candidate_ids"], d["needs_review_candidate_ids"])'
```

Kỳ vọng cuối: `30` dòng, `status=completed`, `phase=pilot_completed`, zero
failure và zero `needs_review`. Sau đó Quân review thủ công tối thiểu 10/30
response trước khi chấp nhận Gate C. Hoàn tất pilot không tự mở Plan 03.

Run tuần tự đã đạt trạng thái này và là baseline hiệu năng cho P02-A006.

## 8. Output

- `outputs/qwen38_pilot_30_v1/run_responses.jsonl`: checkpoint response.
- `outputs/qwen38_pilot_30_v1/run_errors.jsonl`: chỉ xuất hiện nếu có attempt
  lỗi; không chứa prompt hoặc credential.
- `outputs/qwen38_pilot_30_v1/run_manifest.json`: selection/config/source hash,
  resume history, integrity, provider timing và GPU metric theo candidate.

## 9. Pilot đối sánh parallel-2

P02-A006 giữ nguyên model Q4_K_M, KV cache `f16`, context 4096 cho mỗi request,
thinking `MEDIUM`, seed, prompt và đúng 30 candidate của baseline. Run mới dùng
run ID/output riêng, vì vậy không sửa hoặc resume nhầm bundle tuần tự.

### 9.1. Restart service ở parallel-2

`OLLAMA_NUM_PARALLEL` là cấu hình ở cấp tiến trình Ollama server, không phải
tham số của từng request inference. Vì vậy service đã khởi động với
`parallel=1` không thể chuyển sang hai slot chỉ bằng cách chạy lại runner.
Bắt buộc dừng service cũ và khởi động một service mới với
`OLLAMA_NUM_PARALLEL=2`. Việc này chỉ nạp lại model đã có từ cache trên
`/workspace`; không tải lại model từ Internet và không xóa output baseline.

Lần thử lúc 19:05 ngày 02/09/2026 đã được live gate chặn đúng vì service cũ
báo `context_length=4096`, trong khi config parallel-2 yêu cầu
`4096 × 2 = 8192`. Không có request inference nào được gửi; bundle parallel-2
vẫn ở `0/30` và không cần reset.

Trong session `screen` đang giữ Ollama, nhấn `Ctrl+C` sau khi run tuần tự đã
kết thúc. Tạo/attach một session mới:

```bash
screen -S ollama-qwen38-parallel2
```

Trong session đó:

```bash
cd /workspace/quannd/kaggle-backup/edu-benchmark
OLLAMA_NUM_PARALLEL=2 bash scripts/model_providers/run_ollama_server.sh
```

Chờ log có dòng `READY:` kết thúc bằng `parallel=2`. Launcher vẫn giữ service
foreground và chỉ Quân bật/tắt. Với hai slot × 4096 token, `/api/ps` phải báo
`context_length` bằng `8192` và model vẫn nằm hoàn toàn trên GPU:

```bash
curl -fsS http://127.0.0.1:11436/api/ps
```

Trước khi chạy pilot, có thể xác nhận launcher mới thực sự được áp dụng:

```bash
rg 'Configured request parallelism|n_seq_max|n_ctx|READY:' \
  experiments/20260902_082403/logs/ollama-qwen38-service.log | tail -n 20
```

Kỳ vọng có `Configured request parallelism: 2`, `n_seq_max = 2`, tổng
`n_ctx = 8192`, `n_ctx_seq = 4096` và `READY ... parallel=2`. Nếu vẫn thấy
`n_seq_max = 1` hoặc `/api/ps` vẫn báo `4096`, không chạy pilot và gửi lại log
để điều tra.

Nếu chuyển sang thiết bị khác nhưng vẫn SSH vào cùng server, sau khi thấy
`READY` hãy detach mà không dừng service bằng `Ctrl+A`, rồi nhấn `D`. Trên
thiết bị mới, attach lại bằng:

```bash
screen -r ollama-qwen38-parallel2
```

Không nhấn `Ctrl+C` khi chỉ muốn chuyển thiết bị, vì thao tác đó sẽ dừng Ollama.

### 9.2. Preflight parallel-2 không gọi model

Trong terminal khác:

```bash
cd /workspace/quannd/kaggle-backup/edu-benchmark
PYTHON=/workspace/quannd/miniconda3/envs/benchmark_env/bin/python
PARALLEL_CONFIG=experiments/20260902_082403/configs/qwen38-pilot-30-parallel2-v1.json
PARALLEL_LOG=experiments/20260902_082403/logs/qwen38-pilot-30-parallel2-v1.log
set -o pipefail

$PYTHON scripts/benchmark_evaluation/run_target_responses.py \
  --config "$PARALLEL_CONFIG"
```

Preflight phải in `max_concurrency=2`, `gpu_scope=invocation` và checkpoint
`0/30`. Khi có `--execute-api`, live gate còn chặn nếu loaded context không
bằng `4096 × 2`; do đó server parallel-1 không thể vô tình chạy bundle này.

### 9.3. Technical smoke gồm hai request đồng thời

```bash
$PYTHON scripts/benchmark_evaluation/run_target_responses.py \
  --config "$PARALLEL_CONFIG" \
  --execute-api \
  --max-new-records 2 2>&1 | tee -a "$PARALLEL_LOG"
```

Sau khi smoke hoàn tất, kiểm:

```bash
$PYTHON -c 'import json; p="experiments/20260902_082403/outputs/qwen38_pilot_30_parallel2_v1/run_manifest.json"; d=json.load(open(p)); print(d["phase"], d["integrity"], d["failed_candidate_ids"], d["needs_review_candidate_ids"], d["resource_summary"])'
```

Chỉ resume nếu hai record đều completed, không failure/review, model vẫn 100%
GPU và `memory_free_min_gib` còn ít nhất `1.0`. Nếu không đạt, dừng ở hai mẫu;
không tự chuyển sang parallel 3–4.

### 9.4. Resume đủ 30 mẫu parallel-2

```bash
$PYTHON scripts/benchmark_evaluation/run_target_responses.py \
  --config "$PARALLEL_CONFIG" \
  --execute-api 2>&1 | tee -a "$PARALLEL_LOG"
```

Hai worker chỉ gọi provider. Main thread là writer duy nhất cho JSONL và
manifest, nên completion order có thể khác selection order nhưng không có hai
thread cùng ghi artifact. GPU được đo cho toàn invocation song song và lưu tại
`execution_resource_observations`; không gán sai lượng VRAM dùng chung cho từng
candidate.

### 9.5. So sánh với baseline tuần tự

```bash
$PYTHON scripts/benchmark_evaluation/compare_target_run_performance.py \
  --baseline experiments/20260902_082403/outputs/qwen38_pilot_30_v1/run_manifest.json \
  --candidate experiments/20260902_082403/outputs/qwen38_pilot_30_parallel2_v1/run_manifest.json
```

Output báo samples/phút, aggregate output token/giây, mean/median/p95 latency,
VRAM, lỗi/review và `throughput_speedup`. Chỉ cân nhắc parallel 3–4 bằng một
amendment/config mới sau khi Quân chấp nhận kết quả parallel-2.
