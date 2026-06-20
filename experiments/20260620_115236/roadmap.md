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

| ID | Plan | Có thể chạy | Phụ thuộc | Ưu tiên |
|---|---|---|---|---|
| P01 | [Specialist-agent foundation](plans/01-specialist-agent-foundation.md) | Tuần tự đầu tiên | Không | Khẩn cấp |
| P02 | [Literature review PoC](plans/02-literature-review-poc.md) | Sau P01 | P01 | Khẩn cấp |
| P03 | [Human-in-the-loop teacher workflow](plans/03-human-in-the-loop-teacher-workflow.md) | Song song với P01/P02 | Không phụ thuộc code | Khẩn cấp |
| P04 | [Teacher pilot packet](plans/04-teacher-pilot-packet.md) | Sau kết quả sơ bộ P02 và P03 | P02, P03 | Deadline 21/06/2026 |
| P05 | Benchmark specification | Sau PoC | P02, P04 | Chưa viết |
| P06 | Dataset tooling | Sau schema được duyệt | P05 | Chưa viết |
| P07 | Evaluation pipeline | Sau benchmark specification | P05 | Chưa viết |
| P08 | [Agent workspace isolation and evaluator integrity](plans/08-agent-workspace-and-evaluator-hardening.md) | Hậu PoC, trước production-scale parallel writes/quality gates | P01; phối hợp P06/P07 | Backlog, chưa phê duyệt |

## 5. Critical path tới chiều Chủ nhật 21/06/2026

1. Duyệt P01 và P03.
2. Xây/validate hai specialist agent tối thiểu của P01.
3. Chạy P02 ở chế độ rapid evidence review và tạo kết quả sơ bộ có truy vết nguồn.
4. Dùng P03 chuyển bằng chứng sơ bộ thành vai trò và task rõ ràng cho giáo viên.
5. Thực hiện P04 để tạo teacher packet gồm chỉ dẫn, task cards, checklist và sample minh họa.

Nếu không đủ thời gian, ưu tiên chất lượng protocol và tính minh bạch. Không gọi taxonomy hoặc sample là “benchmark v1” khi chưa qua literature review và teacher review.

## 6. Ranh giới artifact để hạn chế sửa chồng chéo

| Plan | Sở hữu chính |
|---|---|
| P01 | `agents/`, adapter agent/skill, agent validation tests |
| P02 | literature protocol, evidence matrix, review và research gaps trong experiment riêng |
| P03 | role model, teacher task contracts, handoff và review workflow |
| P04 | teacher-facing packet, form/template và provisional examples |
| P05 | benchmark taxonomy, task definitions, rubric specification |
| P06 | schema/code nhập liệu và dataset versioning |
| P07 | inference, judge, metrics và reporting |
| P08 | workspace isolation, write leases, protected evaluator boundary và integration gates |

## 7. Trạng thái artifact hiện có

- `experiments/20260618_150902/plan.md`: tài liệu nền, không còn là unit phê duyệt.
- `dataset_design_v0.md` và `dataset_v0/`: prototype minh họa trước literature review; không gửi như đặc tả benchmark chính thức cho giáo viên cho tới khi P04 duyệt hoặc thay thế.
- Hai paper cũ đã cung cấp ngữ cảnh ban đầu nhưng không đủ để chốt khung benchmark.
- P08 là hardening plan để dành sau PoC; không được triển khai cho tới khi trạng thái được đổi rõ ràng thành `APPROVED`.
