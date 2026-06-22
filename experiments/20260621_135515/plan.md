# F01 — Fast-track evidence-backed benchmark framework and teacher handoff

## Trạng thái

- Status: `APPROVED`
- Approved at: `2026-06-21`
- Priority: emergency handoff
- Branch: `feature/C01_P02_P03`
- Base commit: `408405b` — P01 completed
- Dependencies: P01 completed; C01 grounding package available
- Research owner: `research-methodologist`
- Teacher-workflow owner: `teacher-collaboration-designer`
- Domain authority: project lead and expert teachers

Project lead approved implementation on 2026-06-21.

## Điều chỉnh được yêu cầu sau vòng bàn giao đầu tiên

Ngày 21/06/2026, project lead yêu cầu bổ sung ba điều kiện nghiệm thu:

1. tài liệu bàn giao cho giáo viên phải dùng tiếng Việt làm ngôn ngữ chính;
   thuật ngữ hoặc mã tiếng Anh bắt buộc phải có giải thích tiếng Việt;
2. hai tài liệu chương trình bắt buộc phải được lưu trực tiếp trong F01, kèm
   URL gốc, hash và vị trí tham chiếu;
3. mọi mẫu trong `teacher_packet/examples.md` phải ánh xạ trực tiếp tới các mã
   trường trong trang tính dữ liệu đầu vào/đầu ra của workbook khung.

Tên các trang tính hiển thị được Việt hóa:

- `Nhiem_vu`;
- `Du_lieu_vao_ra`;
- `Tieu_chi_cham`;
- `Vai_tro_giao_vien`;
- `Tham_chieu`;
- `Tom_tat_nhiem_vu`;
- `Phieu_tac_gia`;
- `Phieu_tham_dinh`;
- `Hieu_chuan`;
- `Cau_hoi_mo`.

Mã trường kỹ thuật như `student_prompt` và `tutor_response` được giữ nguyên
để bảo đảm khả năng đối chiếu, nhưng luôn đi kèm tên tiếng Việt.

## 1. Quyết định kiến trúc

F01 là một plan fast-track duy nhất, tích hợp phần tối thiểu cần thiết của:

- P02: literature review có truy vết;
- P03: vai trò và quy trình giáo viên;
- P04: tài liệu bàn giao và mẫu minh họa;
- P05: khung task/rubric ứng viên.

F01 không đánh dấu P02–P05 là đã hoàn thành và không sửa các plan gốc. Sản phẩm được gọi là:

> **Khung benchmark ứng viên có căn cứ, sẵn sàng để expert teachers review.**

Không gọi sản phẩm là `benchmark v1`, `validated benchmark` hoặc benchmark chính thức nếu chưa qua teacher review và pilot.

## 2. Mục tiêu bàn giao

Tạo một gói thống nhất trả lời rõ:

1. Benchmark ứng viên gồm những task nào?
2. Mỗi task đánh giá năng lực tutoring nào?
3. Input của task gồm trường gì, kiểu dữ liệu gì và trường nào tùy chọn?
4. Model phải tạo output gì?
5. Rubric chấm từng task gồm tiêu chí nào và dùng thang điểm nào?
6. Tiêu chí nào dựa trên curriculum, literature hoặc teacher judgment?
7. Giáo viên tham gia task với vai trò gì và có quyền quyết định gì?
8. Mẫu minh họa nào giúp giáo viên hình dung input, output và rubric?

Gói phải đọc được theo hai hướng:

- machine-readable artifacts cho engineering;
- một file DOCX tiếng Việt giải thích đầy đủ cho giáo viên và project stakeholders.

## 3. Nguồn bằng chứng và thứ bậc thẩm quyền

### 3.1. Nguồn chương trình bắt buộc

1. Chương trình GDPT môn Tin học ban hành kèm Thông tư 32/2018/TT-BGDĐT.
2. Tài liệu tìm hiểu Chương trình môn Tin học, Bộ GDĐT và Trường ĐHSP Hà Nội, 2019.

Hai specialist bắt buộc xem xét cả hai nguồn.

