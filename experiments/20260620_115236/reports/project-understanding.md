# Ghi nhận hiểu biết ban đầu về dự án

## Mục đích tài liệu

Tài liệu này ghi lại hiểu biết của Codex sau khi đọc tài liệu tổng quan, roadmap hiện hành, các plan, specialist agents, validators/tests, artifact thử nghiệm và tài liệu nguồn trong repository.

Đây là báo cáo định hướng để làm việc đúng bối cảnh. Nó không phải plan triển khai, không phê duyệt taxonomy/dataset/rubric và không thay thế quyết định của project lead hoặc expert teachers.

## 1. Mục tiêu nghiên cứu

Dự án hướng tới một benchmark human-in-the-loop để đánh giá cách LLM đóng vai gia sư môn Tin học lớp 9 bằng tiếng Việt.

Đối tượng đánh giá trước mắt là **hành vi gia sư** của mô hình, chẳng hạn:

- hiểu đúng kiến thức và bài làm của học sinh;
- phát hiện lỗi hoặc misconception;
- giải thích phù hợp với mức hiểu hiện tại;
- đưa phản hồi và gợi ý đúng mức;
- hỗ trợ học sinh tự suy nghĩ thay vì tiết lộ lời giải quá sớm;
- duy trì chiến lược sư phạm qua hội thoại nhiều lượt.

Benchmark phản hồi của mô hình chỉ tạo proxy cho chất lượng tutoring behavior. Nó chưa đủ để kết luận học sinh học tốt hơn. Tuyên bố về learning gain sẽ cần một learner study riêng, có thiết kế thực nghiệm và yêu cầu đạo đức phù hợp.

Mục tiêu dài hạn của project lead là phát triển dự án trong khoảng 6–12 tháng và hướng tới ít nhất một công bố tại hội nghị có thứ hạng cao. Tuy nhiên, repository hiện mới ở giai đoạn proof of concept.

## 2. Trạng thái hiện tại

Roadmap hiện hành là [`../roadmap.md`](../roadmap.md). Kế hoạch tổng ngày 18/06/2026 đã được thay thế bởi hệ thống plan mô-đun và chỉ còn là tài liệu nền.

Trạng thái thực tế:

- P01 — specialist-agent foundation: đã triển khai, nhưng còn chờ kiểm tra custom-agent discovery trong một phiên Codex mới;
- P02 — literature review PoC: `DRAFT_FOR_REVIEW`, chưa được phép triển khai;
- P03 — human-in-the-loop teacher workflow: `DRAFT_FOR_REVIEW`, chưa được phép triển khai;
- P04 — teacher pilot packet: `DRAFT_FOR_REVIEW`, chưa được phép triển khai;
- P05 — benchmark specification: chưa viết;
- P06 — dataset tooling: chưa viết;
- P07 — evaluation pipeline: chưa viết;
- P08 — workspace isolation và evaluator integrity: backlog, ghi rõ `NOT_APPROVED`.

Vì vậy, repository chưa có benchmark taxonomy chính thức, production dataset, rubric đã kiểm định hoặc evaluation pipeline. Những nội dung tương ứng trong plan cũ và `dataset_v0/` chỉ là giả thuyết/prototype để tham khảo.

## 3. Nền tảng nghiên cứu ban đầu

Slide nguồn đề xuất bốn nhóm tiêu chí rộng cho benchmark giáo dục:

1. năng lực học thuật và tư duy;
2. năng lực sư phạm và tương tác;
3. an toàn, đạo đức và guardrails;
4. hiệu năng kỹ thuật và bản địa hóa.

Với Tin học THCS, slide nhấn mạnh tư duy giàn giáo, phân rã bài toán, phát hiện lỗi, trực quan hóa, an toàn số và liêm chính học tập. Đây là định hướng ban đầu, chưa phải taxonomy đã được evidence review và teacher review.

Hai paper được cung cấp tạo ngữ cảnh quan trọng:

