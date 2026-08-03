# Bàn giao — Làm rõ eligibility và thống kê mục III.C

- Delegation ID: `EXP-20260729-KSE-IIIC-ELIGIBILITY-STATISTICS-001`
- Agent: parent thread dùng `benchmark-specification-designer` ở chế độ single-agent
- Status: hoàn thành
- Native thread ID/label: không tạo specialist thread

## Delegation prompt

Bổ sung đoạn dẫn cho Phase 3, viết lại thang điểm requirement đầy đủ, định nghĩa
trạng thái `eligible` bằng các cổng thực tế, coi 628 mẫu còn lại là bị loại theo
quyết định UET, và thay bảng thống kê bằng biểu đồ sinh từ code.

## Follow-up or steer messages

Không có.

## Inputs read

- `kse_submit_manuscript/manuscript/main.tex`
- `tmp_teacher_packet/huong_dan_hnmu_review_task_rubric_nguyen_tac.docx`
- `src/vertex_ai_call/analyze_requirement_scoring.py`
- Kết quả phân tích full run và tập 1.400 mẫu eligible của experiment hiện tại

## Outputs created

- Cập nhật `kse_submit_manuscript/manuscript/main.tex`.
- Thêm `kse_submit_manuscript/analysis_code/plot_phase3_candidate_statistics.py`.
- Sinh `kse_submit_manuscript/manuscript/figures/phase3_candidate_statistics.png`.
- Biên dịch lại `kse_submit_manuscript/manuscript/main.pdf`.

## Result summary

Mục III.C nay có đoạn dẫn và ba bước rõ ràng; thang điểm 1--5 được viết thành
câu hoàn chỉnh. Bản thảo chỉ dùng thuật ngữ `eligible` và định nghĩa bằng các
điều kiện truy vết evidence, số nguyên tắc, rationale phản thực, ranh giới
Feedback/Questioning và độ phủ của tổ hợp. Tổng cộng 1.400 mẫu được giữ lại và
628 mẫu bị loại; các lý do loại được báo cáo với lưu ý có thể chồng lấn. Biểu
đồ ba panel mô tả phân bố lớp, số nguyên tắc bắt buộc và incidence theo nguyên
tắc, được sinh trực tiếp từ CSV 1.400 mẫu.

## Orchestrator decision

Chấp nhận bản sửa trong phạm vi III.C; không thay đổi dữ liệu nguồn hay logic
phân tích Plan 03.

## Uncertainty

Các lý do loại có thể chồng lấn nên tổng incidence lớn hơn 628; điều này đã
được nói rõ trong paper.

## Open questions and next human decisions

UET tiếp tục review các phần còn lại của manuscript.
