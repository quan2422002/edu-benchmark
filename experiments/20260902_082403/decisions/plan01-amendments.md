# Amendments — Plan 01

Experiment: `20260902_082403`  
Baseline: `plans/01-ollama-qwen38-runtime-and-provider.md`

Không có amendment tại thời điểm tạo file.

Baseline được tái cấu trúc khi còn `DRAFT`, trước approval, để Plan 01 chỉ sở
hữu Ollama runtime và model provider. Vì chưa có baseline được phê duyệt nên
thay đổi này không được cấp amendment ID.

Khi phát sinh thay đổi sau approval, thêm mục mới ở cuối file theo thứ tự
`P01-A001`, `P01-A002`, ...; không sửa lại lịch sử quyết định cũ.

## P01-A001 — Launcher hợp nhất pull, preload và log

- Thời điểm: 02/09/2026
- Authority: Quân — project lead
- Nguồn quyết định: phản hồi trực tiếp sau handoff lệnh `screen`

### Bối cảnh

Launcher đã bàn giao chỉ `exec ollama serve`. Vì vậy session screen mới mở API
server, còn model vẫn phải được pull, kiểm và preload bằng nhiều lệnh thủ công.
Quân yêu cầu một file shell sở hữu toàn bộ quá trình đến khi
`qwen3.8:latest` thực sự sẵn sàng phục vụ, đồng thời ghi output vào một file log
để theo dõi tiến độ.

### Thay đổi được duyệt

`scripts/model_providers/run_ollama_server.sh` trở thành launcher hợp nhất:

1. tạo/khóa cache và log, chống hai session trùng bằng `flock`;
2. kiểm asset hash/size, disk, GPU và endpoint trước khi chạy;
3. start Ollama `0.32.14`, chờ `/api/version` đạt;
4. pull/resume `qwen3.8:latest` vào cache trên `/workspace`;
5. gọi metadata-only probe để khóa full digest và xác nhận `Q4_K_M`;
6. preload model bằng `/api/generate` với prompt rỗng, `num_ctx=4096` và
   `keep_alive=-1`;
7. yêu cầu `/api/ps` xác nhận context 4096 và model nằm ít nhất 99% trên GPU;
8. giữ server sống trong session screen và ghi toàn bộ output vào
   `experiments/20260902_082403/logs/ollama-qwen38-service.log`.

Empty-prompt preload không phải provider probe và không sinh response nội dung.
Gate C vẫn chờ Quân yêu cầu call fixture qua `OllamaProvider`. Launcher không đọc
benchmark, không chạy Plan 02 và không tạo target-response JSONL.

### Failure và rollback

Bất kỳ lỗi version/hash/disk/GPU/pull/metadata/preload nào đều làm launcher dừng
server, giữ model layer đã tải để resume và giữ log. Không xóa runtime/cache,
không đổi quant/context/thinking và không chạm system service ở port 11434.

## P01-A002 — Chuyển runtime sang port 11436

- Thời điểm: 02/09/2026
- Authority: Quân — project lead
- Nguồn quyết định: Quân duyệt đổi port sau khi launcher fail-closed

### Bằng chứng

Hai lần launcher chạy lúc 11:01 và 11:06 đều qua asset/cache/GPU preflight rồi
dừng trước pull với lỗi endpoint `127.0.0.1:11435` đã có server. Kiểm host xác
nhận port này do `docker-proxy` thuộc root publish từ container
`172.21.0.2:11434`; API trả Ollama `0.20.7`. System service riêng ở port 11434
trả `0.9.6`. Không instance nào thuộc Plan 01.

Port 11436, 11437 và 11438 đều không listen/không trả API tại thời điểm kiểm.

### Thay đổi được duyệt

- Plan 01 chuyển endpoint canonical sang `http://127.0.0.1:11436`.
- Đồng bộ launcher, provider default, probe default/environment manifest,
  tests, ADR, architecture, runbook và handoff của Plan 01.
- Không dừng hoặc sửa Docker container ở 11435 và system service ở 11434.
- Giữ baseline đã duyệt cùng coordination log lịch sử nguyên trạng; amendment
  này là authority hiện hành cho Plan 01.
- Chưa sửa draft Plan 02–03. Chỉ đồng bộ endpoint sang các plan đó sau khi Quân
  xác nhận launcher ở 11436 đã đạt `READY:`.

## P01-A003 — Vòng đời service do Quân chủ động và sửa contract `keep_alive`

- Thời điểm: 02/09/2026
- Authority: Quân — project lead
- Nguồn quyết định: yêu cầu trực tiếp sau khi phân biệt server chẩn đoán tạm với
  service vận hành

### Bằng chứng

