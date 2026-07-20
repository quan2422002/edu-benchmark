# Roadmap mô-đun cho PoC

## 1. Lý do thay đổi

Plan ngày 18/06/2026 chứa quá nhiều quyết định nghiên cứu, kiến trúc, agent, dataset và evaluation trong một tài liệu. Cách tổ chức đó khó duyệt từng phần, làm tăng rủi ro sửa chồng chéo và tạo cảm giác taxonomy benchmark đã được xác lập dù literature review mới dựa trên hai paper.

Từ ngày 20/06/2026, plan cũ chỉ là tài liệu nền. Mọi phần việc mới phải có plan độc lập, acceptance criteria, test và phạm vi file rõ ràng.

## 2. Nguyên tắc quản trị plan

- Mỗi plan giải quyết một mục tiêu chính và có thể duyệt riêng.
- Mỗi file/thành phần có một plan sở hữu chính; plan sau không sửa artifact đã ổn định nếu không có migration plan.
- Chỉ triển khai plan có trạng thái `APPROVED`.
- Sau triển khai phải chạy test, ghi report và chỉ push GitHub khi acceptance criteria đạt.
- Thay đổi ngoài scope phải tạo plan mới hoặc quay lại bước review.
- PoC ưu tiên ít thành phần nhưng chạy được, dễ giải thích và có bằng chứng.

## 3. Human-in-the-loop là ràng buộc bắt buộc

Hệ thống gồm hai nhóm phối hợp:

- **AI engineers:** xây codebase, schema, công cụ, model runner, validator và hạ tầng tái lập.
- **Expert teachers:** tạo/review/adjudicate nội dung chuyên môn và sư phạm. Giáo viên không phải viết code, sửa YAML hoặc hiểu pipeline kỹ thuật.

Agent hỗ trợ chuẩn hóa quy trình, tổng hợp nghiên cứu và tạo chỉ dẫn; agent không thay thế phán quyết chuyên môn của giáo viên.

## 4. Thứ tự các plan


| ID  | Plan                                                                                                     | Có thể chạy                                                       | Phụ thuộc                                            | Ưu tiên                   |
| --- | -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------ | --------------------------- |
| P01 | [Specialist-agent foundation](plans/01-specialist-agent-foundation.md)                                   | Tuần tự đầu tiên                                                | Không                                                 | Khẩn cấp                  |
| P02 | [Literature review PoC](plans/02-literature-review-poc.md)                                               | Sau P01; lập bài báo hạt giống độc lập với F01, chỉ dùng F01 để đối chiếu sau | P01, C01/F01                                           | Cao — full version         |
| P03 | [Human-in-the-loop teacher workflow](plans/03-human-in-the-loop-teacher-workflow.md)                     | Song song với P02; tham khảo teacher artifacts từ F01 nhưng thiết kế lại theo luận giải mới | P01, C01/F01                                           | Cao — full version         |
| P04 | [Teacher pilot packet](plans/04-teacher-pilot-packet.md)                                                 | Tạo packet mới sau P02/P03; F01 chỉ là ví dụ tham khảo và nguồn phản hồi lịch sử | P02/P03 refinements, C01/F01                           | Cao — teacher review/pilot |
| P05 | Benchmark specification and provenance contract                                                          | Sau full review/teacher feedback                                     | P02, P03, P04, C01/F01                                 | Chưa viết                 |
| P06 | Learning-resource and benchmark data platform                                                            | Sau khi contract dữ liệu đủ ổn định; có thể thiết kế sớm | P05 cho schema benchmark; C01/F01 làm prototype input | Chưa viết                 |
| P07 | Evaluation pipeline                                                                                      | Sau benchmark specification                                          | P05                                                    | Chưa viết                 |
| P08 | [Agent workspace isolation and evaluator integrity](plans/08-agent-workspace-and-evaluator-hardening.md) | Hậu PoC, trước production-scale parallel writes/quality gates     | P01; phối hợp P06/P07                                | Backlog, chưa phê duyệt  |

