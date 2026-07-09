# Roadmap — Bloom-oriented benchmark redesign sau họp 05/07/2026

Experiment: `20260705_215045`
Ngày tạo: 05/07/2026
Trạng thái: `DRAFT` — roadmap tổ chức plan, chưa tự triển khai nội dung benchmark.

## 1. Mục tiêu của roadmap

Roadmap này tách hướng làm sau họp 05/07/2026 thành các plan nhỏ, độc lập, ít chồng chéo. Mục tiêu vận hành là: sau khi một plan đã được duyệt, triển khai, validate và commit, plan sau chỉ được **đọc/consume** artifact đã chốt của plan trước, không sửa lại plan hoặc artifact đã commit. Nếu phát hiện cần thay đổi artifact cũ, tạo một migration plan riêng thay vì sửa ngầm.

Tinh thần thiết kế:

- Học liệu chủ đạo: SGK và SGV môn Tin học THCS trên trang tập huấn `https://taphuan.nxbgd.vn/tap-huan?subjects=11`.
- Phạm vi benchmark trước mắt: Tin học lớp 9, kèm tiền kiến thức lớp 6–8 liên quan.
- Cột `Mức độ nhận thức` ưu tiên theo tài liệu HNMU: `Biết`, `Hiểu`, `Vận dụng`. Không dùng `Vận dụng cao` trong bản hiện tại nếu chưa có revision riêng.
- Rubric ưu tiên rút gọn còn 4–5 tiêu chí, có bằng chứng khoa học; bản P04 hiện giữ R1–R5.
- Giáo viên HNMU cần ví dụ cụ thể theo phiếu tác giả để tạo khoảng 20 mẫu pilot.

## 2. Nguyên tắc chống chồng chéo

1. Mỗi plan sở hữu một nhóm thư mục/file riêng.
2. Plan sau không sửa output của plan trước; chỉ tạo artifact mới hoặc ghi decision/migration request.
3. `coordination/` và `handoffs/` là ngoại lệ append-only: plan nào cũng có thể thêm log/handoff mới, nhưng không sửa log/handoff cũ.
4. `reports/` là vùng báo cáo chung, nhưng mỗi plan chỉ ghi file có prefix plan của mình.
5. Mọi artifact chuyên môn đều giữ trạng thái `draft` hoặc `needs_hnmu_review` cho tới khi có quyết định rõ của HNMU/giáo sư.
6. Nếu một plan cần đổi phạm vi sau khi commit, tạo plan mới kiểu `migration` hoặc `revision`, không chỉnh lại plan đã commit.

## 3. Thứ tự plan


| ID  | Plan                                                                                          | Mục tiêu                                                                                                            | Có thể chạy                                                                       | Sở hữu output chính                 |
| --- | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | -------------------------------------- |
| P02 | [Source scope and topic taxonomy](plans/02-source-scope-topic-taxonomy.md)                    | Chốt nguồn học liệu và tài liệu hỗ trợ: 3 mức nhận thức, giàn giáo cho R3, SGK Tin học 9 là nguồn chính; taxonomy toàn THCS hoãn. | Hoàn tất bản thu gọn; P04 có thể consume `tin9_sgk_topics_v0.csv` nhưng vẫn giữ trạng thái cần HNMU review. | `source_scope/`, `topic_taxonomy/`     |
| P03 | [Chọn lọc và đọc paper có mục tiêu](plans/03-targeted-paper-review-bloom-tutoring.md) | Sàng lọc paper local, viết tóm tắt chi tiết từng paper, rồi tổng hợp evidence matrix cho task/rubric/Bloom. | Có thể chạy ngay; độc lập với học liệu.                                     | `literature_notes/`                    |
| P04 | [Task theo hành vi gia sư và rubric rút gọn](plans/04-bloom-task-taxonomy-and-compact-rubric.md)  | Đã triển khai v0 hai phần lõi của benchmark: task theo hành vi gia sư và rubric R1–R5; chờ HNMU/giáo sư review. | Hoàn tất bản v0 task/rubric-only. | `benchmark_design/`                    |
| P05 | [Ma trận bao phủ tổng quát](plans/05-case-coverage-and-pilot-allocation.md)      | Đã tạo ma trận bao phủ task × mức nhận thức × chủ đề SGK Tin học 9, kèm dạng bài làm/câu hỏi/sản phẩm của học sinh; 20 mẫu chỉ còn là lát cắt pilot, không phải khung chính. | Hoàn tất bản v0; P06 có thể consume `general_coverage_matrix_v0.csv`. | `coverage_design/`                     |
| P06 | [Teacher examples and pilot packet](plans/06-teacher-examples-and-pilot-packet.md)            | Đã tạo 13 ví dụ phiếu tác giả minh họa và gói hướng dẫn/rà soát cho HNMU từ lát cắt đại diện của ma trận P05. | Hoàn tất bản v0, chờ HNMU/giáo sư rà soát. | `teacher_examples/`, `teacher_packet/` |
| P07 | [Pilot sample intake and design check](plans/07-pilot-sample-intake-and-design-check.md)      | Nhận 20 mẫu HNMU, phân tích lệch coverage/Bloom/format và đề xuất revision.                                  | Sau khi có mẫu pilot.                                                              | `pilot_intake/`, `pilot_analysis/`     |

## 4. Dependency graph

```text
P02: SGK Tin học 9 + topic taxonomy v0 ─┐
                                     ├─> P04: task theo hành vi gia sư + compact rubric ─> P05 ─> P06 ─> P07
P03: targeted paper review ──────────┘
```

P02 và P03 có thể chạy song song vì một bên xử lý học liệu/chủ đề, một bên xử lý bằng chứng nghiên cứu. P04 chỉ nên chốt sau khi đã có output tối thiểu từ cả hai.

