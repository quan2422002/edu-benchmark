# Specialist handoff

- Delegation ID: `p02-step1-author-form-review-001`
- Agent: `teacher-collaboration-designer`
- Status: completed via `single-agent fallback`
- Native thread ID/label: `null` / single-agent parent thread

## Delegation prompt

Kiểm tra phiếu tác giả trong `review_form.xlsx` theo Bước 1 của Plan 02. Xác định ý nghĩa từng trường, ai nên điền, trường nào bắt buộc/tùy chọn, điểm mơ hồ, đề xuất sửa và câu hỏi cần UET/HNMU xác nhận. Không sửa Google Sheet.

## Follow-up or steer messages

- Ban đầu không có steer riêng. Người phụ trách dự án yêu cầu thực hiện riêng việc 1 trước để xem kết quả.
- Sau đó người phụ trách dự án nhắc đúng rằng việc 1 còn thiếu phần lấy/snapshot file Google Drive của experiment. Orchestrator đã bổ sung `drive_snapshot/` và cập nhật handoff này.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260620_115236/roadmap.md`
- `AGENTS.md`
- `agents/teacher-collaboration-designer/SKILL.md`
- `agents/teacher-collaboration-designer/references/plain-language-guidelines.md`
- `experiments/20260701_100006/plans/02-author-form-rubric-task-and-learning-resource-sprint.md`
- `experiments/20260701_100006/reports/hnmu-author-form-meeting-structured-notes-20260701.md`
- Google Drive folder `version 20260701_100006`, folder id `18k6oGkD4RJMhcKNjsVc178x2S2f6iur5`
- Google Drive file `review_form.xlsx`, file id `1hx-bmX1hNfdFImfoKlXztGKp9QGCcou1`, modified `2026-07-03T12:37:31.852Z`
- `experiments/20260701_100006/drive_snapshot/drive_file_manifest.csv`
- `experiments/20260701_100006/drive_snapshot/files/teacher_packet/review_form.xlsx`
- `experiments/20260701_100006/drive_snapshot/review_form.extracted.txt`

## Outputs created

- `experiments/20260701_100006/author_form/author_form_field_review.md`
- `experiments/20260701_100006/author_form/author_form_field_matrix.csv`
- `experiments/20260701_100006/drive_snapshot/README.md`
- `experiments/20260701_100006/drive_snapshot/drive_file_manifest.csv`
- `experiments/20260701_100006/drive_snapshot/review_form.extracted.txt`
- `experiments/20260701_100006/drive_snapshot/files/**`
- `experiments/20260701_100006/reports/hnmu-open-questions.md`
- `experiments/20260701_100006/coordination/delegations.jsonl`
- `experiments/20260701_100006/handoffs/p02-step1-author-form-review-001.md`

## Result summary

Phiếu tác giả đủ tốt để pilot/thảo luận, nhưng chưa nên dùng nhập dữ liệu số lượng lớn nếu chưa sửa các điểm chính:

- mã task và chủ đề cần registry/danh sách chuẩn trước;
- định nghĩa `conversation_history` cần sửa theo quy ước “bước = cặp trao đổi học sinh–gia sư”;
- học liệu tham khảo cần mã học liệu ổn định;
- điểm rubric và các điểm phụ cần phân vai reviewer/cross-validator rõ;
- `cross_validator_name` đang mâu thuẫn giữa yêu cầu kiểm tra chéo và mức bắt buộc;
- một số tên kỹ thuật cần sửa sau khi ổn định.

Phần input Drive đã được bổ sung sau nhắc nhở của người phụ trách dự án:

- đã list folder Drive `version 20260701_100006` và 3 thư mục con `teacher_packet`, `literature_review`, `curriculum_sources`;
- đã tải/export 14 file trong Drive experiment vào `drive_snapshot/files/`;
- đã tạo manifest 18 dòng, gồm 4 folder và 14 file;
- đã xác nhận `review_form.xlsx` tải về là `.xlsx` hợp lệ và có bản text audit `review_form.extracted.txt`.

## Orchestrator decision

Không spawn specialist thread vì không có native subagent tool đang callable trong lượt này. Đã dùng canonical skill trong parent thread theo cơ chế `single-agent fallback`, đúng với AGENTS.md khi native specialist visibility không khả dụng.

## Uncertainty

- Google Drive file `review_form.xlsx` là Office `.xlsx`, không phải native Google Sheet; connector Sheets không đọc trực tiếp được bằng range. Sau phần bổ sung, file đã được tải raw vào `drive_snapshot/files/teacher_packet/review_form.xlsx` và trích xuất text audit bằng Python chuẩn.
- Chưa sửa Google Sheet; mọi đề xuất nằm trong artifact local để người phụ trách dự án review trước.
- Chưa chạy validator teacher packet vì output không phải teacher packet/task card theo schema; đây là báo cáo rà soát phiếu.

## Open questions and next human decisions

- Xác nhận bản `review_form.xlsx` nào là bản chính thức để HNMU nhập dữ liệu.
- Xác nhận có được sửa tên cột/tên trường kỹ thuật không.
- Xác nhận quy ước “bước = cặp trao đổi” với HNMU.
- Xác nhận ai là người chấm rubric chính thức.
- Xác nhận `cross_validator_name` bắt buộc với mẫu hoàn thành hay không.