## 5. Critical path lịch sử tới chiều Chủ nhật 21/06/2026

Mục này là bối cảnh lịch sử của deadline tuần trước. C01/F01 đã được tạo như flash plans để kịp có gói bàn giao sơ bộ. Từ sau 23/06/2026, roadmap không coi C01/F01 là bản thay thế cho P02–P07 full version.

1. Duyệt P01 và P03.
2. Xây/validate hai specialist agent tối thiểu của P01.
3. Chạy P02 ở chế độ rapid evidence review và tạo kết quả sơ bộ có truy vết nguồn.
4. Dùng P03 chuyển bằng chứng sơ bộ thành vai trò và task rõ ràng cho giáo viên.
5. Thực hiện P04 để tạo teacher packet gồm chỉ dẫn, task cards, checklist và sample minh họa.

Nếu không đủ thời gian, ưu tiên chất lượng protocol và tính minh bạch. Không gọi taxonomy hoặc sample là “benchmark v1” khi chưa qua literature review và teacher review.

### Hướng tiếp theo sau F01

1. Giáo viên chuyên môn thẩm định gói C01/F01 và ghi quyết định/rationale.
2. P02/P03 full version review lại F01 như tài liệu tham khảo: chỉ giữ ý nào có bằng chứng, luận giải mới và teacher decision; không bê nguyên task/rubric/sample/schema từ F01.
3. P05 chốt benchmark specification và provenance contract dựa trên teacher feedback.
4. P06 thiết kế database học liệu/benchmark trước khi scale authoring/review.
5. P07 chỉ bắt đầu evaluation pipeline khi task/sample/rubric đã có version snapshot rõ ràng.

## 6. Ranh giới artifact để hạn chế sửa chồng chéo


| Plan | Sở hữu chính                                                                                              |
| ---- | ------------------------------------------------------------------------------------------------------------ |
| P01  | `agents/`, adapter agent/skill, agent validation tests                                                       |
| P02  | literature protocol, evidence matrix, review và research gaps trong experiment riêng                       |
| P03  | role model, teacher task contracts, handoff và review workflow                                              |
| P04  | teacher-facing packet, form/template và provisional examples                                                |
| P05  | benchmark taxonomy, task definitions, rubric specification, provenance contract                              |
| P06  | learning-resource registry, benchmark database, teacher-facing lookup/update workflow và dataset versioning |
| P07  | inference, judge, metrics và reporting                                                                      |
| P08  | workspace isolation, write leases, protected evaluator boundary và integration gates                        |

## 7. Trạng thái artifact hiện có

- `experiments/20260618_150902/plan.md`: tài liệu nền, không còn là unit phê duyệt.
- `dataset_design_v0.md` và `dataset_v0/`: prototype minh họa trước literature review; không gửi như đặc tả benchmark chính thức cho giáo viên cho tới khi P04 duyệt hoặc thay thế.
- Hai paper cũ đã cung cấp ngữ cảnh ban đầu nhưng không đủ để chốt khung benchmark.
- `experiments/20260621_052024/`: C01 flash plan, tạo curriculum grounding và 18 mẫu có tham chiếu học liệu/chương trình để kịp bàn giao; đây là input tham khảo quan trọng cho P05/P06 nhưng chưa phải dataset chính thức.
- `experiments/20260621_135515/`: F01 flash plan, tích hợp mini P02–P05 để tạo khung benchmark ứng viên và teacher handoff; không đánh dấu P02–P05 là hoàn thành và không được dùng như nguồn để lấy nguyên task/rubric/sample cho phiên bản sau.
- P08 là hardening plan để dành sau PoC; không được triển khai cho tới khi trạng thái được đổi rõ ràng thành `APPROVED`.

## 8. Ghi chú sau C01/F01: học liệu là dependency bắt buộc

