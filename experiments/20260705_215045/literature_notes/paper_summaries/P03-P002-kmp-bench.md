# P03-P002 — KMP-Bench

Paper: `From Solver to Tutor: Evaluating the Pedagogical Intelligence of LLMs with KMP-Bench`
File local: `document/paper/source_paper/18426-AAAI26.ShiW-NLP.pdf`
Năm/nguồn: 2026, AAAI-26 local PDF
Registry ID: `P03-P002`  
Vai trò trong P03: paper lõi về chuyển từ “model giải bài” sang “model làm gia sư”.

## 1. Vấn đề paper giải quyết

KMP-Bench phê bình việc đánh giá AI tutor chỉ bằng problem-solving accuracy hoặc metric text similarity. Paper cho rằng gia sư Toán cần nhiều năng lực sư phạm hơn: thử thách phù hợp, giải thích, mô hình hóa, luyện tập có hướng dẫn, đặt câu hỏi, phản hồi xây dựng. Mục tiêu của KMP-Bench là đánh giá LLM trong bối cảnh tutoring nhiều lượt và theo nguyên tắc sư phạm.

Vị trí nguồn chính: Abstract; Introduction; Figure 1.

## 2. Benchmark/dataset/task

KMP-Bench có hai module:


| Module       | Mục tiêu                                                                   | Task/năng lực                                                                                        |
| ------------ | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| KMP-Dialogue | Đánh giá năng lực sư phạm tổng thể trong hội thoại nhiều lượt. | Tutor response được so với reference response trong hội thoại đã cắt tại một lượt.        |
| KMP-Skills   | Đánh giá năng lực gia sư nền tảng ở mức hạt nhỏ hơn.            | Multi-turn follow-up problem-solving; error detection and correction; mathematical problem generation. |

Dữ liệu được tạo từ 8K bài toán K-8 đã qua xác thực, lấy từ 9 nguồn, phủ 11 domain Toán và 9 grade levels. Pipeline tạo 4 loại thành phần sư phạm:

1. follow-up questions để mở rộng hiểu biết;
2. error analysis and correction;
3. similar practice problems ở nhiều mức khó;
4. confusion clarifications để xử lý điểm học sinh bối rối.

Các thành phần này được woven thành dialogue flow có tutor persona, student profile và learning objective. Sau đó human reviewers kiểm tra thủ công flow, loại bỏ các flow có vấn đề như hallucinated material hoặc sequencing không hợp lý. Paper báo cáo 451 flow, tương đương 7.6%, bị loại ở bước này. Bộ benchmark cuối có 4.6K tutoring dialogues; ngoài ra paper tạo KMP-Pile 150K dialogues cho huấn luyện.

Vị trí nguồn chính: Figure 1; Tutoring Dialogue Curation; Dataset Statistics.

## 3. Định nghĩa năng lực gia sư

KMP-Bench dùng 6 nguyên tắc sư phạm cốt lõi:

- Challenge;
- Explanation;
- Modelling;
- Practice;
- Questioning;
- Feedback.

Điểm đáng chú ý: nguyên tắc này không chỉ là tag mô tả, mà đi vào cả generation và evaluation. Mỗi tutor turn trong KMP-Dialogue được gắn một hoặc hai nguyên tắc mục tiêu; evaluator kiểm tra phản hồi model theo general criteria và principle-specific criteria.

Vị trí nguồn chính: Abstract; Figure 2; Evaluation Framework; KMP-Dialogue.

## 4. Rubric/metric và cách chấm

Trong KMP-Dialogue, paper tạo bộ 22 tiêu chí chấm:

- 4 general criteria áp dụng cho mọi phản hồi;
- 3 principle-specific criteria cho mỗi trong 6 nguyên tắc sư phạm.

Evaluator so sánh phản hồi model với original tutor turn/reference response và đưa ra Win/Tie/Lose cho từng criterion và overall judgment. Các metric gồm general-level accuracy, principle-level accuracy cho 6 nguyên tắc, overall judgment accuracy và overall accuracy.

Trong KMP-Skills, metric thay đổi theo task: accuracy theo turn cho follow-up problem-solving, F1/correction accuracy/MR-score cho error detection & correction, và pass/fail trên các chiều problem construction/solution correctness/solution quality cho problem generation.

Vị trí nguồn chính: Evaluation Framework; Table 1; Table 2.

## 5. Vai trò chuyên gia con người

Paper dùng human-in-the-loop ở các điểm quan trọng:

- human-crafted few-shot examples để hướng dẫn generation của các component sư phạm;
- manual verification của dialogue flow trước khi mở rộng thành full dialogue;
- human expert annotation để kiểm tra độ tin cậy của LLM evaluator trên subset KMP-Dialogue.

Đây là điểm gần với dự án HNMU: chuyên gia không chỉ viết câu hỏi, mà còn kiểm tra logic sư phạm, sequencing và tính hợp lý của flow.