- **MathTutorBench** phân biệt subject expertise, student understanding và pedagogical ability; kết quả của paper cho thấy giải bài tốt không tự động đồng nghĩa với dạy tốt, đồng thời tutoring dài lượt khó hơn.
- **TutorBench** tập trung vào adaptive explanation, assessment/feedback và active-learning support; dữ liệu do chuyên gia xây dựng và mỗi sample có rubric riêng để LLM judge chấm.

Hai công trình này hỗ trợ giả thuyết rằng benchmark cần đánh giá nhiều hơn factual correctness. Tuy nhiên, chúng chủ yếu thuộc Toán/STEM ở bậc học hoặc bối cảnh khác, nên không đủ để khóa benchmark cho Tin học lớp 9 Việt Nam. Đây chính là lý do P02 yêu cầu rapid evidence review rộng hơn trước khi đề xuất taxonomy, task family hoặc rubric chính thức.

## 4. Mô hình human-in-the-loop

Dự án phân quyền rõ giữa hai nhóm:

- **AI engineers** chịu trách nhiệm về repository, schema, provenance, validators, model runner và evaluation infrastructure.
- **Expert teachers** chịu trách nhiệm về tính đúng chuyên môn, độ phù hợp lớp 9, quyết định sư phạm, authoring/review và adjudication nội dung.

Agent có thể tổng hợp bằng chứng, chuẩn hóa quy trình và chuyển yêu cầu thành hướng dẫn dễ làm. Agent không được tự coi phán đoán của mình là ground truth sư phạm và không thay expert teachers quyết định nội dung.

Thiết kế dự kiến cho teacher workflow tách bốn vai trò:

- Teacher Author tạo tình huống học sinh và tiêu chí mong đợi;
- Teacher Reviewer kiểm tra độc lập và đưa quyết định;
- Teacher Adjudicator giải quyết bất đồng;
- Teacher Pilot Participant kiểm tra độ rõ ràng và khả dụng của hướng dẫn.

Một người không được vừa author vừa là reviewer cuối cho cùng sample. Engineering format check chỉ kiểm tra cấu trúc/thiếu trường, không được biến thành phán quyết chuyên môn.

## 5. Kiến trúc agent hiện có

P01 đã tạo hai specialist tối thiểu:

### `research-methodologist`

Specialist này thiết kế protocol, ghi search/screening log, xây evidence matrix, tổng hợp có truy vết và phân biệt:

- `evidence`: được nguồn hỗ trợ trực tiếp;
- `inference`: suy luận vượt ra ngoài phát biểu trực tiếp của nguồn;
- `open_question`: vấn đề chưa giải quyết hoặc cần con người quyết định.

Evidence matrix có 19 trường bắt buộc, bao gồm publication status, learner level, human expert role, reliability evidence, relevance với dự án và vị trí bằng chứng trong paper. Validator hiện kiểm tra cấu trúc cột, record/title trùng, URL/DOI, publication status và relevance note.

### `teacher-collaboration-designer`

Specialist này chuyển research requirements thành task card và workflow dễ hiểu với giáo viên. Task card phải có mục tiêu, input, các bước, ví dụ đạt/chưa đạt, output, checklist, thời gian và nơi hỗ trợ.

Validator hiện kiểm tra sự tồn tại của packet, headings bắt buộc, template author/reviewer, một số thuật ngữ kỹ thuật bị cấm trong nội dung dành cho giáo viên và việc author bị giao nhầm quyền quyết định của reviewer.

### Canonical source và runtime adapters

Logic chuẩn nằm trong `agents/<name>/SKILL.md` và resources đi kèm. Các file dưới `.codex/agents/`, `.claude/agents/` và `.agents/skills/` chỉ là adapter/discovery layer mỏng, không được fork quy trình chuyên môn.

Runtime tương tác phải dùng native, observable subagent threads. Nested `codex exec`, `claude -p`, daemon hoặc hidden terminal agent bị cấm. Khi runtime không hiển thị được specialist activity, orchestrator phải fail closed hoặc tải canonical skill và làm trong parent thread ở chế độ single-agent.

