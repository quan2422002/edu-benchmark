# P03-P001 — MathTutorBench

Paper: `MathTutorBench: A Benchmark for Measuring Open-ended Pedagogical Capabilities of LLM Tutors`  
File local: `document/paper/source_paper/2502.18940v2.pdf`  
Năm/nguồn: 2025, arXiv preprint  
Registry ID: `P03-P001`  
Vai trò trong P03: paper lõi về đánh giá năng lực gia sư LLM trong hội thoại mở.

## 1. Vấn đề paper giải quyết

Paper xuất phát từ khoảng trống: nhiều đánh giá LLM trong giáo dục chỉ đo khả năng giải bài hoặc dùng metric bề mặt, trong khi gia sư tốt cần hướng dẫn học sinh suy nghĩ, phát hiện lỗi, gợi mở, và không đơn giản đưa đáp án. MathTutorBench đề xuất một benchmark nhanh, tự động hóa được, nhưng vẫn hướng tới năng lực sư phạm trong gia sư Toán.

Vị trí nguồn chính: Abstract; Section 1; Figure 1; Figure 2.

## 2. Benchmark/dataset/task

MathTutorBench chia năng lực gia sư thành 3 nhóm lớn và 7 task:

| Nhóm | Task | Ý nghĩa |
|---|---|---|
| Math Expertise | Problem Solving | Đo năng lực giải bài cơ bản. |
| Math Expertise | Socratic Questioning | Sinh câu hỏi từng bước thay vì chỉ đưa lời giải. |
| Student Understanding | Student Solution Correctness | Xác định lời giải của học sinh đúng/sai. |
| Student Understanding | Mistake Location | Tìm vị trí lỗi đầu tiên trong lập luận của học sinh. |
| Student Understanding | Mistake Correction | Sửa lời giải khi lịch sử hội thoại có bước sai. |
| Teacher Response Generation | Scaffolding Generation | Sinh lượt phản hồi tiếp theo của gia sư trong hội thoại. |
| Teacher Response Generation | Pedagogical Instruction Following | Sinh phản hồi theo hướng dẫn sư phạm rõ hơn, ví dụ nudging/guiding question/không làm học sinh quá tải. |

Nguồn dữ liệu gồm GSM8k, StepVerify, MathDialBridge và biến thể hội thoại dài hơn. Table 1 mô tả số lượng instance và loại input/ground truth cho từng task.

Vị trí nguồn chính: Section 4; Section 4.1; Table 1; Appendix/Figure 5.

## 3. Định nghĩa năng lực gia sư và nguyên tắc sư phạm

Paper nêu một số nguyên tắc sư phạm có thể chuyển thành rubric hoặc policy:

- đúng chuyên môn, không hướng học sinh tới sự kiện sai;
- scaffolding: hỗ trợ bằng gợi ý/câu hỏi thay vì đưa đáp án ngay;
- khuyến khích học sinh tự sửa lỗi sau khi lỗi được nhận diện;
- tránh quá tải nhận thức bằng cách không đưa quá nhiều thông tin trong một lượt.

Điểm đáng chú ý là paper tách rõ “giải đúng bài” khỏi “dạy tốt”. Đây là bằng chứng quan trọng cho thiết kế benchmark của dự án: một AI tutor có thể giỏi giải bài nhưng vẫn kém ở năng lực chẩn đoán lỗi, gợi mở hoặc duy trì hội thoại học tập.

Vị trí nguồn chính: Section 3.2; Section 4.1; Section 6.1.

## 4. Rubric/metric và cách chấm

Với task sinh phản hồi gia sư mở, paper không dùng một đáp án đúng duy nhất. Thay vào đó, paper huấn luyện reward model/critic để chấm chất lượng phản hồi gia sư theo sở thích sư phạm. Dữ liệu preference đến từ nhiều nguồn, trong đó có phản hồi của giáo viên chuyên gia và giáo viên mới/novice trong Bridge, các cặp preference từ MRBench, MathDial và dữ liệu câu hỏi gợi mở.

Cách làm chính:

- tạo cặp phản hồi được ưu tiên và bị từ chối;
- ưu tiên phản hồi có câu hỏi Socratic, probing student understanding, không tiết lộ lời giải đầy đủ;
- dùng pairwise ranking để huấn luyện một score tổng hợp;
- dùng win rate để so sánh phản hồi model với teacher response.

Vị trí nguồn chính: Section 4.3; Section 4.3.2; Section 4.3.3; Table 2; Figure 6; Figure 7.

## 5. Vai trò chuyên gia con người

Paper không phải một quy trình teacher-authoring giống HNMU, nhưng có dùng nguồn dữ liệu liên quan tới giáo viên:

- MathDial chứa hội thoại do human teachers tương tác với simulated students;
- Bridge có phản hồi novice teacher và bản revise bởi expert teacher;
- dữ liệu preference/human annotation từ các benchmark khác được dùng để huấn luyện/đánh giá reward model.

