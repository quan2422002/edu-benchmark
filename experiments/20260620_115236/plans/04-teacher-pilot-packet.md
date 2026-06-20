# P04 — Teacher pilot packet

## Trạng thái

- Status: `DRAFT_FOR_REVIEW`
- Priority: deadline-critical
- Deadline target: chiều Chủ nhật, 21/06/2026
- Dependencies: P03; preliminary findings from P02
- Owner: `teacher-collaboration-designer`
- Required reviewers: project lead + ít nhất một expert teacher

## 1. Mục tiêu

Tạo một gói nhỏ mà giáo viên có thể đọc và bắt đầu thử author/review dữ liệu mà không cần kỹ sư giải thích trực tiếp. Packet là PoC để thu phản hồi về quy trình, không phải đặc tả benchmark cuối cùng.

## 2. Input

- role/task model từ P03;
- teacher-relevant findings sơ bộ từ P02;
- phạm vi dự án: gia sư LLM môn Tin học lớp 9 bằng tiếng Việt;
- prototype hiện có trong `experiments/20260618_150902/dataset_v0/`, chỉ dùng làm raw example và phải review lại.

## 3. Deliverables tối thiểu

```text
teacher_packet/
├── 00-start-here.md
├── 01-role-and-goal.md
├── 02-author-task-card.md
├── 03-review-task-card.md
├── 04-examples.md
├── 05-author-template.xlsx-or-csv
├── 06-review-template.xlsx-or-csv
├── 07-pilot-feedback-form.md
└── 08-open-questions.md
```

### `00-start-here.md`

- packet dùng để làm gì;
- giáo viên cần đọc file nào theo thứ tự;
- thời gian dự kiến;
- nơi gửi kết quả/câu hỏi;
- nhấn mạnh đây là pilot và feedback về chỉ dẫn cũng là output quan trọng.

### Author task card

Giải thích bằng plain language:

1. Chọn một tình huống học sinh lớp 9 cần trợ giúp.
2. Viết lời học sinh theo cách tự nhiên.
3. Thêm bài làm/code nếu tình huống cần.
4. Viết 2–5 điều phản hồi tốt cần làm/không nên làm.
5. Tùy chọn viết một phản hồi minh họa.
6. Tự kiểm tra bằng checklist.

### Review task card

Yêu cầu reviewer kiểm tra riêng:

- đúng kiến thức;
- phù hợp học sinh lớp 9;
- tình huống có đủ thông tin;
- criteria cụ thể và quan sát được;
- không ép chỉ một wording/cách dạy duy nhất;
- example response có tiết lộ đáp án quá sớm hay không;
- quyết định `accept`, `revise`, `reject` và lý do.

## 4. Mẫu minh họa

Packet có 4–6 sample provisional, không chỉ mẫu “đẹp”:

- ít nhất hai sample đạt;
- ít nhất hai sample chưa đạt kèm giải thích;
- ít nhất một sample cần reviewer tranh luận về mức scaffolding;
- bao phủ tối thiểu hai kiểu task khác nhau;
- ghi rõ sample chưa xác nhận coverage chương trình cho tới khi curriculum source được chốt.

Mỗi sample phải trình bày cả input của học sinh, criteria, optional example response và reviewer note.

## 5. Thiết kế template

Ưu tiên bảng tính thay vì YAML. Các cột author nhìn thấy:

```text
topic
student_prompt
student_work
criterion_1
criterion_2
criterion_3
criterion_4
criterion_5
example_response
author_question
```

Các cột reviewer:

```text
sample_id
content_correct
grade_appropriate
criteria_clear
multiple_valid_responses_allowed
decision
revision_request
reviewer_rationale
```

ID/version/provenance do engineering bổ sung; giáo viên không nhập.

## 6. Plain-language rules

- Mỗi câu hướng dẫn ngắn và bắt đầu bằng động từ hành động.
- Giải thích mọi thuật ngữ bắt buộc phải dùng.
- Không dùng “schema”, “metadata”, “rubric polarity”, “ground truth”, “JSON/YAML” trong task card giáo viên.
- Luôn có một ví dụ hoàn chỉnh và một ví dụ phản chứng.
- Không yêu cầu giáo viên suy đoán model behavior hoặc metric kỹ thuật.

## 7. Pilot execution

Nếu có giáo viên sẵn sàng trước deadline:

1. Gửi packet cho 1–2 giáo viên mà không giải thích miệng trước.
2. Mỗi người thử author ít nhất một sample và review một sample.
3. Ghi thời gian, câu hỏi và điểm dừng.
4. Phỏng vấn ngắn hoặc nhận form feedback.
5. Sửa instruction một vòng trước khi gọi packet là `pilot-ready`.

Nếu chưa có người dùng thử, trạng thái tối đa là `READY_FOR_TEACHER_PILOT`, không phải `VALIDATED`.

## 8. Acceptance criteria

- Giáo viên không cần code/Git/YAML.
- Author và reviewer có task card riêng.
- Có 4–6 sample gồm cả đạt và chưa đạt.
- Mọi requirement mang tính nghiên cứu có citation tới P02 hoặc gắn `provisional`.
- Có form feedback và open questions.
- Một người ngoài nhóm kỹ thuật có thể tìm đúng task cần làm trong dưới hai phút.
- Packet ghi rõ domain authority thuộc về giáo viên.
- Prototype cũ không được quảng bá là benchmark chính thức.

## 9. Test cases

- Teacher chỉ điền một criterion: template/instruction phải báo cần bổ sung nhưng không hiển thị lỗi kỹ thuật.
- Teacher để trống example response: vẫn hợp lệ.
- Reviewer chọn `revise`: phải ghi được yêu cầu sửa cụ thể và trả về đúng author.
- Reviewer phát hiện sample ngoài lớp 9: phải chuyển `reject` hoặc escalation.
- Teacher không hiểu “scaffolding”: packet phải có cách diễn đạt tiếng Việt thay thế hoặc giải thích ngắn.

## 10. File ownership

P04 chỉ sở hữu packet/template/provisional examples. P04 không sửa:

- agent implementation;
- literature evidence;
- benchmark taxonomy chính thức;
- production dataset schema/code.

## 11. Handoff sau pilot

- Usability findings quay lại P03 để sửa workflow.
- Teacher disagreements và open questions chuyển P02/P05.
- Accepted provisional samples chỉ được nhập dataset thật sau P05/P06.

## 12. Quyết định duyệt

- `APPROVE P04` sau khi có output sơ bộ P02 và workflow P03;
- duyệt trước cấu trúc packet nhưng chờ findings để viết nội dung;
- rút gọn sample count nếu deadline không cho phép, nhưng không bỏ negative examples và feedback form.