## 6. Observability và coordination

Mỗi delegation hợp lệ phải có:

1. thông báo trước về specialist, task, input, quyền ghi và output;
2. native thread có thể quan sát khi runtime hỗ trợ;
3. event append-only theo schema trong `experiments/_templates/`;
4. handoff ghi prompt, steer messages, artifact, kết quả, quyết định, uncertainty và câu hỏi còn mở.

P01 đã có ba forward-test handoff:

- research specialist nhận ra thiếu evidence, từ chối suy diễn learning gain và giới hạn khả năng chuyển kết quả sang Tin học lớp 9 Việt Nam;
- lần chạy đầu của teacher specialist lộ hai lỗi về thuật ngữ kỹ thuật và chồng lấn vai trò;
- canonical skill/validator được siết lại và lần chạy mới đã pass behavioral test.

Custom-agent discovery theo tên chưa pass trong phiên tạo adapter vì runtime chỉ nạp adapter lúc bắt đầu session. Report P01 yêu cầu kiểm tra lại trong một phiên Codex CLI/App mới trước khi đánh dấu hoàn tất và push.

## 7. Prototype dữ liệu cũ

`experiments/20260618_150902/dataset_v0/` chứa một manifest tối giản, ba sample minh họa và CSV template cho giáo viên.

Ý tưởng hữu ích của prototype:

- metadata chung nằm ở cấp dataset;
- giáo viên tập trung vào `topic`, `student_prompt`, `student_work`, 2–5 criteria và optional example response;
- ID/version/provenance có thể do engineering bổ sung;
- example response chỉ là một cách trả lời tốt, không phải đáp án duy nhất.

Ba sample hiện minh họa lỗi thụt lề, yêu cầu viết hộ chương trình và việc mới truy cập một phần tử thay vì duyệt danh sách.

Tuy nhiên:

- `curriculum_source` vẫn là `null`;
- coverage chương trình lớp 9 chưa được xác nhận;
- task family, criteria và sample chưa qua literature review đầy đủ;
- prototype không được gửi như benchmark specification hay teacher packet chính thức.

P04 có thể dùng chúng làm raw examples, nhưng phải review và viết lại theo bằng chứng P02 cùng workflow P03.

## 8. Hướng đi mô-đun

Critical path được thiết kế như sau:

```text
P01 specialist foundation
  → P02 traceable literature review
  → P03 teacher roles and task contracts
  → P04 teacher pilot packet
  → P05 benchmark specification
  → P06 dataset tooling
  → P07 evaluation pipeline
```

P02 phải tạo search protocol, search/screening logs, evidence matrix, bibliography, rapid review, research gaps và teacher-relevant findings. Mọi benchmark implication phải có nguồn hoặc được gắn là hypothesis.

