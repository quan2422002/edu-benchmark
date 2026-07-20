# Merged agent audit notes — HNMU lớp 8–9 sau chính sách draft-as-keep

Ngày đồng bộ: 19/07/2026  
Trạng thái: `synced_from_draft_fragment_as_keep_policy`

## 1. Chính sách hiện hành

Nếu fragment học liệu có `status = draft` nhưng đã khớp đúng metadata và nội dung cần kiểm, trạng thái `draft` **không tự động** làm tiêu chí bị `uncertain` và không tự động đưa mẫu vào hàng đợi review.

Chỉ giữ `uncertain` khi:

- không tìm thấy fragment phù hợp;
- evidence thiếu hoặc quá mơ hồ;
- có dấu hiệu mâu thuẫn/lệch/sai nội dung;
- lỗi định dạng, trùng lặp hoặc vấn đề sư phạm cần HNMU/UET xác nhận.

## 2. Bản checklist hiện hành

```text
merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Bản backup trước chính sách này:

```text
merged/raw_dialogue_checklist_results.regex_repaired.pre_draft_policy.csv
```

## 3. Các file đã đồng bộ theo chính sách mới

- `merged/quality_check_suggestions.csv`
- `merged/hnmu_review_queue_suggestions.csv`
- `merged/merge_validation_summary.json`

Các bản trước chính sách này được giữ bằng hậu tố `.pre_draft_policy` nếu file đã tồn tại.

## 4. Kết quả sau đồng bộ

- Số dòng `uncertain` được chuyển thành `pass`: 560
- Phân bố chuyển đổi theo tiêu chí: {'RAW-CON-01': 154, 'RAW-CON-02': 98, 'RAW-CON-06': 154, 'RAW-CON-07': 154}
- Số mẫu: 588
- Số tiêu chí/mẫu: [18]
- Số dòng checklist: 10584
- Phân bố checklist: {'pass': 9968, 'uncertain': 614, 'fail': 2}
- Phân bố gợi ý chất lượng: {'needs_human_review': 299, 'fail': 1, 'keep': 288}
- Số mẫu trong hàng đợi specialist review: 300
- Phân bố priority review: {'trung bình': 295, 'cao': 5}

## 5. Diễn giải nhanh

Bản này không còn đẩy mẫu vào review chỉ vì fragment đang ở trạng thái `draft`. Hàng đợi review còn lại phản ánh các trường hợp cần kiểm thật hơn: thiếu fragment/evidence, lỗi định dạng, nguy cơ trùng lặp, hoặc điểm sư phạm/hội thoại chưa chắc.