C01/F01 cho thấy benchmark không thể chỉ có task và rubric trừu tượng. Mỗi sample cần truy vết được tới một hoặc nhiều căn cứ học liệu/chương trình cụ thể. Giáo viên khi tạo hoặc thẩm định sample cần có cách dễ dàng:

- tìm học liệu phù hợp;
- trích đúng đoạn, bài, bảng, câu hỏi hoặc artifact gốc;
- lấy mã tham chiếu ổn định;
- gắn nhiều mã học liệu vào câu hỏi học sinh, bài làm, phản hồi tutor và tiêu chí rubric;
- thấy học liệu đó đang còn hiệu lực, đã bị sửa, bị thay thế hay bị ngừng dùng.

Kho học liệu không cố định. Vì vậy P06 không nên chỉ là “dataset tooling” dạng file CSV. P06 cần trở thành một data platform tối thiểu để quản lý đồng thời học liệu, task benchmark, sample, rubric, review và version snapshot.

## 9. Thiết kế định hướng cho P06 database học liệu/benchmark

### 9.1. Nguyên tắc dữ liệu

- Học liệu gốc được quản lý theo version bất biến; sửa học liệu tạo version mới thay vì ghi đè version cũ.
- Benchmark sample phải tham chiếu tới version/fragment cụ thể, không chỉ tới tên file hoặc URL chung.
- Xóa học liệu nên là `retire/tombstone`; không hard-delete version đã được benchmark release dùng.
- Mỗi benchmark release phải snapshot chính xác task version, sample revision, rubric version và học liệu fragment version.
- Mã giáo viên sử dụng phải ổn định, dễ đọc và có thể copy, ví dụ `LM-016#F003`, nhưng database vẫn giữ khóa nội bộ riêng.
- Search/semantic retrieval có thể hỗ trợ tìm kiếm, nhưng nguồn chân lý vẫn là record versioned có hash, location và reviewer decision.

### 9.2. Entity cốt lõi đề xuất

P06 nên thiết kế tối thiểu các nhóm bảng sau:

```text
learning_resource
resource_version
resource_fragment
benchmark_task
task_version
rubric_dimension
rubric_version
benchmark_sample
sample_revision
sample_resource_reference
teacher_review
adjudication_decision
benchmark_release
release_snapshot
```

Ý nghĩa chính:

- `learning_resource`: tài nguyên logic như sách, bài học, workbook, file Scratch, PDF chương trình.
- `resource_version`: một phiên bản cụ thể của tài nguyên, có hash, ngày nhập, nguồn, trạng thái và người nhập.
- `resource_fragment`: đoạn/bài/bảng/câu hỏi/vùng nội dung có thể được giáo viên trích dẫn.
- `benchmark_task` và `task_version`: định nghĩa nhóm nhiệm vụ và các thay đổi qua thời gian.
- `rubric_dimension` và `rubric_version`: tiêu chí, anchor, lỗi nghiêm trọng và trạng thái hiệu chuẩn.
- `benchmark_sample` và `sample_revision`: sample logic và từng lần sửa.
- `sample_resource_reference`: bảng nối nhiều-nhiều giữa sample revision/rubric criterion và học liệu fragment; có vai trò như `question_basis`, `student_work_basis`, `expected_tutor_basis`, `rubric_basis`.
- `teacher_review`: review độc lập của giáo viên, gồm điểm, quyết định, rationale và câu hỏi mở.
- `adjudication_decision`: quyết định phân xử khi có bất đồng.
- `benchmark_release` và `release_snapshot`: đóng băng một tập task/sample/rubric/resource version để chạy evaluation tái lập.

### 9.3. Workflow dành cho giáo viên

P06 cần ưu tiên giao diện hoặc workflow quen thuộc, không yêu cầu giáo viên viết SQL/YAML/Git:

