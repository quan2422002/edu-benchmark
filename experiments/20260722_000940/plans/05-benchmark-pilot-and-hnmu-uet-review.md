# Plan 05 — Chọn benchmark pilot và tổ chức HNMU/UET review

Experiment: `20260722_000940`  
Trạng thái: `DRAFT` — chưa được duyệt, không triển khai  
Ngày lập: 23/07/2026  
Phụ thuộc: Plan 04 hoàn thành

## 1. Mục tiêu

Plan 05 chọn một tập candidate provisional-pass có coverage chủ đích, chuẩn bị gói review dễ dùng cho HNMU/UET, thu quyết định độc lập và phân xử bất đồng trước khi phát hành benchmark pilot v0.

Plan có hai milestone:

- **05A — Packet ready**: chọn mẫu, phân công và tạo gói review;
- **05B — Review completed**: nhập quyết định, phân xử và tạo readiness report.

Nếu mới hoàn thành 05A nhưng chưa nhận phản hồi HNMU/UET, trạng thái phải là `WAITING_FOR_HUMAN_REVIEW`, không được đánh dấu `COMPLETED`.

## 2. Authority và vai trò

### UET/AI engineers

- chuẩn bị candidate, học liệu, trace và form;
- chạy validation;
- không thay giáo viên quyết định chuyên môn/sư phạm.

### HNMU reviewer

- kiểm kiến thức, tính sư phạm, gold response, nguyên tắc/rubric và khả năng dùng để chấm;
- chọn `accept`, `revise`, `reject`, hoặc `abstain`;
- không review chính mẫu mình đã author nếu có thể xác định tác giả.

### Adjudicator

- xem các trường hợp reviewer bất đồng;
- ghi quyết định cuối và rationale;
- không phải là author/reviewer duy nhất của cùng mẫu.

### Pilot participant

- thử dùng form/task card;
- phản hồi độ rõ, thời gian, điểm khó hiểu;
- không mặc nhiên có authority phê duyệt benchmark.

## 3. Decision gates trước khi triển khai

### D05-01 — kích thước pilot

Đề xuất mặc định: 40 candidate, 10 mẫu mỗi lớp.  
Người phụ trách có thể đổi số lượng trước approval dựa vào năng lực reviewer.

### D05-02 — staffing

Cần chốt:

- số reviewer;
- một hay hai reviewer độc lập mỗi mẫu;
- adjudicator;
- thời hạn;
- cách tránh self-review.

Khuyến nghị nghiên cứu: hai reviewer độc lập cho mỗi mẫu; mọi bất đồng và `abstain` đi adjudication. Nếu nguồn lực không đủ, phải ghi rõ sampling/risk.

### D05-03 — release threshold

Cần chốt:

- điều kiện `accept`;
- revision có được sửa và review lại trong cùng plan không;
- mức agreement tối thiểu;
- sample còn evidence `draft` có được vào model-evaluation pilot không.

## 4. Input chỉ đọc

- `outputs/benchmark_candidate_audit/full_v0/candidate_quality_suggestions.csv`
- `outputs/benchmark_candidate_audit/full_v0/candidate_checklist_results.csv`
- `outputs/benchmark_candidate_audit/full_v0/candidate_evidence_links.csv`
- `outputs/benchmark_candidate_audit/full_v0/candidate_duplicate_clusters.csv`
- `outputs/benchmark_candidate_audit/full_v0/candidate_leakage_flags.csv`
- candidate/trace từ Plan 02;
- nguyên tắc/rubric/serious-error/provenance từ Plan 03;
- coverage summary từ Plan 03;
- Plan 04 report.

Chỉ candidate có agent-assisted `candidate_quality_decision = pass` được chọn mặc định. Đây vẫn là provisional pass, không phải HNMU-confirmed pass.

## 5. Cách chọn pilot

Bộ chọn deterministic và versioned.

Ràng buộc cứng:

- đúng kích thước D05-01;
- cân bằng theo lớp trong giới hạn đã chốt;
- không lấy candidate `need_human_review`/`failed`;
- không lấy hai candidate trong cùng duplicate cluster nếu không có lý do;
- đủ trace, evidence link, task và rubric;
- không có leakage/serious-error blocking chưa giải quyết.

Mục tiêu phủ:

- lớp 6–9;
- task v1 đã được Plan 03 chốt;
- `Biết`, `Hiểu`, `Vận dụng`;
- nhiều topic/lesson;
- split strategy;
- dạng input/hành vi học sinh;
- mức độ dài hội thoại.

