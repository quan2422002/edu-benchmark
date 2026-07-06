# Plan 03 — Chọn lọc và đọc paper có mục tiêu cho Bloom/task/rubric gia sư

Trạng thái: `APPROVED_STEP_4A_DONE` — Bước 1, Bước 2A và synthesis Bước 4A cho 3 paper tier A đã hoàn thành; P03 chưa đóng vì có thể đọc thêm paper sau  
Experiment: `20260705_215045`  
Owner chính: `research-methodologist`  
Có thể chạy độc lập: Có, không phụ thuộc SGK/SGV taxonomy.  
Ưu tiên hiện tại: Cao — người phụ trách dự án muốn ưu tiên P03 trước.

## 1. Mục tiêu

Đọc có mục tiêu các paper đã có trong `document/paper/source_paper/` để xây dựng nền bằng chứng cho thiết kế task theo Bloom, rubric rút gọn và quy trình tạo benchmark gia sư LLM. Plan này không làm literature review rộng; trọng tâm là các paper có liên quan trực tiếp hoặc gián tiếp mạnh tới:

1. đánh giá năng lực gia sư của LLM;
2. thiết kế benchmark giáo dục/K-12;
3. phân tầng độ khó/Bloom hoặc năng lực nhận thức;
4. thiết kế rubric, vai trò chuyên gia con người và độ tin cậy chấm;
5. bối cảnh tiếng Việt hoặc benchmark tiếng Việt, nếu có giá trị chuyển giao.

Tinh thần triển khai: **chọn lọc paper trước, tóm tắt chi tiết từng paper sau, rồi mới tổng hợp thành ma trận bằng chứng và báo cáo tổng quát**. Cách này giúp kiểm soát từng nguồn riêng lẻ trước khi đưa ra kết luận thiết kế.

## 2. Câu hỏi review

1. Các benchmark gia sư LLM hiện tại chia task hoặc năng lực gia sư như thế nào?
2. Các paper giáo dục/K-12 hoặc benchmark theo năng lực nhận thức dùng Bloom/độ khó ra sao?
3. Rubric trong các benchmark liên quan thường có bao nhiêu tiêu chí, tiêu chí nào quan sát được trực tiếp từ phản hồi/hội thoại?
4. Vai trò của chuyên gia con người trong authoring, review, adjudication và validation được tổ chức thế nào?
5. Các paper đo hoặc kiểm soát độ phủ kiến thức, độ khó và đa dạng định dạng như thế nào?
6. Kết luận nào có thể chuyển sang benchmark gia sư LLM môn Tin học lớp 9 Việt Nam, và kết luận nào chỉ nên coi là suy luận cần giáo sư/HNMU xác nhận?

## 3. Nguồn paper local và hướng chọn lọc ban đầu

Nguồn paper local hiện nằm trong:

```text
document/paper/source_paper/
```

Danh sách ứng viên ban đầu, dựa trên metadata và trang đầu PDF:

