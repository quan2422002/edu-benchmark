# C01 — Gói curriculum grounding có tham chiếu cho giáo viên

## Trạng thái

- Status: `APPROVED`
- Approved at: `2026-06-21`
- Priority: urgent
- Dependency: P01 đã hoàn thành
- Downstream: P03, P04 và P05
- Primary specialist: `research-methodologist`
- Supporting specialist: `teacher-collaboration-designer`
- Domain authority: project lead và expert teachers môn Tin học lớp 9

Plan này chỉ được triển khai sau khi trạng thái đổi thành `APPROVED`.

## 1. Mục tiêu

Tạo một gói có phạm vi được quyết định theo coverage, có thể bàn giao sớm cho giáo viên, giúp họ hiểu:

- nội dung nào thuộc phạm vi Tin học lớp 9;
- cách tạo câu hỏi, câu trả lời minh họa và rubric;
- cách ghi căn cứ cho từng mẫu tới đúng tài liệu, trang, phần/mục/bảng và đoạn liên quan;
- phần nào dựa trên chương trình, phần nào dựa trên nghiên cứu và phần nào vẫn cần giáo viên phán quyết.

C01 không xây benchmark specification, không phê duyệt item bank và không tạo production dataset.

## 2. Nguồn bắt buộc

Hai specialist phải xem xét cả hai nguồn sau:

### Nguồn chuẩn tắc

Chương trình giáo dục phổ thông môn Tin học, ban hành kèm Thông tư số 32/2018/TT-BGDĐT:

`https://thcslamsonq6.hcm.edu.vn/hoat-dong-chuyen-mon/chuong-trinh-giao-duc-pho-thong-mon-tin-hoc-ban-hanh-kem-theo-thong-tu-so-32201/ctmb/30978/387356`

Nguồn này xác định phạm vi, mạch kiến thức, năng lực và yêu cầu cần đạt của lớp 9. Khi triển khai cần xác minh thêm URL chính thức cấp Bộ hoặc cổng văn bản pháp luật nếu có.

### Nguồn giải thích/bồi dưỡng

Tài liệu tìm hiểu Chương trình môn Tin học trong Chương trình GDPT 2018, Bộ GDĐT và Trường Đại học Sư phạm Hà Nội, 2019:

`https://dtbdtx.hnue.edu.vn/Portals/0/Tai%20lieu%20tim%20hieu%20chuong%20trinh%20mon%20Tin%20hoc_1.pdf`

Nguồn này hỗ trợ diễn giải mục tiêu, NLa–NLe, DL/ICT/CS, phương pháp dạy học và đánh giá. Nó không thay thế văn bản chương trình.

Mỗi trích xuất phải ghi:

```text
reference_id
title
url
publisher
year
grade
strand/topic
section_or_table
page
location_note
short_excerpt_or_paraphrase
accessed_at
```

Chỉ link URL là chưa đủ.

## 3. Vai trò của workbook

Input read-only:

`document/teacher_training_curriculum/Benchmark Tin học THCS.xlsx`

Chỉ tham khảo:

- tên và ý nghĩa các trường trong `Item_Bank`;
- cấu trúc review trong `Expert_Form`;
- cách trình bày question, answer, rubric và item type;
- một số mẫu để nhận diện điểm tốt/chưa tốt.

Không mặc định kế thừa:

- taxonomy hoặc tỷ lệ phân bổ item;
- answer/rubric;
- difficulty;
- competency mapping;
- trạng thái `draft_v1`;
- toàn bộ 40 item lớp 9.

Workbook hiện có 160 item, trong đó 40 item lớp 9; toàn bộ expert-review và pilot fields đang trống. Vì vậy workbook là nguồn thiết kế nội bộ, không phải ground truth.

Khi đọc workbook:

- dùng `openpyxl==3.1.5` trong `benchmark_env`;
- mở với `data_only=False`, `keep_links=True`;
- không gọi `save()`;
- không sửa file nguồn;
- dùng table `Table_1` và `Table_2`, không dựa vào used range `A1:Z1000`;
- giữ nguyên nội dung bắt đầu bằng `=` thay vì thay bằng cached formula result.

## 4. Contract bắt buộc cho mẫu minh họa

Mỗi mẫu phải tối thiểu có:

