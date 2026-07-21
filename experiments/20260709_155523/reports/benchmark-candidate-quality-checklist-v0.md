# Checklist kiểm định ứng viên mẫu benchmark v0

Experiment: `20260709_155523`  
Nguồn gốc: tách từ `benchmark-quality-checklist-v0.md` ngày 17/07/2026  
Dùng cho: Plan 06 và các bước sau khi dữ liệu thô đã được chuyển đổi thành ứng viên mẫu benchmark  
Trạng thái: `v0_for_benchmark_candidate_review`

## 1. Phạm vi sử dụng

Checklist này chỉ dùng cho mẫu đã được chuyển đổi từ dữ liệu thô HNMU sang cấu trúc ứng viên benchmark. Ở giai đoạn này, mẫu đã hoặc dự kiến đã có các trường như:

- `benchmark_sample_id`;
- `raw_sample_id`;
- `student_prompt`;
- `conversation_history`;
- `gold_response`;
- `answer` hoặc `Đáp án`;
- task;
- rubric áp dụng;
- metadata học liệu;
- truy vết tới dữ liệu thô và evidence SGK/SGV.

Không dùng checklist này để kiểm file Excel thô trực tiếp. Nếu chỉ có dữ liệu thô HNMU, dùng `raw-dialogue-quality-checklist-v0.md`.

## 2. Căn cứ

| Căn cứ | Bài học dùng cho kiểm ứng viên benchmark |
|---|---|
| MathTutorBench | Mẫu benchmark cần đánh giá được năng lực gia sư, gồm hiểu học sinh, gợi mở, phản hồi sư phạm và hỗ trợ giải quyết vấn đề. |
| KMP-Bench | Mẫu cần có flow hội thoại rõ, evidence học liệu đáng tin, và tránh các flow lỗi hoặc không có giá trị đánh giá. |
| TutorBench | Rubric, phản hồi tham chiếu và tiêu chí chấm cần có chuyên gia kiểm tra; không nên đánh giá bằng so khớp chữ đơn thuần. |
| VietLegal/V-Legal | Mẫu benchmark cần truy vết nguồn, kiểm trùng/rò rỉ và có quy trình review/phân xử. |
| Tài liệu HNMU về mức nhận thức | Khi kiểm metadata mức nhận thức, dùng bản Markdown chuẩn hóa `shared/learning_resources/agent_context/hnmu_cognitive_level_method_canonical.md`, có nguồn gốc từ file `Biểu hiện mức độ nhận thức _Tin học.docx`. |

## 3. Output tối thiểu cho mỗi ứng viên mẫu benchmark

| Trường | Ý nghĩa |
|---|---|
| `benchmark_sample_id` | Mã ứng viên mẫu benchmark. |
| `raw_sample_id` | Mã mẫu thô nguồn, để truy vết ngược. |
| `conversion_status` | `converted`, `needs_revision`, hoặc `reject`. |
| `candidate_quality_decision` | `pass`, `fail`, hoặc `needs_human_review`. |
| `confidence_score` | Mức tự tin của kiểm định tự động/agent. |
| `failure_reasons` | Lý do chưa đạt hoặc cần xem lại. |
| `task_id` | Nhiệm vụ benchmark được gán. |
| `rubric_ids` | Các tiêu chí chấm áp dụng. |
| `evidence_fragment_ids` | Fragment SGK/SGV làm căn cứ. |
| `raw_trace` | File/sheet/dòng gốc HNMU. |
| `review_notes` | Ghi chú cho UET/HNMU. |

## 4. Checklist cấu trúc mẫu benchmark

| Mã | Tiêu chí | Câu hỏi kiểm tra | Công cụ chính | Quyết định mặc định |
|---|---|---|---|---|
| BEN-STR-01 | Có đủ trường benchmark lõi | Mẫu có `student_prompt`, `conversation_history`, `gold_response`, `Đáp án`, task, rubric, truy vết không? | Code | Thiếu trường lõi → `needs_human_review` hoặc `fail`. |
| BEN-STR-02 | Tách đúng `student_prompt` | `student_prompt` có đúng là tuyên bố/yêu cầu ban đầu của học sinh không? | Agent + raw trace | Sai rõ → sửa hoặc review. |
| BEN-STR-03 | Tách đúng `conversation_history` | Lịch sử hội thoại có chứa các lượt sau tuyên bố ban đầu và trước phản hồi mục tiêu không? | Agent + raw trace | Sai rõ → sửa hoặc review. |
| BEN-STR-04 | Tách đúng `gold_response` | `gold_response` có phải phản hồi gia sư mục tiêu cần chấm không? | Agent + raw trace | Không rõ → review. |
| BEN-STR-05 | Tách riêng `Đáp án` | Đáp án đúng cho đề bài có bị lẫn vào `gold_response` không? | Agent | Lẫn rõ → sửa hoặc review. |
| BEN-STR-06 | Truy vết hai chiều | Có thể đi từ mẫu benchmark về raw HNMU và từ raw HNMU tới mẫu benchmark không? | Code | Thiếu truy vết → chưa đạt. |

