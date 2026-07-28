# Trạng thái manuscript KSE 2026

Cập nhật: 28/07/2026

## Đã hoàn thành

- Plan đã được UET phê duyệt để bắt đầu triển khai.
- Đã tạo source LaTeX theo `IEEEtran` conference mode.
- Đã viết bản nháp đầu tiên của `Introduction`.
- Đã viết bản nháp đầu tiên của `Related Work and Background`.
- Đã tạo `references.bib` với 15 nguồn được dùng trực tiếp.

## Giới hạn hiện tại

- Tên và thứ tự tác giả, affiliation và corresponding author chưa được
  cung cấp nên source đang dùng placeholder.
- Abstract và các phần Method, Results, Discussion, Conclusion chưa được
  viết.
- Bản thảo hiện biên dịch thành công bằng `latexmk`/`pdflatex`/`bibtex`
  trên TeX Live 2023; PDF nền hiện có ba trang. Còn một cảnh báo
  `underfull hbox` trong danh sách đóng góp, một cảnh báo tương tự trong
  Related Work và một cảnh báo URL hơi tràn ở bibliography; các cảnh báo
  này không làm hỏng bản PDF.
- Các nhãn và kết quả đã được đại diện UET phê duyệt được dùng làm
  ground truth vận hành của nghiên cứu. Việc kiểm định hiệu lực đo lường
  rộng hơn là câu hỏi nghiên cứu tiếp theo, không phải lý do hạ thấp trạng
  thái dữ liệu trong phần giới thiệu.

## Bước gần nhất

1. UET rà soát câu chuyện khoa học, mức độ claim và độ dài hai phần nền.
2. Bổ sung thông tin tác giả/đơn vị.
3. Biên dịch lại và kiểm tra giới hạn sáu trang sau mỗi phần mới.
4. Viết `Dataset and Construction` và hình pipeline.

## Nhật ký tìm kiếm cho claim tính mới — 28/07/2026

Câu hỏi: đã có benchmark công khai nào đánh giá phản hồi gia sư AI bằng
tiếng Việt cho môn Tin học THCS hay chưa?

Phạm vi tìm kiếm:

- nguồn học thuật và kho chính: arXiv, ACL Anthology, ACM/SIGCSE, EDM;
- đối chiếu bổ sung: ICLR workshop, OpenAlex, trang benchmark công khai
  và Hugging Face;
- nguồn Việt Nam bổ sung: trang cơ quan giáo dục/đại học và truy vấn tiếng
  Việt;
- truy vấn tiếng Anh: `Vietnamese AI tutor benchmark Informatics
  education`, `Vietnamese tutoring benchmark large language model
  education`, `Vietnamese educational benchmark LLM tutoring dialogue`,
  `computer science AI tutor benchmark LLM pedagogical dialogue`;
- truy vấn tiếng Việt/miền: `gia sư AI benchmark Tin học`, `gia sư AI
  tiếng Việt đánh giá mô hình`, `Vietnamese Informatics AI tutor`,
  `Vietnamese computer science education LLM tutor benchmark`.
- truy vấn mở rộng sau UET review: `DeepEduBench Tin học`,
  `Vietnamese virtual tutoring LLM`, `Vietnamese programming education
  benchmark AI tutor`, `computer science AI tutor benchmark`,
  `programming education LLM tutor evaluation`.

Tiêu chí đưa vào: công trình hoặc nguồn tổ chức mô tả benchmark, bộ dữ
liệu, giao thức đánh giá hoặc hệ thống gia sư LLM có liên quan trực tiếp
đến tiếng Việt, giáo dục hoặc Tin học/lập trình. Các kết quả chỉ nói về
chatbot phổ thông, học ngôn ngữ Việt như ngoại ngữ, quản lý giáo dục hoặc
đánh giá kiến thức không có hành vi gia sư được giữ làm đối chứng nhưng
không được coi là tiền nhiệm trực tiếp. Lượt tìm dừng khi hai vòng truy
vấn Anh–Việt mở rộng không phát hiện thêm nhóm tiền nhiệm mới; giao diện
tìm kiếm không cung cấp tổng số kết quả ổn định nên bảng chỉ ghi các kết
quả liên quan đã sàng lọc.

Kết quả sàng lọc mở rộng:

| Nguồn | Tiếng Việt | Đánh giá năng lực gia sư | Tin học/lập trình | THCS | Dữ liệu hội thoại giáo viên |
|---|---:|---:|---:|---:|---:|
| VNHSGE | Có | Không | Không | Không | Không |
| ViMath-Bench | Có | Không | Không | Không xác định | Không |
| VMLU | Có | Không | Có một số miền Tin học | Có cấp THCS, không phải Tin học THCS | Không |
| DeepEduBench | Có | Có | Không được tài liệu công khai xác định | Không được xác định | Không được xác định |
| Thử nghiệm gia sư STEM Việt Nam | Có | Có | Không | K--12 | Không |
| PoC ĐHQGHN--Z.AI | Có | Có | Không | Lớp 6--9 | Không phải benchmark công khai |
| Emo-SocraTeach-Multi | Có | Dữ liệu huấn luyện, không phải benchmark | Không | Không xác định | Dịch từ hội thoại sinh tổng hợp |
| CSTutorBench | Không | Có | Có | Có | Tình huống được thiết kế |
| Shin và cộng sự | Không | Có | Có | Không, bậc đại học | Có, từ CodeHelp |
| Jordan và cộng sự | Có | Không | Có | Không xác định | Không |

Phân xử claim:

- Bác bỏ claim rộng `benchmark đầu tiên cho gia sư AI tiếng Việt` vì
  DeepEduBench và thử nghiệm gia sư STEM tiếng Việt đã tồn tại.
- Không claim là benchmark Tin học đầu tiên nói chung vì CSTutorBench đã
  đánh giá gia sư lập trình khối ở THCS.
- Giữ kết luận hẹp: trong phạm vi nguồn công khai đã sàng lọc, chưa tìm
  thấy benchmark kết hợp đồng thời (i) phản hồi bằng tiếng Việt, (ii)
  chương trình Tin học lớp 6--9, (iii) sinh lượt phản hồi gia sư kế tiếp
  có điều kiện theo lịch sử hội thoại, và (iv) candidate được chuyển đổi
  từ hội thoại sư phạm do giáo viên biên soạn, có truy vết học liệu.
- Trong paper, ưu tiên diễn đạt bằng `we found no publicly documented
  benchmark that combines...` thay cho từ `first`. Phải chạy lại lượt
  tìm kiếm cuối ngay trước submission.
- DeepEduBench được giữ trong Related Work như một sáng kiến công khai
  chưa peer review và chỉ chứng minh sự tồn tại/phạm vi tự công bố; không
  được dùng làm căn cứ phương pháp. Báo cáo PoC ĐHQGHN--Z.AI được loại
  khỏi paper chính nhưng vẫn giữ trong nhật ký sàng lọc.