Quy tắc:

- nguồn chương trình chuẩn tắc xác định **học sinh lớp 9 cần biết/làm được gì**;
- tài liệu bồi dưỡng hỗ trợ diễn giải nhưng không ghi đè nguồn chuẩn tắc;
- mọi mapping phải có trang, mục/bảng và location note cụ thể.

### 3.2. Nguồn nội bộ

- `document/teacher_training_curriculum/Benchmark Tin học THCS.xlsx`;
- C01: `experiments/20260621_052024/**`;
- prototype cũ trong `experiments/20260618_150902/`.

Các nguồn này chỉ cung cấp field, ví dụ và giả thuyết thiết kế. Chúng không phải ground truth và không thay literature hoặc teacher judgment.

### 3.3. Literature

Literature xác định:

- tutoring capability nào đáng đánh giá;
- task format nào đã được sử dụng;
- rubric/metric nào có cơ sở;
- human expert tham gia như thế nào;
- giới hạn của automatic metric và LLM-as-a-judge.

Curriculum trả lời **đánh giá tutoring trên nội dung nào**. Literature trả lời **đánh giá chất lượng tutoring theo cách nào**.

## 4. Câu hỏi literature review

1. Literature định nghĩa tutoring quality và pedagogical capability như thế nào?
2. Những task nào được dùng để đánh giá explanation, diagnosis, feedback, hinting, scaffolding và multi-turn tutoring?
3. Trong Computer Science/programming education, learner error, misconception, algorithm và code feedback được biểu diễn ra sao?
4. Input/output unit của các benchmark hiện có là gì?
5. Rubric dimensions và scoring scale nào được dùng?
6. Có evidence nào về inter-rater reliability, expert agreement hoặc rubric validation?
7. Expert teachers/educators tham gia authoring, review, annotation, calibration và adjudication như thế nào?
8. Automatic metrics và LLM-as-a-judge có failure mode nào trong educational evaluation?
9. Benchmark xử lý answer leakage, over-helping, safety, bias và learner agency như thế nào?
10. Có evidence nào liên quan THCS, tiếng Việt, low-resource language hoặc Informatics education?

## 5. Mức độ literature review

F01 thực hiện **rapid evidence review mở rộng**, không tuyên bố là full systematic review.

### 5.1. Cụm bằng chứng bắt buộc

1. LLM/AI tutoring benchmarks.
2. Pedagogical feedback, scaffolding, hinting và student-state diagnosis.
3. Computer Science/programming education, debugging và misconception.
4. Human rubric design, teacher annotation và inter-rater reliability.
5. Automatic evaluation, LLM-as-a-judge, bias và validity.
6. Multilingual, low-resource hoặc middle-school evidence khi có.

### 5.2. Coverage target

- discovery ít nhất 50 candidate records;
- title/abstract screening toàn bộ candidate;
- full-text extraction mục tiêu 20–30 nguồn cốt lõi;
- mỗi cụm 1–5 phải có ít nhất ba nguồn cốt lõi hoặc được ghi là evidence gap;
- cụm 6 không ép đủ số nếu literature thực sự thiếu;
- thực hiện backward/forward citation chaining từ các nguồn cốt lõi.

Con số không thay thế chất lượng. Stopping rule đạt khi:

- sáu cụm đã được tìm có hệ thống;
- hai vòng search/citation chaining liên tiếp không tạo thêm task family hoặc rubric dimension quan trọng;
- mọi khoảng trống còn lại được ghi rõ.

### 5.3. Phạm vi thời gian

- ưu tiên nghiên cứu 2018–2026;
- cho phép nguồn trước 2018 nếu là nền tảng trực tiếp về intelligent tutoring, feedback, rubric hoặc reliability;
- ngày chốt search: ngày F01 bắt đầu triển khai;
- mọi kết luận “mới nhất” phải được xác minh tại thời điểm search.

### 5.4. Nguồn tìm kiếm