Model đã pull thành công, metadata probe xác nhận digest đầy đủ
`22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643`,
Q4_K_M và cache đúng trên `/workspace`. Launcher sau đó nhận HTTP 400 ở bước
preload vì gửi `keep_alive` dưới dạng chuỗi `"-1"`; response body thật là
`time: missing unit in duration "-1"`. Một server chẩn đoán tạm xác nhận
preload và `/api/chat` đều trả HTTP 200 khi dùng số `-1`, model load 100% GPU ở
context 4096. Server tạm đã được dừng sau chẩn đoán và không phải service dự án.

### Thay đổi được duyệt

1. `keep_alive` của launcher, provider probe và kiểm thử dùng số `-1`.
2. Launcher vẫn chạy foreground trong session `screen`, in `READY:` rồi chờ
   server; không tự thoát sau preload và không tự khởi động cùng hệ thống.
3. Chỉ Quân chạy lệnh bật/tắt canonical trong runbook. Probe và Codex status
   check không được ngầm tạo một server thay thế.
4. Lỗi HTTP preload phải giữ response body trong log; retry health-check không
   in traceback JSON khi endpoint mới đang khởi động.
5. Model/cache đã tải được giữ nguyên. Plan 02–03 tiếp tục đóng cho đến khi
   service do Quân bật đạt `READY:` và provider probe đạt.

## P01-A004 — Dừng service bằng interrupt trong session

- Thời điểm: 02/09/2026
- Authority: Quân — project lead
- Nguồn quyết định: phản hồi trực tiếp về thao tác vận hành `screen`

### Thay đổi được duyệt

- Cách dừng canonical là attach bằng `screen -r ollama-qwen38`, sau đó nhấn
  `Ctrl+C` như interrupt một foreground process thông thường.
- Không dùng `screen -X quit` làm hướng dẫn dừng chính và không cần một thông
  điệp log riêng ngoài cleanup/exit hiện có của launcher.
- Các contract khác của P01-A003 không đổi: Quân sở hữu vòng đời service, probe
  không tự start/stop, và `keep_alive` tiếp tục dùng số `-1`.

## P01-A005 — Tương thích curl 7.68 khi giữ HTTP error body

- Thời điểm: 02/09/2026
- Authority: Quân — project lead
- Nguồn quyết định: lỗi lần chạy service do Quân khởi động lúc 15:00–15:02

### Bằng chứng và sửa lỗi

Hai lần chạy mới đều qua version, pull cache và metadata, rồi dừng trước khi gửi
preload vì `/usr/bin/curl` là bản 7.68.0 và không nhận tùy chọn
`--fail-with-body`. Đây là lỗi tương thích launcher, không phải lỗi Ollama,
model, GPU hoặc payload preload.

Launcher thay tùy chọn này bằng contract tương thích curl cũ: dùng
`--write-out` để thu HTTP status cùng response body, tách hai phần trong Bash,
giữ response body trong log và fail-closed nếu status không thuộc 2xx. Không
thay đổi lifecycle, endpoint, model, context hoặc quyền bật/tắt của Quân.

## P01-A006 — Gate VRAM nhận biết model đã preload

- Thời điểm: 02/09/2026
- Authority: Quân — project lead
- Nguồn quyết định: kiểm tra đóng Plan 01 trên service đạt `READY:`

### Bằng chứng và sửa lỗi

Gate C đầu tiên dừng trước provider call vì tái sử dụng điều kiện pre-load “GPU
còn ít nhất 20 GiB” trong khi model hợp lệ đã preload 100% GPU và còn khoảng
5,8 GiB. Điều kiện này đúng trước một load mới nhưng tự mâu thuẫn sau Gate B.

Probe nay chấp nhận một trong hai trạng thái: đủ 20 GiB để load mới, hoặc đúng
model tag đã preload với `size_vram >= 99% size` và context 4096. Runtime
manifest giữ số VRAM thô để audit. Provider fixture sau sửa đạt toàn bộ check,
không thay đổi service hoặc cấu hình model.

## P01-A007 — Opt-in runtime parallel-2 cho pilot Plan 02

- Thời điểm: 02/09/2026
- Authority: Quân — project lead
- Nguồn quyết định: yêu cầu trực tiếp sau khi review mức dùng VRAM của pilot

Launcher giữ mặc định `OLLAMA_NUM_PARALLEL=1` để không thay đổi contract lịch
sử, nhưng chấp nhận giá trị opt-in `2` cho pilot hiệu năng P02-A006. Giá trị
khác 1 hoặc 2 bị từ chối. Launcher truyền parallelism vào runtime probe, ghi
giá trị trong log/manifest và yêu cầu loaded context bằng
`4096 × OLLAMA_NUM_PARALLEL` trước khi in `READY:`.

Thay đổi không tự restart service, không gọi model và không mở parallel 3–4.
Quân vẫn sở hữu vòng đời screen; P02 live gate chịu trách nhiệm kiểm parallel-2
trước khi chạy bundle đối sánh riêng.
