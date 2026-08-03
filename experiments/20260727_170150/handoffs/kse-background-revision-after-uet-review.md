# Specialist handoff

- Delegation ID: `EXP-20260728-KSE-BACKGROUND-REVISION-001`
- Agent: `research-methodologist` (single-agent fallback in parent thread)
- Status: `completed`
- Native thread ID/label: `null`

## Delegation prompt

Sửa Introduction và Related Work theo review của đại diện UET; điều tra
claim tính mới cho benchmark gia sư AI Tin học THCS tiếng Việt.

## Follow-up or steer messages

- Tách khoảng trống theo miền, ngôn ngữ và nguồn dữ liệu.
- Rút phương pháp khỏi Introduction.
- Không dùng câu tự hạ thấp giá trị claim trong Introduction.
- Đưa nền tảng sư phạm lên trước benchmark và thêm tiếng Việt/miền chuyên
  biệt.

## Inputs read

- `kse_submit_manuscript/manuscript/main.tex`
- Các nguồn kế thừa về KMP-Bench, MathTutorBench, TutorBench, ECD và dàn
  giáo thích ứng
- VNHSGE, VMLU, EDM 2026 programming-tutor evaluation, SIGCSE 2024
  multilingual programming-exercise generation, và báo cáo PoC ĐHQGHN–Z.AI

## Outputs created

- Cập nhật `kse_submit_manuscript/manuscript/main.tex`
- Cập nhật `kse_submit_manuscript/manuscript/references.bib`
- Cập nhật `kse_submit_manuscript/notes/manuscript_status.md`
- Cập nhật `kse_submit_manuscript/notes/claim_evidence_registry.csv`

## Result summary

Introduction đã tách ba khoảng trống, rút chi tiết phương pháp và bỏ câu
model-assisted/provisional. Related Work đổi thứ tự sang nền tảng sư phạm
trước, benchmark sau, rồi tiếng Việt/miền chuyên biệt. Claim đầu tiên dùng
cấu trúc có điều kiện `To the best of our knowledge` và có nhật ký tìm kiếm.

Lượt rà mở rộng sau đó phát hiện hai tiền nhiệm quan trọng:
`DeepEduBench` đã đánh giá năng lực dạy và học bằng tiếng Việt, còn
`CSTutorBench` đã đánh giá gia sư lập trình khối ở THCS. Vì vậy, claim
rộng “benchmark đầu tiên cho gia sư AI tiếng Việt” bị bác bỏ. Manuscript
hiện chỉ khẳng định rằng chưa tìm thấy benchmark công khai kết hợp đủ bốn
thuộc tính: tiếng Việt, Tin học lớp 6--9, sinh phản hồi gia sư kế tiếp có
lịch sử hội thoại, và candidate chuyển đổi từ hội thoại giáo viên có truy
vết học liệu.

Source LaTeX đã được biên dịch thành công thành PDF ba trang bằng TeX Live
2023 sau khi bổ sung các nguồn gần nhất.

Sau góp ý tiếp theo của UET, manuscript đã:

- chuyển các phép liệt kê trong Introduction và Related Work sang cấu
  trúc đánh số `(i)`, `(ii)`,... kết hợp dấu chấm phẩy;
- xóa câu bình luận trực tiếp về việc suy đoán “đầu tiên” không đứng vững;
- loại báo cáo PoC ĐHQGHN--Z.AI khỏi paper;
- giữ DeepEduBench chỉ như nguồn công khai chưa peer review để chứng minh
  sáng kiến tồn tại, không dùng làm căn cứ cho thiết kế phương pháp.

## Orchestrator decision

UET approval được xem là thẩm quyền vận hành của benchmark. Paper không tự
hạ thấp annotation trong Introduction; các giới hạn hiệu lực đo lường được
đặt đúng chỗ ở phần Discussion/Limitations.

## Uncertainty

Novelty claim là kết luận từ tìm kiếm có mục tiêu, không phải chứng minh
phủ định tuyệt đối. Cần kiểm lại ngay trước submission.

## Open questions and next human decisions

- UET duyệt cách định vị claim ở giao điểm bốn thuộc tính và mức độ mô tả
  hai tiền nhiệm gần nhất là DeepEduBench và CSTutorBench.
- Quyết định có giữ nguồn institutional report trong bản sáu trang hay chỉ
  giữ các paper học thuật nếu cần cắt references.
