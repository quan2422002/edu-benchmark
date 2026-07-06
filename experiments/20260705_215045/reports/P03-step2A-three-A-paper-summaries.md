# P03 — Báo cáo Bước 2A: Tóm tắt chi tiết 3 paper tier A

Ngày tạo: 06/07/2026  
Experiment: `20260705_215045`  
Phạm vi: chỉ tóm tắt 3 paper có `priority_tier = A` trong `paper_selection_registry.csv`.

## 1. Artifact đã tạo

| Paper ID | File tóm tắt | Vai trò |
|---|---|---|
| `P03-P001` | `literature_notes/paper_summaries/P03-P001-mathtutorbench.md` | Căn cứ mạnh cho việc tách năng lực giải bài khỏi năng lực gia sư; scaffolding; student understanding. |
| `P03-P002` | `literature_notes/paper_summaries/P03-P002-kmp-bench.md` | Căn cứ mạnh cho khung “solver → tutor”, hội thoại nhiều lượt, nguyên tắc sư phạm và human verification. |
| `P03-P003` | `literature_notes/paper_summaries/P03-P003-tutorbench.md` | Căn cứ mạnh cho use case gia sư, sample-specific rubric, expert authoring, Bloom analysis và LLM-judge validation. |

Protocol dùng cho bước này: `literature_notes/review_protocol.md`.

## 2. Kết luận nhanh cho P04

1. Cả 3 paper đều ủng hộ việc không đánh giá AI tutor chỉ bằng đáp án đúng. Gia sư cần năng lực chẩn đoán hiểu lầm, gợi mở, phản hồi, thích ứng với học sinh.
2. Có thể thiết kế benchmark theo hai lớp: mức Bloom/độ khó của nhiệm vụ và hành vi gia sư trong hội thoại.
3. Rubric nên quan sát được từ response/hội thoại. Tuy nhiên, TutorBench và KMP-Bench dùng nhiều tiêu chí hơn mục tiêu của dự án, nên P04 cần gom lại thành 3–4 tiêu chí chính.
4. Human expert giữ vai trò quan trọng ở authoring, verification và validation; không nên để LLM tự sinh/tự chấm mà không có kiểm soát.
5. Bloom hữu ích, nhưng không nên hiểu máy móc là mức Bloom càng cao thì LLM tutor càng khó xử lý. TutorBench cho thấy performance không nhất thiết tăng/giảm theo thứ tự Bloom.

## 3. Candidate design claims mạnh nhất

| Claim | Nguồn hỗ trợ | Mức chuyển giao |
|---|---|---|
| Tách “giải đúng” khỏi “dạy tốt”. | MathTutorBench; KMP-Bench; TutorBench | Mạnh, dùng trực tiếp cho P04. |
| Cần task về hiểu/chẩn đoán trạng thái học sinh. | MathTutorBench; TutorBench | Mạnh, cần Việt hóa sang lỗi Tin học 9. |
| Cần task/tiêu chí về gợi mở, không tiết lộ đáp án khi mục tiêu là active learning. | MathTutorBench; TutorBench | Mạnh, nhưng phải có ngoại lệ khi học sinh cần lời giải trực tiếp. |
| Rubric cần cụ thể, kiểm tra được và có thể trace tới phản hồi. | TutorBench; KMP-Bench | Mạnh, nhưng số lượng rubric phải rút gọn. |
| LLM judge chỉ nên dùng sau khi validation với human experts. | TutorBench; KMP-Bench | Mạnh cho phase sau; chưa nên dùng làm evaluator chính ngay. |

## 4. Việc chưa làm

- Chưa tóm tắt `A-`, `B+`, `B` papers: LongTutor, K-12EduBench, VLegal-Bench.
- Chưa tạo `evidence_to_design_matrix.csv`.
- Chưa viết synthesis tổng quát cuối P03.
- Chưa xác minh URL/DOI cho các paper có `not_verified_local_pdf_only`.

## 5. Đề xuất bước tiếp theo

Nếu cần output nhanh cho P04, bước kế tiếp nên tạo `evidence_to_design_matrix.csv` từ 3 summaries này trước. Nếu muốn nền chắc hơn về Bloom/coverage/tiếng Việt, nên tóm tắt thêm `P03-P005` K-12EduBench và `P03-P006` VLegal-Bench trước khi tạo matrix.