P03 biến bằng chứng và yêu cầu thành workflow giáo viên không đòi hỏi kỹ năng kỹ thuật.`IMPL

P04 tạo packet nhỏ để giáo viên có thể tự author/review sample, có cả ví dụ đạt và chưa đạt, feedback form và open questions. Nếu chưa pilot với giáo viên thật, trạng thái tối đa chỉ là `READY_FOR_TEACHER_PILOT`.

P05–P07 chỉ nên bắt đầu sau khi upstream artifacts được review. Cách tổ chức này nhằm tránh việc prototype sớm vô tình trở thành “benchmark v1”.

## 9. Các ranh giới cần giữ

- Không triển khai plan chưa ghi rõ `APPROVED`.
- Chỉ sửa path thuộc ownership của plan đang active.
- Không khóa taxonomy từ hai paper seed.
- Không suy rộng kết quả từ môn Toán, cấp THPT/AP hoặc tiếng Anh sang Tin học lớp 9 tiếng Việt mà không nêu limitation.
- Không dùng LLM judge làm nguồn chân lý duy nhất.
- Không coi response quality là learning outcome.
- Không yêu cầu giáo viên làm việc kỹ thuật.
- Không thu thập hoặc dùng dữ liệu học sinh thật trong MVP nếu chưa có consent, de-identification và ethics review.
- Không mô tả worktree/prompt instruction như một security sandbox; P08 nêu rõ P01 hiện mới có process controls, chưa có filesystem enforcement.
- Không sửa hoặc nới evaluator trong cùng task tạo sản phẩm đang được evaluator đó chấm.

## 10. Các quyết định nghiên cứu còn mở

Những câu hỏi quan trọng chưa được chốt gồm:

- nguồn chương trình, bộ sách hoặc giáo trình Tin học lớp 9 chuẩn;
- topic/learning objectives được đưa vào benchmark đầu tiên;
- ngôn ngữ lập trình cần hỗ trợ;
- target venue và timeline submission;
- quy mô/ngân sách cho expert annotation và API;
- nguồn student errors/misconceptions;
- cách xây human gold set và ngưỡng agreement;
- chiến lược judge calibration, hidden test và contamination control;
- cách tách điểm chuyên môn, hiểu học sinh và sư phạm;
- điều kiện để mở rộng sang multimodal, safety track hoặc learner study.

Các câu hỏi này cần evidence từ P02, quyết định của project lead và phán quyết của expert teachers; không nên được Codex tự chốt.

## 11. Cách Codex nên làm việc tiếp trong repository

Trước mỗi thay đổi, Codex cần:

1. đọc roadmap và plan liên quan;
2. xác nhận plan đã được duyệt và path ownership;
3. bảo toàn mọi thay đổi không liên quan của người dùng;
4. khai báo rõ delegation nếu dùng specialist;
5. dùng đúng specialist canonical hoặc single-agent fallback;
6. ghi coordination events/handoff cho delegation;
7. chạy validators/tests liên quan bằng đúng executable:
   `/home/quannda/miniconda3/envs/benchmark_env/bin/python`;
8. cập nhật `ARCHITECTURE.md` khi component/runtime/ownership thay đổi;
9. cập nhật `README.md` khi onboarding, command hoặc trạng thái dự án thay đổi;
10. báo cáo trung thực phần đã kiểm tra, phần chưa kiểm tra và quyết định còn cần con người.

Trong môi trường Windows hiện tại, đường dẫn Python Linux bắt buộc không thể chạy trực tiếp và WSL chưa được cài. Đây là hạn chế runtime cần nêu rõ nếu một task sau yêu cầu validation; không được âm thầm dùng system Python hoặc Conda base để thay thế.

## 12. Kết luận

Dự án hiện có một nền móng quản trị và specialist-agent khá rõ, nhưng phần benchmark khoa học vẫn chủ ý để mở. Giá trị quan trọng nhất của giai đoạn hiện tại không phải là nhanh chóng tạo nhiều sample, mà là xây chuỗi truy vết:

```text
evidence
  → provisional requirement
  → teacher task
  → human decision
  → benchmark specification
  → dataset/evaluation artifact
```

Nếu giữ đúng chuỗi này, repository có thể phát triển từ PoC nhỏ thành một benchmark có cơ sở nghiên cứu, có trách nhiệm và đủ khả năng audit để phục vụ công bố khoa học.

## Tài liệu đã đọc

- `README.md`, `ARCHITECTURE.md`, `AGENTS.md`;
- roadmap, P01–P04 và P08;
- P01 implementation report, metadata, coordination schema/log và handoffs;
- canonical skills, references, validators, adapters và tests của hai specialist;
- plan nền ngày 18/06/2026 và prototype `dataset_v0`;
- `user_diary.md`;
- slide dự án;
- MathTutorBench (`2502.18940v2`);
- TutorBench (`2510.02663v1`).

Ghi nhận ngày 20/06/2026, theo trạng thái repository tại thời điểm đọc.