## 5. Checklist task, hành vi gia sư và phạm vi đánh giá

Ở giai đoạn ứng viên benchmark, task là đơn vị chính đại diện cho hành vi gia sư cần đánh giá. Vì vậy độ phủ hành vi gia sư không kiểm ở dữ liệu thô, mà kiểm sau khi mỗi mẫu đã được chuyển đổi và gán task.

### 5.1. Độ phủ task/hành vi gia sư ở cấp tập ứng viên

| Mã | Tiêu chí | Câu hỏi kiểm tra | Công cụ chính | Quyết định mặc định |
|---|---|---|---|---|
| BEN-COV-01 | Phủ task/hành vi gia sư | Tập ứng viên có phủ các task đã chốt hoặc đang dùng trong bản v0 không? | Code + task registry | Vùng thiếu → ghi vào báo cáo coverage, chưa tự loại mẫu. |
| BEN-COV-02 | Phân bố task có chủ đích | Task nào nhiều/ít mẫu có giải thích được theo mục tiêu benchmark và học liệu không? | Code + người điều phối | Không yêu cầu đều tuyệt đối; cần giải thích được. |
| BEN-COV-03 | Task gắn với dạng câu hỏi phù hợp | Với từng task, dạng câu hỏi/bài làm có phù hợp để làm lộ hành vi gia sư cần kiểm không? | Agent + task spec | Không chắc → UET/HNMU review. |
| BEN-COV-04 | Task gắn với mức nhận thức phù hợp | Mức nhận thức là metadata hỗ trợ, không thay thế task; phân bố ba mức Biết, Hiểu, Vận dụng trong từng task có hợp lý không? | Code + agent + tài liệu HNMU về mức nhận thức | Lệch mạnh → ghi cờ review thiết kế. |

Ghi chú cho `BEN-COV-04`:

- Mức nhận thức dùng ba mức trong tài liệu HNMU: `Biết`, `Hiểu`, `Vận dụng`.
- Nếu dữ liệu nguồn ghi `Nhận biết` hoặc `Thông hiểu`, có thể ánh xạ tương ứng về `Biết` và `Hiểu`.
- Khi kiểm mức nhận thức, không ánh xạ máy móc theo một động từ đơn lẻ; cần đối chiếu với hành động, đối tượng và yêu cầu cụ thể được nêu trong bản Markdown chuẩn hóa từ tài liệu HNMU.
- Mức nhận thức chỉ là metadata hỗ trợ thiết kế/coverage, không thay thế task hành vi gia sư.

### 5.2. Kiểm từng mẫu sau khi gán task

| Mã | Tiêu chí | Câu hỏi kiểm tra | Công cụ chính | Quyết định mặc định |
|---|---|---|---|---|
| BEN-TASK-01 | Gán task đúng | Task có phản ánh hành vi gia sư mà mẫu muốn kiểm không? | Agent + task spec | Không chắc → UET/HNMU review. |
| BEN-TASK-02 | Không dùng mức nhận thức làm task chính | Mức nhận thức được giữ như metadata, không thay thế task hành vi gia sư. | Agent | Lệch thiết kế → sửa. |
| BEN-TASK-03 | Input đủ cho model | Mẫu có đủ ngữ cảnh để model đóng vai gia sư phản hồi không? | Agent | Thiếu ngữ cảnh → sửa hoặc loại. |
| BEN-TASK-04 | Không rò đáp án không cần thiết | Input không vô tình chứa đáp án nếu task yêu cầu gia sư gợi mở. | Agent | Rò đáp án làm hỏng task → sửa. |
| BEN-TASK-05 | Bám phạm vi Tin học THCS | Mẫu có nằm trong phạm vi học liệu/tiền kiến thức được chấp nhận không? | Agent + học liệu | Không chắc → review. |

## 6. Checklist rubric và khả năng chấm

| Mã | Tiêu chí | Câu hỏi kiểm tra | Công cụ chính | Quyết định mặc định |
|---|---|---|---|---|
| BEN-RUB-01 | Rubric áp dụng được | Mỗi rubric được gán có thể quan sát từ phản hồi model không? | Agent + rubric spec | Không quan sát được → bỏ/sửa rubric áp dụng. |
| BEN-RUB-02 | Không chồng chéo quá mức | Các rubric không đo cùng một lỗi theo cách gây nhập nhằng. | Agent | Cần UET chốt nếu mơ hồ. |
| BEN-RUB-03 | Có thang điểm rõ | Mẫu dùng rubric theo thang Likert 1–5 hoặc thang đã chốt. | Code + agent | Thiếu thang → chưa đạt. |
| BEN-RUB-04 | Gold response hỗ trợ chấm | `gold_response` thể hiện phản hồi gia sư lý tưởng, làm căn cứ so sánh định tính, không chỉ là đáp án. | Agent + HNMU | Không đủ lý tưởng → review/sửa. |
| BEN-RUB-05 | Có điều kiện lỗi nghiêm trọng nếu áp dụng | Nếu mẫu có điều kiện loại/điểm thấp đặc biệt, phải ghi rõ. | Agent | Thiếu nhưng cần → review. |