- ACL Anthology;
- ACM Digital Library;
- IEEE Xplore;
- ERIC;
- arXiv;
- Semantic Scholar hoặc OpenAlex cho discovery/citation chaining;
- publisher/proceedings chính thức để xác minh metadata và full text.

Google Scholar chỉ dùng discovery nếu cần; claim cuối phải trỏ tới nguồn gốc kiểm tra được.

## 6. Search, screening và extraction

### 6.1. Search log

Mỗi lượt tìm ghi:

```text
search_id
database
searched_at
query
filters
result_count
notes
```

### 6.2. Screening log

Mỗi candidate ghi:

```text
candidate_id
title
year
url_or_doi
title_abstract_decision
full_text_decision
exclusion_reason
reviewer
```

Search log và screening log được lưu chung trong `literature/review_log.csv`.
Mỗi dòng có `record_type = search | screening` và chỉ điền các trường phù
hợp. Cách gộp này giảm số file nhưng vẫn giữ nguyên khả năng tái lập và audit.

### 6.3. Evidence matrix

Dùng schema chuẩn của `research-methodologist`, tối thiểu gồm:

```text
record_id
title
year
venue
url_or_doi
publication_status
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
evidence_location
reviewer_notes
```

Mỗi claim quan trọng phải truy tới section/page/table/figure. Không trích dài và không tự tạo citation.

### 6.4. Quality controls

- resolve duplicate và preprint/published version;
- ghi publication status;
- audit lại ít nhất 20% included records;
- audit ngược ít nhất năm claim: report → matrix → paper location;
- tách `evidence`, `inference` và `open_question`;
- ghi rõ hạn chế khi suy rộng từ Toán, đại học hoặc tiếng Anh sang Tin học lớp 9 tiếng Việt.

## 7. Cách hình thành benchmark task

Task chỉ được đưa vào core framework khi thỏa cả hai:

1. có curriculum reference phù hợp với Tin học lớp 9;
2. có literature support cho tutoring capability/task/rubric, hoặc được ghi rõ `provisional_low_evidence`.

Các task candidate ban đầu từ C01:

1. giải thích/làm rõ khái niệm;
2. hỗ trợ đánh giá thông tin hoặc hành vi số;
3. phản hồi lập luận của học sinh;
4. lập kế hoạch hoạt động/sản phẩm số;
5. review sản phẩm số hoặc kết quả mô phỏng;
6. hỗ trợ xây dựng thuật toán;
7. chẩn đoán và sửa thuật toán/chương trình;
8. hỗ trợ khám phá nghề nghiệp không định kiến.

Đây là candidate set, không phải kết luận. Literature review có thể:

- giữ nguyên;
- gộp task bị trùng capability;
- tách task có input/output hoặc rubric khác bản chất;
- chuyển task ít evidence sang appendix;
- loại task không phù hợp mục tiêu benchmark.

Mọi thay đổi phải có rationale và traceability.

## 8. Contract của mỗi benchmark task

Mỗi task trong sheet `Tasks` của `benchmark_framework.xlsx` và
`task_specification.md` phải có:

```text
task_id
task_name_vi
purpose
tutoring_capabilities
curriculum_reference_ids
research_reference_ids
evidence_status
interaction_mode
input_fields
input_data_types
output_contract
rubric_dimension_ids
critical_failures
teacher_roles
example_ids
known_limitations
```

### 8.1. Input

Fast-track framework chỉ chuẩn hóa các dạng:

- `student_prompt`: UTF-8 Vietnamese text, bắt buộc;
- `student_work`: tùy task; text, pseudocode, code snippet, step list, table-like text hoặc mô tả sản phẩm số;
- `conversation_history`: danh sách lượt `role + text` cho task multi-turn;
- `task_context`: mục tiêu học tập, giới hạn nhiệm vụ và curriculum reference IDs;
- `artifact_description`: mô tả chữ có cấu trúc khi chưa chuẩn hóa ảnh/file sản phẩm thật.

Ảnh, âm thanh, video và file phần mềm gốc nằm ngoài scope fast-track, trừ khi plan amendment định nghĩa storage, privacy và evaluation contract.