## 5. Artifact ownership


| Vùng artifact      | Owner plan | Ghi chú                                                                         |
| ------------------- | ---------- | -------------------------------------------------------------------------------- |
| `source_scope/`     | P02        | Phạm vi nguồn P02 bản thu gọn: SGK Tin học 9, tài liệu mức nhận thức, tài liệu giàn giáo.                   |
| `topic_taxonomy/`   | P02        | Danh sách chủ đề/bài học v0 từ mục lục SGK Tin học 9; bài học thuộc chủ đề qua `parent_id`.       |
| `literature_notes/` | P03        | Protocol, notes, evidence matrix, synthesis claim.                               |
| `benchmark_design/` | P04        | Task theo hành vi gia sư, luận giải task, rubric R1–R5 rút gọn và luận giải rubric.                   |
| `coverage_design/`  | P05        | Ma trận bao phủ tổng quát, định nghĩa trục bao phủ, dạng bài làm của học sinh, chỉ số chọn lát cắt pilot.                 |
| `teacher_examples/` | P06        | Ví dụ phiếu tác giả đã điền.                                            |
| `teacher_packet/`   | P06        | Hướng dẫn pilot cho HNMU, không yêu cầu giáo viên làm việc kỹ thuật. |
| `pilot_intake/`     | P07        | 20 mẫu nhận từ HNMU hoặc bản tổng hợp local.                              |
| `pilot_analysis/`   | P07        | Phân tích mẫu pilot và đề xuất revision plan.                             |

## 6. Vai trò của experiment `20260701_100006`

Được dùng làm input lịch sử, không phải nguồn chân lý cuối:

- Phiếu tác giả và luận giải trường dữ liệu: dùng cho P06.
- Task T01–T07 theo hành vi gia sư: dùng như nhãn phụ/case tương tác trong P04/P05.
- Rubric D1–D9: dùng làm nguồn gom về 3–4 rubric trong P04.
- Learning-resource fragments v0: dùng tạm trước khi P02 chuẩn hóa SGK/SGV.

Không sửa artifact cũ trong `20260701_100006` từ roadmap này.

## 7. Tiêu chí “commit xong không phải sửa lại”

Một plan chỉ nên commit khi:

- có trạng thái rõ: `DRAFT`, `APPROVED`, `COMPLETED`, hoặc `SUPERSEDED_BY_<plan>`;
- có output đúng phạm vi đã khai báo;
- có validation/handoff;
- có danh sách quyết định còn mở;
- plan sau có thể đọc output mà không cần sửa lại plan này.

Nếu chưa đạt, để plan/artifact ở trạng thái draft và không coi là nền cho plan sau.

## 8. Ưu tiên cập nhật ngày 05/07/2026

Người phụ trách dự án ưu tiên triển khai P03 trước. P03 vẫn độc lập với P02: P03 xử lý bằng chứng nghiên cứu từ paper local, còn P02 xử lý SGK Tin học 9 và danh sách chủ đề/bài học v0. P04 chỉ nên chốt sau khi đã có output tối thiểu từ cả P02 và P03.

P03 được cập nhật theo flow: chọn lọc paper → tóm tắt chi tiết từng paper → evidence matrix → synthesis tổng quát cho thiết kế.

## Cập nhật P02 bản thu gọn - 06/07/2026

P02 được đánh dấu hoàn tất ở phạm vi rút gọn: 3 mức nhận thức, giàn giáo cho R3/note, SGK Tin học 9 làm nguồn chủ đề v0. Các phần OCR toàn văn và phân mảnh học liệu chuyển sang P08/later.

## Cập nhật P04 - 06/07/2026

P04 đã được revise để không dùng Bloom/mức nhận thức làm task chính. Sau phản hồi ngày 06/07/2026, P04 được thu hẹp vào hai phần lõi: task theo hành vi gia sư và rubric rút gọn R1–R5; catalog mã lỗi nghiêm trọng để plan sau.

## Cập nhật P04 triển khai - 06/07/2026

P04 task/rubric-only đã tạo `benchmark_tasks.csv`, `rubrics.csv`, luận giải task, luận giải rubric và câu hỏi mở. Tất cả task/rubric ở trạng thái `needs_hnmu_review`; catalog mã lỗi nghiêm trọng để plan sau.

## Cập nhật P05 triển khai - 06/07/2026

P05 đã chuyển từ “phân bổ đúng 20 mẫu pilot” sang ma trận bao phủ tổng quát. Artifact chính là `coverage_design/general_coverage_matrix_v0.csv` với 96 ô bao phủ: 4 task × 3 mức nhận thức × 8 cụm chủ đề SGK Tin học 9. Các câu hỏi mở P04 được coi là tạm chốt để tiếp tục tiến độ; nếu HNMU/giáo sư phản hồi sau, cập nhật ở lớp quy tắc/ưu tiên thay vì phá cấu trúc ma trận.

## Cập nhật P05 student_work_type - 06/07/2026

P05 đã bổ sung trục `student_work_type` để thể hiện rõ dạng bài làm/câu hỏi/sản phẩm của học sinh trong từng ô bao phủ. Ma trận vẫn giữ 96 ô để tránh làm nổ số tổ hợp, nhưng mỗi ô có thêm dạng bài làm chính/phụ và ghi chú cho P06.

## Cập nhật P06 triển khai - 07/07/2026

P06 đã tạo 13 ví dụ minh họa từ ma trận bao phủ P05, đủ phủ 4 nhiệm vụ gia sư, 3 mức nhận thức, 8 cụm chủ đề SGK Tin học 9 và 9 dạng bài làm/câu hỏi của học sinh. Gói `teacher_packet/` dùng cho HNMU ở mức thử nghiệm, chưa phải dữ liệu chính thức.
