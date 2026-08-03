# Bàn giao pilot 80 mẫu — Plan 05

- Delegation ID: `EXP-20260729-PLAN05-PILOT80-001`
- Agent: `benchmark-specification-designer` ở chế độ single-agent
- Status: `completed_without_api_calls`
- Native thread ID/label: không có; skill canonical được nạp trong parent thread

## Delegation prompt

Thu hẹp pilot từ 240 xuống khoảng 80 candidate nhưng vẫn bảo đảm bao phủ;
chuẩn bị target pilot và judge pilot để project lead tự chạy và tự rà kết
quả do không còn thời gian cho một lượt chấm chuyên gia mới.

## Follow-up or steer messages

Người dùng yêu cầu chỉ code, gói lệnh vào file shell và không tự gọi API.

## Inputs read

- `README.md`, `ARCHITECTURE.md` và roadmap active
- Plan 05, pool 1.400 candidate eligible, requirement full run
- Hai target smoke v2, judge smoke retry1, rubric/error catalog và tài liệu LearnLM chính thức của Google

## Outputs created

- `outputs/benchmark_evaluation/pilot_80_v1/candidate_manifest.json`
- `src/edu_benchmark/benchmark_evaluation/pilot.py`
- `scripts/benchmark_evaluation/build_pilot_manifest.py`
- `scripts/benchmark_evaluation/run_pilot_80_targets.sh`
- `scripts/benchmark_evaluation/run_pilot_80_judge.sh`
- Test pilot và cập nhật runner/Plan 05/protocol/roadmap/README/architecture

## Result summary

Manifest có 80 candidate thuộc 80 family, đúng 20 mẫu mỗi lớp và 54 cặp
lớp–bài học. Incidence Challenge/Explanation/Feedback/Modelling/Practice/
Questioning là 8/48/41/14/12/35. History rỗng/không rỗng là 39/41;
Bloom remember/understand/apply là 24/31/25. Ba cấu hình target preflight
đạt: Gemini baseline, Llama 4 Maverick và Gemini+LearnLM-oriented prompt.
Cấu hình thứ ba là prompt ablation trên cùng Gemini, không phải model độc
lập. Tổng cận trên gồm mọi retry của target và judge là 49,851744 USD, dưới
trần pilot 55 USD. Không có API call trong lần cài đặt này.

## Orchestrator decision

Bàn giao hai wrapper executable. Chạy target trước; wrapper này lần lượt
chạy ba cấu hình. Chỉ chạy judge sau khi cả ba cấu hình đều xuất đủ 80
response hợp lệ, tổng cộng 240 response.

## Uncertainty

Pilot lấy quá mẫu nguyên tắc hiếm nên không đại diện phân bố quần thể. Judge
Gemini cùng model với một target và không có calibration người–judge độc
lập mới. Kết quả chỉ mang tính thăm dò.

## Open questions and next human decisions

- Project lead chạy target wrapper, kiểm manifest và lỗi.
- Khi đủ 240 response, chạy judge wrapper rồi yêu cầu Codex rà kết quả theo `target_run_id`.
- Dùng hai phán quyết chuyên gia trên smoke anchor để soi false positive và
  false negative của serious-error detection.