```text
sample_id
topic
learning_requirement
student_prompt
student_work
example_response
rubric_criteria
curriculum_reference_ids
research_reference_ids
teacher_judgment_notes
status
```

Mỗi rubric criterion phải có:

```text
criterion_id
criterion_text
reference_ids
evidence_status
```

`evidence_status` chỉ nhận:

- `supported`;
- `provisional`;
- `teacher_judgment`;
- `open_question`.

Một mẫu chỉ được đưa vào gói bàn giao khi:

- có ít nhất một `curriculum_reference_id`;
- tham chiếu curriculum có page và location cụ thể;
- mọi criterion có `reference_ids` hoặc được gắn rõ `teacher_judgment/open_question`;
- expert teacher được ghi là người xác nhận cuối về chuyên môn và sư phạm.

Nếu P02 chưa hoàn tất, `research_reference_ids` được để trống và hành vi tutoring liên quan phải gắn `provisional`; không được tạo citation giả.

## 5. Deliverables

C01 chỉ tạo:

```text
experiments/20260621_052024/
├── metadata.yaml
├── plan.md
├── grounding/
│   ├── source_registry.csv
│   ├── grade9_reference_matrix.csv
│   ├── reference_contract.md
│   ├── workbook_field_notes.md
│   ├── sample_template.csv
│   ├── example_coverage_proposal.md
│   ├── reference_grounded_examples.md
│   └── teacher_review_questions.md
├── coordination/
│   ├── delegations.jsonl
│   └── handoffs/
└── report.md
```

`reference_grounded_examples.md` chứa số mẫu provisional được project lead duyệt sau khi specialist hoàn thành phân loại các nhóm mẫu cần thiết. Không ấn định số lượng trước khi chưa có coverage analysis. Đây là ví dụ để giáo viên phản biện, không phải benchmark v1.

Không tạo tool production, schema dùng chung, agent mới hoặc artifact ngoài experiment.

### 5.1. Ý nghĩa của từng thành phần

#### `metadata.yaml`

File quản trị experiment, trả lời các câu hỏi:

- experiment có ID và tên gì;
- kế thừa experiment nào;
- đang ở trạng thái `draft`, `approved`, `running` hay `completed`;
- ai chịu trách nhiệm;
- artifact nào dự kiến được tạo;
- kết quả sau này gắn với Git commit nào.

File này không chứa nội dung chuyên môn hoặc kết quả nghiên cứu.

#### `plan.md`

Là hợp đồng thực hiện C01, quy định:

- mục tiêu và phạm vi;
- nguồn bắt buộc;
- vai trò của specialist và expert teachers;
- deliverables;
- validation và acceptance criteria;
- file nào được phép đọc/ghi.

Plan không phải kết quả. Khi chưa `APPROVED`, không được tạo các artifact còn lại.

#### `grounding/source_registry.csv`

Danh mục nguồn được sử dụng. Mỗi nguồn có một `source_id` ổn định và metadata như:

```text
source_id
title
publisher
year
url_or_path
authority_role
accessed_at
notes
```

Ví dụ:

```text
SRC-CURR-001  Chương trình GDPT môn Tin học 2018
SRC-GUIDE-001 Tài liệu tìm hiểu chương trình môn Tin học
SRC-WB-001    Benchmark Tin học THCS.xlsx
```

Mục đích:

- tránh ghi lại toàn bộ thông tin nguồn trong từng sample;
- phân biệt nguồn chuẩn tắc, nguồn giải thích và workbook nội bộ;
- tạo điểm bắt đầu để audit provenance.

`authority_role` mô tả vai trò của nguồn, không phải điểm chất lượng:

- `normative`: văn bản quy định yêu cầu chương trình;
- `interpretive`: tài liệu giải thích/bồi dưỡng;
- `internal_draft`: tài liệu thiết kế nội bộ chưa thẩm định.

#### `grounding/grade9_reference_matrix.csv`

Bảng trích xuất những yêu cầu chương trình lớp 9 cần dùng để phân loại và xây các mẫu minh họa.

Mỗi dòng đại diện cho một căn cứ có thể truy vết:

```text
reference_id
source_id
grade
strand
topic
learning_requirement
page
section_or_table
location_note
short_excerpt_or_paraphrase
```

