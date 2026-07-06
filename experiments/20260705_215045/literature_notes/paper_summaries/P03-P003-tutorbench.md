# P03-P003 — TutorBench

Paper: `TutorBench: A Benchmark To Assess Tutoring Capabilities Of Large Language Models`  
File local: `document/paper/source_paper/2510.02663v1.pdf`  
Năm/nguồn: 2025, arXiv preprint  
Registry ID: `P03-P003`  
Vai trò trong P03: paper lõi về task gia sư, sample-specific rubric, expert authoring và đánh giá theo Bloom/tutoring skills.

## 1. Vấn đề paper giải quyết

TutorBench nhắm vào việc đánh giá LLM khi được dùng như learning aid/gia sư. Paper cho rằng benchmark kiến thức/lập luận thông thường chưa đo đủ năng lực con người-trung-tâm của tutoring: nhận diện nhu cầu học sinh, thích ứng, cá nhân hóa hướng dẫn, giữ đúng chuyên môn và hỗ trợ thay vì chỉ giải bài.

Vị trí nguồn chính: Abstract; Section 1; Section 2.

## 2. Benchmark/dataset/task

TutorBench gồm 1,490 samples ở high-school/AP STEM, phủ 6 môn: Biology, Physics, Chemistry, Statistics, Calculus và Computer Science. Dataset có cả text-only và multimodal; paper nêu 828 samples có hình ảnh bài làm hoặc nội dung học sinh đưa lên.

Ba use case chính:

| Use case | Ý nghĩa | Tương ứng với dự án Tin học 9 |
|---|---|---|
| Adaptive Explanation Generation | Giải thích thích ứng với hiểu nhầm hoặc câu hỏi tiếp theo của học sinh. | Gia sư giải thích khái niệm/thuật toán/code theo nền của học sinh. |
| Assessment and Feedback | Phân tích bài làm/lời giải của học sinh, chỉ lỗi và phản hồi. | Chấm/sửa lỗi code, thuật toán, nhận định khái niệm. |
| Active Learning Support | Đưa hint/câu hỏi gợi mở để học sinh tự đi tiếp, không lộ đáp án. | Gợi ý từng bước khi học sinh mắc kẹt. |

Paper chọn các use case này vì muốn đánh giá khả năng tutor calibrate response to student needs thay vì sinh lời giải chuẩn chung cho mọi học sinh.

Vị trí nguồn chính: Section 2.1; Figure 1; Figure 2; Appendix A.2/Figure 7.

## 3. Định nghĩa năng lực gia sư, Bloom và difficulty

TutorBench không dùng Bloom làm cấu trúc task chính, nhưng dùng Bloom để phân tích difficulty/cognitive demand. Paper dùng ba LLM mạnh gán nhãn Bloom cho samples; nếu ít nhất hai model đồng thuận thì gán category, bao phủ hơn 97% samples. Kết quả cho thấy performance không đi theo thứ tự khó dễ đơn giản của Bloom; ví dụ model có thể làm tốt ở mức “evaluate” nhưng kém hơn ở “remember” nếu nhiệm vụ đòi hỏi nhớ/nêu rõ thông tin theo ngữ cảnh.

Paper cũng phân tích tutoring skills ở mức rubric tag, gồm: identifying core difficulty/misconception, identifying correct/incorrect student steps, recalling/stating knowledge, providing alternative solutions, including examples/analogies, asking guiding questions, providing step-by-step help.

Vị trí nguồn chính: Section 3.4; Section 3.5; Figure 4; Figure 5.

## 4. Rubric/metric và cách chấm

TutorBench dùng rubric riêng cho từng sample. Mỗi sample có 3–39 rubric criteria; toàn dataset có 15,220 criteria. Rubric được thiết kế để self-contained, mutually exclusive và collectively comprehensive. Mỗi criterion được chấm pass/fail bởi LLM judge. Paper dùng trọng số:

- `+5` cho critical positive criteria;
- `+1` cho non-critical criteria;
- `-5` cho undesirable behavior, ví dụ tiết lộ final answer trong active learning.

Điểm cuối là weighted average của các binary pass/fail ratings, chuẩn hóa về khoảng `[0, 1]`.

Rubric criteria được tag theo nhiều chiều:

- evaluation dimensions: instruction following, style/tone, truthfulness, visual reasoning, visual perception, conciseness/relevance, student-level calibration, emotional component;
- tutoring skills: asking guiding questions, identifying misconceptions, recognizing correct/incorrect steps, including examples/analogies, alternative solutions, stating knowledge, step-by-step help;
- explicit/implicit;
- objective/subjective.

Vị trí nguồn chính: Section 2.3; Section 2.4; Section 3.1; Appendix A.3/Table 2; Appendix A.5.

## 5. Vai trò chuyên gia con người

Human experts viết questions và rubrics theo subject. Paper yêu cầu expert có Bachelor trở lên và có kinh nghiệm tutoring hoặc professional experience trong subject tương ứng. Appendix A.1 nêu mỗi example có câu hỏi, nội dung theo use case, golden tutoring response và rubric criteria do chuyên gia viết. Sau đó paper dùng 5 model mạnh để tạo response và giữ lại các sample đủ khó: ít nhất 3/5 model đạt dưới 50% weighted score.