Không yêu cầu phân bố đều tuyệt đối. Mọi fallback/gap phải ghi vào selection report.

## 6. Teacher review packet

### 6.1. Nội dung giáo viên nhận

Mỗi mẫu hiển thị bằng ngôn ngữ dễ đọc:

- mã mẫu;
- lớp, bài học và vị trí;
- yêu cầu ban đầu của học sinh;
- lịch sử trao đổi;
- phản hồi gia sư dự kiến;
- đáp án chuyên môn;
- trích đoạn học liệu liên quan;
- nguyên tắc/rubric được gợi ý;
- câu hỏi review;
- ô quyết định và lý do.

Không yêu cầu giáo viên thao tác với code, Git, JSON, YAML hoặc cấu hình model.

### 6.2. Task cards bắt buộc

Teacher packet có task card riêng cho:

- reviewer;
- adjudicator;
- pilot participant;
- author/reviser nếu D05-03 cho phép revision.

Mỗi task card phải có:

1. `Mục tiêu`
2. `Vì sao cần task này`
3. `Bạn nhận được gì`
4. `Các bước thực hiện`
5. `Ví dụ đạt yêu cầu`
6. `Ví dụ cần sửa`
7. `Bạn cần nộp gì`
8. `Checklist tự kiểm tra`
9. `Thời gian dự kiến`
10. `Khi cần hỗ trợ`

Mỗi loại việc mới có một ví dụ hoàn chỉnh và một counterexample giải thích vì sao chưa đạt.

### 6.3. Reviewer form

Mỗi review record có:

- `benchmark_candidate_id`
- `reviewer_id`
- `review_round`
- `subject_correctness`
- `pedagogical_quality`
- `task_fit`
- `rubric_usability`
- `evidence_fit`
- `gold_response_quality`
- `decision`
- `reason`
- `requested_revision`
- `reviewed_at`

Các rating/decision phải có hướng dẫn tiếng Việt rõ, không chỉ đưa mã.

## 7. Review và adjudication contract

### Reviewer decisions

- `accept`
- `revise`
- `reject`
- `abstain`

Đây là workflow action, không thay thế canonical quality labels.

### Adjudication

Candidate vào adjudication khi:

- reviewer bất đồng;
- có `abstain`;
- một reviewer phát hiện serious error;
- revision làm thay đổi gold response/task/evidence;
- candidate có edge case được D05-03 chỉ định.

Adjudication record:

- reviewer decisions;
- disagreement dimensions;
- evidence considered;
- final action;
- rationale;
- adjudicator ID và timestamp.

### Final pilot status

- `accepted_for_model_evaluation_pilot`
- `revision_required`
- `rejected_from_pilot`
- `pending_adjudication`

Chỉ status đầu được xuất sang benchmark pilot v0.

## 8. Thay đổi code cụ thể

### 8.1. `src/edu_benchmark/teacher_review/`

Tạo:

- `schema.py`: review/adjudication contracts;
- `pilot_selection.py`: deterministic constrained selection;
- `review_assignment.py`: reviewer assignment và self-review checks;
- `packet.py`: teacher-friendly tables/workbook;
- `review_ingest.py`: validate returned forms;
- `adjudication.py`: build disagreement queue và apply recorded human decisions;
- `readiness.py`: agreement/coverage/readiness metrics;
- `pipeline.py`: orchestration.

### 8.2. CLI

Tạo:

- `scripts/teacher_review/build_benchmark_pilot_packet.py`
- `scripts/teacher_review/validate_returned_reviews.py`
- `scripts/teacher_review/build_adjudication_queue.py`
- `scripts/teacher_review/build_benchmark_pilot_release.py`

Script không tự tạo quyết định con người.

`packet.py` phải giữ canonical CSV làm source of truth và tạo workbook `.xlsx` bằng writer có test trong package (standard-library OpenXML hoặc dependency đã được project phê duyệt). Không được thêm package vào môi trường ngoài một plan/approval dependency rõ ràng.

### 8.3. Teacher collaboration skill khi plan được duyệt

Được dùng một `teacher-collaboration-designer` để soạn role definitions, task cards, examples, counterexamples và feedback questions.

Allowed writes riêng:

`outputs/benchmark_pilot/pilot_v0/teacher_packet_draft/`

Orchestrator chạy `scripts/validate_teacher_packet.py`, rà ngôn ngữ và merge sang packet phát hành. Không fan-out nhiều instance.

