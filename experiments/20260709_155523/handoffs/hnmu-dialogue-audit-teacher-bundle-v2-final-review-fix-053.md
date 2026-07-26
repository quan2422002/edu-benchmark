# Specialist handoff

- Delegation ID: `hnmu-dialogue-audit-teacher-bundle-v2-final-review-fix-053`
- Agent: orchestrator single-agent, áp dụng `hnmu-dialogue-auditor` và `teacher-collaboration-designer`
- Status: hoàn thành và đã validate, chờ project lead review local
- Native thread ID/label: không có; lượt sửa hẹp trên pipeline Plan 08b

## Delegation prompt

Sửa các lỗi review cuối: kết luận fragment phải đúng scope từng lớp, lớp 8 phải ghi không thể ước lượng 8/8 adjusted analyses, pooled vẫn kiểm soát grade + auditor_group, và nhãn pass trong workbook 03 phải nói rõ đây là trạng thái tổng thể chính thức. Rebuild từ pipeline; không sửa tay workbook, không commit/push/upload.

## Follow-up or steer messages

Không có specialist thread. Hai skill canonical được áp dụng trong parent thread để phân biệt official status với checklist pass rate và viết diễn giải thống kê dễ đọc, không mang tính nhân quả.

## Inputs read

- Code builder và validator Plan 08b hiện tại.
- Bundle v2 đã validate trước lượt sửa.
- Hai checklist repaired/canonical và hai nguồn official status được loader Plan 08 đọc lại trong build/validator.

## Outputs created

- Rebuild `03_thong_ke_pass_reject_giua_cac_khoi.xlsx`.
- Rebuild năm workbook `*_phan_tich_fragment_va_ket_qua_cham*.xlsx`.
- Rebuild README root, báo cáo tổng quan và README của bốn lớp.
- Thêm regression tests cho scope kết luận, invariant lớp 8 và nhãn official status.

## Result summary

- Lớp 6: 8/8 adjusted analyses ước lượng được; 4 có p-value dưới 0,05; 4 đổi chiều; kết luận chỉ nói kiểm soát auditor_group.
- Lớp 7: 8/8 ước lượng được; 5 có p-value dưới 0,05; 4 đổi chiều; kết luận chỉ nói kiểm soát auditor_group.
- Lớp 8: 8/8 adjusted analyses có `sample_count=0`, `0/6` strata đủ biến thiên, `estimable=false`; kết luận ghi rõ không thể ước lượng và không dùng crude như bằng chứng độc lập.
- Lớp 9: 6/8 ước lượng được, 2/8 không thể; 3 adjusted analyses có p-value dưới 0,05; 6 đổi chiều; kết luận chỉ nói kiểm soát auditor_group.
- Pooled: 8/8 ước lượng được; kết luận ghi đúng kiểm soát đồng thời grade và auditor_group.
- Nhãn pass trong workbook 03 đổi thành “Đạt theo trạng thái tổng thể chính thức”.
- Semantic diff xác nhận mọi data row của năm workbook fragment, hệ số, p-value, effect size, sample count, warning và style không đổi. Workbook 03 chỉ đổi đúng năm ô status label; mọi style/layout không đổi. Tất cả CSV không đổi hash.

## Orchestrator decision

Giữ nguyên dữ liệu và hệ số đã validate; chỉ chấp nhận thay đổi diễn giải, nhãn và tài liệu liên quan. Dừng để project lead review; không stage, commit, push hoặc upload.

## Uncertainty

Hiển thị thực tế bằng Excel/LibreOffice vẫn chưa được kiểm tra trên server vì không có spreadsheet renderer. Freeze pane, filter, wrap text, style, width, single-sheet và merged-cell invariants đã được kiểm tra bằng openpyxl và không đổi so với snapshot trước.

## Open questions and next human decisions

- Project lead mở nhanh workbook lớp 8 và workbook pooled trong Excel/LibreOffice để duyệt câu kết luận cuối.
- Project lead quyết định các bước Git/upload sau review; task này không thực hiện các bước đó.
