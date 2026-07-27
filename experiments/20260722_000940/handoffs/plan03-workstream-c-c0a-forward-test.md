# Bàn giao Cổng C0a — kiểm thử chuyển tiếp specialist gán nguyên tắc

- Delegation ID: `PLAN03-C-C0A-FORWARD-001`, `PLAN03-C-C0A-FORWARD-002`
- Specialist: `pedagogical-principle-annotator`
- Trạng thái: đạt sau một vòng hiệu chỉnh hợp đồng vận hành
- Native thread: `/root/plan03_c0a_forward`, `/root/plan03_c0a_forward_v2`

## Nhiệm vụ được giao

Hai lượt chạy độc lập lần lượt áp dụng quy trình hai vòng lên năm ca biên đã được UET phê duyệt. Specialist không được đọc file chứa đáp án UET. Lượt thứ hai dùng một thread mới, không được đọc bundle thất bại của lượt thứ nhất.

## Điều chỉnh sau lượt thứ nhất

Lượt thứ nhất qua kiểm tra cấu trúc nhưng chỉ khớp `1/5` kỳ vọng ngữ nghĩa. Nguyên nhân là hợp đồng chưa ngăn đủ rõ việc lấy hành động bề mặt trong `gold_response` để thay đổi nguyên tắc vốn được xác định từ nhu cầu không thể bỏ của bối cảnh.

Hợp đồng `agents/pedagogical-principle-annotator/references/two_pass_annotation_contract.md` được bổ sung các quy tắc:

- reference chỉ làm đổi nhãn khi cung cấp thông tin sư phạm mới, tương thích với bối cảnh;
- câu hỏi, ví dụ hoặc yêu cầu giải thích xuất hiện bề mặt không tự tạo hoặc thay nhãn;
- khi gold bỏ qua nhu cầu không thể thiếu của bối cảnh, giữ nhãn vòng 1 và ghi `conflict`;
- khóa các ranh giới `Questioning–Explanation`, `Feedback–Questioning`, `Challenge–Practice` và nguyên tắc–năng lực.

Không thay taxonomy, codebook hoặc đáp án UET.

## Input

- `outputs/benchmark_specification/task_discovery/forward_test/principle_annotation_pass1_input.csv`
- `outputs/benchmark_specification/task_discovery/forward_test/principle_annotation_reference_input.csv`
- `outputs/benchmark_specification/task_discovery/forward_test/principle_annotation_reference_manifest.json`
- `outputs/benchmark_specification/teacher_review_packets/workstream_c_c0_gate/forward_test_cases.csv`, chỉ được orchestrator mở sau khi specialist đóng handoff

## Output

- Bundle thất bại được giữ để truy vết tại `outputs/benchmark_specification/task_discovery/forward_test/run/`.
- Bundle đạt nằm tại `outputs/benchmark_specification/task_discovery/forward_test/run_v2/`.

## Kết quả

- Validator cấu trúc: đạt.
- Đối chiếu kỳ vọng UET: `5/5`.
- `reference_effect`: bốn `unchanged`, một `conflict`.
- Khoảng trống độ phủ: `0`.
- Hàng đợi UET: một ca `FT-C05`, là xung đột có chủ đích giữa nhu cầu giải thích của context và gold chỉ giao thêm bài luyện tập.

## Quyết định của orchestrator

Cổng C0a được mở. Hai instance A/B của Cổng C0b được phép chạy trên cùng lô 40 với vùng ghi độc lập. Bundle lượt thứ nhất không được dùng làm input cho C0b.

## Bất định

Kết quả này chỉ chứng minh specialist tuân thủ năm ranh giới đã khóa; chưa chứng minh tính tái lập trên dữ liệu thật. Cổng C0b đo phần đó.

## Quyết định tiếp theo của UET

UET không cần gán mù. Sau khi A/B đóng handoff, UET review bảng bất đồng, mọi coverage gap, mọi context–gold conflict và mẫu đồng thuận được chọn theo plan.
