# Plan 03 — Registry và promotion artifact benchmark dùng chung

Experiment: `20260806_145124`
Trạng thái: `DRAFT — AWAITING PLAN 02 COMPLETION AND PROJECT-LEAD APPROVAL`
Phụ thuộc: Plan 01–02

## 1. Mục tiêu

Đưa các nền tảng benchmark ổn định ra khỏi cây experiment khó tìm, nhưng vẫn
giữ provenance và không biến kết quả tạm thời thành ground truth. Shared là nơi
tiêu thụ chuẩn; experiment vẫn là nơi tạo ra và lưu lịch sử run.

## 2. Phạm vi artifact

Plan phải inventory và xác minh trước khi promote:

- checklist audit hội thoại 18 tiêu chí;
- 665 hội thoại có disposition `pass` sau Phase 1;
- 2.028 candidate đã conversion/validation từ 665 family;
- selection tạm dùng 1.400 candidate từ Plan 03 cũ, cùng provenance của 628
  candidate cần review và trạng thái 0 blocked;
- capability, pedagogical principle và rubric library đang dùng, với trạng thái
  `provisional`/`awaiting_review` đúng thực tế.

Nguồn đã biết gồm experiment `20260722_000940`, snapshot kế thừa và output của
`20260727_170150`; inventory phải xác định nguồn chuẩn thay vì chọn file theo tên.

## 3. Registry và manifest

`shared/benchmark/artifact_registry.csv` tối thiểu có:

- `artifact_id`, `artifact_type`, `version`, `status`, `canonical_path`;
- `source_experiment`, `source_path`, `sha256`, `schema_version`;
- count chính (`dialogue`, `family`, `candidate`) khi áp dụng;
- `approval_authority`, `approved_at`, `supersedes`, `access_policy`, `notes`.

Mỗi bundle có manifest ghi nguồn, transformation command/code version, checksum,
count invariant, schema và giới hạn sử dụng. Registry không tự nâng trạng thái
phê duyệt.

## 4. Cách biểu diễn selection 1.400

Không sao chép toàn bộ payload 1.400 dòng nếu có thể join từ candidate pool.
`selection.csv` giữ candidate ID, family ID nếu cần, disposition, reason và
provenance. `requirement_scores.csv` chỉ giữ trường cần để tái lập selection.
Materialized evaluation input là derived artifact và thuộc experiment run.

## 5. Các bước triển khai dự kiến

1. Lập source inventory và consumer inventory.
2. Đối chiếu checksum, schema và invariant 18/665/2.028/1.400/628/0.
3. Xác định quyền truy cập, dữ liệu nhạy cảm và file được phép track trong Git.
4. Tạo registry/schema/README và script promotion idempotent.
5. Promote theo bundle có version; không sửa file nguồn lịch sử.
6. Chuyển consumer đại diện sang canonical path và chạy equivalence test.
7. Ghi deprecation map; chưa xóa snapshot cũ trong plan này.

## 6. Phạm vi ghi dự kiến

- `shared/benchmark/`
- code promotion/validation trong package và CLI mỏng tương ứng
- `tests/`
- consumer paths được liệt kê trước trong amendment/status của Plan 03
- docs và experiment artifacts của Plan 03

## 7. Nghiệm thu

- Người mới tìm được checklist, 665, 2.028 và selection 1.400 từ một README và
  registry duy nhất.
- Candidate pool được mô tả đúng là output conversion đã validate, không phải raw.
- Selection 1.400 được gọi `provisional_evaluation_pool`, không gọi benchmark v1.
- Count/checksum/join invariant khớp nguồn; duplicate ID bằng 0.
- Mọi artifact provisional ghi đúng authority UET/HNMU còn thiếu.
- Consumer đại diện cho kết quả y hệt trước/sau migration.
- Payload không được phép commit không xuất hiện trong Git.

## 8. Rủi ro và rollback

Rủi ro lớn nhất là chọn nhầm snapshot hoặc ngầm xác nhận dữ liệu. Canonical path
chỉ được công bố sau equivalence report; rollback bằng deprecation map ngược về
source path, không xóa source experiment.

## 9. Quyết định cần duyệt

- Artifact nào được track trực tiếp trong Git, artifact nào dùng external locator.
- Authority/status chính xác cho checklist, selection và rubric provisional.
- Có giữ `requirement_scores.csv` trong shared hay chỉ giữ hash/locator.
