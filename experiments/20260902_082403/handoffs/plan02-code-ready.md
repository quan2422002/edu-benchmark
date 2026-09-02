# Handoff

- Event ID: `EXP-20260902_082403-P02-CODE-READY-024`
- Plan ID: `P02`
- Mode: `single-agent`
- Agent: orchestrator
- Status: code-ready; inference awaiting operator
- Native thread ID/label: `not-applicable`

## Task or delegation request

Cài provider-neutral target runner, khóa config/selection pilot Qwen3.8 30 mẫu,
kiểm thử offline và giao lệnh để Quân tự chạy.

## Follow-up or scope changes

`P02-A001` đồng bộ endpoint Plan 01 sang port `11436`. `P02-A002` làm rõ chỉ
Quân có quyền gọi benchmark model; agent chỉ cài code, kiểm thử và viết runbook.
`P02-A003`–`P02-A005` lần lượt reset pilot để đo GPU đồng nhất, công bố metric
VRAM bằng GiB và bổ sung progress bar/ETA cùng log qua `tee`. `P02-A006` thêm
bundle đối sánh concurrency-2 tách biệt sau khi baseline tuần tự đủ 30/30.

## Inputs read

- Baseline/status/roadmap Plan 02 và final report Plan 01.
- Runner Vertex lịch sử, `PreparedTutorRequest` và model-provider contracts.
- Full candidate manifest 1.400, requirement-scoring run/analysis, grounding pool
  và instruction bundle v2; tất cả được khóa SHA-256 trong config.

## Outputs created

- `src/edu_benchmark/benchmark_evaluation/target_runner.py`
- `scripts/benchmark_evaluation/run_target_responses.py`
- `tests/benchmark_evaluation/test_target_runner.py`
- `experiments/20260902_082403/configs/qwen38-pilot-30-v1.json`
- `experiments/20260902_082403/runbooks/plan02-qwen38-pilot.md`
- `experiments/20260902_082403/outputs/qwen38_pilot_30_v1/`

## Result summary

Code/offline gate sẵn sàng. Selection có 30 ID duy nhất, giữ 10 anchor
instruction-v2, phân bố lớp 8/8/7/7 và hai extreme input làm smoke. Runner giữ
JSONL checkpoint, error attempts, hash-drift gate, local cost basis, normalized
finish state và resume theo candidate ID.

Do hiểu sai phạm vi trước khi Quân làm rõ, agent đã tạo 4 response rồi interrupt
run. Theo yêu cầu sau đó của Quân và `P02-A003`, hai artifact chứa kết quả này
đã bị xóa để pilot chạy lại đồng nhất từ 0/30. Runner nay sampling GPU theo từng
candidate và checkpoint metric trong manifest. Run tuần tự do Quân vận hành đã
hoàn tất 30/30. CLI nay hỗ trợ concurrency giới hạn 2 với single-writer
persistence; GPU metric song song được ghi theo invocation. Config/output mới
giữ nguyên 30 candidate để đối sánh trực tiếp. Agent không gọi inference.

## Orchestrator decision

Không gọi thêm model. Giữ Plan 02 `in_progress`, gate mở chờ Quân restart
service ở parallel-2, chạy smoke hai request đồng thời rồi mới resume 28 nếu
VRAM gate đạt. Plan 03 tiếp tục đóng.

## Uncertainty

Thống kê ETA/tài nguyên đầy đủ và chất lượng 10 mẫu chưa thể kết luận trước khi
operator hoàn thành pilot.

## Open questions and next human decisions

- Quân chạy pilot đối sánh parallel-2 theo mục 9 của runbook.
- Quân chấp nhận/từ chối Gate C sau review tối thiểu 10 response.

## Cập nhật vận hành lúc 19:27 ngày 02/09/2026

Lần chạy bundle parallel-2 lúc 19:05 đã dừng ở live preflight, trước model call:
service còn là tiến trình cũ với `n_seq_max=1` và `/api/ps` báo
`context_length=4096`, không khớp config yêu cầu `8192`. Bundle vẫn sạch
`0/30`; không cần xóa hay reset artifact.

Runbook mục 9.1 nay ghi rõ `OLLAMA_NUM_PARALLEL` chỉ được đọc khi Ollama server
khởi động. Quân phải restart service với `OLLAMA_NUM_PARALLEL=2`; thao tác này
chỉ nạp model từ cache, không download lại. Runbook cũng bổ sung cách detach
`screen` bằng `Ctrl+A`, `D` để chuyển thiết bị mà không dừng service.
