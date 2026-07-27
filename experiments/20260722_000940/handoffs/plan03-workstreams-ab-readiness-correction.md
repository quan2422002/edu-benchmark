> **CẬP NHẬT SAU BÀN GIAO:** Workstreams A–B vẫn hợp lệ, nhưng đề xuất tái sử dụng nhánh tám nhiệm vụ/20 nhãn đã bị hủy. Nhánh đó hiện là legacy; C dùng sáu nguyên tắc KMP. Xem `plan03-workstream-c-principle-architecture-sync.md`.

# Specialist handoff

- Delegation ID: `PLAN03-AB-READINESS-CORRECTION-002`
- Agent: orchestrator ở chế độ đơn tác nhân, sử dụng các skill chuẩn `research-methodologist`, `benchmark-specification-designer` và `teacher-collaboration-designer`
- Status: `completed`
- Native thread ID/label: không có; thực hiện trong luồng chính do chỉ thị không tạo subagent

## Delegation prompt

Rà lại mức sẵn sàng của Workstreams A–B, sửa các lỗi cấu trúc/provenance/trạng thái còn sót và đồng bộ toàn bộ tài liệu trước khi bắt đầu Workstream C. Không thực hiện mã hóa ngữ nghĩa của C.

## Follow-up or steer messages

Người phụ trách dự án cho phép chạy ngoài sandbox và yêu cầu mọi lệnh Python dùng `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.

## Inputs read

- `README.md`, `ARCHITECTURE.md` và roadmap hiện hành;
- Plan 03, hai báo cáo Plan 03 và manifest công bố Workstream B;
- ma trận bằng chứng Workstream A và toàn bộ bundle năng lực Workstream B;
- gói review `teacher_review_packets/workstream_b_round1/`;
- mã publisher, schema, validator và các test liên quan;
- ba skill chuẩn và các hướng dẫn/tài liệu tham chiếu bắt buộc của chúng.

## Outputs created

- sửa `evidence_matrix.csv` và `capability_overlap_matrix.csv` về đúng schema;
- tăng cường validator trong `agents/research-methodologist/scripts/validate_evidence_matrix.py` và `src/edu_benchmark/benchmark_specification/schema.py`;
- bổ sung regression test cho dòng CSV thiếu/thừa cột và vị trí bằng chứng rỗng;
- công bố lại bundle Workstream B và manifest trạng thái `ready_for_workstream_c`;
- đồng bộ Plan 03, roadmap, README, ARCHITECTURE, báo cáo và gói review;
- tạo bàn giao này và ghi sự kiện phối hợp tương ứng.

## Result summary

Workstream A và B hiện nhất quán ở mức UET phê duyệt tạm thời để khám phá nhiệm vụ. Tất cả CSV liên quan có độ rộng dòng đúng; tám input khóa có mã băm khớp; bundle nguồn và bản công bố khớp; gói review nói rõ HNMU sẽ xem gói tích hợp sau D. Tám nhiệm vụ hạt giống và 20 nhãn do tác nhân tạo được giữ như bản nháp chuẩn bị trước, chưa phải kết quả Workstream C.

## Orchestrator decision

Chấp nhận bundle A–B ở trạng thái `READY_FOR_WORKSTREAM_C`. Không chấp nhận bất kỳ taxonomy, nhãn nhiệm vụ, kết quả hiệu chỉnh hoặc agreement nào của C trong lần sửa này.

## Uncertainty

- Sáu năng lực chưa được HNMU xác nhận.
- `CAP-CARE` vẫn có căn cứ trực tiếp yếu hơn các miền còn lại.
- Khả năng phân biệt ổn định các ranh giới năng lực phải được kiểm bằng task, rubric và ví dụ ở C–D.

## Open questions and next human decisions

- Người phụ trách dự án quyết định thời điểm chính thức bắt đầu Workstream C.
- HNMU quyết định nội dung chuyên môn–sư phạm trong gói tích hợp sau D.
- Các bản nháp 8 nhiệm vụ/20 nhãn chỉ được tái sử dụng sau khi codebook và quy trình hiệu chỉnh của C được xem lại.