### 8.2. Output

Output chính của model:

- `tutor_response`: phản hồi tự nhiên bằng tiếng Việt;
- với multi-turn: phản hồi cho lượt hiện tại, không sinh toàn bộ hội thoại giả định;
- không yêu cầu hoặc lưu private chain-of-thought.

Annotation/evaluation output được lưu riêng:

```text
criterion_scores
critical_failure_flags
reviewer_decision
reviewer_rationale
```

## 9. Rubric framework

F01 ưu tiên analytic rubric thay vì một điểm chung duy nhất.

Các dimension candidate:

1. tính đúng chuyên môn;
2. phù hợp curriculum và lớp 9;
3. nhận diện đúng trạng thái/bài làm của học sinh;
4. chất lượng giải thích, feedback hoặc hint;
5. giữ learner agency, không đưa lời giải quá sớm;
6. rõ ràng, hành động được và phù hợp ngôn ngữ học sinh;
7. an toàn, đạo đức, không định kiến;
8. tiêu chí đặc thù của task.

Literature review phải xác nhận, gộp, tách hoặc loại từng dimension.

### 9.1. Thang điểm 0–5

F01 dùng thang đánh giá hiệu suất sáu mức `0–5`, có hình thức gần với
Likert nhưng không gọi là **Likert chuẩn**. Likert truyền thống thường đo mức
độ đồng ý với một phát biểu; thang này đo chất lượng quan sát được của phản
hồi tutoring.

| Điểm | Nhãn | Ý nghĩa chung |
|---:|---|---|
| 0 | Không thể chấp nhận | Sai nghiêm trọng, không thực hiện tiêu chí hoặc gây hại; thường đi kèm critical failure. |
| 1 | Rất yếu | Có dấu hiệu liên quan nhưng sai/thiếu phần lớn; cần viết lại gần như toàn bộ. |
| 2 | Yếu | Đạt một phần nhỏ; còn lỗi hoặc thiếu sót lớn làm giảm đáng kể giá trị tutoring. |
| 3 | Đạt tối thiểu | Đáp ứng phần cốt lõi nhưng còn điểm cần cải thiện; có thể sử dụng sau chỉnh sửa nhỏ hoặc review. |
| 4 | Tốt | Đúng, phù hợp và hữu ích; chỉ còn hạn chế nhỏ không ảnh hưởng mục tiêu chính. |
| 5 | Rất tốt | Thực hiện đầy đủ, chính xác, phù hợp và nhất quán; là mẫu mạnh cho tiêu chí đang xét. |
| N/A | Không áp dụng | Tiêu chí không phù hợp task/sample; không tính vào mẫu số. |

Các mô tả trên là anchor chung. Mỗi criterion phải có anchor riêng cho
`0`, `1`, `2`, `3`, `4`, `5`; không được chỉ sao chép nguyên mô tả chung.

Thang `0–5` là thang thứ bậc (`ordinal`). Không mặc định rằng khoảng cách từ
`1→2` bằng `4→5`, và không diễn giải điểm trung bình như đại lượng liên tục
nếu chưa có kiểm chứng.

### 9.2. Tổng hợp điểm

- Báo cáo vector điểm theo từng dimension là kết quả chính.
- Có thể báo cáo trung bình không trọng số trên các criterion áp dụng như
  summary phụ, nhưng phải kèm từng điểm thành phần.
- Không đặt trọng số hoặc ngưỡng pass/fail trong F01 nếu chưa có literature,
  teacher calibration và reliability evidence.
- `N/A` bị loại khỏi mẫu số, không được quy thành `0`.
- Critical failure không được bù bằng điểm cao ở tiêu chí khác. Một phản hồi
  có critical failure phải được flag và review riêng dù điểm trung bình cao.

### 9.3. Reliability và calibration

Trước khi dùng thang điểm để so sánh model:

