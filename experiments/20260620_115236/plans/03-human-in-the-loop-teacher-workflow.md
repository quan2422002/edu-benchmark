# P03 — Human-in-the-loop teacher workflow

## Trạng thái

- Status: `DRAFT_FOR_REVIEW`
- Priority: urgent
- Dependency: none for reviewing role/process design; implementation through `teacher-collaboration-designer` depends on P01
- Inputs when available: P02 teacher-relevant findings
- Process owner: project lead + `teacher-collaboration-designer`
- Domain authority: expert teachers

## 1. Mục tiêu

Xác định rõ giáo viên làm gì, nhận input gì, tạo output gì và bàn giao cho ai. Workflow phải dùng được với người chỉ có chuyên môn Tin học/sư phạm, không yêu cầu code, Git, YAML, benchmark engineering hoặc machine learning.

## 2. Nguyên tắc

- Expert teachers là thành phần bắt buộc, không phải bước review tùy chọn.
- AI/agent hỗ trợ chuẩn bị và kiểm tra hình thức; giáo viên quyết định tính đúng chuyên môn và sư phạm.
- Mỗi task phải có mục tiêu, input, từng bước, ví dụ, output template và checklist hoàn thành.
- Một người không vừa author vừa là reviewer cuối của cùng sample.
- Bất đồng phải được ghi lại và adjudicate, không âm thầm ghi đè.
- Giáo viên làm trên tài liệu/bảng tính quen thuộc; AI engineers chịu trách nhiệm chuyển đổi định dạng kỹ thuật.

## 3. Vai trò con người

### Teacher Author

Nhiệm vụ:

- đề xuất tình huống học sinh thực tế;
- cung cấp bài làm/lỗi/misconception nếu có;
- mô tả điều phản hồi tốt cần làm và cần tránh;
- viết một phản hồi minh họa khi hữu ích.

Không làm:

- viết schema/code;
- cấu hình model;
- gán metric kỹ thuật hoặc model score.

### Teacher Reviewer

Nhiệm vụ:

- kiểm tra tính đúng kiến thức;
- kiểm tra phù hợp lớp 9 và ngôn ngữ học sinh;
- kiểm tra criteria có rõ và chấm được;
- phát hiện nhiều cách trả lời hợp lệ bị rubric loại nhầm;
- đề xuất `accept`, `revise` hoặc `reject` kèm lý do.

Reviewer không sửa âm thầm nội dung author; feedback phải truy vết được.

### Teacher Adjudicator

Nhiệm vụ:

- giải quyết bất đồng author–reviewer hoặc reviewer–reviewer;
- quyết định wording cuối về chuyên môn/sư phạm;
- ghi ngắn gọn rationale;
- chuyển open research question về project lead khi không thể giải quyết bằng chuyên môn.

### Teacher Pilot Participant

Nhiệm vụ:

- thử làm task từ chỉ dẫn mà không được giải thích thêm;
- ghi chỗ mơ hồ, thuật ngữ khó hiểu và thời gian thực hiện;
- đánh giá template có phản ánh đúng cách giáo viên suy nghĩ hay không.

## 4. Vai trò kỹ thuật và agent

### AI Engineer

- tạo form/spreadsheet và validation;
- sinh ID, version, provenance;
- chuyển dữ liệu sang format máy đọc;
- chạy model/evaluation;
- không sửa nội dung sư phạm nếu chưa được teacher review.

### `research-methodologist`

- cung cấp evidence-backed requirements và uncertainty;
- không giao trực tiếp paper dài cho giáo viên nếu có thể tóm tắt chính xác.

### `teacher-collaboration-designer`

- tạo task card/plain-language instruction;
- kiểm tra form không giao việc kỹ thuật;
- tổng hợp feedback mà không thay đổi ý chuyên môn;
- duy trì handoff giữa teacher team và engineering team.

## 5. Task contract chuẩn

Mỗi teacher task card phải có:

```text
Tên task
Mục tiêu
Vì sao task này cần thiết
Input giáo viên nhận được
Các bước thực hiện
Ví dụ đạt / chưa đạt
Output cần nộp
Checklist tự kiểm tra
Thời gian dự kiến
Người review / nơi gửi phản hồi
```

## 6. Task set cho PoC

### T01 — Đề xuất tình huống học sinh

- Owner: Teacher Author
- Input: topic/learning objective và template.
- Output: student prompt, optional student work, 2–5 criteria, optional example response.
- Review: T02.

### T02 — Review sample

- Owner: Teacher Reviewer
- Input: sample không hiển thị danh tính author nếu khả thi.
- Output: correctness, age appropriateness, rubric clarity, decision, comments.
- Escalation: T03 khi bất đồng.

### T03 — Adjudicate disagreement

- Owner: Teacher Adjudicator
- Input: sample, author rationale, reviewer comments.
- Output: final decision và rationale.

### T04 — Review research-to-practice findings

- Owner: ít nhất một Teacher Reviewer.
- Input: `teacher_relevant_findings.md` từ P02.
- Output: agree/disagree/unclear cho từng implication và ví dụ phản chứng nếu có.

### T05 — Usability pilot

- Owner: Teacher Pilot Participant.
- Input: packet P04.
- Output: completion time, questions asked, ambiguous instructions, proposed improvements.

## 7. Workflow trạng thái sample

```text
draft_by_teacher
  → engineering_format_check
  → teacher_review
  → accepted
      hoặc revision_requested → draft_by_teacher
      hoặc adjudication → accepted/rejected
```

Format check chỉ kiểm tra thiếu trường/định dạng; không được tự động đánh giá đúng sai sư phạm.

## 8. Deliverables

P03 khi triển khai tạo:

```text
teacher_workflow/
├── roles.md
├── task-contract-template.md
├── author-task-card.md
├── review-task-card.md
├── adjudication-task-card.md
├── pilot-feedback-form.md
└── handoff-contract.md
```

## 9. Acceptance criteria

- Tất cả task card tránh yêu cầu code, YAML, Git hoặc ML terminology.
- Mỗi task có example đạt/chưa đạt và output cụ thể.
- Author, reviewer, adjudicator có quyền và trách nhiệm không chồng lấn.
- Có đường xử lý bất đồng và revision.
- Engineering format check không được thay phán quyết chuyên môn.
- Ít nhất một giáo viên có thể đọc task card và diễn đạt lại đúng nhiệm vụ mà không cần kỹ sư giải thích thêm.
- Có form thu usability feedback để cải tiến packet.

## 10. Test

Thực hiện tabletop test với ba tình huống:

1. Sample thiếu `criteria`.
2. Reviewer cho rằng example response đúng kiến thức nhưng đưa đáp án quá sớm.
3. Hai giáo viên bất đồng về mức trợ giúp phù hợp.

Workflow phải chỉ rõ ai xử lý, artifact nào thay đổi và quyết định được ghi ở đâu.

## 11. File ownership

P03 sở hữu role/task/handoff documents. P03 không sở hữu:

- literature conclusions;
- benchmark taxonomy;
- dataset parser/schema code;
- model evaluation.

## 12. Quyết định duyệt

- `APPROVE P03` để xây workflow song song với P01/P02;
- sửa tên/số lượng vai trò;
- yêu cầu một giáo viên tham gia đồng thiết kế trước khi implementation.