Điểm chuyển giao cho dự án: dữ liệu chuyên gia con người vẫn quan trọng, nhất là khi cần phân biệt phản hồi “nghe có vẻ hay” với phản hồi thực sự tốt về mặt sư phạm.

Vị trí nguồn chính: Section 4.2; Table 2; Section 6.2.

## 6. Bằng chứng validation/kết quả chính

Các kết quả đáng dùng cho P04:

1. Năng lực giải bài không tự động chuyển thành năng lực gia sư. Paper báo cáo trade-off giữa expertise/student understanding/pedagogy ở nhiều model.
2. Hội thoại dài hơn làm gia sư khó hơn; model dễ giảm chất lượng khi ngữ cảnh dài hơn.
3. Reward model huấn luyện trên pedagogical preference tốt hơn các judge/reward model tổng quát trong việc phân biệt expert vs novice teacher response.
4. Pedagogical instruction following là một năng lực riêng: có model cải thiện khi prompt ghi rõ nguyên tắc sư phạm, có model không cải thiện.

Vị trí nguồn chính: Section 6.1; Section 6.2; Table 3; Table 4; Figure 3; Figure 4.

## 7. Điểm có thể chuyển sang dự án Tin học 9

### Bằng chứng

- Nên tách năng lực “giải đúng” khỏi năng lực “dạy đúng cách”. Với Tin học 9, model không chỉ cần trả lời đúng về thuật toán/code/khái niệm, mà còn phải chẩn đoán hiểu lầm và gợi mở phù hợp.
- Benchmark nên có nhóm task về student understanding: nhận diện đúng/sai, vị trí lỗi, sửa lỗi hoặc phản hồi khi học sinh có lời giải sai.
- Với hội thoại gia sư, nên có tiêu chí về scaffolding: không đưa đáp án ngay khi nhiệm vụ yêu cầu gợi mở.
- Cần kiểm soát độ dài/ngữ cảnh hội thoại vì hội thoại dài hơn có thể làm giảm chất lượng gia sư.

### Suy luận cho P04

- Rubric rút gọn của dự án có thể gom thành: đúng chuyên môn; hiểu trạng thái/lỗi của học sinh; chất lượng hỗ trợ sư phạm; tuân thủ ràng buộc/ranh giới nghiêm trọng.
- Các task Bloom nên được kết hợp với hành vi gia sư: ví dụ “Vận dụng” không chỉ yêu cầu giải bài mà yêu cầu tutor giúp học sinh tự đi tới lời giải.

## 8. Giới hạn khi chuyển sang Tin học THCS Việt Nam

- Paper tập trung Toán, không phải Tin học; các kiểu lỗi trong lập trình/Scratch/Python có thể khác lỗi giải toán.
- Paper không đo learning outcome; không thể kết luận rằng model đạt điểm cao sẽ giúp học sinh học tốt hơn.
- Benchmark không bao phủ đầy đủ safety; dự án vẫn cần policy lỗi nghiêm trọng riêng.
- Dữ liệu hội thoại không quá dài; chưa đủ bằng chứng cho tutoring dài hạn.
- Quy trình reward model phức tạp hơn nhu cầu PoC hiện tại; dự án có thể học nguyên tắc, không nhất thiết triển khai reward model ngay.

Vị trí nguồn chính: Limitations; Ethics Statement.

## 9. Candidate claims cho evidence matrix

| Claim candidate | Nhãn | Vị trí nguồn | Ghi chú chuyển giao |
|---|---|---|---|
| Cần tách năng lực giải bài khỏi năng lực gia sư. | bằng chứng | Section 1; Section 6.1; Table 4 | Rất phù hợp cho P04. |
| Benchmark gia sư nên có task chẩn đoán lỗi/học sinh hiểu sai. | bằng chứng | Section 4.1; Table 1 | Chuyển sang lỗi thuật toán/code cần HNMU xác nhận. |
| Scaffolding/không đưa đáp án ngay là tiêu chí sư phạm quan trọng. | bằng chứng | Section 3.2; Section 4.3; Figure 7 | Cần gắn với từng task, tránh áp dụng máy móc khi học sinh cần đáp án trực tiếp. |
| Hội thoại dài làm năng lực gia sư khó hơn. | bằng chứng | Section 6.1 | Có ích cho metadata số bước/lượt. |
| Safety nên tách thành policy riêng vì MathTutorBench chưa bao phủ. | suy luận | Limitations | Phù hợp với hướng serious error policy của dự án. |

## 10. Câu hỏi mở

1. Với Tin học 9, “mistake location” nên áp dụng cho code, thuật toán, khái niệm hay cả ba?
2. Có task nào học sinh cần được trả lời trực tiếp thay vì luôn Socratic/gợi mở không?
3. Rubric rút gọn nên giữ scaffolding như một tiêu chí riêng hay gộp vào “chất lượng hỗ trợ sư phạm”? 