### 8.4. Tests

Tạo `tests/teacher_review/`:

- `test_pilot_selection.py`
- `test_review_assignment.py`
- `test_review_schema.py`
- `test_adjudication.py`
- `test_readiness.py`
- `test_teacher_review_pipeline.py`

Test tối thiểu:

1. chỉ provisional-pass candidate được chọn;
2. selection size và grade quota đúng;
3. duplicate cluster constraint;
4. deterministic selection;
5. reviewer không review sample của chính mình khi author mapping có;
6. reviewer assignment count đúng D05-02;
7. unknown decision/rating bị reject;
8. review thiếu reason khi `revise/reject` bị reject;
9. disagreement vào adjudication;
10. code không tự điền adjudicator decision;
11. final release chỉ gồm accepted status;
12. coverage/readiness counts khớp;
13. teacher packet validator pass.

## 9. Quy trình thực hiện

### Milestone 05A

1. Chốt D05-01, D05-02 và D05-03.
2. Chọn pilot deterministic.
3. Tạo role definitions và task cards.
4. Tạo reviewer assignments.
5. Sinh packet đọc được và canonical internal tables.
6. Chạy packet/usability validation.
7. Gửi cho HNMU/UET qua kênh do người phụ trách dự án thực hiện.

### Milestone 05B

1. Nhận form review.
2. Validate completeness/identity/decision.
3. Tạo disagreement/adjudication queue.
4. Nhập quyết định adjudicator; không để code quyết định.
5. Nếu có revision, tạo version mới và review lại theo D05-03.
6. Build accepted pilot release.
7. Tính agreement, coverage và readiness.
8. Viết report/handoff.

## 10. Output dự kiến

### Selection và packet

`outputs/benchmark_pilot/pilot_v0/`

- `pilot_selection.csv`
- `pilot_selection_summary.json`
- `review_assignments.csv`
- `benchmark_pilot_review_source.csv`
- `benchmark_pilot_review_packet.xlsx`

`outputs/benchmark_pilot/pilot_v0/teacher_packet/`

- `role_definitions.md`
- `reviewer_task_card.md`
- `adjudicator_task_card.md`
- `pilot_participant_task_card.md`
- `revision_task_card.md` nếu áp dụng;
- `review_examples.md`
- `pilot_feedback_questions.md`

### Review/adjudication/release

- `returned_reviews.csv`
- `review_validation_errors.csv`
- `adjudication_queue.csv`
- `adjudication_decisions.csv`
- `benchmark_samples_pilot_v0.csv`
- `pilot_coverage_summary.csv`
- `pilot_readiness_metrics.json`

### Report/handoff

- `reports/plan05-benchmark-pilot-readiness-summary.md`
- `handoffs/plan05-benchmark-pilot-and-review.md`
- coordination events append-only.

## 11. Allowed writes

Khi được duyệt:

- `src/edu_benchmark/teacher_review/`
- `scripts/teacher_review/`
- `tests/teacher_review/`
- `experiments/20260722_000940/outputs/benchmark_pilot/`
- `experiments/20260722_000940/reports/plan05-*`
- `experiments/20260722_000940/handoffs/plan05-*`
- coordination logs append-only;
- `README.md`, `ARCHITECTURE.md` khi status/component thay đổi.

Không sửa candidate/audit/spec source từ Plan 02–04. Revision phải tạo version mới và giữ provenance.

## 12. Cổng hoàn thành

### Gate 05A

1. Decision gates được chốt.
2. Selection deterministic và coverage/fallback được báo cáo.
3. Reviewer assignment không vi phạm self-review.
4. Task cards đủ role, action, examples, counterexamples, self-check và escalation.
5. Packet validator pass.

### Gate 05B

1. Mọi selected candidate có đủ review theo D05-02 hoặc disposition rõ.
2. Mọi disagreement/abstain được adjudicate.
3. Không có human decision do code/agent tự điền.
4. Release chỉ gồm candidate accepted.
5. Agreement, coverage và unresolved risks được báo cáo.
6. HNMU authority và mọi revision được truy vết.
7. Tests/validators pass bằng `benchmark_env`.

## 13. Ngoài phạm vi

- Không gửi email/tin nhắn cho HNMU nếu người phụ trách chưa yêu cầu.
- Không chấm model.
- Không công bố benchmark chính thức.
- Không đưa candidate chưa review vào production benchmark.
- Không commit.
