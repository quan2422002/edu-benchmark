# Specialist handoff

- Delegation ID: `hnmu-dialogue-fragment-root-focus-summary-057`
- Agent: orchestrator single-agent, áp dụng `teacher-collaboration-designer`
- Status: hoàn thành và đã validate, chờ project lead review local
- Native thread ID/label: không có; refactor riêng file 05 root của Plan 08b

## Delegation prompt

Đơn giản hóa file phân tích fragment root để chỉ trả lời liệu tỷ lệ tiêu chí có dẫn fragment cao hơn có đi kèm trạng thái đạt chính thức cao hơn hay không. Chỉ thay đổi cách trình bày; giữ nguyên bốn file theo lớp, phụ lục kỹ thuật, dữ liệu và phương pháp. Không commit, push hoặc upload.

## Follow-up or steer messages

Không có specialist thread. Skill `teacher-collaboration-designer` được áp dụng trong parent thread để chuyển kết quả kỹ thuật thành câu hỏi, kết luận, giải thích và lưu ý bằng tiếng Việt phổ thông.

## Inputs read

- Generator, validator, docs và regression tests của bundle v2.
- Bundle v2 đã validate trước lượt sửa.
- Snapshot trước sửa: `/tmp/hnmu-root-summary-before.zYPmXK/bundle`.

## Outputs created

- Refactor `fragment_analysis_hnmu_compact.py` để file root dùng layout khối văn bản tối đa ba cột.
- Cập nhật pipeline/validator, README, báo cáo tổng quan và manifest.
- Rebuild bundle v2 bằng staging và atomic replacement.
- Cập nhật regression tests cho câu hỏi trọng tâm, kết luận động và bảo toàn file lớp/phụ lục.

## Result summary

- File root chỉ hiển thị một câu hỏi dựa trên `fragment_criterion_coverage × official_pass`.
- Kết quả hiện tại của cặp trọng tâm: crude `r=0.1250178390`, adjusted `r=-0.0932743777`; crude có bằng chứng, adjusted không có bằng chứng và vẫn estimable. Các số này chỉ nằm trong phụ lục kỹ thuật.
- Kết luận HNMU được sinh: chưa thể khẳng định mẫu được dẫn fragment đầy đủ hơn có tỷ lệ đạt cao hơn; khi so sánh cùng khối lớp và nhóm chấm không còn thấy khác biệt rõ ràng.
- Root workbook có một sheet, 14 hàng, tối đa 3 cột, 0 table, 0 filter, không freeze pane; render ở zoom thông thường đọc được mà không cuộn ngang.
- So sánh snapshot: 24/24 CSV giữ nguyên SHA-256; 5/5 phụ lục, 4/4 summary theo lớp và 7/7 workbook khác giữ nguyên toàn bộ cell values.
- Validator standalone đạt: 1.050 mẫu, 18.900 khóa tiêu chí, 665 pass, 382 need_human_review, 3 failed, path leaks bằng 0.
- Bộ regression liên quan đạt 14 test; test bổ sung chứng minh kết luận thay đổi theo dữ liệu cũng đạt.

## Orchestrator decision

Chỉ file 05 root dùng summary một câu hỏi. File 07 theo lớp giữ nguyên schema 8 dòng; toàn bộ phân tích bổ sung tiếp tục nằm trong phụ lục kỹ thuật. Dừng để project lead review; không stage, commit, push hoặc upload.

## Uncertainty

Không có sai lệch dữ liệu được phát hiện. Bản render được tạo từ nội dung, kích thước hàng/cột và style của workbook bằng công cụ hệ thống vì server không có LibreOffice.

## Open questions and next human decisions

- Project lead mở file 05 root để duyệt lần cuối cách diễn đạt.
- Project lead quyết định bước Git/upload riêng sau review.
