# P02 — Literature review PoC

## Trạng thái

- Status: `DRAFT_FOR_REVIEW`
- Priority: urgent
- Dependency: P01 `research-methodologist`
- Downstream: P04 teacher packet, P05 benchmark specification
- Research owner: `research-methodologist`
- Human reviewers: project lead và ít nhất một expert teacher khi đánh giá hàm ý sư phạm

## 1. Mục tiêu

Thực hiện rapid evidence review đủ rộng và có thể kiểm tra lại trước khi đề xuất taxonomy, benchmark task hoặc rubric. Kết quả phải cho biết:

- năng lực nào của LLM tutor đã được đánh giá trong literature;
- benchmark hiện có dùng task, dữ liệu, rubric và metric gì;
- expert teachers tham gia ở bước nào và theo quy trình nào;
- hạn chế của automatic metrics và LLM-as-a-judge;
- khoảng trống cho Tin học lớp 9 bằng tiếng Việt;
- điểm nào là bằng chứng, điểm nào chỉ là giả thuyết cần giáo viên xác nhận.

## 2. Câu hỏi review

1. Literature định nghĩa “tutoring quality” và pedagogical capability như thế nào?
2. Những task families nào được dùng để đánh giá giải thích thích ứng, chẩn đoán lỗi, feedback, hinting và multi-turn tutoring?
3. Với computer science/programming education, lỗi và misconception của học sinh được mô hình hóa ra sao?
4. Human experts tham gia authoring, review, annotation, adjudication và validation như thế nào?
5. Rubric/metric nào có evidence về reliability hoặc agreement với con người?
6. Các benchmark xử lý answer leakage, academic integrity, contamination và model/judge bias như thế nào?
7. Có nghiên cứu nào liên quan tới học sinh THCS, giáo dục Việt Nam hoặc ngôn ngữ tài nguyên thấp?

## 3. Phạm vi tìm kiếm

### Nhóm chủ đề

- LLM/AI tutor evaluation và tutoring benchmark;
- pedagogical capability, scaffolding, Socratic tutoring, adaptive explanation;
- feedback, misconception diagnosis và student modeling;
- programming/computer-science education và automated feedback;
- human annotation, rubric design, inter-rater reliability;
- LLM-as-a-judge cho open-ended educational responses;
- multilingual/Vietnamese educational NLP khi có liên quan.

### Nguồn ưu tiên

- ACL Anthology;
- arXiv;
- ACM Digital Library;
- IEEE Xplore;
- ERIC;
- Semantic Scholar/OpenAlex để discovery và citation chaining;
- trang proceedings hoặc publisher chính thức khi xác minh metadata.

Google Scholar chỉ dùng để discovery khi cần; mọi claim cuối phải trỏ tới paper/proceedings/publisher có thể truy cập hoặc metadata xác minh được.

## 4. Search strategy

Tạo nhóm truy vấn, ví dụ:

```text
("large language model" OR LLM) AND (tutor OR tutoring) AND
(benchmark OR evaluation OR rubric)

(LLM OR "generative AI") AND (programming education OR computer science education) AND
(feedback OR misconception OR debugging)

(AI tutor OR intelligent tutoring system) AND
(human evaluation OR teacher annotation OR inter-rater reliability)

(LLM-as-a-judge OR automatic evaluation) AND
(education OR tutoring) AND (rubric OR reliability)
```

Agent phải lưu nguyên truy vấn, nguồn tìm kiếm, ngày tìm, số kết quả và cách chọn. Thực hiện lần theo trích dẫn ngược/xuôi từ các bài báo hạt giống.

Bài báo hạt giống phải được lập độc lập từ câu hỏi rà soát, truy vấn tìm kiếm, nguồn gợi ý của giáo sư/HNMU nếu có, và lần theo trích dẫn từ các nguồn đủ liên quan. Không dùng F01 làm nguồn hạt giống chính vì F01 là sản phẩm làm gấp, có nguy cơ khóa rà soát vào các giả định ban đầu. F01 chỉ được dùng như danh sách đối chiếu sau khi đã có danh mục hạt giống độc lập: nếu F01 có bài báo/ý nào xuất hiện lại, ghi rõ vì sao được giữ; nếu không, ghi là sản phẩm lịch sử hoặc câu hỏi mở.

## 5. Inclusion và exclusion

### Include

