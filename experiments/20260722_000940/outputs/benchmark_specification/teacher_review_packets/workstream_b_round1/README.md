# Hồ sơ quyết định UET — mô hình năng lực trước khám phá nhiệm vụ

Trạng thái: **UET phê duyệt tạm thời để khám phá nhiệm vụ ngày 26/07/2026; HNMU chưa rà soát. Workstream C chưa chính thức bắt đầu.**

Người phụ trách dự án, với vai trò đại diện UET, đã cho phép dùng sáu năng lực làm giả thuyết đầu vào của Workstream C. Quyết định này không xác nhận sáu năng lực là tiêu chí cuối và không được báo cáo như kết quả đã được HNMU thẩm định.

HNMU sẽ không nhận một vòng review riêng chỉ có mô hình năng lực. Sau Workstream D, HNMU sẽ nhận một gói tích hợp gồm năng lực, hệ thống nhiệm vụ, tiêu chí hai tầng, cổng lỗi nghiêm trọng và ví dụ phản hồi tốt–trung bình–kém. Cách tổ chức này giúp giáo viên thấy trực tiếp các khái niệm được vận hành trong benchmark và giảm số vòng tham vấn rời rạc.

## Phạm vi hồ sơ hiện tại

- căn cứ đo lường và nghiên cứu đã tổng hợp ở Workstreams A–B;
- mô hình sáu năng lực tạm thời;
- quyết định UET cho sáu năng lực và hai cặp ranh giới trọng yếu;
- câu hỏi cần giữ lại cho gói HNMU tích hợp sau D;
- hai phiếu nhiệm vụ cũ được chuyển thành **mẫu tham khảo đã hoãn**, không phải nhiệm vụ đang giao cho HNMU.

Hồ sơ này không ghi nhận bất kỳ quyết định nào của HNMU. Nhánh tám nhiệm vụ và 20 nhãn thử đã chuyển sang `legacy/eight_task_candidate_branch/`; chúng không thuộc hồ sơ quyết định này và không còn là đầu vào Workstream C.

## Vai trò

- **Đại diện UET:** quyết định phạm vi tạm dùng cho khám phá nhiệm vụ và ghi rõ giới hạn suy luận.
- **HNMU:** rà soát chuyên môn–sư phạm trong gói tích hợp sau Workstream D.
- **Điều phối viên:** bảo đảm phê duyệt tạm thời của UET không bị trình bày thành xác nhận của HNMU.

## Danh mục

| Tài liệu | Mục đích hiện tại |
|---|---|
| `capability_review_guide.md` | Định nghĩa dễ đọc, ranh giới và giới hạn quan sát của sáu năng lực. |
| `capability_research_basis.md` | Bản đồng bộ với nguồn công bố nội bộ, nêu nguồn gốc mã nghiên cứu, nội dung hỗ trợ và giới hạn suy luận. |
| `capability_review_decisions.csv` | Sáu quyết định UET tạm thời. |
| `capability_overlap_review_decisions.csv` | Hồ sơ đủ 15 cặp; chỉ các dòng có trạng thái UET mới là quyết định tạm thời. |
| `capability_adjudication_decisions.csv` | Hai quyết định UET về ranh giới `STATE–DIAG` và `STRAT–SCAFF`. |
| `consultation_questions.md` | Câu hỏi sẽ tái sử dụng trong gói HNMU tích hợp sau D. |
| `capability_review_task_card.md` | Mẫu review đã hoãn, chỉ dùng làm nguồn thiết kế gói tích hợp. |
| `capability_adjudication_task_card.md` | Mẫu phân xử đã hoãn, chỉ kích hoạt nếu gói tích hợp phát sinh bất đồng. |

## Thứ tự sử dụng

1. Dùng ba bảng quyết định để truy vết cổng UET hiện tại.
2. Dùng hướng dẫn và căn cứ nghiên cứu để xây Workstream C, nhưng không coi chúng là taxonomy hay tiêu chí đã xác nhận.
3. Sau Workstream D, biên soạn lại task card tích hợp cho HNMU bằng các ví dụ cụ thể; không gửi riêng hồ sơ này như một vòng review đang hoạt động.
