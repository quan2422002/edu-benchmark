# Handoff C0b - annotator_a

- Phạm vi: 40 candidate theo batch khóa trong `principle_annotation_reference_manifest.json`.
- Artifact:
  - `principle_annotation_pass1.csv`
  - `principle_annotation_final.csv`
  - `principle_annotation_review_queue.csv`
  - `principle_annotation_run_manifest.json`
  - `handoff.md`
- Trạng thái kiểm tra: hash input và canonical docs khớp manifest; ordered ID giữa pass1 và reference trùng nhau; pass 1 đã được ghi trước khi mở reference; bundle final đã được đóng.
- Kết quả gắn nhãn: thay đổi 18/40, giữ nguyên 22/40, khoảng trống 0/40, xung đột 0/40.
- Không có `coverage_gap_reason` và không có `reference_effect=conflict`.
- `review_status` của mọi dòng AI vẫn là `needs_uet_review`; `adjudication_status` để trống.
- Bất định còn lại: một số biên giữa `Feedback` và `Questioning`, và giữa `Practice` và `Modelling`, vẫn cần UET chốt nếu muốn chuẩn hóa ranh giới dài hạn.
- Quyết định UET cần có: duyệt hoặc điều chỉnh 18 dòng đổi nhãn sau reference, và xác nhận có cần bổ sung quy tắc biên cho nhóm câu hỏi dẫn dắt / mẫu thao tác hay không.
