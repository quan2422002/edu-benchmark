# Specialist handoff

- Delegation ID: `hnmu-dialogue-fragment-hnmu-summary-appendix-055`
- Agent: orchestrator single-agent, áp dụng `teacher-collaboration-designer`
- Status: hoàn thành và đã validate, chờ project lead review local
- Native thread ID/label: không có; thay đổi lớp trình bày trong Plan 08b

## Delegation prompt

Thiết kế lại năm workbook phân tích fragment để HNMU đọc được mà không cần kiến thức thống kê chuyên sâu. Mỗi workbook chính chỉ có 8 dòng, đặt kết quả chưa điều chỉnh và sau điều chỉnh cạnh nhau; toàn bộ dữ liệu kỹ thuật cũ phải chuyển sang phụ lục riêng, truy vết bằng khóa ổn định. Không thay đổi dữ liệu, phương pháp, hệ số, trạng thái hoặc nguồn canonical; không commit/push/upload.

## Follow-up or steer messages

Không có specialist thread. Skill `teacher-collaboration-designer` được áp dụng trong parent thread để tách nhiệm vụ đọc nghiệp vụ khỏi kiểm toán kỹ thuật, chuẩn hóa ngôn ngữ tiếng Việt và giữ giới hạn không nhân quả.

## Inputs read

- Builder, renderer, validator và regression tests Plan 08b.
- Bundle v2 đã validate trước lượt sửa.
- Các output canonical được loader hiện hành đọc lại trong build/validator.
- Snapshot trước sửa: `/tmp/hnmu-fragment-hnmu-before.mbDnSE/bundle`.

## Outputs created

- Rebuild file 05 root và file 07 của bốn lớp thành bản tóm tắt HNMU, mỗi file 8 dòng × 12 cột.
- Tạo `05_phu_luc_ky_thuat_phan_tich_fragment.xlsx` ở root, 379 dòng × 29 cột.
- Tạo file 08 phụ lục kỹ thuật ở lớp 6–9, lần lượt 46, 47, 77 và 63 dòng × 29 cột.
- Tạo `DANH_MUC_FILE.md` và cập nhật README root, báo cáo tổng quan, README từng lớp.
- Thêm renderer summary–appendix, bộ sinh tài liệu HNMU và regression tests.

## Result summary

- Schema summary gồm 10 cột yêu cầu cùng hai cột bổ sung: `Số mẫu sau điều chỉnh` để tránh hiểu sai khi adjusted dùng ít mẫu hơn, và `Mã đối chiếu` để nối sang phụ lục.
- Phụ lục giữ nguyên 28 cột kỹ thuật trước đây và chỉ thêm cột 29 `Mã đối chiếu`.
- Semantic comparison xác nhận 0 khác biệt ở 28 cột kỹ thuật của cả năm phụ lục; toàn bộ coefficient, p-value, sample count, effect size, estimable, warning và method không đổi.
- Toàn bộ 24 CSV không đổi SHA-256. Bảy workbook không liên quan có 0 cell-value differences.
- Root và bốn file lớp đều có 8 dòng summary; lớp 8 có 8/8 adjusted sample count bằng 0 và `Không thể ước lượng`.
- Kết luận root: “Có một số mối liên hệ trong phân tích chưa điều chỉnh, nhưng kết quả không nhất quán hoặc thay đổi sau khi kiểm soát khối lớp và nhóm chấm. Vì vậy, chưa có bằng chứng cho thấy mức độ sử dụng fragment có mối liên hệ độc lập và ổn định với kết quả chấm.”
- Validator: 1.050 mẫu, 18.900 khóa tiêu chí, 665 pass, 382 need_human_review, 3 failed, path leaks 0, một sheet/workbook.
- 12 test liên quan pass bằng `/home/dknguyen/miniconda3/envs/edu_ai/bin/python`.

## Orchestrator decision

Giữ file 05/file 07 làm điểm đọc đầu tiên cho HNMU và dùng file phụ lục chỉ khi cần kiểm toán. Không tạo chart vì không giúp trả lời câu hỏi nghiệp vụ tốt hơn bảng 8 dòng. Dừng để project lead review; không stage, commit, push hoặc upload.

## Uncertainty

Không có sai lệch dữ liệu được phát hiện. Hiển thị thực tế trong Excel/LibreOffice chưa được mở bằng GUI trên server; cấu trúc, style, wrap text, freeze pane, filter và giá trị đã được kiểm tra bằng openpyxl.

## Open questions and next human decisions

- Project lead mở nhanh file 05 root và file 07 lớp 8 để duyệt ngôn ngữ/kích thước cột.
- Project lead quyết định bước Git/upload riêng sau review; task này không thực hiện các bước đó.
