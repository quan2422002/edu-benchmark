# Amendments — Plan 02

Experiment: `20260902_082403`  
Baseline: `plans/02-provider-neutral-target-runner-and-qwen38-pilot.md`

## P02-A001 — Đồng bộ endpoint runtime đã khóa ở Plan 01

Ngày: 2026-09-02  
Trạng thái: áp dụng

Baseline Plan 02 còn ghi endpoint đề xuất là `127.0.0.1:11435`. Sau quá trình
triển khai và nghiệm thu Plan 01, runtime chính thức do Quân quản lý đã được
khóa ở `http://127.0.0.1:11436` theo `P01-A002`. Toàn bộ preflight và model call
của Plan 02 phải dùng port `11436`; không có service ẩn hoặc fallback port.

Thay đổi này chỉ đồng bộ dependency đã nghiệm thu, không thay model, digest,
prompt, selection hay generation settings.

Baseline được tái cấu trúc khi còn `DRAFT`, trước approval, để Plan 02 sở hữu
provider-neutral target runner và pilot 2→30. Vì chưa có baseline được phê duyệt
nên thay đổi này không được cấp amendment ID.

Các thay đổi tiếp theo dùng ID `P02-A002`, `P02-A003`, ...; không sửa lại lịch
sử quyết định cũ.

## P02-A002 — Quyền gọi benchmark model thuộc Quân

Ngày: 2026-09-02  
Trạng thái: áp dụng

Quân làm rõ rằng “triển khai Plan 02” chỉ cho phép agent cài code, kiểm thử
offline, viết runbook và cung cấp lệnh. Chỉ Quân chủ động chạy inference. Agent
không được tự chạy technical smoke, pilot hoặc full run khi chưa có chỉ thị gọi
model riêng biệt.

Trước khi nhận được làm rõ này, agent đã chạy technical smoke hai mẫu và bắt
đầu resume; Quân yêu cầu dừng và process được interrupt ngay. JSONL đã kịp ghi
4 response hợp lệ. Giữ nguyên chúng như audit/checkpoint, không xóa hoặc viết
lại. Manifest được preflight kế tiếp đối chiếu từ JSONL; khi Quân chạy lại,
runner chỉ xử lý 26 ID còn thiếu.

## P02-A003 — Reset pilot và bắt buộc đo GPU theo từng candidate

Ngày: 2026-09-02  
Trạng thái: áp dụng

Quân yêu cầu xóa hai artifact chứa kết quả 4 response đầu
(`run_responses.jsonl`, `run_manifest.json`) và chạy lại pilot từ 0/30 để mọi
candidate có cùng contract đo GPU. Đây là thao tác reset có chủ đích; bốn
response cũ không còn là checkpoint của bundle hoạt động.

Runner được bổ sung monitor tùy chọn, không thay hành vi mặc định của consumer
cũ. Config Qwen3.8 bật `nvidia-smi` sampling mỗi 0,2 giây trên đúng GPU UUID đã
khóa. Mỗi response lưu baseline/peak/after VRAM, minimum free VRAM, utilization,
nhiệt độ và power trong `run_manifest.provider_observations[].resource_usage`;
manifest được checkpoint atomic sau từng response. Không thêm output file thứ
tư và không đổi target-response JSONL schema.

## P02-A004 — Chuẩn hóa metric VRAM sang GiB

Ngày: 2026-09-02  
Trạng thái: áp dụng

Theo yêu cầu của Quân, artifact không lưu dung lượng GPU theo MiB. Monitor vẫn
đọc đơn vị native MiB của `nvidia-smi` ở nội bộ, sau đó chia `1024` và làm tròn
4 chữ số thập phân trước khi ghi. Tất cả field công bố dùng hậu tố `_gib`, ví
dụ `memory_used_peak_gib` và `memory_free_min_gib`. Cách ghi này tương ứng GPU
RTX 3090 có tổng dung lượng `24.0 GiB`, tránh nhập nhằng với GB thập phân.

## P02-A005 — Progress/ETA gọn và log quan sát được

Ngày: 2026-09-02  
Trạng thái: áp dụng

Theo phản hồi của Quân, CLI không dump toàn bộ manifest ra terminal sau mỗi
lệnh. Khi thực thi API, runner phát sự kiện có cấu trúc theo candidate để CLI
hiển thị bằng `tqdm`: tiến độ, elapsed/ETA, tốc độ, candidate vừa hoàn tất,
completed/review/failed, latency, token và VRAM peak/free theo GiB. Retry và lỗi
được in thành dòng riêng mà không phá progress bar. Kết thúc chỉ in summary
ngắn; manifest vẫn là artifact provenance đầy đủ.

Runbook dùng `2>&1 | tee -a` để cùng một luồng quan sát được trên terminal và
lưu vào log experiment, đồng thời bật `pipefail` để không che mã lỗi của
runner. Thay đổi chỉ thuộc giao diện vận hành và callback tùy chọn; không đổi
prompt, selection, generation settings, persistence schema hay quyền gọi model.

## P02-A006 — Pilot đối sánh concurrency 2

Ngày: 2026-09-02  
Trạng thái: áp dụng

Sau khi baseline tuần tự hoàn tất 30/30, Quân duyệt cài đặt pilot đối sánh với
hai request đồng thời để tận dụng VRAM còn trống. Bundle mới giữ nguyên model,
digest, Q4_K_M, KV cache f16, context 4096 cho mỗi request, thinking MEDIUM,
seed, prompt và đúng 30 candidate; run ID/output directory riêng ngăn resume
chéo hoặc ghi đè baseline.

Target runner nhận `max_concurrency=2`, dùng bounded thread pool chỉ cho provider
calls và giữ toàn bộ append/checkpoint ở main thread. Với concurrency lớn hơn
1, GPU là tài nguyên dùng chung nên metric được ghi theo invocation vào
`execution_resource_observations`, không được diễn giải là mức dùng riêng của
một candidate. CLI live gate yêu cầu loaded context bằng `num_ctx × parallel`.

Gate chia hai bước: hai request technical smoke chạy đồng thời; chỉ khi không
failure/review/CPU offload và còn ít nhất 1 GiB VRAM mới resume đủ 30. Utility
so sánh đọc hai manifest để báo throughput, aggregate token/s, latency, VRAM và
speedup. Parallel 3–4 chưa được duyệt. Agent chỉ cài code/runbook và không chạy
inference.
