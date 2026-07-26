# Bàn giao bundle Phase 1 v2 phân theo loại và theo lớp

- Mã công việc: `hnmu-dialogue-audit-teacher-bundle-v2-050`
- Chế độ: single-agent/orchestrator; dùng skill `hnmu-dialogue-auditor` và `teacher-collaboration-designer`
- Trạng thái: đã sửa cấu trúc, build và validate; chờ project lead review local
- Runtime: `/home/dknguyen/miniconda3/envs/edu_ai/bin/python`

## Phạm vi

Chỉ refactor lớp đóng gói. Logic allowlist, join và kiểm tra canonical của Plan 08 được tái sử dụng. Không chạy lại experiment hoặc audit; không đọc `shared/**`; không sửa 15 nguồn canonical; không sửa hoặc ghi đè bundle v1. Bundle v2 phẳng sai đã được xóa trước khi tạo lại.

## Cấu trúc đầu ra

Root chỉ có năm mục dùng chung:

- `README.md`
- `01_bao_cao_tong_quan.md`
- `02_checklist_tieu_chi.xlsx`
- `03_thong_ke_pass_reject_giua_cac_khoi.xlsx`
- `04_thong_ke_do_phu_mau_pass_giua_cac_khoi.xlsx`

Bốn thư mục `lop_6/`, `lop_7/`, `lop_8/`, `lop_9/` có cùng bảy file: README, dữ liệu chuẩn hóa, độ phủ mẫu pass, kết quả tổng thể, kết quả từng tiêu chí, cảnh báo thiếu/sai trường và ứng viên trùng lặp.

## Kết quả dữ liệu

- Tổng mẫu: 1.050; lớp 6 = 238, lớp 7 = 224, lớp 8 = 280, lớp 9 = 308.
- Trạng thái toàn bộ: 665 `pass`, 382 `need_human_review`, 3 `failed`, 385 `non_pass`.
- Chi tiết tiêu chí: 18.900 dòng; theo lớp = 4.284, 4.032, 5.040, 5.544.
- Cảnh báo thiếu/sai trường theo lớp = 1, 1, 1, 19; tổng 22.
- Ứng viên trùng lặp theo lớp = 0, 0, 0, 1.
- Độ phủ mẫu pass theo lớp có 20, 18, 26, 31 dòng; root có 95 dòng so sánh bốn khối.
- Chi-square = 61,7950937242; df = 6; p = 1,9421246523e-11; Cramér’s V = 0,1715407681.

## Kiểm tra

- Validator độc lập trên bundle đích: đạt.
- Bốn thư mục tạo phân hoạch rời nhau đủ 1.050 `sample_id`; không mất, trùng hoặc sai lớp.
- Mọi CSV rỗng vẫn có header; README từng lớp ghi số bản ghi, bao gồm số 0.
- Bảy workbook root/từng lớp đều có đúng một sheet dữ liệu chính.
- SHA-256 của đúng 15 nguồn canonical khớp trước/sau build.
- Checksum bundle v1 trước/sau giữ nguyên: `db1c7b808b7edb1a2ef80abff46817c5a37b84a94451270f32df344508d01134`.
- Test v2, hồi quy v1 và checklist: `13 passed in 121.47s`.
- Test tích hợp chặn mọi lần mở đường dẫn dưới `shared/**`: đạt.
- Builder v2 từ chối chạy khi thư mục đích đã tồn tại.

## Quyết định còn lại

Project lead duyệt nội dung và cách trình bày local. Không thực hiện `git add`, commit, push, upload hoặc `rclone` trước khi có chỉ dẫn riêng.
