# Bàn giao — Khởi tạo experiment và roadmap cải tổ repository

- Coordination ID: `EXP-20260806-REFACTOR-BOOTSTRAP-001`
- Agent: `orchestrator` — single-agent planning mode
- Trạng thái: `completed`
- Native thread ID/label: không có; không ủy quyền specialist

## Yêu cầu

Tạo một experiment mới, viết roadmap bao quát toàn bộ quá trình cải tổ và chia
thành các plan để project lead duyệt tuần tự.

## Ghi chú và quyết định đã tiếp nhận

- Người đọc chỉ cần hiểu thứ tự thời gian của baseline/amendment; quan hệ chi
  tiết nếu cần để cho máy đọc.
- ID experiment dùng timestamp `YYYYMMDD_HHMMSS`; runbook lưu exact operational
  procedure của experiment.
- 665 là dialogue pass sau Phase 1; 2.028 là candidate pool sau conversion;
  1.400 là selection tạm dùng sau Plan 03, chưa phải benchmark freeze.
- `pyproject.toml` chuẩn hóa install/import package; environment lock vẫn là một
  yêu cầu riêng.
- Kế hoạch ban đầu được giữ ổn định sau duyệt; thay đổi tình thế đi theo timeline
  amendment/status/final report.

## Input đã đọc

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260727_170150/roadmap.md`
- `experiments/20260727_170150/metadata.yaml`
- `experiments/_templates/handoff.md`
- `experiments/_templates/coordination-event.schema.json`
- Các path nguồn hiện có của checklist, candidate pool, rubric, review queue và
  shared learning resources/prompts được inventory ở mức lập kế hoạch.

## Output đã tạo

- `experiments/20260806_145124/metadata.yaml`
- `experiments/20260806_145124/roadmap.md`
- Bảy file plan trong `experiments/20260806_145124/plans/`
- `experiments/20260806_145124/coordination/coordination_log.jsonl`
- Handoff này

## Tóm tắt kết quả

Roadmap chia migration thành bảy gate: quản trị plan; packaging/môi trường;
promotion artifact shared; config/runbook/path; ranh giới `src`–`scripts`;
retention/cleanup; và validation/closeout. Mỗi plan có phạm vi, bước triển khai,
acceptance criteria, rủi ro, rollback và quyết định cần duyệt.

## Quyết định của orchestrator

- Giữ toàn bộ plan ở `DRAFT`.
- Không tạo status YAML/amendment template ngay trong lượt bootstrap vì đó là
  nội dung cần được project lead duyệt trong Plan 01.
- Không cập nhật `README.md` hoặc `ARCHITECTURE.md`: experiment mới chưa làm thay
  đổi kiến trúc/runtime đang có hiệu lực.
- Không di chuyển/xóa dữ liệu và không sửa các thay đổi manuscript hiện có của
  người dùng.

## Bất định

- Environment lock và OS matrix của CI sẽ cần chốt ở Plan 02.
- Quyền lưu trực tiếp payload HNMU/candidate trong Git cần chốt ở Plan 03.
- Kho external/archive và action cleanup phá hủy cần duyệt riêng ở Plan 06.

## Quyết định tiếp theo của con người

Project lead đọc `roadmap.md`, sau đó duyệt hoặc yêu cầu sửa riêng
`plans/01-planning-governance-and-decision-records.md`. Chưa cần duyệt Plan 02–07
trước khi Plan 01 hoàn tất.

