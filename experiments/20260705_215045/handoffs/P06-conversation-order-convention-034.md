# Specialist handoff

- Delegation ID: P06-conversation-order-convention-034
- Agent: teacher-collaboration-designer
- Status: completed
- Native thread ID/label: single-agent mode in parent Codex thread; no hidden subprocess

## Delegation prompt

Revise P06 teacher examples and teacher packet so `conversation_history` follows the new sheet “quy ước” from `review_form.xlsx`: `student_prompt` + `student_work` form the opening student step; `conversation_history` records later exchanges; `gold_response` is the final tutor response.

## Follow-up or steer messages

User requested direct implementation after confirming the examples did not fully comply with the new convention.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260705_215045/roadmap.md`
- `experiments/20260705_215045/plans/06-teacher-examples-and-pilot-packet.md`
- Google Drive `review_form.xlsx`, sheet “quy ước”
- `experiments/20260705_215045/teacher_examples/author_form_example_*.md`
- `experiments/20260705_215045/teacher_packet/05-author-template.md`

## Outputs created

- Updated `experiments/20260705_215045/teacher_examples/author_form_example_*.md`
- Updated `experiments/20260705_215045/teacher_packet/05-author-template.md`
- Updated `experiments/20260705_215045/teacher_packet/04-examples.md`
- Updated `experiments/20260705_215045/reports/P06-teacher-examples-and-packet-summary.md`
- Created this handoff

## Result summary

- Examples with only an opening student question now state that there has been no exchange after the opening step.
- Examples with follow-up exchanges now start `conversation_history` with the tutor and end with the student.
- The author template now explains the convention explicitly for teachers.

Changed example files: author_form_example_01_khai_niem_the_gioi_ki_thuat_so.md, author_form_example_02_trac_nghiem_thiet_bi_so.md, author_form_example_03_tu_luan_danh_gia_thong_tin.md, author_form_example_04_chan_doan_hieu_lam_nguon_thong_tin.md, author_form_example_05_giai_thich_ban_quyen_internet.md, author_form_example_06_phan_hoi_tinh_huong_mat_khau.md, author_form_example_07_goi_y_trinh_bay_thong_tin.md, author_form_example_08_phan_hoi_cong_thuc_if.md, author_form_example_09_chan_doan_nham_countif_sumif.md, author_form_example_10_goi_y_sap_xep_tep_thu_muc.md, author_form_example_11_phan_hoi_code_python.md, author_form_example_12_goi_y_thuat_toan_tim_max.md, author_form_example_13_phan_hoi_nghe_nghiep_tin_hoc.md

## Orchestrator decision

Treat this as a P06 convention revision, not a benchmark-design change. Task/rubric/coverage selections are unchanged.

## Uncertainty

The exact phrase “Chưa có trao đổi sau bước mở đầu” should be confirmed by HNMU if they prefer an empty cell or another placeholder in the spreadsheet.

## Open questions and next human decisions

- HNMU/UET should confirm whether `conversation_history` may be empty/placeholder when there is no exchange after the opening student step.
