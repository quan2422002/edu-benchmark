# Ghi chú rà soát bằng chứng có mục tiêu

Ngày tạo: 04/07/2026  
Nguồn: `drive_snapshot/files/literature_review/evidence_matrix.xlsx`  
Phạm vi: chỉ kiểm tra nhanh các claim nhạy cảm để phục vụ sprint, chưa thay thế literature review đầy đủ.

| Claim cần chống lưng | Nguồn trong snapshot | Giới hạn | Cách dùng tạm thời |
| --- | --- | --- | --- |
| Giàn giáo, giữ quyền chủ động, tránh đưa lời giải quá sớm | LIT-002; LIT-005; LIT-006; LIT-028 | Có nhiều nguồn tutoring/AI tutor, nhưng phần lớn không phải Tin học 9 Việt Nam. | Dùng làm căn cứ tạm cho D5; cần HNMU hiệu chuẩn theo giới hạn số bước hội thoại. |
| Nhận diện trạng thái/lỗi của học sinh trước khi phản hồi | LIT-004; LIT-005; LIT-010; LIT-014; LIT-015; LIT-018 | Bằng chứng tốt hơn ở toán/lập trình nhập môn; chưa trực tiếp cho toàn bộ Tin học 9. | Dùng cho D3 và T03/T06. |
| Phản hồi cần đúng, rõ, có bước tiếp theo khả thi | LIT-005; LIT-014; LIT-015; LIT-020 | Các rubric tổng quát cần dịch sang tiêu chí giáo viên dễ chấm. | Dùng cho D1/D4/D7. |
| An toàn, công bằng, tránh định kiến và thiên lệch đánh giá | LIT-020; LIT-023; LIT-024; LIT-025 | Một số nguồn là meta-evaluation, không phải tutoring trực tiếp. | Dùng cho D8 và lỗi E06/E07/E10; cần HNMU/UET chốt policy. |
| Task hướng nghiệp không định kiến | LIT-020; LIT-023; LIT-024 | Bằng chứng tutoring trực tiếp còn mỏng; chủ yếu là nguyên tắc responsible AI/fairness. | T07 nên giữ `needs_hnmu_review`. |

## Kết luận tạm

- Các tiêu chí về chẩn đoán lỗi, gợi ý từng bước, không làm thay và phản hồi có thể hành động có căn cứ tương đối tốt từ literature về AI tutor/tutoring trong toán và lập trình.
- Các task T02, T04, T07 vẫn cần thận trọng vì bằng chứng trực tiếp cho Tin học 9 Việt Nam còn hạn chế.
- Không nên gọi rubric/task hiện tại là bản chính thức trước khi HNMU xác nhận và trước khi literature review đầy đủ hoàn tất.