Giải thích:

- `reference_id`: mã căn cứ ổn định, ví dụ `CURR-G9-CS-001`;
- `grade`: lớp, trong C01 luôn là lớp 9;
- `strand`: mạch nội dung lớn;
- `topic`: chủ đề cụ thể trong mạch;
- `learning_requirement`: yêu cầu học sinh cần biết hoặc làm được;
- `page`: số trang trong tài liệu;
- `section_or_table`: phần, mục hoặc bảng chứa căn cứ;
- `location_note`: mô tả chi tiết vị trí, ví dụ hàng nào trong bảng;
- `short_excerpt_or_paraphrase`: trích đoạn ngắn hoặc diễn giải trung thành.

`strand` được dịch là **mạch nội dung** hoặc **mạch kiến thức lớn**:

- `DL` — Digital Literacy: học vấn số, thông tin, đạo đức và an toàn trong môi trường số;
- `ICT` — Information and Communication Technology: sử dụng và ứng dụng công nghệ thông tin–truyền thông;
- `CS` — Computer Science: khoa học máy tính, thuật toán, lập trình và giải quyết vấn đề.

Quan hệ phân cấp:

```text
Môn Tin học
└── Mạch nội dung / strand
    └── Chủ đề / topic
        └── Yêu cầu cần đạt / learning requirement
```

Trong tài liệu gửi giáo viên dùng tên tiếng Việt `Mạch nội dung`; mã `DL/ICT/CS` chủ yếu phục vụ dữ liệu kỹ thuật và đối chiếu literature.

#### `grounding/reference_contract.md`

Quy định chung về cách ghi tham chiếu để mọi artifact dùng cùng một chuẩn.

Nội dung tối thiểu:

- trường bắt buộc của một reference;
- cách ghi trang, phần, mục, bảng và location note;
- khi nào được trích nguyên văn và khi nào nên diễn giải;
- cách nối một rubric criterion tới nhiều reference;
- cách dùng các nhãn evidence status;
- cách xử lý nguồn không có số trang;
- quy tắc không được bịa URL, số trang, DOI hoặc trích dẫn.

Các nhãn evidence status:

- `supported`: có căn cứ trực tiếp;
- `provisional`: đề xuất tạm thời, đang chờ literature hoặc teacher review;
- `teacher_judgment`: quyết định chuyên môn/sư phạm thuộc giáo viên, không được tài liệu quy định trực tiếp;
- `open_question`: chưa đủ căn cứ để quyết định.

#### `grounding/workbook_field_notes.md`

Giải thích cách C01 tham khảo workbook mà không coi workbook là ground truth.

File này ghi:

- tên và ý nghĩa các field hữu ích;
- field nào có thể tái sử dụng trong template;
- field nào cần đổi tên cho giáo viên dễ hiểu;
- field nào đang là giả định chưa được thẩm định;
- rủi ro kỹ thuật hoặc nội dung đã phát hiện.

Ví dụ:

| Field | Ý nghĩa | Cách sử dụng |
|---|---|---|
| `item_id` | Mã item | Tham khảo quy tắc đặt ID |
| `grade` | Lớp | C01 chỉ nhận lớp 9 |
| `strand` | Mạch nội dung | Hiển thị cho giáo viên là `Mạch nội dung` |
| `question` | Câu hỏi/tình huống | Dùng làm field lõi |
| `correct_answer` | Đáp án | Với câu hỏi mở cần hiểu là đáp án/gợi ý tham khảo |
| `rubric` | Hướng dẫn chấm | Nên tách thành các criterion nhỏ |
| `expected_difficulty` | Độ khó dự kiến | Chưa coi là đã xác nhận |
| `status` | Trạng thái | `draft_v1` không đồng nghĩa được duyệt |

File này không chỉnh sửa workbook và không tự động nhập item vào dataset.

#### `grounding/sample_template.csv`

Biểu mẫu cấu trúc để mô tả một sample có căn cứ.

Các field chính:

```text
sample_id
topic
learning_requirement
student_prompt
student_work
example_response
rubric_criteria
curriculum_reference_ids
research_reference_ids
teacher_judgment_notes
status
```

Giải thích:

