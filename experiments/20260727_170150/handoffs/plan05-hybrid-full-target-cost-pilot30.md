# Bàn giao phương án hybrid full target + judge cost-pilot 30 — Plan 05

- Mã công việc: `EXP-20260729-PLAN05-HYBRID-COSTPILOT30-001`
- Chế độ: `benchmark-specification-designer` được nạp trong parent thread, single-agent
- Trạng thái: `completed_without_api_calls_ready_for_user_execution`

## Quyết định đã khóa

1. Sinh full 1.400 mẫu cho ba cấu hình target, tổng 4.200 response.
2. Judge đúng 30 candidate khóa trước trên cả ba cấu hình, tổng 90 phép so sánh.
3. Chỉ sau khi phân tích usage cost-pilot mới cân nhắc judge full Gemini baseline + Llama; LearnLM không được judge full.

## Input

- `outputs/benchmark_candidate_pool/eligible_without_plan03_review.csv`
- `outputs/benchmark_evaluation/full_1400_v1/candidate_manifest.json`
- `outputs/benchmark_evaluation/pilot_80_v1/candidate_manifest.json`
- Ba instruction/configuration đã khóa trong Plan 05

## Output cài đặt

- `src/edu_benchmark/benchmark_evaluation/cost_pilot.py`
- `scripts/benchmark_evaluation/build_judge_cost_pilot_manifest.py`
- `outputs/benchmark_evaluation/full_1400_v1/judge_cost_pilot_30/candidate_manifest.json`
- `scripts/benchmark_evaluation/run_judge_cost_pilot_30.sh`
- `run-kind=cost-pilot` trong judge runner
- `run_full_1400_judge.sh` giới hạn còn baseline + Llama

## Kết quả kiểm tra

Manifest cost-pilot có 30 ID thuộc 30 family, phân bố lớp 8/8/7/7 và bao phủ đủ sáu nguyên tắc, history, Bloom, kích thước tập nguyên tắc cùng độ dài context. Judge builder lọc đúng các ID này từ ba file full bằng code. Không có API trả phí nào được gọi trong lúc cài đặt.

## Ngân sách và cổng

- Full target ba cấu hình: cận trên bảo thủ 127,09032 USD; ngoại suy smoke khoảng 18,678072 USD.
- Judge cost-pilot 90 phép: cận trên 15,97104 USD; ngoại suy smoke khoảng 3,223544 USD.
- Full judge hai model: 2.800 phép; cận trên 496,8768 USD nên vẫn đóng.

## Trình tự bàn giao

Người dùng chạy full target trước. Khi đủ 4.200 response hợp lệ, cập nhật số tiền đã chi rồi chạy judge cost-pilot. Sau đó quay lại phân tích usage và chất lượng; không chạy wrapper full judge trước quyết định UET tiếp theo.

## Cập nhật sau recovery Gemini

Gemini baseline đã đạt 1.400/1.400 với chi phí target + recovery là
16,306311 USD. Wrapper full nay xác minh rồi bỏ qua baseline, chỉ chạy Llama
và LearnLM; chi phí thực tế Llama được chuyển vào budget gate LearnLM.
Wrapper judge chặn nếu ba target chưa hoàn chỉnh và có thể tự tính mốc chi
phí từ 56,52 USD lịch sử cùng ba manifest. Preflight hai target còn lại đã
đạt; chưa gọi API cho Llama, LearnLM hoặc cost-pilot trong lần cập nhật này.

## Cập nhật retry Llama sau lỗi 429

Lượt Llama đầu đã ghi 1.314/1.400 response hoàn chỉnh với chi phí ước tính
0,36434345 USD. Có 86 mẫu chưa ghi được; toàn bộ 1.111 exception theo
attempt là HTTP 429 `RESOURCE_EXHAUSTED`. LearnLM không khởi chạy do wrapper
dừng đóng.

Runner hiện đối chiếu output đã có và chỉ gửi lại 86 ID còn thiếu. Cấu hình
retry được hạ xuống 2 worker, tối đa hai retry, exponential backoff 15–60
giây và jitter xác định tối đa 5 giây. Chi phí cũ được giữ và chi phí lượt
resume được cộng vào manifest cùng `resume_history`. Preflight không gọi API
đã đạt với 86 request và cận trên 0,574721 USD. LearnLM chỉ được mở sau khi
Llama đạt đủ 1.400/1.400; judge cost-pilot vẫn chưa chạy.

## Cập nhật recovery LearnLM 2.048

Llama đã đạt 1.400/1.400 sau khi retry 86 mẫu. LearnLM ghi đủ 1.400 record
nhưng có 386 response `MAX_TOKENS`; 1.014 response còn lại hoàn chỉnh.
Wrapper `run_recover_learnlm_2048.sh` khóa đúng 386 ID, giữ bundle v3 và
chạy thẳng ở giới hạn 2.048 token. Staging nằm trong `/tmp`; JSONL chính chỉ
được thay 386 dòng bằng merge nguyên tử khi toàn bộ recovery hoàn chỉnh.
Preflight đã đạt với cận trên 27,250056 USD; chưa gọi API recovery hoặc
judge cost-pilot trong lần cập nhật này.

## Cập nhật resume judge cost-pilot

Lượt judge đầu hoàn thành 70/90 phép chấm với chi phí 3,439951 USD. Hai mươi
phép còn thiếu gồm 16 lỗi DNS tạm thời và bốn output không hợp lệ. Runner
hiện phân loại DNS/connection failure là retryable, dùng 8 worker và
exponential backoff 5–30 giây với jitter tối đa 2 giây. Preflight không gọi
API xác nhận 70 existing, 20 pending, cận trên 3,54912 USD và không thay đổi
ba artifact hiện có.
