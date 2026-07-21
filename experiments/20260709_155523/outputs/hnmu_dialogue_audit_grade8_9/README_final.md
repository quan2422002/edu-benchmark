# Gói kết quả chính — kiểm toán dữ liệu hội thoại HNMU lớp 8–9

Thư mục này chứa gói kết quả chính của lượt kiểm toán dữ liệu hội thoại thô HNMU lớp 8–9. File này chỉ mô tả các thành phần không bị `.gitignore` loại khỏi gói kết quả chính.

## File cấp root

- `normalized_dialogue_rows.csv`: bản dẫn xuất có cấu trúc từ Excel gốc, gồm 588 mẫu. Dùng file này để truy vết `sample_id`, file nguồn, dòng nguồn, lớp, bài học, câu hỏi, đáp án SGV và hội thoại.
- `coverage_summary.csv`: thống kê độ phủ toàn batch theo lớp, chủ đề, bài học theo lớp, mức nhận thức và file nguồn.
- `missing_field_report.csv`: các lỗi thiếu trường hoặc lỗi cấu trúc cơ học phát hiện được bằng code.
- `duplicate_candidates.csv`: ứng viên trùng/gần trùng phát hiện bằng so khớp văn bản. Với batch lớp 8–9 hiện tại, file này có 1 cặp ứng viên trùng.

## Thư mục con chính

- `checklists/`: snapshot checklist dùng cho lượt audit này. Xem `checklists/README_final.md`.
- `agent_shard_audit/`: kết quả chính sau specialist audit. Xem `agent_shard_audit/README_final.md`.
- `reports/`: bản copy các report cần đọc cùng output. Xem `reports/README_final.md`.

## File chính để review từng mẫu

File cấp mẫu chính là:

```text
agent_shard_audit/merged/quality_check_suggestions.csv
```

Phân bố hiện tại:

- 427 mẫu `pass`;
- 160 mẫu `need_human_review`;
- 1 mẫu `failed`.

Khi cần xem lý do chi tiết theo từng tiêu chí, dùng:

```text
agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
```

## Không thuộc gói kết quả chính

Các file/thư mục bị `.gitignore` loại như per-shard, regex-repair intermediate, backup `.pre_*`, hoặc output kiểm cơ học cũ không được mô tả trong `README_final.md`. Nếu cần truy vết lịch sử chạy, xem `README.md` ở từng thư mục hoặc các report kỹ thuật tương ứng.