- `sample_id`: mã duy nhất của mẫu;
- `student_prompt`: câu hỏi/lời nói tự nhiên của học sinh;
- `student_work`: bài làm, code hoặc lập luận nếu có;
- `example_response`: một phản hồi minh họa, không phải cách trả lời duy nhất;
- `rubric_criteria`: danh sách hành vi cụ thể dùng để review/chấm phản hồi;
- `curriculum_reference_ids`: căn cứ về nội dung lớp 9;
- `research_reference_ids`: căn cứ literature cho hành vi tutoring;
- `teacher_judgment_notes`: phần giáo viên giải thích quyết định chuyên môn/sư phạm;
- `status`: trạng thái như `provisional`, `needs_revision` hoặc `teacher_reviewed`.

CSV này là contract dữ liệu kỹ thuật. P04 có thể chuyển nó thành Excel/Google Sheets thân thiện hơn; không yêu cầu giáo viên sửa CSV trực tiếp.

#### `grounding/example_coverage_proposal.md`

Đề xuất phân loại các nhóm mẫu cần minh họa trước khi quyết định số lượng.

Mỗi nhóm mẫu phải mô tả:

```text
example_type_id
tên loại mẫu
mục tiêu minh họa
mạch nội dung/chủ đề liên quan
loại tình huống học sinh
hành vi tutoring cần thể hiện
đặc điểm làm nó khác các loại còn lại
curriculum reference dự kiến
research basis nếu đã có
số mẫu tối thiểu đề xuất
số mẫu tốt hơn đề xuất
effort ước tính
```

Phân loại không được chỉ dựa trên item type như MCQ hay short answer. Nó phải xem xét ít nhất:

- mạch nội dung DL/ICT/CS;
- loại hoạt động: giải thích, chẩn đoán lỗi, phản hồi, hinting hoặc hỗ trợ giải quyết vấn đề;
- có/không có `student_work`;
- single-turn hoặc multi-turn;
- mức độ mở của đáp án/rubric;
- trường hợp đạt yêu cầu và trường hợp cần sửa;
- yêu cầu teacher judgment đặc biệt.

File này là cơ sở để project lead quyết định mỗi loại cần bao nhiêu mẫu. Nó không tự động trở thành taxonomy benchmark của P05.

#### `grounding/reference_grounded_examples.md`

Chứa các mẫu đã điền hoàn chỉnh để giáo viên đọc và phản biện. Số lượng chỉ được chốt sau decision gate về coverage và số mẫu cho từng loại.

Mỗi mẫu trình bày:

1. yêu cầu cần đạt;
2. câu hỏi của học sinh;
3. bài làm của học sinh nếu có;
4. câu trả lời minh họa;
5. rubric criteria;
6. reference của từng criterion;
7. điểm còn provisional;
8. câu hỏi cần giáo viên quyết định.

Ví dụ rút gọn:

```text
Criterion: Xác định đúng lỗi đầu tiên trong thuật toán.
Reference IDs: CURR-G9-CS-001
Evidence status: supported

Criterion: Gợi ý để học sinh tự sửa trước khi đưa lời giải.
Reference IDs: LIT-004
Evidence status: provisional
```

File này là sản phẩm dễ đọc cho con người. Nó không thay thế dữ liệu có cấu trúc trong `sample_template.csv`.

#### `grounding/teacher_review_questions.md`

Danh sách câu hỏi giúp expert teachers review mẫu một cách nhất quán.

Ví dụ:

- Câu hỏi có thuộc phạm vi lớp 9 không?
- Reference có thực sự hỗ trợ nội dung sample không?
- Cách diễn giải yêu cầu chương trình có chính xác không?
- Câu hỏi và phản hồi có phù hợp lứa tuổi không?
- Đáp án minh họa có đúng kiến thức không?
- Rubric có cụ thể, quan sát được và cho phép nhiều cách trả lời hợp lệ không?
- Criterion nào là yêu cầu chương trình?
- Criterion nào là lựa chọn sư phạm cần teacher judgment?
- Quyết định cuối: `accept`, `revise` hay `reject`?

Đây là cầu nối từ artifact nghiên cứu sang công việc giáo viên; không chứa code hoặc thuật ngữ triển khai không cần thiết.

#### `coordination/delegations.jsonl`

Nhật ký append-only của việc giao task cho specialist.

Mỗi event ghi:

- specialist;
- task;
- input;
- allowed write paths;
- native thread ID;
- trạng thái;
- output;
- câu hỏi còn mở.

File này phục vụ audit hoạt động agent, không gửi cho giáo viên như tài liệu hướng dẫn.

#### `coordination/handoffs/`

Chứa file bàn giao của từng delegation.

Ví dụ:

```text
c01-research-001.md
c01-teacher-design-001.md
```

Mỗi handoff ghi prompt, inputs, outputs, kết quả, uncertainty, quyết định của orchestrator và việc cần con người xử lý.

#### `report.md`

Báo cáo tổng kết sau khi C01 triển khai:

- nguồn đã sử dụng;
- requirement đã trích;
- mẫu đã tạo;
- validation đã chạy;
- kết quả teacher review;
- mẫu nào `accept/revise/reject`;
- limitations và open questions;
- đề xuất handoff cho P03/P04/P05.

### 5.2. Luồng dữ liệu

```text
Hai nguồn chương trình
        ↓
source_registry.csv
        ↓
grade9_reference_matrix.csv
        ↓
reference_contract.md
        ↓
sample_template.csv
        ↓
example_coverage_proposal.md
        ↓
reference_grounded_examples.md
        ↓
teacher_review_questions.md
        ↓
Expert-teacher review
        ↓
report.md
```

`workbook_field_notes.md` đứng bên cạnh luồng chính và chỉ cung cấp cấu trúc tham khảo từ workbook.

`coordination/` ghi lại specialist nào đã tạo hoặc kiểm tra từng artifact.

Ba tầng deliverable:

1. **Bằng chứng:** source registry và reference matrix.
2. **Sản phẩm cho giáo viên:** template, examples và review questions.
3. **Quản trị/audit:** metadata, plan, coordination và report.

## 6. Phân công

### `research-methodologist`

- đọc hai nguồn bắt buộc;
- trích yêu cầu cần đạt lớp 9 với vị trí nguồn;
- lập source registry và reference matrix;
- kiểm tra mọi claim/mẫu có căn cứ hoặc nhãn uncertainty;
- tham khảo workbook nhưng không coi workbook là evidence chuẩn tắc.

### `teacher-collaboration-designer`

- bắt buộc đọc hai nguồn và reference matrix;
- dùng workbook để tham khảo cấu trúc field và ví dụ;
- phối hợp phân loại các nhóm mẫu cần minh họa;
- sau khi project lead duyệt số lượng cho từng nhóm, tạo mẫu và câu hỏi review bằng ngôn ngữ giáo viên;
- không tự xác nhận correctness, grade fit hoặc pedagogical suitability.

### Expert teachers

- xác nhận cách diễn giải yêu cầu chương trình;
- review câu hỏi, câu trả lời minh họa và từng rubric criterion;
- đánh dấu `accept`, `revise` hoặc `reject`;
- bổ sung teacher judgment khi nguồn không quy định trực tiếp.

Không tạo `curriculum-domain-expert` trong C01 và không sửa canonical skill/adapters của hai specialist P01.

## 7. Quy trình

1. Ghi hash workbook và metadata của hai nguồn.
2. `research-methodologist` trích tập yêu cầu cần đạt lớp 9 cần thiết để xác định các nhóm mẫu.
3. Orchestrator audit ngược mỗi requirement về đúng trang/mục/bảng.
4. Hai specialist tạo `example_coverage_proposal.md`, phân loại các nhóm mẫu và giải thích coverage.
5. Orchestrator dừng tại decision gate và hỏi project lead số lượng mẫu cho từng loại. Thông tin trình project lead gồm:
   - danh sách loại mẫu;
   - căn cứ chương trình của từng loại;
   - điểm khác biệt giữa các loại;
   - số mẫu tối thiểu và số mẫu tốt hơn được đề xuất;
   - tổng effort ước tính.
6. Project lead quyết định số lượng mẫu cho từng loại. Không tạo bộ examples trước quyết định này, ngoài tối đa một ví dụ cấu trúc nếu cần để giải thích loại mẫu.
7. `teacher-collaboration-designer` tạo template và số mẫu provisional đã được duyệt.
8. Mỗi thành phần của mẫu được nối với reference ID.
9. Expert teacher review toàn bộ mẫu đã tạo.
10. Ghi disagreement, revision và open question; không sửa âm thầm.
11. Bàn giao artifact cho P03/P04; P05 mới có quyền promote thành benchmark requirement.

