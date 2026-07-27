# Specialist handoff

- Delegation ID: `PLAN03-C-CODEBOOK-RESTORATION-001`
- Agent: `benchmark-specification-designer` trong chế độ single-agent
- Status: `completed`
- Native thread ID/label: không có; chưa spawn specialist gán nhãn

## Task

Khôi phục file codebook active từ bản tám nhiệm vụ legacy về bản sáu nguyên tắc, đồng bộ quy trình hai vòng và pilot hai instance, rồi mở lại integrity gate trước Workstream C.

## Kết quả

- Bản sáu nguyên tắc tái dựng khớp chính xác hash manifest cũ `d87742644cddb5c82030a3bcc7918493336365071e9399118438bcd66ff430b8` trước khi ghi.
- Chỉ mục 3 và mục 8 được đồng bộ thêm với Plan hiện tại: hai vòng context/reference và hai instance độc lập trên cùng lô 40.
- Hash codebook active mới: `926554872c434db32d7a97f4281d0eb947d485fe740fb4a8c8f269c99ba0f2a5`.
- Bản tám nhiệm vụ legacy vẫn giữ nguyên hash `c3a6d242485e1d6e6f6dac5f4ef6235e41350278f4d7e8462c4364ff22b365e7` trong thư mục `legacy`.
- Manifest đã chuyển integrity gate sang `passed`; số nhãn nguyên tắc chính thức vẫn là 0.

## Input

- `outputs/benchmark_specification/plan03_workstream_c_principle_design_manifest.json`
- `outputs/benchmark_specification/task_discovery/pedagogical_principles.csv`
- `outputs/benchmark_specification/legacy/eight_task_candidate_branch/task_discovery_codebook.md`
- Plan 03 và roadmap hiện hành

## Output

- `outputs/benchmark_specification/task_discovery/task_discovery_codebook.md`
- `outputs/benchmark_specification/plan03_workstream_c_principle_design_manifest.json`
- Plan 03, roadmap và README đã bỏ trạng thái blocker

## Next step

Triển khai Cổng C0a: tạo specialist, adapter, reference, input hai vòng, validator/test và forward test. Chưa chạy lô 40 trong lần đồng bộ này.
