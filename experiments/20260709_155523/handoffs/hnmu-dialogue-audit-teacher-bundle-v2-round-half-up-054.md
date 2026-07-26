# Specialist handoff

- Delegation ID: `hnmu-dialogue-audit-teacher-bundle-v2-round-half-up-054`
- Agent: orchestrator single-agent, áp dụng `teacher-collaboration-designer`
- Status: hoàn thành và đã validate, chờ project lead review local
- Native thread ID/label: không có; lượt sửa hẹp trên pipeline Plan 08b

## Delegation prompt

Thống nhất quy tắc làm tròn tỷ lệ phần trăm trong Markdown và workbook thành `ROUND_HALF_UP` với hai chữ số thập phân. Trường hợp 91/224 của lớp 7 phải hiển thị 40.63%. Rà soát toàn bộ tỷ lệ theo counts canonical, rebuild, validate, không commit/push/upload.

## Follow-up or steer messages

Không có specialist thread. Skill canonical được áp dụng trong parent thread để giữ diễn giải và nhãn tỷ lệ dễ đọc cho giáo viên; thay đổi chỉ tác động lớp trình bày và validation.

## Inputs read

- Builder và validator Plan 08b hiện tại.
- Bundle v2 đã validate trước lượt sửa.
- Các nguồn canonical được loader Plan 08 đọc lại trong build/validator.
- Snapshot trước sửa: `/tmp/hnmu-rounding-before.OicDfI/bundle`.

## Outputs created

- Rebuild `01_bao_cao_tong_quan.md`.
- Rebuild `03_thong_ke_pass_reject_giua_cac_khoi.xlsx`.
- Rebuild workbook độ phủ ở root và bốn workbook độ phủ theo lớp.
- Rebuild bundle v2 atomically; các file không liên quan có nội dung semantic không đổi.
- Thêm regression tests cho `ROUND_HALF_UP` và giá trị 91/224.

## Result summary

- `91/224` được hiển thị là `40.63%` trong báo cáo Markdown và workbook.
- 16 tỷ lệ trong báo cáo được đối chiếu với counts canonical; chỉ giá trị 40.62% cũ cần đổi.
- 898 ô phần trăm trong toàn bộ workbook được rà soát; tất cả dùng định dạng `0.00%`, không còn khác biệt giữa kết quả format float mặc định và `ROUND_HALF_UP`.
- Semantic diff với snapshot: báo cáo chỉ đổi một tỷ lệ; workbook trạng thái chỉ đổi 18 giá trị tỷ lệ sang precision hiển thị; workbook độ phủ chỉ đổi 70 giá trị tỷ lệ tương ứng; workbook fragment, hệ số thống kê, style và toàn bộ CSV không đổi.
- Validator xác nhận 1.050 mẫu, 18.900 khóa tiêu chí, counts trạng thái và hash nguồn canonical không đổi.
- Sáu test mục tiêu pass bằng `/home/dknguyen/miniconda3/envs/edu_ai/bin/python`.

## Orchestrator decision

Chuẩn hóa count-derived percentage values ngay trong generator bằng `Decimal` và `ROUND_HALF_UP`, thay vì phụ thuộc cách format float hoặc ứng dụng mở workbook. Giữ nguyên các hệ số và dữ liệu thống kê fragment. Dừng để project lead review; không stage, commit, push hoặc upload.

## Uncertainty

Không có sai lệch làm tròn nào khác được phát hiện. Việc kiểm tra dựa trên nội dung workbook được mở lại bằng openpyxl; không chạy Excel/LibreOffice GUI trên server.

## Open questions and next human decisions

- Project lead duyệt báo cáo và ô lớp 7 trong workbook 03.
- Project lead quyết định bước Git/upload riêng sau review; task này không thực hiện các bước đó.