Để kiểm tra LLM judge, paper thu 3 human-expert ratings per rubric criterion trên 250 samples, tổng 2,475 rubric criteria, từ 69 experts.

Vị trí nguồn chính: Section 1; Section 2.3; Section 3.7; Appendix A.1.

## 6. Bằng chứng validation/kết quả chính

Các kết quả đáng dùng:

1. Các frontier LLM chưa bão hòa benchmark: không model nào vượt 56% overall; best model đạt khoảng 55.65%.
2. Adaptive explanation là use case khó; average score được paper nêu thấp hơn so với kỳ vọng của model mạnh.
3. Bloom/difficulty không tuyến tính với performance; cần cẩn trọng khi giả định mức Bloom cao luôn khó hơn mức Bloom thấp trong bối cảnh tutoring response.
4. LLM judge alignment với human experts khá cao trong thiết lập của paper: mean inter-human agreement khoảng 0.75, LLM-human agreement khoảng 0.78, F1 khoảng 0.82 với majority vote trên non-critical rubric criteria.
5. Models tương đối tốt hơn ở nhận diện bước đúng/sai, nhưng yếu hơn ở ví dụ/analogy và alternative solutions.

Vị trí nguồn chính: Section 3.1; Table 1; Figure 3; Section 3.4; Section 3.5; Section 3.7; Figure 6.

## 7. Điểm có thể chuyển sang dự án Tin học 9

### Bằng chứng

- Ba use case của TutorBench rất gần với benchmark gia sư: giải thích thích ứng, phản hồi bài làm, gợi ý học tập chủ động.
- Vai trò expert teacher/subject expert trong viết question, golden response và rubric phù hợp với mô hình HNMU authoring.
- Rubric nên cụ thể theo sample/task, tự đủ nghĩa và có thể kiểm tra được bằng quan sát response.
- Serious error có thể tách bằng trọng số âm hoặc policy riêng, ví dụ lỗi tiết lộ đáp án khi task yêu cầu hint.
- Cần tag rubric/task theo kỹ năng gia sư để phân tích điểm mạnh/yếu của model, không chỉ tính điểm tổng.

### Suy luận cho P04

- Vì dự án muốn rubric rút gọn 3–4 tiêu chí, không nên sao chép mô hình 3–39 criteria/sample. Tuy nhiên, có thể học cách viết tiêu chí quan sát được, mutually exclusive và gắn với từng sample.
- Các tag của TutorBench có thể là nguồn để gom rubric: đúng chuyên môn/truthfulness; phù hợp học sinh/student-level calibration; chất lượng gợi mở/hỗ trợ; tuân thủ instruction/boundary.
- Bloom nên dùng để phân tầng task/coverage, nhưng không nên giả định máy móc rằng Bloom cao hơn luôn khó hơn đối với LLM tutor.

## 8. Giới hạn khi chuyển sang Tin học THCS Việt Nam

- Paper là high-school/AP STEM, không phải THCS Việt Nam.
- Dataset có Computer Science nhưng không đồng nghĩa với chương trình Tin học 9 Việt Nam.
- Paper dùng nhiều rubric criteria cho mỗi sample; điều này có thể quá tải cho HNMU trong giai đoạn pilot.
- Paper đánh giá final response trong conversation đã định sẵn; chưa đo đầy đủ thích ứng động qua nhiều lượt tự do.
- LLM judge alignment được kiểm tra trong setup riêng của paper; không thể tự động suy ra judge sẽ đáng tin trong tiếng Việt/Tin học 9.

Vị trí nguồn chính: Section 5 Limitations; Section 3.7.

## 9. Candidate claims cho evidence matrix

| Claim candidate | Nhãn | Vị trí nguồn | Ghi chú chuyển giao |
|---|---|---|---|
| Benchmark gia sư nên bao gồm adaptive explanation, assessment/feedback và active learning support. | bằng chứng | Section 2.1; Conclusion | Rất phù hợp cho P04/P05. |
| Rubric cần cụ thể, tự đủ nghĩa, tránh chồng chéo và có thể kiểm tra được. | bằng chứng | Section 2.3 | Phù hợp với phiếu tác giả/HNMU. |
| Serious error có thể được xử lý bằng penalty mạnh hoặc policy tách riêng. | bằng chứng + suy luận | Section 2.3 | P04 nên quyết định dùng rubric hay serious-error policy. |
| Bloom hữu ích để phân tích cognitive demand nhưng không tuyến tính với độ khó của LLM. | bằng chứng | Section 3.4; Figure 4 | Cảnh báo cho thiết kế task theo Bloom. |
| LLM judge cần validation với human experts trước khi dùng làm evaluator chính. | bằng chứng | Section 3.7; Figure 6 | Rất quan trọng cho phase sau, chưa nên tự động hóa chấm ngay. |

## 10. Câu hỏi mở

1. Với giai đoạn pilot, có nên giữ 3 use case của TutorBench làm nhãn phụ bên cạnh Bloom không?
2. Serious error nên là rubric thứ 4, trọng số âm, hay policy loại trừ riêng?
3. Nếu HNMU viết rubric/sample-specific criteria quá chi tiết, có làm trái mục tiêu rút gọn 3–4 rubric không? Cần cơ chế mapping từ chi tiết về rubric rút gọn.
