# Specialist handoff

- Delegation ID: `hnmu-dialogue-audit-teacher-bundle-v2-repaired-052`
- Agent: orchestrator single-agent, áp dụng `hnmu-dialogue-auditor` và `teacher-collaboration-designer`
- Status: hoàn thành và đã validate, chờ project lead review local
- Native thread ID/label: không có; thực hiện single-agent theo Plan 08b đã `APPROVED`

## Delegation prompt

Rà soát và sửa pipeline, rebuild toàn bộ bundle Phase 1 v2 từ checklist repaired/canonical, bổ sung bốn CSV tổng hợp root, rebuild độ phủ bài học và phân tích fragment, chuẩn hóa đường dẫn, rồi validate toàn bộ. Không chạy lại audit, không sửa nguồn canonical, không commit/push/upload.

## Follow-up or steer messages

Không có specialist thread. Hai skill canonical được dùng trong parent thread để giữ đúng provenance audit và cách trình bày dễ đọc cho giáo viên. Không có phán quyết chuyên môn HNMU/UET nào bị thay thế.

## Inputs read

- Checklist lớp 6–7: `outputs/hnmu_dialogue_audit/agent_shard_audit/merged/raw_dialogue_checklist_results.repaired.csv`.
- Checklist lớp 8–9: `outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv`.
- Trạng thái chính thức: hai file `agent_shard_audit/merged/quality_check_suggestions.csv` tương ứng.
- Dữ liệu chuẩn hóa, missing report, duplicate candidates, coverage summary, review queue và báo cáo canonical trong allowlist Plan 08.
- Danh mục 75 bài học: `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv`.
- Repair report: `outputs/hnmu_dialogue_audit/reports/hnmu-dialogue-auditor-shard-repair-20260718.md`.

Không mở hoặc dereference các giá trị nằm trong cột `source_file`.

## Outputs created

- Rebuild toàn bộ `deliverables/hnmu_dialogue_audit_phase1_v2/` bằng cơ chế staging + atomic replacement.
- Bổ sung bốn CSV root: file 06–09.
- Rebuild file độ phủ root và bốn file độ phủ theo lớp từ danh mục bài học đầy đủ.
- Rebuild năm workbook fragment từ checklist repaired và thiết kế lại phần hướng dẫn/kết luận/bảng dữ liệu.
- Thêm pipeline `dialogue_audit.teacher_bundle_v2_complete`, lớp phân tích repaired, regression tests và chuyển các CLI v2/fragment sang builder canonical mới.

## Result summary

- Join 1.050/1.050 mẫu; phân hoạch lớp 6/7/8/9 là 238/224/280/308.
- Có 18.900 khóa `(sample_id, criterion_id)` duy nhất; phân phối sau repair là 1.050 mẫu × 18 tiêu chí. RAW-CON-06/07 đã có trong nguồn repaired lớp 6–7.
- Trạng thái chính thức không đổi: pass 106/132/209/218, tổng 665; need_human_review 382; failed 3.
- Trước repair, fragment pipeline đọc 18.284 khóa và lớp 6–7 có 154 mẫu × 18, 308 mẫu × 16. Sau repair tăng 616 dòng tiêu chí và mọi mẫu có đủ 18 tiêu chí.
- Bốn CSV root có lần lượt 1.050, 22, 1 và 1.050 dòng; duplicate được chạy lại trên toàn bộ lớp 6–9, không có candidate liên lớp đạt quy tắc/ngưỡng 0,96.
- Danh mục độ phủ có 17/16/20/22 bài; số bài không có mẫu pass là 6/5/4/3.
- Phân tích thô dùng point-biserial cho `official_pass`, Spearman cho `checklist_pass_rate`; adjusted dùng demeaning/rank residualization trong `auditor_group`, và pooled dùng strata `grade × auditor_group`.
- Kết quả pooled repaired không ổn định: một số hệ số giảm gần 0, đổi chiều hoặc chỉ ước lượng được trên strata có đủ biến thiên. Kết luận bàn giao không mang tính nhân quả và nêu chưa có bằng chứng về liên hệ độc lập, ổn định.
- Đường dẫn nội bộ trong `source_file`/evidence được thay bằng basename; một ví dụ đường dẫn Windows trong nội dung được chuyển từ dạng tuyệt đối sang tên thư mục tương đối. Validator không tìm thấy `experiments/`, `outputs/`, `shared/` hoặc đường dẫn tuyệt đối trong bundle.

## Orchestrator decision

Giữ nguyên toàn bộ nguồn canonical và bundle v1. Dùng bundle v2 repaired làm bản duy nhất chờ review local. Không stage, commit, push hoặc upload.

## Uncertainty

- Lớp 8 không có auditor_group nào đủ biến thiên đồng thời cho các adjusted estimate; các dòng này ghi “Không thể ước lượng” và không có p-value.
- Một số metric lớp 9 và nhiều strata lớp 6–7 cũng không đủ biến thiên. Pooled adjusted chỉ dùng 308–350 mẫu tùy metric; workbook ghi số mẫu và cảnh báo cụ thể.
- Không có LibreOffice/soffice hoặc renderer spreadsheet trên máy. Bố cục được kiểm tra bằng openpyxl (freeze pane, filter, độ rộng, wrap, fill, number format, không merged cell/NaN) và preview SVG tạm; không có kiểm tra hiển thị bằng ứng dụng Excel thực.

## Open questions and next human decisions

- Project lead mở thử năm workbook fragment trong Excel/LibreOffice và xác nhận cách đọc/màu sắc trước bàn giao HNMU.
- Project lead quyết định stage/commit và tự upload sau khi review; task này không thực hiện các bước đó.
