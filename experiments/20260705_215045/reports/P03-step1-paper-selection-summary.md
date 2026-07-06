# P03 — Báo cáo Bước 1: Sàng lọc paper local

Ngày tạo: 05/07/2026  
Experiment: `20260705_215045`  
Phạm vi: chỉ sàng lọc paper local trong `document/paper/source_paper/`; chưa viết tóm tắt chi tiết từng paper.

## 1. Kết quả ngắn gọn

Đã sàng lọc 7 PDF local:

- `include`: 6 paper;
- `defer`: 1 paper;
- `exclude`: 0 paper.

Artifact chính: `experiments/20260705_215045/literature_notes/paper_selection_registry.csv`.

## 2. Paper nên đọc ở Bước 2

| Mã | Paper | Vai trò trong P03 |
|---|---|---|
| `P03-P001` | MathTutorBench: A Benchmark for Measuring Open-ended Pedagogical Capabilities of LLM Tutors | Liên quan trực tiếp nhất tới benchmark gia sư LLM dạng mở; có khả năng cung cấp căn cứ cho năng lực sư phạm, rubric và cách tách năng lực gia sư khỏi năng lực giải bài. |
| `P03-P002` | From Solver to Tutor: Evaluating the Pedagogical Intelligence of LLMs with KMP-Bench | Trọng tâm đúng vào rủi ro dự án: LLM không chỉ giải bài mà phải hành xử như gia sư. Hữu ích để định nghĩa task/rubric về năng lực sư phạm. |
| `P03-P003` | TutorBench: A Benchmark To Assess Tutoring Capabilities Of Large Language Models | Liên quan trực tiếp tới các năng lực gia sư như giải thích thích ứng, phản hồi bài làm và gợi ý học tập; có nhắc sample-specific rubrics và dữ liệu do chuyên gia tạo. |
| `P03-P004` | LongTutor: Benchmarking Large Language Models for Long-term Personalized Tutoring | Hữu ích cho khía cạnh lịch sử hội thoại, cá nhân hóa và nhiều lượt tương tác. Không phải lõi Bloom, nhưng giúp kiểm soát thiết kế mẫu hội thoại gia sư. |
| `P03-P005` | K-12EduBench: A Benchmark for Evaluating Large Language Models’ Knowledge, Problem-Solving, and Educational Goal Cognition in K-12 Education | Không chuyên về gia sư hội thoại, nhưng liên quan trực tiếp tới K-12, kiến thức, giải quyết vấn đề và mục tiêu giáo dục; hữu ích cho coverage và mức nhận thức. |
| `P03-P006` | VLegal-Bench: Cognitively Grounded Benchmark for Vietnamese Legal Reasoning of Large Language Models | Không thuộc giáo dục/gia sư, nhưng có giá trị về benchmark tiếng Việt và phân tầng nhận thức trong bối cảnh Việt Nam; có thể hỗ trợ cách lập Bloom/độ khó. |

## 3. Paper tạm hoãn

| Mã | Paper | Lý do defer |
|---|---|---|
| `P03-P007` | VMLU Benchmarks: A comprehensive benchmark toolkit for Vietnamese LLMs | Có giá trị về benchmark tiếng Việt, nhưng chưa thấy liên quan trực tiếp tới gia sư, Bloom, rubric giáo dục hoặc Tin học THCS trong sàng lọc đầu. Giữ lại để đọc sau nếu cần căn cứ về benchmark tiếng Việt. |

## 4. Lưu ý khi sang Bước 2

1. Nên đọc trước ba paper gia sư lõi: `P03-P001`, `P03-P002`, `P03-P003`.
2. `P03-P004` hữu ích cho lịch sử hội thoại/cá nhân hóa, nhưng có thể để sau nếu cần chạy nhanh.
3. `P03-P005` hỗ trợ coverage và mức nhận thức trong K-12.
4. `P03-P006` chỉ nên dùng như bằng chứng hỗ trợ về benchmark tiếng Việt và phân tầng nhận thức; không dùng làm bằng chứng trực tiếp về gia sư.
5. `P03-P007` chưa đọc sâu trong pass đầu để tránh làm loãng trọng tâm P03.

## 5. Giới hạn của bước này

- Việc sàng lọc dựa trên metadata và 1–2 trang đầu PDF, chưa phải full-text review.
- Một số paper chưa có URL/DOI ổn định trong registry; cần xác minh trước khi đưa vào ma trận bằng chứng cuối.
- Chưa tạo `review_protocol.md`; nếu bước sau bắt đầu trích xuất bằng chứng/kết luận, cần tạo protocol trước hoặc song song ngay đầu bước 2.
