# P03 — Tổng hợp literature cho thiết kế P04 từ 3 paper tier A

Ngày tạo: 06/07/2026  
Experiment: `20260705_215045`  
Phạm vi: chỉ dùng 3 paper `priority_tier = A` đã tóm tắt trong Bước 2A:

- `P03-P001` — MathTutorBench.
- `P03-P002` — KMP-Bench.
- `P03-P003` — TutorBench.

Báo cáo này là synthesis tạm đủ để P04 bắt đầu thiết kế task/rubric. Đây chưa phải literature review cuối cùng; sau này có thể mở rộng với LongTutor, K-12EduBench, VLegal-Bench hoặc paper khác.

## 1. Kết luận điều hành

Ba paper tier A cho một thông điệp rất nhất quán: **AI tutor không thể được đánh giá chỉ bằng khả năng trả lời đúng hoặc giải đúng bài**. Gia sư LLM cần được đánh giá thêm ở khả năng hiểu trạng thái học sinh, chẩn đoán lỗi/hiểu lầm, đưa gợi ý vừa đủ, phản hồi phù hợp, và tuân thủ mục tiêu sư phạm của từng lượt hội thoại.

Vì vậy, P04 nên thiết kế benchmark theo hai lớp:

1. **Lớp nhận thức/nội dung**: mức Bloom, chủ đề SGK/SGV, dạng bài Tin học.
2. **Lớp hành vi gia sư**: tutor đang giải thích thích ứng, phản hồi bài làm, gợi ý để học sinh tự đi tiếp, hay xử lý lỗi/hiểu lầm.

Bloom vẫn hữu ích, nhưng không nên là định danh chính của task. TutorBench cho thấy hiệu năng model không nhất thiết đi theo thứ tự Bloom một cách tuyến tính; do đó P04 nên đưa Bloom vào một cột/metadata riêng, ví dụ `Mức độ nhận thức`, còn cột `task` nên dựa trên hành vi gia sư cần thực hiện trong hội thoại. Nói ngắn gọn: Bloom trả lời “nhiệm vụ học tập sâu đến mức nào?”, còn task trả lời “gia sư phải làm gì với học sinh trong lượt này?”.

## 2. P04 nên kế thừa gì từ từng paper?


| Paper          | Nên kế thừa                                                                                                                                                                      | Không nên bê nguyên xi                                                                                                                                  |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MathTutorBench | Tách`expertise`, `student understanding`, `teacher response generation`; task về đúng/sai, vị trí lỗi, sửa lỗi, scaffolding; cảnh báo hội thoại dài khó hơn.        | Không bê nguyên taxonomy Toán; không dùng reward model như yêu cầu PoC; không kết luận về learning outcome.                                    |
| KMP-Bench      | Tư duy “solver → tutor”; đánh giá hội thoại theo nguyên tắc sư phạm; human verification của dialogue flow; phân biệt holistic dialogue và foundational skills.     | Không bê 22 criteria; không thay human review bằng LLM evaluator; không lấy nguyên 6 principle làm rubric chính nếu quá nặng.                   |
| TutorBench     | Ba use case: adaptive explanation, assessment/feedback, active learning support; sample-specific rubric; expert authoring; Bloom analysis; validation LLM judge với human experts. | Không bê 3–39 criteria/sample; không giả định LLM judge tin cậy cho tiếng Việt/Tin học 9; không dùng Bloom như thước đo khó tuyến tính. |

## 3. Claim có bằng chứng trực tiếp

Các claim dưới đây có thể đưa sang P04 như nền thiết kế khá chắc, với điều kiện vẫn ghi rõ giới hạn domain:


| Claim                                                                                 | Nguồn     | Ý nghĩa cho P04                                                                                                     |
| ------------------------------------------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------- |
| Cần tách “giải đúng” khỏi “dạy tốt”.                                      | `P03-C001` | Mọi task không nên chỉ hỏi đáp án cuối; phải xem tutor hỗ trợ học sinh thế nào.                        |
| Cần task về hiểu/chẩn đoán trạng thái học sinh.                              | `P03-C002` | Nên có task/rubric liên quan đến nhận diện lỗi code/thuật toán/khái niệm hoặc hiểu lầm của học sinh. |
| Gợi mở/scaffolding là năng lực gia sư cốt lõi.                                | `P03-C003` | Khi task yêu cầu active learning, tutor không nên tiết lộ lời giải ngay.                                      |
| Task nên dựa vào kiểu hành vi gia sư trong hội thoại.                    | `P03-C004` | Bloom nên là cột `Mức độ nhận thức`; task nên mô tả tutor đang giải thích, phản hồi, gợi ý hay chẩn đoán. |
| Rubric phải quan sát được, tự đủ nghĩa và tránh chồng chéo.              | `P03-C005` | Rubric P04 cần reviewer nhìn vào response là chấm được, không cần suy đoán ý đồ ẩn.                   |
| Human expert cần tham gia authoring, review và validation.                          | `P03-C007` | HNMU phải giữ vai trò quyết định chuyên môn/sư phạm; agent chỉ hỗ trợ cấu trúc hóa.                   |
| LLM judge cần validation với human experts trước khi dùng làm evaluator chính. | `P03-C008` | Giai đoạn hiện tại nên ưu tiên rubric cho người chấm; tự động hóa chấm để sau.                       |
| Bloom hữu ích nhưng không tuyến tính với độ khó của LLM tutor.             | `P03-C009` | Dùng Bloom làm cột `Mức độ nhận thức`, nhưng không dùng Bloom làm định danh task hoặc thước đo khó duy nhất. |

## 4. Suy luận có kiểm soát cho P04

Các điểm sau không phải paper nói trực tiếp về Tin học 9 Việt Nam, nhưng là suy luận hợp lý từ ba paper và bối cảnh dự án:

1. P04 nên dùng cấu trúc **hành vi gia sư × mức độ nhận thức** thay vì Bloom-only. Trong đó, hành vi gia sư là cơ sở đặt `task`, còn Bloom là cột `Mức độ nhận thức` của từng mẫu.
2. Rubric nên rút về một bộ tiêu chí gọn, khoảng 4–5 tiêu chí chính, vì rubric quá nhiều tiêu chí sẽ gây tải cho giáo viên HNMU trong pilot.
3. Serious error nên có policy riêng hoặc mapping rõ với rubric, thay vì để lẫn trong điểm thường.
4. Metadata nên ghi tối thiểu bối cảnh hội thoại: số bước/lượt trước đó, trạng thái học sinh, mục tiêu lượt tutor.
5. Các task liên quan “vị trí lỗi” cần được Việt hóa sang lỗi Tin học: lỗi code, lỗi thuật toán, lỗi hiểu khái niệm, lỗi diễn giải yêu cầu.

## 5. Đề xuất task/rubric ban đầu cho P04

### 5.1. Task và cột mức độ nhận thức khuyến nghị

P04 nên tách hai khái niệm vốn dễ bị trộn:

- `task`: loại hành vi gia sư mà benchmark muốn kiểm tra;
- `Mức độ nhận thức`: mức Bloom của nội dung học tập trong mẫu.

Cách tách này hợp lý hơn Bloom-only vì ba paper tier A đều nhấn mạnh năng lực gia sư nằm ở cách tutor tương tác với học sinh, không chỉ ở độ khó nhận thức của nội dung. Bloom vẫn quan trọng, nhưng nên là một cột riêng trong phiếu tác giả để kiểm soát coverage và độ sâu nhận thức.

| Thành phần | Giá trị gợi ý | Vai trò |
|---|---|---|
| `task` | Dựa trên hành vi gia sư: giải thích thích ứng; phản hồi bài làm/lời giải; gợi ý học tập chủ động; chẩn đoán lỗi/hiểu lầm | Định nghĩa tutor phải làm gì trong lượt hội thoại. |
| `Mức độ nhận thức` | Nhận biết; Thông hiểu; Vận dụng; Vận dụng cao | Mô tả độ sâu nhận thức của nội dung học tập theo Bloom. |
| Chủ đề học liệu | Theo taxonomy SGK/SGV P02 | Kiểm soát coverage Tin học 9 và tiền kiến thức 6–8. |
| Format | Khái niệm; trắc nghiệm; tự luận; sửa lỗi code; viết/hoàn thiện thuật toán hoặc chương trình | Kiểm soát đa dạng định dạng bài. |

Một bộ task v0 có thể bắt đầu như sau:

| Mã gợi ý | Task theo hành vi gia sư | Căn cứ từ paper | Ghi chú |
|---|---|---|---|
| T1 | Giải thích thích ứng theo mức hiểu của học sinh | TutorBench adaptive explanation; MathTutorBench teacher response generation | Dùng khi học sinh hỏi khái niệm/cách làm và tutor cần giải thích vừa sức. |
| T2 | Phản hồi bài làm, lời giải hoặc lập luận của học sinh | TutorBench assessment/feedback; KMP-Bench feedback/error correction | Dùng khi đã có bài làm/câu trả lời/lập luận của học sinh cần nhận xét. |
| T3 | Gợi ý từng bước để học sinh tự đi tiếp | TutorBench active learning support; MathTutorBench scaffolding | Dùng khi mục tiêu là giàn giáo, không đưa ngay lời giải cuối. |
| T4 | Chẩn đoán lỗi, hiểu lầm hoặc điểm mắc kẹt của học sinh | MathTutorBench student understanding/mistake location; KMP-Bench error detection and correction; TutorBench misconception tags | Có thể là task riêng hoặc nhãn bắt buộc trong T2/T3; cần P04 chốt để tránh chồng chéo. |

Đề xuất của mình: P04 nên coi T1–T3 là ba task lõi dễ giải thích với HNMU, còn T4 là ứng viên cần cân nhắc kỹ. Nếu T4 được để riêng, nó phải tập trung vào “tutor xác định đúng vấn đề của học sinh” hơn là vừa chẩn đoán vừa dạy lại đầy đủ. Nếu không, T4 sẽ chồng lên T2 và T3. Một phương án an toàn là để T4 làm **nhãn kỹ năng phụ** trong bản pilot, rồi nâng thành task riêng nếu HNMU thấy cần.

### 5.2. Rubric rút gọn gợi ý

Dựa trên ba paper và đối chiếu với phiếu tác giả đã chốt sơ bộ ở experiment `20260701_100006`, một rubric 5 tiêu chí có vẻ hợp lý hơn bản 4 tiêu chí ban đầu. Lý do là R4 cũ đang gộp quá nhiều ý: tuân thủ nhiệm vụ, không vượt phạm vi, tránh lỗi nghiêm trọng, và an toàn/đạo đức. Trong khi đó, phiếu tác giả đã có hai trường riêng:

- `truthfulness_score` — độ chính xác về kiến thức;
- `boundary_adherence_score_list` — tính tuân thủ ranh giới.

Vì vậy, P04 nên tách rõ **đúng kiến thức** khỏi **tuân thủ ranh giới/phạm vi**. Hai tiêu chí này liên quan nhưng không thay thế nhau: một phản hồi có thể đúng kiến thức nhưng vẫn vượt phạm vi lớp 9, tiết lộ lời giải khi task yêu cầu gợi mở, hoặc vi phạm ranh giới an toàn/định kiến.


| Mã gợi ý | Tiêu chí                                                 | Căn cứ từ paper                                                                         | Ghi chú                                                                       |
| ----------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| R1          | Độ chính xác về kiến thức và bám học liệu          | MathTutorBench; TutorBench truthfulness                                                    | Tương ứng gần nhất với `truthfulness_score`; chấm nội dung đúng/sai khi đối chiếu SGK/SGV và học liệu tham khảo. |
| R2          | Hiểu đúng trạng thái/lỗi/nhu cầu của học sinh     | MathTutorBench student understanding; TutorBench misconception/steps; KMP error correction | Rất quan trọng cho gia sư, không chỉ giải bài.                          |
| R3          | Hỗ trợ sư phạm phù hợp                               | MathTutorBench scaffolding; KMP principles; TutorBench active learning/adaptivity          | Bao gồm gợi mở, giải thích vừa sức, không quá tải.                   |
| R4          | Tuân thủ mục tiêu, phạm vi và ràng buộc của task   | TutorBench instruction following; KMP principle-specific criteria                           | Chấm việc tutor có bám yêu cầu của mẫu, phạm vi Tin học 9/tiền kiến thức liên quan, lịch sử hội thoại, yêu cầu gợi mở hay yêu cầu trả lời trực tiếp hay không. |
| R5          | Tuân thủ ranh giới an toàn, đạo đức, pháp lý và không định kiến | TutorBench negative weights; MathTutorBench safety limitation; phiếu tác giả `boundary_adherence_score_list` | Tương ứng gần nhất với `boundary_adherence_score_list`; nên chấm riêng với ranh giới an toàn/đạo đức/pháp lý/định kiến và các ranh giới sư phạm đặc thù. |