1. ít nhất hai reviewer chấm chung một tập mẫu calibration;
2. ghi disagreement ở từng criterion;
3. sửa anchor bị hiểu khác nhau;
4. báo agreement/reliability phù hợp với dữ liệu thứ bậc;
5. không tuyên bố rubric ổn định nếu evidence reliability chưa đạt hoặc chưa
   được đo.

Critical failure tối thiểu cần xem xét:

- sai kiến thức trọng yếu;
- vượt ngoài phạm vi hoặc yêu cầu lớp 9;
- hướng dẫn không an toàn/phi đạo đức;
- định kiến hoặc xâm phạm quyền riêng tư;
- tiết lộ lời giải hoàn chỉnh khi task yêu cầu scaffolding;
- bỏ qua dữ kiện/bài làm cốt lõi của học sinh.

Mỗi rubric criterion phải có:

```text
criterion_id
criterion_name
description
score_0_anchor
score_1_anchor
score_2_anchor
score_3_anchor
score_4_anchor
score_5_anchor
applicable_task_ids
reference_ids
evidence_status
teacher_review_status
```

## 10. Vai trò của giáo viên

### Teacher Curriculum Validator

- xác nhận nội dung đúng chương trình và mức lớp 9;
- xác nhận chủ đề lựa chọn/prerequisite;
- không chấm chất lượng search protocol.

### Teacher Task Author

- đề xuất tình huống học sinh và bài làm thực tế;
- xác nhận nhiều cách trả lời hợp lệ;
- không tự phê duyệt sample của mình.

### Teacher Rubric Reviewer

- kiểm tra criterion quan sát/chấm được;
- kiểm tra score anchor không loại nhầm câu trả lời hợp lệ;
- tham gia calibration trên sample chung.

### Teacher Independent Reviewer

- review task/sample không do mình author;
- chọn `accept`, `revise` hoặc `reject` kèm lí do.

### Teacher Adjudicator

- xử lí bất đồng;
- ghi quyết định và rationale;
- chuyển research question về project lead khi không thể giải quyết bằng chuyên môn.

Mỗi benchmark task phải ghi rõ:

- vai trò giáo viên tham gia;
- input họ nhận;
- quyết định họ có quyền đưa ra;
- output họ bàn giao;
- người nhận tiếp theo.

## 11. Mẫu minh họa

F01 dùng 18 mẫu C01 làm seed, không mặc định giữ nguyên.

Quy trình:

1. map mỗi mẫu vào task framework mới;
2. nối `research_reference_ids` từ literature;
3. sửa criterion provisional khi có evidence;
4. giữ `teacher_judgment` nếu literature không quyết định được;
5. loại hoặc chuyển appendix nếu task bị gộp/loại;
6. không chuyển sample sang approved nếu chưa có teacher review.

Tài liệu DOCX phải có:

- ít nhất một mẫu hoàn chỉnh cho mỗi core task;
- cả mẫu tốt và mẫu có vấn đề;
- input, output minh họa, rubric và giải thích cách chấm;
- link/reference rõ tới curriculum và literature;
- appendix hoặc đường dẫn tới toàn bộ sample set.

## 12. Deliverables

Đầu ra được rút gọn thành ba tầng. Giáo viên chỉ cần đọc tầng 3; các file ở
tầng 1 và 2 chủ yếu phục vụ nghiên cứu, engineering và audit.

```text
Tầng 1 — Bằng chứng
Literature + chương trình Tin học lớp 9
              ↓
Tầng 2 — Khung benchmark
Task + input/output + rubric + vai trò giáo viên
              ↓
Tầng 3 — Gói bàn giao
Hướng dẫn + ví dụ + biểu mẫu + DOCX
```

```text
experiments/20260621_135515/
├── metadata.yaml
├── plan.md
├── literature/
│   ├── review_protocol.md
│   ├── review_log.csv
│   ├── evidence_matrix.csv
│   └── rapid_review.md
├── benchmark/
│   ├── benchmark_framework.xlsx
│   ├── task_specification.md
│   └── traceability_matrix.csv
├── teacher_packet/
│   ├── 00-start-here.md
│   ├── author-and-review-guide.md
│   ├── examples.md
│   └── review_form.xlsx
├── deliverables/
│   └── Khung_benchmark_Tin_hoc_9.docx
├── coordination/
│   ├── delegations.jsonl
│   └── handoffs/
└── report.md
```