- paper mô tả benchmark/dataset/evaluation cho AI/LLM tutor;
- paper về pedagogical quality có task/rubric/metric cụ thể;
- paper computer-science education có learner error, feedback hoặc tutoring interaction;
- paper phương pháp đánh giá human/LLM judge liên quan trực tiếp;
- nguồn có đủ phương pháp để trích evidence.

### Exclude hoặc tách nền

- opinion/blog không có phương pháp nghiên cứu;
- chỉ đo factual QA mà không có tutoring behavior;
- paper chỉ xây tutor nhưng không đánh giá pedagogical behavior;
- nguồn trùng phiên bản, giữ bản mới/peer-reviewed phù hợp nhất;
- claim không thể truy vết tới nguồn gốc.

## 6. Mức độ review

### Rapid review cho deadline 21/06/2026

- discovery tối thiểu 30 candidate records;
- screen title/abstract toàn bộ candidate;
- đọc sâu tối thiểu 12–20 nguồn cốt lõi, tùy mức liên quan và thời gian truy cập;
- bao phủ ít nhất bốn cụm: tutoring benchmark, learning science/pedagogy, CS education, evaluation reliability;
- tạo kết luận sơ bộ và danh sách uncertainty.

### Full review sau PoC

- mở rộng database/search string;
- double-screen một subset;
- quality appraisal;
- cập nhật review theo protocol có version;
- dùng full review để khóa benchmark specification.

Không dùng con số nguồn như thước đo duy nhất. Coverage và traceability quan trọng hơn việc gom thật nhiều citation.

## 7. Evidence matrix

Mỗi nguồn tối thiểu có:

```text
record_id
title
year
venue
url_or_doi
study_type
education_domain
learner_level
tutoring_capabilities
task_or_dataset
human_expert_role
rubric_or_metric
reliability_evidence
main_findings
limitations
relevance_to_project
evidence_quote_or_location
reviewer_notes
```

`evidence_quote_or_location` lưu section/page/table để kiểm tra lại, không sao chép đoạn dài vào report.

## 8. Deliverables

Trong experiment con của P02:

```text
literature/
├── search_protocol.md
├── search_log.csv
├── screening_log.csv
├── evidence_matrix.csv
├── bibliography.bib
├── rapid_review.md
├── research_gaps.md
└── teacher_relevant_findings.md
```

`teacher_relevant_findings.md` phải viết bằng ngôn ngữ rõ ràng, chỉ nêu findings ảnh hưởng tới việc giáo viên author/review dữ liệu.

## 9. Quality controls

- Mọi claim trong synthesis có citation hoặc được gắn `inference`/`open question`.
- Deduplicate theo DOI/title.
- Ít nhất 20% included sources được orchestrator kiểm tra lại extraction.
- Expert teacher review các kết luận về tính phù hợp sư phạm; họ không phải review search code.
- Ghi rõ publication status (peer-reviewed/preprint).
- Không suy rộng từ Toán/THPT sang Tin học lớp 9 mà không ghi limitation.
- Không dùng ranking model từ một benchmark để kết luận learning outcome.

## 10. Acceptance criteria

- Search protocol và log đủ để người khác chạy lại.
- Evidence matrix không có record thiếu source URL/DOI và relevance note.
- Rapid review bao phủ đủ bốn cụm chủ đề.
- Mỗi đề xuất benchmark requirement có ít nhất một source hoặc được đánh dấu hypothesis.
- Có phần riêng về human expert roles và reliability.
- Có phần riêng về evidence gap cho Tin học lớp 9 tiếng Việt.
- Project lead kiểm tra extraction sample; expert teacher xác nhận/ phản biện teacher-relevant findings.
- Không sửa taxonomy chính thức hoặc schema dataset trong P02.

## 11. Test/validation

Chạy validator từ P01 để kiểm tra:

- required columns;
- URL/DOI presence;
- duplicate records;
- allowed evidence labels;
- claims không có source marker trong review draft.

Thực hiện một audit thủ công: chọn ngẫu nhiên ít nhất ba claim và lần ngược từ report → matrix → paper location.

## 12. Handoff

- P03 nhận phần human roles và workflow evidence.
- P04 nhận teacher-relevant findings và provisional task implications.
- P05 chỉ bắt đầu khi rapid review được đánh dấu `reviewed`; taxonomy vẫn là provisional cho tới full review.

## 13. Quyết định duyệt

- `APPROVE P02` sau khi P01 hoàn thành;
- sửa review questions/search scope;
- yêu cầu full systematic review trước mọi teacher packet (đổi deadline/scope tương ứng).