## 8. Quan hệ với các plan khác

### P02

P02 vẫn là literature review độc lập. C01 không sửa evidence matrix của P02.

Khi P02 có kết quả, `research_reference_ids` được nối vào mẫu để giải thích hành vi tutoring/rubric. Curriculum reference giải thích **dạy nội dung gì**; research reference giải thích **đánh giá cách dạy như thế nào**.

### P03

P03 dùng `teacher_review_questions.md` và reference contract để hoàn thiện task review cho giáo viên.

### P04

P04 có thể đưa tập mẫu đã được project lead chốt số lượng và đã qua teacher review vào teacher packet. Không gửi nguyên workbook 160 item như packet.

### P05

P05 quyết định taxonomy, task definition, rubric specification và việc tái sử dụng item.

## 9. Ngoài phạm vi

C01 không:

- audit/crosswalk toàn bộ 40 item lớp 9;
- chỉnh sửa hoặc chuẩn hóa workbook;
- ingest toàn bộ thư mục `TapHuan-GV-TinHoc9`;
- phân tích video lớp học;
- dùng dữ liệu học sinh thật;
- thực hiện literature review P02;
- tạo benchmark taxonomy, production dataset hoặc evaluation pipeline;
- tạo specialist mới;
- sửa `SKILL.md`, scripts, references hoặc adapters của hai specialist hiện có.

## 10. Validation

- hai source record có URL, publisher, year và authority role;
- mỗi curriculum requirement có page và location;
- mọi reference ID duy nhất;
- coverage proposal phân biệt rõ các loại mẫu và giải thích vì sao chúng không trùng nhau;
- project lead đã ghi quyết định số lượng cho từng loại;
- mọi mẫu đã được duyệt số lượng đều có curriculum reference;
- mọi rubric criterion có reference hoặc uncertainty label;
- không citation/DOI/page nào được tự bịa;
- workbook hash không đổi;
- không có file nào trong `document/` bị sửa;
- expert teacher review đủ 100% mẫu đã tạo;
- chọn ngẫu nhiên ba criterion và truy ngược:

```text
criterion
→ reference_id
→ source
→ page/section/table
→ excerpt/paraphrase
→ teacher decision
```

## 11. Acceptance criteria

- Gói grounding đủ để giáo viên hiểu cách tạo/review một mẫu có căn cứ.
- Hai specialist đã xem xét hai nguồn bắt buộc.
- Có `example_coverage_proposal.md` phân loại đủ các nhóm mẫu cần minh họa.
- Project lead đã quyết định rõ số lượng mẫu cho từng nhóm trước khi examples được tạo.
- Có đủ số mẫu provisional theo quyết định đó, bao gồm cả mẫu đạt và mẫu cần sửa khi phù hợp.
- Câu hỏi, câu trả lời và rubric đều truy vết được.
- Workbook chỉ được dùng làm tài liệu tham khảo cấu trúc/mẫu.
- Mọi điểm chưa có research evidence được ghi `provisional`.
- Expert teachers giữ quyền quyết định cuối.
- Không thay đổi P01, P02, P03, P04 hoặc production code.

## 12. File ownership

C01 được phép tạo/sửa sau approval:

- `experiments/20260621_052024/**`.

C01 chỉ được đọc:

- workbook đã nêu;
- hai nguồn chương trình bắt buộc;
- artifact P02 khi được bàn giao;
- canonical instructions của hai specialist.

C01 không được đọc sâu:

- `document/teacher_training_curriculum/TapHuan-GV-TinHoc9/**`;
- file video lớp học.

C01 không được sửa bất kỳ file nào trong `document/`.

## 13. Quyết định duyệt

Người dùng có thể:

- `APPROVE C01`;
- sửa tiêu chí phân loại hoặc thông tin cần trình tại decision gate;
- yêu cầu chỉ làm template/reference matrix, chưa tạo mẫu;
- yêu cầu thêm một nguồn học liệu cụ thể qua plan amendment;
- từ chối và tiếp tục P02/P03 mà chưa có grounding package.