## 7. Checklist học liệu và truy vết

| Mã | Tiêu chí | Câu hỏi kiểm tra | Công cụ chính | Quyết định mặc định |
|---|---|---|---|---|
| BEN-EVD-01 | Có evidence SGK/SGV | Mẫu trỏ được tới fragment hoặc nguồn học liệu liên quan không? | Retrieval API | Thiếu evidence → `needs_human_review`. |
| BEN-EVD-02 | Evidence khớp nội dung | Evidence có thật sự hỗ trợ câu hỏi/đáp án/gold response không? | Agent | Không khớp → sửa hoặc loại. |
| BEN-EVD-03 | Trạng thái evidence rõ | Evidence đang là `draft`, `reviewed`, hay cần HNMU xác nhận? | Code + registry | `draft` → không coi là xác nhận cuối. |
| BEN-EVD-04 | Không bịa nguồn | Không tự tạo mã học liệu hoặc nguồn không có trong registry. | Code + agent | Bịa nguồn → `fail`. |
| BEN-EVD-05 | Giữ nguồn thô | Mẫu benchmark vẫn giữ link về raw HNMU, không chỉ giữ bản đã chuyển đổi. | Code | Thiếu raw trace → chưa đạt. |

## 8. Checklist chất lượng sư phạm của mẫu benchmark

| Mã | Tiêu chí | Câu hỏi kiểm tra | Công cụ chính | Quyết định mặc định |
|---|---|---|---|---|
| BEN-PED-01 | Phù hợp phương pháp dàn giáo | Gold response và/hoặc hội thoại nền có thể hiện mức hỗ trợ phù hợp không? | Agent + tài liệu dàn giáo HNMU | Không chắc → HNMU review. |
| BEN-PED-02 | Phù hợp lứa tuổi | Ngôn ngữ và bước gợi mở có phù hợp học sinh THCS không? | Agent + HNMU | Không chắc → review. |
| BEN-PED-03 | Không đưa lời giải quá sớm nếu task yêu cầu gợi mở | Gold response có cân bằng giữa hỗ trợ và không làm thay học sinh không? | Agent | Lộ lời giải sai mục tiêu → sửa. |
| BEN-PED-04 | Có giá trị phân biệt tutor | Mẫu có khả năng làm lộ khác biệt giữa tutor tốt/trung bình/kém không? | Agent + thử nghiệm sau | Không rõ → không ưu tiên pilot. |
| BEN-PED-05 | Không mâu thuẫn đáp án/học liệu | Phản hồi lý tưởng không mâu thuẫn SGK/SGV hoặc đáp án. | Agent + retrieval | Mâu thuẫn rõ → `fail`. |

## 9. Checklist trùng/gần trùng và rò rỉ benchmark

| Mã | Tiêu chí | Cách kiểm | Công cụ chính | Quyết định mặc định |
|---|---|---|---|---|
| BEN-DUP-01 | Trùng/gần trùng với mẫu benchmark khác | So sánh input, gold response, đáp án, metadata. | Code | Gộp hoặc chọn đại diện. |
| BEN-DUP-02 | Nhiều mẫu từ cùng raw dialogue | Nếu một raw tạo nhiều mẫu, từng mẫu phải có mục tiêu/task riêng và truy vết rõ. | Code + agent | Mơ hồ → review. |
| BEN-DUP-03 | Rò đáp án trong input | Kiểm input có chứa nội dung làm model chỉ cần chép lại không. | Agent | Rò nghiêm trọng → sửa. |
| BEN-DUP-04 | Lặp khuôn gold response | Nhiều `gold_response` quá giống nhau, làm giảm đa dạng benchmark. | Code + agent | Gắn cờ đa dạng. |

## 10. Điều kiện đưa vào benchmark pilot

Một ứng viên mẫu benchmark chỉ nên đưa vào pilot khi:

1. Có đủ cấu trúc benchmark lõi.
2. Có raw trace và evidence học liệu.
3. Task và rubric áp dụng được.
4. Task được gán phản ánh đúng hành vi gia sư cần đánh giá, và góp phần vào độ phủ task/hành vi gia sư của tập benchmark.
5. `gold_response` là phản hồi gia sư lý tưởng, không chỉ là đáp án.
6. Không có mâu thuẫn rõ với SGK/SGV.
7. Không rò đáp án làm hỏng mục tiêu task.
8. Không trùng/gần trùng nghiêm trọng với mẫu khác.
9. Nếu còn `needs_human_review`, phải có quyết định UET/HNMU trước khi dùng chính thức.

## 11. Giới hạn

- Checklist này chưa thay thế đánh giá chuyên môn HNMU.
- Checklist này không dùng cho raw Excel trực tiếp.
- Checklist này không chấm model; nó chỉ kiểm ứng viên mẫu benchmark trước khi dùng để chấm model.
- Một số tiêu chí cần task/rubric đã ổn định; nếu task/rubric còn thay đổi, kết quả checklist chỉ là tạm thời.