1. AI engineer hoặc giáo viên được phân quyền upload/thêm học liệu.
2. Hệ thống tự tạo `resource_version`, hash và bản trích xuất xem trước.
3. Người phụ trách chia/chỉnh fragment bằng giao diện đọc được: bài, mục, bảng, câu hỏi, đoạn văn, file đính kèm.
4. Giáo viên tìm kiếm theo lớp, chủ đề, bài, từ khóa, loại tài nguyên hoặc mã chương trình.
5. Giáo viên copy/chọn mã fragment khi tạo sample; hệ thống tự ghi reference link.
6. Khi học liệu bị sửa/xóa, hệ thống hiển thị sample nào bị ảnh hưởng và cần review lại.
7. Khi chốt release, hệ thống đóng băng version để evaluation không đổi theo kho học liệu đang sống.

### 9.4. Phần có thể học từ C01/F01

C01/F01 chỉ là nguồn tham khảo lịch sử và prototype input. P06/P05 có thể học
cách F01 truy vết nguồn, đặt mã, tổ chức teacher packet và ghi rationale, nhưng
không được mặc định kế thừa nguyên taxonomy, rubric, sample, schema hoặc script
của F01. Mọi phần lấy lại từ F01 phải được đối chiếu với literature review đầy đủ,
chương trình/học liệu đã version hóa và quyết định của giáo viên.

Có thể tái sử dụng về mặt thiết kế:

- `source_registry.csv`: ý tưởng source có authority role và hash.
- `grade9_reference_matrix.csv` / `curriculum_reference_matrix.csv`: reference phải có page, section/table, location note và paraphrase.
- `reference_contract.md`: phân biệt curriculum, research, internal draft và evidence status.
- `example_source_registry.csv`: ánh xạ `material_id` tới file học liệu, vị trí bài tập, sample IDs và SHA-256.
- `traceability_matrix.csv`: nối task, curriculum reference, literature reference, rubric criteria và sample.
- teacher packet/review form: gợi ý workflow để giáo viên chọn, review và ghi rationale.

Không nên bê nguyên thành production code:

- `_extract_learning_materials.py` hard-code danh sách file và chỉ trích xuất DOCX thô.
- `_revise_f01_examples.py` nhúng sample, workbook update và DOCX generation trong một script lớn.
- CSV/Markdown hiện chỉ phù hợp audit nhanh, chưa đủ transaction, permission, version lifecycle hoặc concurrent edit.
- artifact F01 là snapshot ứng viên, chưa phải schema bền vững cho P06.

### 9.5. Quyết định kỹ thuật để dành cho plan P06

P06 khi viết plan cần quyết định:

- database mặc định là PostgreSQL ngay từ đầu hay SQLite prototype rồi migrate;
- file gốc lưu trong database, filesystem content-addressed hay object storage;
- fragmenting strategy cho PDF, DOCX, XLSX, Scratch/project files và hình ảnh;
- có cần full-text search trước hay thêm vector search sau;
- mô hình permission cho AI engineer, teacher author, reviewer và adjudicator;
- import/export format để giáo viên vẫn có thể dùng Excel/Docs khi cần;
- migration từ C01/F01 vào database hay chỉ dùng làm tài liệu tham khảo; mặc định nên ưu tiên tham khảo và nhập lại có kiểm soát thay vì import nguyên trạng.

## 10. Agent token/cost policy sau F01

F01 cho thấy việc spawn nhiều `research-methodologist` cùng lúc có thể rất tốn token. Từ sau ngày 23/06/2026:

- `research-methodologist` được pin mặc định sang `gpt-5.4-mini` trong Codex adapter;
- orchestrator không spawn nhiều instance của cùng một specialist trong một task nếu người dùng chưa duyệt rõ số lượng và lý do;
- literature/database work nên ưu tiên chia theo artifact hoặc câu hỏi cụ thể, không fan-out rộng chỉ vì có thể;
- khi cần full-depth reasoning, orchestrator phải nói rõ tradeoff chi phí/chất lượng trước khi nâng model hoặc tăng số agent.
