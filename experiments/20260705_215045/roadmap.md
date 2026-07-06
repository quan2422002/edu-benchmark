# Roadmap — Bloom-oriented benchmark redesign sau họp 05/07/2026

Experiment: `20260705_215045`
Ngày tạo: 05/07/2026
Trạng thái: `DRAFT` — roadmap tổ chức plan, chưa tự triển khai nội dung benchmark.

## 1. Mục tiêu của roadmap

Roadmap này tách hướng làm sau họp 05/07/2026 thành các plan nhỏ, độc lập, ít chồng chéo. Mục tiêu vận hành là: sau khi một plan đã được duyệt, triển khai, validate và commit, plan sau chỉ được **đọc/consume** artifact đã chốt của plan trước, không sửa lại plan hoặc artifact đã commit. Nếu phát hiện cần thay đổi artifact cũ, tạo một migration plan riêng thay vì sửa ngầm.

Tinh thần thiết kế:

- Học liệu chủ đạo: SGK và SGV môn Tin học THCS trên trang tập huấn `https://taphuan.nxbgd.vn/tap-huan?subjects=11`.
- Phạm vi benchmark trước mắt: Tin học lớp 9, kèm tiền kiến thức lớp 6–8 liên quan.
- Task ưu tiên theo độ khó/Bloom: `Nhận biết`, `Thông hiểu`, `Vận dụng`, `Vận dụng cao`.
- Rubric ưu tiên rút gọn còn 3–4 tiêu chí, có bằng chứng khoa học.
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
| P02 | [Source scope and topic taxonomy](plans/02-source-scope-topic-taxonomy.md)                    | Snapshot/list SGK/SGV, chuẩn hóa chủ đề xuyên suốt THCS, xác định đơn vị coverage.                       | Có thể chạy ngay; độc lập với paper review.                                   | `source_scope/`, `topic_taxonomy/`     |
| P03 | [Chọn lọc và đọc paper có mục tiêu](plans/03-targeted-paper-review-bloom-tutoring.md) | Sàng lọc paper local, viết tóm tắt chi tiết từng paper, rồi tổng hợp evidence matrix cho task/rubric/Bloom. | Có thể chạy ngay; độc lập với học liệu.                                     | `literature_notes/`                    |
| P04 | [Bloom task taxonomy and compact rubric](plans/04-bloom-task-taxonomy-and-compact-rubric.md)  | Thiết kế task theo Bloom và rubric 3–4 tiêu chí dựa trên P02/P03.                                             | Sau P02/P03 hoặc chạy bản nháp với input cũ, nhưng chỉ finalize sau P02/P03. | `benchmark_design/`                    |
| P05 | [Case coverage and 20-sample allocation](plans/05-case-coverage-and-pilot-allocation.md)      | Lập bảng bao phủ tình huống và phân bổ 20 mẫu pilot.                                                         | Sau P02/P04.                                                                         | `coverage_design/`                     |
| P06 | [Teacher examples and pilot packet](plans/06-teacher-examples-and-pilot-packet.md)            | Tạo ví dụ phiếu tác giả và gói hướng dẫn HNMU.                                                             | Sau P05.                                                                             | `teacher_examples/`, `teacher_packet/` |
| P07 | [Pilot sample intake and design check](plans/07-pilot-sample-intake-and-design-check.md)      | Nhận 20 mẫu HNMU, phân tích lệch coverage/Bloom/format và đề xuất revision.                                  | Sau khi có mẫu pilot.                                                              | `pilot_intake/`, `pilot_analysis/`     |

## 4. Dependency graph

```text
P02: SGK/SGV scope + topic taxonomy ─┐
                                     ├─> P04: Bloom task + compact rubric ─> P05 ─> P06 ─> P07
P03: targeted paper review ──────────┘
```

P02 và P03 có thể chạy song song vì một bên xử lý học liệu/chủ đề, một bên xử lý bằng chứng nghiên cứu. P04 chỉ nên chốt sau khi đã có output tối thiểu từ cả hai.

## 5. Artifact ownership


| Vùng artifact      | Owner plan | Ghi chú                                                                         |
| ------------------- | ---------- | -------------------------------------------------------------------------------- |
| `source_scope/`     | P02        | Danh sách SGK/SGV, trạng thái snapshot/OCR, nguồn taphuan.                   |
| `topic_taxonomy/`   | P02        | Chủ đề chuẩn xuyên suốt THCS, alias từ SGK/SGV, đơn vị coverage.       |
| `literature_notes/` | P03        | Protocol, notes, evidence matrix, synthesis claim.                               |
| `benchmark_design/` | P04        | Bloom task registry, compact rubric, evidence-to-spec mapping.                   |
| `coverage_design/`  | P05        | Case coverage matrix, 20-sample allocation, coverage risk notes.                 |
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

Người phụ trách dự án ưu tiên triển khai P03 trước. P03 vẫn độc lập với P02: P03 xử lý bằng chứng nghiên cứu từ paper local, còn P02 xử lý SGK/SGV và taxonomy chủ đề. P04 chỉ nên chốt sau khi đã có output tối thiểu từ cả P02 và P03.

P03 được cập nhật theo flow: chọn lọc paper → tóm tắt chi tiết từng paper → evidence matrix → synthesis tổng quát cho thiết kế.