| Mức ưu tiên | File | Tên paper | Lý do đưa vào/giữ lại |
|---|---|---|---|
| A — đọc chính | `2502.18940v2.pdf` | MathTutorBench: A Benchmark for Measuring Open-ended Pedagogical Capabilities of LLM Tutors | Liên quan trực tiếp nhất tới gia sư LLM, task mở, năng lực sư phạm và rubric. |
| A — đọc chính | `18426-AAAI26.ShiW-NLP.pdf` | From Solver to Tutor: Evaluating the Pedagogical Intelligence of LLMs with KMP-Bench | Trọng tâm “từ người giải bài sang gia sư”, đánh giá năng lực sư phạm, rất gần với hướng dự án. |
| A — đọc chính | `2510.02663v1.pdf` | TutorBench: A Benchmark To Assess Tutoring Capabilities Of Large Language Models | Có các năng lực như giải thích thích ứng, phản hồi bài làm, gợi ý học tập; hữu ích cho task/rubric. |
| A — đọc chính nếu đủ thời gian | `2026.acl-long.1371.pdf` | LongTutor: Benchmarking Large Language Models for Long-term Personalized Tutoring | Hữu ích cho lịch sử hội thoại, cá nhân hóa dài hạn, và bối cảnh nhiều bước/lượt. |
| B — đọc hỗ trợ | `12310-AAAI26.YeY-NLP.pdf` | K-12EduBench: A Benchmark for Evaluating Large Language Models’ Knowledge, Problem-Solving, and Educational Goal Cognition in K-12 Education | Liên quan K-12, mục tiêu giáo dục và năng lực giải quyết vấn đề; hỗ trợ phần coverage/độ khó giáo dục phổ thông. |
| B — đọc hỗ trợ | `2512.14554v5.pdf` | VLegal-Bench: Cognitively Grounded Benchmark for Vietnamese Legal Reasoning of Large Language Models | Không phải giáo dục/gia sư, nhưng có giá trị về benchmark tiếng Việt và phân tầng nhận thức/Bloom trong domain Việt Nam. |
| C — sàng lọc, có thể defer | `2025.acl-long.563.pdf` | VMLU Benchmarks: A comprehensive benchmark toolkit for Vietnamese LLMs | Hữu ích cho bối cảnh benchmark tiếng Việt, nhưng có thể ít liên quan trực tiếp tới gia sư/Bloom; chỉ giữ nếu có phần phương pháp đáng dùng. |

Lưu ý: bảng trên là **đề xuất ưu tiên ban đầu**, không phải kết luận cuối. Khi triển khai, vẫn phải tạo `paper_selection_registry.csv` và ghi rõ quyết định include/defer/exclude cho từng paper.

## 4. Không làm trong plan này

- Không thiết kế taxonomy task cuối cùng.
- Không tạo rubric cuối cùng.
- Không xử lý SGK/SGV hoặc chuẩn hóa chủ đề học liệu.
- Không tạo ví dụ phiếu tác giả.
- Không mở rộng tìm paper trên internet nếu chưa được người phụ trách dự án duyệt riêng.
- Không sửa evidence matrix cũ nếu đã commit; tạo matrix mới trong experiment này.
- Không kết luận thay giáo sư/HNMU về tính phù hợp sư phạm của rubric/task.

## 5. Quy trình triển khai

### 5.1. Bước 0 — Chốt review protocol

Giữ file `literature_notes/review_protocol.md`, nhưng viết lại theo phạm vi P03 mới:

- câu hỏi review;
- tiêu chí chọn/loại paper;
- stopping rule;
- quy tắc phân biệt `evidence`, `inference`, `open_question`;
- quy tắc gắn vị trí bằng chứng: section/page/table/figure;
- quy tắc không đánh đồng preprint và peer-reviewed paper.

### 5.2. Bước 1 — Sàng lọc paper local

Tạo registry cho toàn bộ PDF trong `document/paper/source_paper/`. Mỗi paper cần có:

- mã paper nội bộ;
- tên file;
- tên paper;
- năm;
- venue/arXiv nếu có;
- publication status;
- mức ưu tiên;
- quyết định: `include`, `defer`, hoặc `exclude`;
- lý do quyết định.

Kết quả của bước này giúp sau này nhìn lại biết vì sao một paper được dùng hoặc không được dùng.

### 5.3. Bước 2 — Tóm tắt chi tiết từng paper được chọn

Mỗi paper được chọn cần có một file `.md` riêng trong `literature_notes/paper_summaries/`. Không viết thẳng vào synthesis tổng quát trước khi có tóm tắt từng paper.

Mỗi file tóm tắt nên có cấu trúc tối thiểu:

1. Thông tin nguồn: title, authors, year, venue/arXiv, file path.
2. Vấn đề paper giải quyết.
3. Benchmark/dataset/task mà paper xây dựng hoặc dùng.
4. Cách paper định nghĩa năng lực, độ khó, Bloom hoặc hành vi gia sư.
5. Rubric/metric và cách chấm.
6. Vai trò chuyên gia con người.
7. Bằng chứng về độ tin cậy hoặc validation.
8. Điểm có thể chuyển sang dự án Tin học 9.
9. Giới hạn khi chuyển sang bối cảnh Việt Nam, THCS, môn Tin học.
10. Các claim candidate để đưa vào evidence matrix.

### 5.4. Bước 3 — Tạo ma trận bằng chứng

Sau khi có tóm tắt chi tiết từng paper, mới tạo `literature_notes/evidence_to_design_matrix.csv`. Matrix này không chỉ là bibliography; mỗi dòng phải nối một claim thiết kế với nguồn cụ thể.

Ví dụ claim thiết kế:

- Vì sao task theo Bloom là hợp lý.
- Vì sao cần tách năng lực gia sư khỏi năng lực giải bài.
- Vì sao rubric nên rút gọn và quan sát được.
- Vì sao cần vai trò expert teacher trong authoring/review.
- Vì sao cần đo coverage/độ khó/đa dạng định dạng.

### 5.5. Bước 4 — Viết tổng hợp cho thiết kế P04

Chỉ sau khi có per-paper summaries và evidence matrix, viết `reports/P03-literature-synthesis-for-design.md`. Báo cáo này phải trả lời ngắn gọn:

- P04 nên kế thừa gì từ paper nào;
- điểm nào có evidence trực tiếp;
- điểm nào chỉ là suy luận có kiểm soát;
- điểm nào cần giáo sư/HNMU xác nhận.

## 6. Output sở hữu

Plan này chỉ ghi vào:

```text
experiments/20260705_215045/literature_notes/
experiments/20260705_215045/literature_notes/paper_summaries/
experiments/20260705_215045/reports/P03-*.md
experiments/20260705_215045/handoffs/P03-*.md
```

Artifact dự kiến:

| File/thư mục | Vai trò | Lý do tạo |
|---|---|---|
| `literature_notes/review_protocol.md` | Quy tắc đọc, sàng lọc và dừng review. | Giữ review có kiểm soát, không lan man thành literature review rộng. |
| `literature_notes/paper_selection_registry.csv` | Registry toàn bộ PDF local và quyết định include/defer/exclude. | Giúp audit vì sao paper nào được dùng hoặc không dùng. |
| `literature_notes/paper_summaries/` | Thư mục chứa tóm tắt chi tiết từng paper. | Tránh evidence matrix bị thành hộp đen; mỗi paper có hồ sơ riêng để kiểm tra. |
| `literature_notes/paper_summaries/<paper_id>.md` | Một file tóm tắt chi tiết cho một paper được chọn. | P04 có thể đọc nhanh từng nguồn mà không phải mở PDF ngay. |
| `literature_notes/evidence_to_design_matrix.csv` | Ma trận claim thiết kế → paper/source → mức bằng chứng → giới hạn. | Là đầu vào chính cho P04 khi thiết kế task/rubric. |
| `literature_notes/evidence_gap_and_transfer_limits.md` | Tổng hợp khoảng trống và giới hạn chuyển giao. | Ngăn việc lấy paper Toán/Luật/K-12 nước ngoài áp thẳng sang Tin học 9 Việt Nam. |
| `reports/P03-literature-synthesis-for-design.md` | Bản tổng hợp bằng tiếng Việt cho người phụ trách/giáo sư. | Dùng để ra quyết định thiết kế mà không phải đọc toàn bộ note chi tiết. |
| `handoffs/P03-*.md` | Bàn giao khi hoàn thành P03. | Ghi rõ artifact, uncertainty và câu hỏi cần người quyết định. |

## 7. Acceptance criteria

