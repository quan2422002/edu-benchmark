# Bàn giao bản sửa phương pháp C0b

- Delegation ID: `PLAN03-C-C0B-METHOD-REVISION-001`
- Agent: `research-methodologist` và `benchmark-specification-designer` ở chế độ single-agent trong parent thread
- Status: `completed`
- Native thread ID/label: không có; không spawn specialist mới

## Delegation prompt

Điều tra lại nguồn gốc sáu nguyên tắc, sửa phần đối chiếu trước–sau có thể xác định bằng code, giảm tài liệu bắt buộc đọc của specialist và đề xuất quy tắc đa nhãn không dùng nhãn phụ để che bất định.

## Follow-up or steer messages

Không có. Ba specialist của C0a/C0b đã hoàn tất công việc cũ; không thay đổi đầu vào khi các thread đang chạy.

## Inputs read

- `agents/research-methodologist/SKILL.md`
- `agents/benchmark-specification-designer/SKILL.md`
- bản xem trước chính thức *Making Every Lesson Count*
- KMP-Bench, Sections 2.3 và 3.1
- bundle A/B và báo cáo C0b
- năm tài liệu nguồn gốc được khóa trong manifest C0b đầu tiên

## Outputs created

- cập nhật ma trận nguồn, bằng chứng, phát biểu và nhật ký tìm kiếm của Workstream A;
- cập nhật `pedagogical_principles.csv` và `task_discovery_codebook.md` ở trạng thái chờ UET duyệt;
- cập nhật skill/hợp đồng runtime của `pedagogical-principle-annotator`;
- bổ sung `reconcile_principle_annotation_draft.py` và kiểm thử hồi quy;
- cập nhật Plan 03, roadmap, báo cáo C0b, gói nội dung paper, README và ARCHITECTURE.

## Result summary

- `changed`/`unchanged` được suy ra bằng code; agent chỉ quyết định `conflict`.
- Specialist chỉ đọc đầy đủ ba CSV ngắn; hai Markdown dài được khóa hash và chỉ mở khi cần giải quyết ranh giới.
- Sáu nguyên tắc được diễn giải như các chức năng có quan hệ qua lại, không phải sáu lớp loại trừ.
- Chỉ giữ hai nhãn khi cả hai chức năng độc lập và không thể bỏ; không tự động chuyển nhãn bất đồng thành nhãn phụ.
- Packet 29 dòng là bằng chứng chẩn đoán, chưa yêu cầu UET phân xử từng mẫu.

## Orchestrator decision

Không chạy lại C0a/C0b và không mở C1 trước khi UET duyệt hoặc sửa bản ranh giới, quy tắc đa nhãn và lô phân tầng 10 ứng viên mỗi lớp 6–9.

## Uncertainty

Allison–Tharby không cung cấp giao thức gán nhãn hậu nghiệm hoặc thứ tự chính–phụ. Quy tắc chọn nhãn chính hiện vẫn là suy luận thiết kế của dự án.

## Open questions and next human decisions

- UET duyệt hoặc sửa sáu ranh giới chức năng.
- UET duyệt quy tắc chỉ đồng gán khi hai chức năng độc lập và không thể bỏ.
- UET quyết định có giữ ngưỡng trùng nhãn chính `1.00` sau khi thứ tự chính–phụ được xác định là quy ước dự án hay không.