Vị trí nguồn chính: Figure 1; Dialogue Flow Generation and Verification; Ablation/Analysis of KMP-Dialogue Evaluator.

## 6. Bằng chứng validation/kết quả chính

Các kết quả đáng dùng:

1. Model giỏi problem-solving chưa chắc giỏi tutoring dialogue. Paper nêu rõ math-specialized model có thể thua general model ở năng lực sư phạm.
2. KMP-Dialogue cho thấy sự khác nhau theo từng nguyên tắc sư phạm; ví dụ có model mạnh ở Explanation/Questioning, model khác mạnh ở Challenge/Feedback.
3. KMP-Skills cho thấy các task có lời giải kiểm chứng được dễ hơn các task yêu cầu phản hồi sư phạm tinh tế.
4. Paper kiểm tra LLM evaluator bằng 300 instances do human experts annotate và báo cáo alignment trung bình khoảng 89.8%.
5. Error analysis chỉ ra lỗi phổ biến như flawed scaffolding, evasion by substitution và vague questioning.

Vị trí nguồn chính: Table 1; Table 2; Table 3; Main Results; Figure 3.

## 7. Điểm có thể chuyển sang dự án Tin học 9

### Bằng chứng

- Benchmark gia sư cần đo “pedagogical intelligence”, không chỉ đo giải bài đúng.
- Task nên có cả hội thoại tổng thể và kỹ năng nền tảng: theo dự án Tin học 9 có thể là hỏi gợi mở, phát hiện lỗi code/thuật toán, sửa/lý giải lỗi, tạo bài luyện tập tương tự.
- Mỗi response nên được đánh giá theo tiêu chí chung và tiêu chí gắn với mục tiêu sư phạm cụ thể của turn/task.
- Human review nên kiểm tra sequencing và soundness của hội thoại, không chỉ correctness của đáp án.

### Suy luận cho P04

- 6 nguyên tắc của KMP có thể không bê nguyên xi, nhưng có thể dùng để thiết kế nhãn phụ hoặc rubric dimension: gợi mở, giải thích, phản hồi, luyện tập, mô hình hóa, thử thách phù hợp.
- Với Tin học 9, “problem generation” có thể chuyển thành task tạo bài tập tương tự hoặc biến thể, nhưng đây có thể nằm sau phase pilot nếu scope quá rộng.
- Việc gắn tutor persona/student profile/learning objective rất phù hợp với phiếu tác giả nếu HNMU có thể cung cấp bối cảnh học sinh.

## 8. Giới hạn khi chuyển sang Tin học THCS Việt Nam

- Paper thuộc Toán K-8, không phải Tin học THCS Việt Nam.
- Dữ liệu phần lớn được sinh bằng LLM rồi kiểm tra; dự án hiện ưu tiên dữ liệu do giáo viên HNMU tạo và rà soát.
- Evaluation dùng LLM evaluator; với PoC của dự án, cần cẩn trọng để không thay thế expert-teacher judgment.
- 22 criteria của KMP-Dialogue có thể quá nặng so với mục tiêu rubric rút gọn 3–4 tiêu chí; nên học cấu trúc chứ không sao chép số lượng rubric.

## 9. Candidate claims cho evidence matrix


| Claim candidate                                                                                                              | Nhãn        | Vị trí nguồn                                     | Ghi chú chuyển giao                                         |
| ---------------------------------------------------------------------------------------------------------------------------- | ------------ | --------------------------------------------------- | ------------------------------------------------------------- |
| Nên đánh giá gia sư bằng tiêu chí sư phạm, không chỉ accuracy giải bài.                                        | bằng chứng | Abstract; Introduction; Main Results                | Rất phù hợp với P04.                                      |
| Có thể tách benchmark thành holistic dialogue và foundational tutoring skills.                                          | bằng chứng | Abstract; Evaluation Framework                      | Hữu ích để phân biệt task chính và nhãn phụ.        |
| Human verification cần kiểm tra soundness/sequence của hội thoại.                                                       | bằng chứng | Figure 1; Dialogue Flow Generation and Verification | Gần với vai trò HNMU.                                      |
| Các nguyên tắc Challenge/Explanation/Modelling/Practice/Questioning/Feedback có thể là nguồn thiết kế rubric/nhãn. | bằng chứng | KMP-Dialogue; Figure 2                              | Cần Việt hóa và rút gọn.                                |
| Rubric 22 tiêu chí của KMP nên được gom lại cho PoC.                                                                 | suy luận    | Evaluation Framework                                | Phù hợp với yêu cầu rubric 3–4 tiêu chí của dự án. |

## 10. Câu hỏi mở

1. Với Tin học 9, nguyên tắc “Modelling” nên hiểu là mô hình hóa lời giải, minh họa tư duy giải bài, hay mô hình hóa thuật toán/code?
2. Có cần task “tạo bài tập tương tự” ngay trong pilot không, hay để sau?
3. HNMU có thể review sequencing của hội thoại ở mức nào nếu số mẫu tăng lên?