Đề xuất điều chỉnh: P04 nên viết R1–R5 như bộ rubric compact tạm thời, nhưng **mã lỗi nghiêm trọng vẫn nên là policy riêng** và có bảng mapping sang rubric bị ảnh hưởng. Ví dụ:

- `Sai kiến thức trọng yếu` ảnh hưởng trực tiếp R1, có thể kéo theo yêu cầu loại/chỉnh mẫu nếu HNMU xác nhận.
- `Vượt phạm vi lớp 9` hoặc không bám task ảnh hưởng trực tiếp R4.
- `Không an toàn hoặc vi phạm ranh giới`, `Củng cố định kiến`, `Bịa nguồn hoặc quy định` ảnh hưởng trực tiếp R5.
- `Tiết lộ toàn bộ kết quả` khi task yêu cầu gợi mở có thể ảnh hưởng R3 và R4, nhưng không nên mặc định chấm 0 toàn bộ task nếu policy chưa quy định.

Nói cách khác: rubric dùng để chấm mức độ chất lượng quan sát được; mã lỗi nghiêm trọng dùng để đánh dấu các vi phạm có thể cap điểm, yêu cầu sửa, hoặc loại mẫu. Quan hệ giữa hai phần này cần được P04 định nghĩa rõ và HNMU xác nhận.

## 6. Điểm cần giáo sư/HNMU xác nhận

1. **Ba use case của TutorBench** nên là task chính, nhãn phụ, hay chỉ là nguồn gợi ý? Sau phản hồi 06/07/2026, hướng hợp lý là dùng các hành vi gia sư này làm cơ sở đặt task; Bloom chuyển thành cột `Mức độ nhận thức` trong phiếu tác giả.
2. **Khi nào tutor được trả lời trực tiếp?** Không nên biến “không đưa đáp án ngay” thành luật tuyệt đối; nó chỉ nên áp dụng khi task yêu cầu gợi mở/active learning.
3. **Serious error xử lý thế nào?** Cần chốt: policy tách ngoài, trọng số âm, cap điểm từng rubric, hay loại mẫu. Sau phản hồi 06/07/2026, hướng hợp lý nhất là rubric R1–R5 chấm chất lượng, còn mã lỗi nghiêm trọng là policy riêng có mapping sang R1–R5.
4. **Mistake location trong Tin học 9 nghĩa là gì?** Cần phân biệt lỗi khái niệm, lỗi thuật toán, lỗi cú pháp/code, lỗi đọc đề.
5. **LLM judge có dùng trong phase này không?** Từ ba paper, câu trả lời an toàn là chưa dùng làm evaluator chính nếu chưa validate với HNMU.

## 7. Giới hạn của synthesis này

- Cả ba paper tier A đều không phải benchmark tiếng Việt THCS.
- Hai paper thiên mạnh về Toán; TutorBench là high-school/AP STEM.
- Chưa có căn cứ từ SGK/SGV Tin học 9; phần nội dung học liệu phải chờ P02.
- Chưa đọc LongTutor, K-12EduBench, VLegal-Bench; vì vậy phần long-term personalization, K-12 coverage rộng và benchmark tiếng Việt/cognitive grounding vẫn còn thiếu.
- Ba paper chủ yếu đo chất lượng phản hồi hoặc benchmark score; không đủ để kết luận về kết quả học tập thực tế của học sinh.

## 8. Input cụ thể cho P04

P04 có thể bắt đầu từ các artifact sau:

1. `literature_notes/evidence_to_design_matrix.csv` — ma trận claim-level, dùng trực tiếp để trace mỗi quyết định thiết kế.
2. `literature_notes/evidence_matrix.csv` — ma trận study-level theo schema validator hiện có.
3. `literature_notes/paper_summaries/P03-P001-mathtutorbench.md`
4. `literature_notes/paper_summaries/P03-P002-kmp-bench.md`
5. `literature_notes/paper_summaries/P03-P003-tutorbench.md`

Khuyến nghị khi viết P04: mọi task/rubric sinh ra từ synthesis này nên có cột `evidence_claim_id` trỏ về các claim `P03-Cxxx`. Nếu claim là `suy luận` hoặc có `human_decision_needed = yes`, P04 nên đánh dấu `needs_hnmu_review` hoặc `needs_professor_decision`.
