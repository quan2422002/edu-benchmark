# P03 Review protocol — đọc paper có mục tiêu cho Bloom/task/rubric gia sư

Ngày tạo: 06/07/2026
Experiment: `20260705_215045`
Trạng thái: `active_for_P03_step2A`
Phạm vi hiện tại: đọc 3 paper có `priority_tier = A` trong `paper_selection_registry.csv`.

## 1. Mục tiêu review

Review này không nhằm tổng quan toàn bộ lĩnh vực. Mục tiêu là rút bằng chứng có kiểm soát để hỗ trợ thiết kế benchmark gia sư LLM môn Tin học lớp 9 Việt Nam, đặc biệt là:

1. phân tách năng lực giải bài/kiến thức khỏi năng lực gia sư;
2. xác định các kiểu task gia sư nên có;
3. hiểu cách các benchmark hiện có dùng rubric, tiêu chí chấm và chuyên gia con người;
4. xác định giới hạn khi chuyển giao từ Toán/STEM/K-8/high-school sang Tin học THCS Việt Nam;
5. chuẩn bị input cho `evidence_to_design_matrix.csv` ở bước sau.

## 2. Nguồn và stopping rule

Nguồn chỉ gồm PDF local trong `document/paper/source_paper/`. Không mở rộng tìm kiếm web trong bước này.

Bước 2A dừng khi có tóm tắt chi tiết cho 3 paper tier A:

- `P03-P001`: MathTutorBench.
- `P03-P002`: KMP-Bench.
- `P03-P003`: TutorBench.

Các paper `A-`, `B+`, `B`, `C` chưa đọc sâu trong bước này.

## 3. Câu hỏi trích xuất

Mỗi paper được đọc theo cùng bộ câu hỏi:

1. Paper giải quyết vấn đề gì trong đánh giá gia sư LLM?
2. Benchmark/dataset/task được thiết kế như thế nào?
3. Paper định nghĩa năng lực gia sư, độ khó, Bloom hoặc hành vi sư phạm ra sao?
4. Rubric/metric và cách chấm là gì?
5. Chuyên gia con người tham gia ở bước nào?
6. Có bằng chứng về độ tin cậy/validation không?
7. Điểm nào có thể dùng cho benchmark Tin học 9?
8. Điểm nào chỉ là suy luận hoặc câu hỏi mở cần giáo sư/HNMU xác nhận?

## 4. Quy tắc nhãn bằng chứng

### 4.1. Mục đích của nhãn

Các nhãn này dùng để tránh trộn lẫn ba loại nhận định khác nhau khi đọc paper:

1. điều paper thật sự nói;
2. điều ta suy ra cho dự án Tin học 9;
3. điều vẫn cần giáo sư/HNMU hoặc review bổ sung xác nhận.

Nếu không tách ba loại này, rất dễ xảy ra lỗi “paper nói A trong bối cảnh Toán/STEM, nhưng ta vô thức biến thành kết luận chắc chắn cho Tin học 9 Việt Nam”.

### 4.2. Ý nghĩa từng nhãn

| Nhãn | Nghĩa | Khi nào dùng | Ví dụ trong P03 |
|---|---|---|---|
| `bằng chứng` | Paper nêu trực tiếp ý này, có thể trỏ tới section/table/figure. | Dùng khi câu viết là kết quả, mô tả phương pháp, hoặc giới hạn được paper nói rõ. | “TutorBench dùng rubric riêng cho từng sample, do human experts viết” — có thể trỏ tới Section 2.3 và Appendix A.1. |
| `suy luận` | Ta rút ra hệ quả hợp lý cho dự án, nhưng paper không nói trực tiếp về Tin học 9/HNMU. | Dùng khi chuyển ý từ paper sang thiết kế benchmark của dự án. | “Phiếu tác giả của HNMU nên buộc giáo viên ghi rõ tiêu chí quan sát được” là suy luận từ TutorBench, không phải paper nói về HNMU. |
| `câu hỏi mở` | Chưa đủ căn cứ để quyết; cần hỏi giáo sư/HNMU, đọc thêm paper, hoặc chờ dữ liệu pilot. | Dùng khi có nhiều phương án thiết kế đều có thể hợp lý. | “Lỗi nghiêm trọng nên là rubric riêng, trọng số âm, hay policy tách riêng?” |

### 4.3. Dùng ở đâu?

Các nhãn này được dùng ở ba lớp artifact:

1. Trong từng file tóm tắt paper: phần `Candidate claims cho evidence matrix` có cột `Nhãn` để đánh dấu claim là `bằng chứng`, `suy luận`, hay `câu hỏi mở`.
2. Trong `evidence_to_design_matrix.csv` ở bước sau: nên có cột `support_label` hoặc `claim_label` với ba giá trị trên, để P04 biết claim nào đủ chắc để dùng làm nền thiết kế, claim nào chỉ là suy luận.
3. Trong synthesis cuối P03: các kết luận gửi sang P04 phải nói rõ đâu là kết luận được paper hỗ trợ trực tiếp, đâu là đề xuất của nhóm, đâu là quyết định cần hỏi giáo sư/HNMU.

Lưu ý kỹ thuật: validator hiện tại của `agents/research-methodologist/scripts/validate_evidence_matrix.py` kiểm tra schema study-level và chưa bắt buộc cột nhãn claim-level. Nếu tạo một matrix theo đúng schema validator đó, ghi nhãn này trong cột `reviewer_notes`. Nếu tạo `evidence_to_design_matrix.csv` dạng claim-level cho P04, thêm cột riêng `support_label` để đọc dễ hơn.

### 4.4. Dùng như thế nào khi viết summary?

Khi viết một nhận định, làm theo thứ tự sau:

1. Hỏi: “Paper có nói trực tiếp điều này không?” Nếu có, gắn `bằng chứng` và ghi vị trí nguồn.
2. Nếu paper không nói trực tiếp nhưng ta thấy có ích cho dự án, gắn `suy luận` và nói rõ bước chuyển từ paper sang dự án.
3. Nếu nhận định ảnh hưởng tới thiết kế task/rubric nhưng chưa đủ chắc, gắn `câu hỏi mở` và ghi người cần quyết định.

Không được biến benchmark chất lượng phản hồi thành bằng chứng về kết quả học tập nếu paper không đo kết quả học tập. Ví dụ: nếu paper chỉ cho thấy model đạt điểm cao hơn trên rubric phản hồi, ta chỉ được nói model phản hồi tốt hơn theo rubric đó; không được kết luận học sinh sẽ học tốt hơn.

## 5. Quy tắc vị trí nguồn

Ưu tiên ghi vị trí theo `Section`, `Table`, `Figure`, `Appendix`. Nếu một ý được rút từ nhiều đoạn, ghi nhiều vị trí. Không cần trích nguyên văn dài; tóm tắt bằng diễn giải tiếng Việt.

## 6. Output của bước này

- `literature_notes/paper_summaries/P03-P001-mathtutorbench.md`
- `literature_notes/paper_summaries/P03-P002-kmp-bench.md`
- `literature_notes/paper_summaries/P03-P003-tutorbench.md`
- `reports/P03-step2A-three-A-paper-summaries.md`

Bước này chưa tạo `evidence_to_design_matrix.csv`; matrix sẽ được tạo ở bước sau sau khi người phụ trách kiểm tra summaries.