### 12.1. File quản trị

#### `metadata.yaml`

Ghi ID, trạng thái, branch, experiment cha và danh sách artifact. File này
không chứa kết luận chuyên môn; giáo viên không cần đọc.

#### `plan.md`

Là hợp đồng triển khai: mục tiêu, nguồn, phạm vi, quy trình, validation và
acceptance criteria. Plan không phải kết quả nghiên cứu.

#### `report.md`

Tổng kết sau triển khai: đã tìm gì, framework nào được đề xuất, validation
nào đã chạy, limitation và việc tiếp theo. Nếu chưa có teacher review, report
phải giữ trạng thái `READY_FOR_EXPERT_REVIEW`.

### 12.2. Tầng 1 — `literature/`

#### `review_protocol.md`

Gom câu hỏi review, database, search string, inclusion/exclusion, extraction
schema và stopping rule. Nó trả lời: “Review được tiến hành theo quy tắc nào?”

#### `review_log.csv`

Gom search log và screening log. Nó ghi đã tìm ở đâu, query gì, có bao nhiêu
kết quả, paper nào được chọn/loại và lí do. Nó trả lời: “Review có tái lập và
kiểm tra lại được không?”

#### `evidence_matrix.csv`

Mỗi dòng là một nghiên cứu đã đọc sâu: task/dataset, tutoring capability,
rubric/metric, vai trò chuyên gia, reliability, kết quả, hạn chế và vị trí
bằng chứng. Đây là nguồn chính để giải thích vì sao một task hoặc criterion
được đề xuất.

#### `rapid_review.md`

Gom bốn nội dung trước đây tách thành nhiều file:

1. tổng hợp kết quả literature;
2. khoảng trống nghiên cứu;
3. finding liên quan trực tiếp tới giáo viên;
4. danh mục tài liệu tham khảo.

Các phần phải có heading riêng để vẫn truy cập được độc lập.

### 12.3. Tầng 2 — `benchmark/`

#### `benchmark_framework.xlsx`

Workbook trung tâm của khung benchmark, gồm các sheet:

- `Tasks`: danh sách task, mục tiêu, capability, interaction mode và status;
- `Inputs_Outputs`: field, kiểu dữ liệu, bắt buộc/tùy chọn và ví dụ;
- `Rubric_Criteria`: criterion, anchor `0–5`, critical failure và evidence;
- `Teacher_Roles`: vai trò, input nhận, quyền quyết định, output và handoff;
- `References`: curriculum/literature IDs và metadata rút gọn.

Khi triển khai điều chỉnh ngôn ngữ, các sheet trên được đổi tên hiển thị lần
lượt thành `Du_lieu_vao_ra`, `Tieu_chi_cham`, `Vai_tro_giao_vien` và
`Tham_chieu`; nội dung và vai trò dữ liệu không thay đổi.

Việc gom vào một workbook giúp project lead, giáo viên và engineering đối
chiếu trong một file thay vì mở nhiều CSV.

#### `task_specification.md`

Giải thích bằng văn bản từng task: mục tiêu, input/output, trường hợp sử dụng,
ngoài phạm vi, rubric áp dụng, vai trò giáo viên và example IDs. Workbook là
dữ liệu có cấu trúc; file này là bản giải thích dễ đọc.

#### `traceability_matrix.csv`

Cho phép audit:

```text
task
→ curriculum requirement
→ literature claim
→ rubric criterion
→ example
→ teacher decision
```

Tách file này vì kiểm tra orphan ID và provenance thuận tiện hơn khi dùng CSV.

### 12.4. Tầng 3 — `teacher_packet/`

#### `00-start-here.md`

Trang bắt đầu ngắn: mục tiêu, thứ tự đọc, thời gian dự kiến, việc cần làm và
nơi ghi câu hỏi.

