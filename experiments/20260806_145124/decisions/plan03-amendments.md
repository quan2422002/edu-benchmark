# Amendments — Plan 03

Experiment: `20260806_145124`
Baseline: `plans/03-shared-benchmark-artifact-registry-and-promotion.md`

## P03-A001 — Khóa nguồn, authority và phạm vi payload shared

- Thời điểm: `2026-08-07T23:08:37+07:00`
- Người quyết định: orchestrator, trong phạm vi Plan 03 đã được project lead duyệt
- Quyết định:
  - track trực tiếp checklist 18 tiêu chí, 665 dialogue Phase 1, candidate pool
    2.028 dòng, trace, disposition, selection tối giản 1.400 dòng, score tối
    giản 2.028 dòng và các specification CSV/Markdown đang dùng;
  - không copy `run_full.jsonl`, raw XLSX, model prompt/response thô hoặc output
    evaluation lớn vào `shared/benchmark/`; manifest chỉ giữ locator và SHA-256
    khi cần truy vết nguồn local/experiment;
  - gọi tập 1.400 là `provisional_evaluation_pool`, không phải benchmark v1;
  - giữ checklist và 665 dialogue ở trạng thái vận hành tạm, candidate pool ở
    trạng thái conversion-validated, còn capability/principle/rubric ở trạng
    thái `needs_hnmu_review` đúng nguồn;
  - consumer đại diện được migrate là
    `scripts/benchmark_specification/build_principle_grounding_pool.py`, chỉ đổi
    default candidate input sang shared candidate pool; source experiment vẫn
    được giữ và không xóa.
- Lý do: các payload được track trực tiếp đều đã có trong Git ở nguồn lịch sử và
  đủ nhỏ; raw model JSONL bị ignore và chứa nhiều trường không cần cho việc tái
  lập selection. Bảng compact tránh nhân bản payload 1.400 dòng tự chứa 23 cột.
- Ảnh hưởng: người dùng tìm các mốc 18/665/2.028/1.400 từ một registry; mọi
  bundle có manifest, checksum, count, authority và limitation riêng.
- Không thay đổi: nhãn, dialogue text, candidate content, score model, rubric,
  decision UET/HNMU, source experiment và output lịch sử.

## P03-A002 — Thay mô tả nguồn bằng link tới đúng file lịch sử

- Thời điểm: `2026-08-08T19:45:11+07:00`
- Người quyết định: project lead yêu cầu sửa source inventory trong final report
- Quyết định:
  - cột nguồn của inventory phải trỏ trực tiếp tới từng file lịch sử được
    promotion đọc, không chỉ mô tả tên experiment hoặc loại artifact;
  - bundle canonical được trình bày ở cột riêng bằng link tới thư mục shared;
  - với checklist, report phân biệt snapshot inherited thực sự được đọc với
    `source_experiment` upstream được lưu trong manifest.
- Lý do: người đọc cần mở được ngay đầu vào cụ thể và phân biệt provenance với
  consumption path canonical.
- Ảnh hưởng: chỉ sửa khả năng truy vết trong tài liệu Plan 03.
- Không thay đổi: payload shared, manifest, checksum, registry, authority,
  selection, nhãn hoặc kết luận gate của Plan 03.