- Có `review_protocol.md` trước khi viết kết luận.
- Có registry cho toàn bộ PDF trong `document/paper/source_paper/`.
- Mỗi paper được `include` có một file tóm tắt `.md` riêng.
- Mỗi claim thiết kế quan trọng trong synthesis có dòng tương ứng trong `evidence_to_design_matrix.csv` hoặc được gắn nhãn `inference/open_question`.
- Không đánh đồng preprint và peer-reviewed paper nếu publication status khác nhau.
- Có phân biệt bằng chứng trực tiếp về gia sư LLM và bằng chứng suy luận từ benchmark giáo dục/domain khác.
- Output đủ để P04 dùng mà không cần đọc lại toàn bộ PDF ngay, nhưng vẫn có đường dẫn nguồn để kiểm tra.

## 8. Validation

- Chạy `agents/research-methodologist/scripts/validate_evidence_matrix.py` nếu tạo evidence matrix theo schema.
- Kiểm tra mọi row có source ID, title, URL/file path, evidence note và evidence location.
- Kiểm tra mỗi paper `include` trong registry có file tóm tắt tương ứng.
- Kiểm tra mỗi claim trong synthesis có evidence ID hoặc nhãn `inference/open_question`.
- Chạy `pytest tests/agents -q` sau khi tạo artifact nếu có thay đổi ảnh hưởng tài liệu/validator.

## 9. Handoff

Handoff phải chỉ rõ:

- paper nào được include, defer, exclude và lý do;
- task/rubric nào có evidence mạnh;
- task/rubric nào chỉ có evidence gián tiếp;
- điểm nào cần hỏi giáo sư/HNMU;
- P04 nên đọc file nào trước.

## 10. Trạng thái triển khai

- 05/07/2026: Người phụ trách yêu cầu ưu tiên P03 và làm từng bước.
- 05/07/2026: Bước 1 — Sàng lọc paper local đã hoàn thành. Artifact chính: `literature_notes/paper_selection_registry.csv`; báo cáo đọc nhanh: `reports/P03-step1-paper-selection-summary.md`.
- Bước tiếp theo nên là Bước 0/2 kết hợp: tạo `review_protocol.md` rồi viết tóm tắt chi tiết cho các paper `include`, ưu tiên `P03-P001`, `P03-P002`, `P03-P003`.

- 06/07/2026: Bước 2A — Tóm tắt chi tiết 3 paper tier A đã hoàn thành. Artifact chính: `literature_notes/review_protocol.md`, `literature_notes/paper_summaries/P03-P001-mathtutorbench.md`, `literature_notes/paper_summaries/P03-P002-kmp-bench.md`, `literature_notes/paper_summaries/P03-P003-tutorbench.md`; báo cáo đọc nhanh: `reports/P03-step2A-three-A-paper-summaries.md`.

- 06/07/2026: Bước 3A/4A — Tạo `literature_notes/evidence_to_design_matrix.csv`, `literature_notes/evidence_matrix.csv` và viết `reports/P03-literature-synthesis-for-design.md` dựa trên 3 paper tier A. P03 chưa đóng; có thể mở rộng với paper khác sau.
- 06/07/2026: Revision Step 4A (`handoffs/P03-step4A-rubric-split-revision-009.md`) — Sau phản hồi của người phụ trách, cập nhật đề xuất rubric trong `reports/P03-literature-synthesis-for-design.md`: tách R4 cũ thành R4 tuân thủ mục tiêu/phạm vi/ràng buộc task và R5 tuân thủ ranh giới an toàn/đạo đức/pháp lý/không định kiến; giữ mã lỗi nghiêm trọng là policy riêng có mapping sang R1–R5.
- 06/07/2026: Revision Step 4A (`handoffs/P03-step4A-task-bloom-separation-revision-010.md`) — Sau phản hồi của người phụ trách, cập nhật đề xuất task trong `reports/P03-literature-synthesis-for-design.md`: `task` dựa trên hành vi gia sư; Bloom chuyển thành cột/metadata `Mức độ nhận thức`.
