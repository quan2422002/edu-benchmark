# Specialist handoff

- Delegation ID: `hnmu-dialogue-fragment-score-analysis-051`
- Agent: orchestrator single-agent, áp dụng `hnmu-dialogue-auditor` và `teacher-collaboration-designer`
- Status: hoàn thành và đã validate, chờ project lead review
- Native thread ID/label: không có; thực hiện single-agent theo Plan 08b

## Delegation prompt

Bổ sung phân tích mối liên hệ giữa mức độ tham chiếu fragment với trạng thái pass chính thức và tỷ lệ tiêu chí pass, ở cấp `sample_id`, cho từng lớp 6–9 và toàn bộ dữ liệu. Không chạy lại audit, không sửa nguồn canonical, không ghi đè workbook hiện có, không commit/push/upload.

## Follow-up or steer messages

Không có specialist thread. Yêu cầu được thực hiện trực tiếp vì đây là phân tích hậu kiểm trên output canonical đã có, không thay thế phán quyết chuyên môn của giáo viên.

## Inputs read

- `outputs/hnmu_dialogue_audit/agent_shard_audit/merged/raw_dialogue_checklist_results.csv`
- `outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.csv`
- `outputs/hnmu_dialogue_audit/agent_shard_audit/merged/quality_check_suggestions.csv`
- `outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/quality_check_suggestions.csv`
- Bundle v2 hiện có để cập nhật sáu tài liệu Markdown và đối chiếu bốn file trạng thái tổng thể.

Không đọc hoặc dereference `shared/**`.

## Outputs created

- `deliverables/hnmu_dialogue_audit_phase1_v2/05_phan_tich_fragment_va_ket_qua_cham_giua_cac_khoi.xlsx`
- `deliverables/hnmu_dialogue_audit_phase1_v2/lop_6/07_phan_tich_fragment_va_ket_qua_cham.xlsx`
- `deliverables/hnmu_dialogue_audit_phase1_v2/lop_7/07_phan_tich_fragment_va_ket_qua_cham.xlsx`
- `deliverables/hnmu_dialogue_audit_phase1_v2/lop_8/07_phan_tich_fragment_va_ket_qua_cham.xlsx`
- `deliverables/hnmu_dialogue_audit_phase1_v2/lop_9/07_phan_tich_fragment_va_ket_qua_cham.xlsx`
- Đã cập nhật README root, báo cáo tổng quan và README của bốn lớp.

## Result summary

- Join thành công 1.050/1.050 mẫu; pass chính thức 106, 132, 209, 218.
- Checklist thô có 18.284 khóa `(sample_id, criterion_id)` duy nhất.
- Lớp 6–7 có 154 mẫu chấm 18 tiêu chí và 308 mẫu chấm 16 tiêu chí; khác biệt trùng auditor/shard và không được tự điền hai tiêu chí còn thiếu.
- Tương quan pooled thô giữa fragment và `checklist_pass_rate` dương, nhưng gần 0 và không có ý nghĩa sau kiểm soát `grade × auditor_group`.
- Quan hệ với `official_pass` pooled vẫn dương sau điều chỉnh nhưng không ổn định về chiều/độ mạnh giữa lớp và auditor; không diễn giải nhân quả.
- Năm workbook đều có đúng một sheet; validator mở lại và đối chiếu toàn bộ dòng kết quả.

## Orchestrator decision

Giữ kết luận thận trọng bắt buộc: chưa có bằng chứng về mối liên hệ độc lập và ổn định; sự khác biệt quy trình chấm là một nguồn confounding quan trọng. Dừng để project lead review, không stage/commit/push/upload.

## Uncertainty

Một số strata không có biến thiên outcome hoặc fragment metric. Các strata đó được ghi `estimable = false`, không sinh p-value; adjusted estimate chỉ dùng strata có biến thiên đồng thời.

## Open questions and next human decisions

- Project lead xác nhận cách trình bày thống kê và kết luận trước khi bàn giao HNMU.
- Giáo viên HNMU/UET quyết định liệu có cần phân tích bổ sung theo quy trình phân công auditor sau khi có thiết kế thu thập cân bằng hơn hay không.