#### `author-and-review-guide.md`

Gom vai trò, workflow, author task card và reviewer task card. File phải tách
rõ hai phần để một người không vừa author vừa phê duyệt mẫu của mình. Mỗi phần
có mục tiêu, input, các bước, ví dụ đạt/chưa đạt, output, checklist, thời gian
và đường escalation.

#### `examples.md`

Trình bày **đầy đủ cả 18 mẫu C01** với input, output, rubric `0–5`, lịch sử
trao đổi và danh sách mã lỗi nghiêm trọng. Bao gồm cả mẫu tốt, mẫu có vấn đề
và mẫu cần giáo viên tranh luận; không chỉ trưng bày “mẫu đẹp”. Yêu cầu này
được bổ sung sau góp ý của project lead ngày 21/06/2026.

#### `review_form.xlsx`

Workbook giáo viên sử dụng trực tiếp, gồm các sheet:

- `Huong_dan`;
- `Task_summary`;
- `Author_form`;
- `Sample_review`;
- `Rubric_calibration`;
- `Open_questions`.

Trong bản bàn giao tiếng Việt, các sheet này được đổi tên hiển thị thành
`Tom_tat_nhiem_vu`, `Phieu_tac_gia`, `Phieu_tham_dinh`, `Hieu_chuan` và
`Cau_hoi_mo`.

Giáo viên không phải nhập ID kỹ thuật hoặc sửa CSV/JSON/YAML.

### 12.5. Sản phẩm bàn giao chính

#### `deliverables/Khung_benchmark_Tin_hoc_9.docx`

Tài liệu tiếng Việt gửi giáo viên và stakeholder, gồm:

1. tóm tắt điều hành;
2. phạm vi và trạng thái;
3. nguồn chương trình và literature;
4. cách hình thành task framework;
5. từng task với input/output;
6. rubric `0–5`, critical failure và ví dụ chấm;
7. vai trò/quy trình giáo viên;
8. mẫu minh họa;
9. limitation và quyết định còn mở;
10. glossary và tài liệu tham khảo.

DOCX là sản phẩm đọc chính. Các file khác cung cấp bằng chứng và dữ liệu nguồn
để kiểm tra các kết luận trong DOCX. DOCX phải được render và kiểm tra trực
quan trước bàn giao.

### 12.6. `coordination/`

Nhật ký nội bộ về specialist, task, input/output, thread ID, uncertainty và
handoff. Không phải tài liệu hướng dẫn gửi giáo viên.

## 13. Quy trình triển khai

1. Khóa protocol, câu hỏi review, search strings và stopping rule.
2. `research-methodologist` chạy search, screening, extraction và synthesis.
3. Orchestrator audit ít nhất 20% extraction và năm claim.
4. Kết hợp literature với C01 curriculum grounding.
5. Đề xuất task families và ghi quyết định giữ/gộp/tách/loại.
6. Viết task/input/output và rubric framework.
7. `teacher-collaboration-designer` tạo teacher packet và các sheet
   `Teacher_Roles` trong workbook.
8. Map và cập nhật 18 mẫu C01.
9. Tạo `review_form.xlsx`.
10. Tạo DOCX và render QA.
11. Chạy validators và traceability audit.
12. Bàn giao ở trạng thái `READY_FOR_EXPERT_REVIEW`.

Nếu có teacher review trong thời gian triển khai:

13. Ghi mọi quyết định và revision.
14. Chỉ các task/sample được duyệt mới chuyển thành `teacher_reviewed`.

## 14. Validation

Chạy bằng:

`D:\conda-envs\benchmark_env\python.exe`

Tối thiểu:

```powershell
D:\conda-envs\benchmark_env\python.exe `
  agents/research-methodologist/scripts/validate_evidence_matrix.py `
  experiments/20260621_135515/literature/evidence_matrix.csv

```

Bổ sung validation:

- candidate/included counts và duplicate check;
- mọi included record có URL/DOI và evidence location;
- mọi task có curriculum + research reference hoặc low-evidence label;
- mọi rubric criterion có đủ anchor `0–5`, reference và evidence status;
- giá trị điểm chỉ nhận `0, 1, 2, 3, 4, 5, N/A`;
- critical failure được lưu riêng và không bị phép tính trung bình che khuất;
- mọi example ID map tới task hợp lệ;
- mọi teacher role có input, authority, output và handoff;
- traceability không có orphan ID;
- workbook có đúng các sheet bắt buộc;
- `author-and-review-guide.md` có đủ hai role, heading task-card và đường
  escalation;
- workbook/C01 input không bị sửa;
- DOCX render không có text bị cắt, bảng vỡ hoặc heading mồ côi;
- `git diff --check` pass cho experiment.

Canonical `validate_teacher_packet.py` hiện kiểm tra cấu trúc P04 nhiều file,
không khớp packet rút gọn. F01 không sửa canonical validator. Khi nghiệm thu,
orchestrator tạo một compatibility view tạm thời từ bốn file teacher packet
để chạy validator, sau đó xóa view tạm; đồng thời audit trực tiếp packet rút
gọn. Compatibility view không phải deliverable và không được commit.

## 15. Acceptance criteria

- Literature review bao phủ đủ sáu cụm và đạt stopping rule.
- Có ít nhất 50 candidate và mục tiêu 20–30 full-text records; thiếu coverage phải được giải thích.
- Mọi synthesis claim có source marker hoặc label `inference/open_question`.
- `benchmark_framework.xlsx` trả lời đầy đủ task, input, output, rubric và
  teacher role.
- Core task có ít nhất một curriculum reference.
- Core task có ít nhất hai research records độc lập hoặc được chuyển khỏi core/ghi low evidence rõ ràng.
- Rubric dùng đủ anchor `0–5` quan sát được, giữ `N/A` riêng, flag critical
  failure và không mặc định trọng số/ngưỡng pass chưa được kiểm chứng.
- Có traceability end-to-end.
- 18 mẫu C01 được map, sửa hoặc loại với rationale.
- DOCX giải thích đầy đủ và có mẫu giúp giáo viên hình dung.
- Giáo viên giữ quyền quyết định cuối về correctness, grade fit và pedagogical suitability.
- Nếu chưa có teacher review, trạng thái tối đa là `READY_FOR_EXPERT_REVIEW`.
- Không sửa canonical skills, adapters, các plan gốc hoặc production code.

## 16. Ngoài phạm vi

F01 không:

- tuyên bố systematic review đầy đủ;
- tạo production dataset;
- xây model runner hoặc evaluation pipeline;
- khóa trọng số/điểm pass benchmark;
- chuẩn hóa ảnh, video hoặc file phần mềm gốc;
- dùng dữ liệu học sinh thật;
- phân tích thư mục học liệu lộn xộn hoặc video lớp học;
- thay expert teacher bằng agent hoặc automatic judge;
- đánh dấu P02–P05 là completed.

## 17. File ownership

F01 được phép tạo/sửa sau approval:

- `experiments/20260621_135515/**`;
- `README.md` và `ARCHITECTURE.md` chỉ khi cần cập nhật trạng thái/kiến trúc bàn giao, sau khi artifacts đã ổn định.

F01 chỉ đọc:

- `experiments/20260621_052024/**`;
- hai nguồn chương trình bắt buộc;
- workbook;
- P02/P03/P04 plans;
- canonical specialist instructions;
- literature nguồn ngoài.

F01 không sửa:

- `document/**`;
- `agents/**`;
- `.agents/**`;
- `.codex/**`;
- `.claude/**`;
- các experiment cũ.

## 18. Quyết định duyệt

Project lead có thể:

- `APPROVE F01`;
- sửa coverage target của literature;
- yêu cầu bỏ/thêm deliverable;
- yêu cầu DOCX chỉ dành cho giáo viên hoặc thêm phần kỹ thuật;
- yêu cầu một expert teacher review bắt buộc trước khi bàn giao;
- từ chối fast-track và quay lại P02→P03→P04→P05 tuần tự.
