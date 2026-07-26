# Plan 08b — Đóng gói lại kết quả Phase 1 theo loại deliverable

Experiment: `20260709_155523`
Trạng thái: `APPROVED`
Ngày duyệt: 21/07/2026
Người duyệt: project lead
Người thực hiện: Codex ở chế độ single-agent

## Mục tiêu

Thay riêng lớp trình bày của Plan 08 bằng bundle v2 tổ chức theo loại deliverable. Tái sử dụng logic đọc allowlist, join và validation canonical đã pass; không chạy lại experiment hoặc specialist audit.

## Ràng buộc

- Không sửa 15 nguồn canonical và không đọc `shared/**`.
- Không sửa hoặc ghi đè `deliverables/hnmu_dialogue_audit_phase1/`.
- Chỉ tạo `deliverables/hnmu_dialogue_audit_phase1_v2/`.
- Giữ nguyên nội dung trường văn bản; giữ `grade` và `sample_id` ở các bảng cần truy vết.
- Mỗi workbook chỉ có một sheet dữ liệu chính.
- File độ phủ nhóm pass phải join theo `sample_id`, lọc `quality_decision = pass` rồi tính lại theo lớp và chiều độ phủ.
- Dùng trực tiếp `/home/dknguyen/miniconda3/envs/edu_ai/bin/python`.
- Không stage, commit, push, upload hoặc chạy `rclone`.

## Deliverable v2

Root chỉ chứa tài liệu dùng chung và bảng so sánh giữa các khối:

- `README.md`
- `01_bao_cao_tong_quan.md`
- `02_checklist_tieu_chi.xlsx`
- `03_thong_ke_pass_reject_giua_cac_khoi.xlsx`
- `04_thong_ke_do_phu_mau_pass_giua_cac_khoi.xlsx`

Mỗi thư mục `lop_6/`, `lop_7/`, `lop_8/`, `lop_9/` có cùng bảy file:

- `README.md`
- `01_du_lieu_tho_sau_chuan_hoa.csv`
- `02_thong_ke_do_phu_mau_pass.xlsx`
- `03_ket_qua_cham_tong_the_tung_mau.csv`
- `04_ket_qua_cham_chi_tiet_tung_tieu_chi.csv`
- `05_mau_thieu_sai_truong_du_lieu.csv`
- `06_ung_vien_trung_lap.csv`

## Bổ sung phân tích fragment đã duyệt ngày 21/07/2026

Giữ nguyên bundle phân lớp đã có và bổ sung một workbook phân tích fragment–kết quả chấm trong từng thư mục lớp, một workbook pooled/so sánh giữa khối ở root, cùng cập nhật README/báo cáo liên quan. Phân tích đọc đúng hai raw checklist merged và hai quality suggestion canonical, lấy `quality_decision` làm trạng thái chính thức, tổng hợp ở cấp `sample_id`, không chạy lại audit, không đọc `shared/**`, không ghi đè workbook đã có và không commit/push/upload.

## Đặc tả hợp nhất đã duyệt ngày 22/07/2026

Rà soát và rebuild toàn bộ bundle từ checklist repaired/canonical hiện hành; bổ sung bốn CSV tổng hợp ở root; tính lại duplicate trên toàn bộ lớp 6–9; left join độ phủ pass từ danh mục bài học đầy đủ; rebuild phân tích fragment ở cấp `sample_id`; thiết kế lại workbook fragment để giáo viên tự đọc; chuẩn hóa mọi đường dẫn bàn giao thành tên file hoặc đường dẫn tương đối; validate toàn bộ bundle. Được phép thay thế bundle v2 hiện tại bằng bản build đã validate; không sửa nguồn canonical, không chạy lại audit, không commit, push hoặc upload.

Đặc tả hợp nhất này thay thế ràng buộc cũ về việc không đọc `shared/**` ở đúng một ngoại lệ: builder được đọc `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv` làm danh mục 75 bài học để left join độ phủ. Builder vẫn không được dereference bất kỳ giá trị `source_file` nào.

Cây root hiện hành có `05_report_fragment_va_ty_le_dat.md`, `05_phu_luc_ky_thuat_phan_tich_fragment.xlsx` và bốn CSV `06`–`09`; mỗi thư mục lớp có thêm file `07_phan_tich_fragment_va_ket_qua_cham.xlsx`, nên có tám file tính cả README.

## Chỉnh sửa review cuối ngày 22/07/2026

Sửa generator kết luận fragment để file từng lớp chỉ mô tả điều chỉnh theo `auditor_group`, file pooled mô tả điều chỉnh theo `grade × auditor_group`, và lớp 8 ghi rõ 8/8 adjusted analyses không thể ước lượng. Đổi nhãn pass trong workbook 03 thành “Đạt theo trạng thái tổng thể chính thức”. Rebuild từ pipeline và giữ nguyên toàn bộ hệ số thống kê.

## Thiết kế lại bản tóm tắt fragment cho HNMU ngày 22/07/2026

Theo yêu cầu trực tiếp của project lead, giữ nguyên dữ liệu và phương pháp phân tích nhưng tách lớp trình bày: file 05 ở root và file 07 trong từng lớp trở thành bản tóm tắt 8 dòng bằng tiếng Việt dễ đọc; toàn bộ 379/46/47/77/63 dòng kỹ thuật được chuyển nguyên vẹn sang phụ lục riêng và bổ sung một `Mã đối chiếu` ổn định. Root có thêm `DANH_MUC_FILE.md`; mỗi workbook vẫn chỉ có một sheet dữ liệu chính. Validator phải chứng minh hệ số, p-value, sample count và `estimable` không đổi, lớp 8 vẫn có 8/8 adjusted analyses không thể ước lượng, và summary nối đủ với phụ lục.

## Thu gọn bản tóm tắt HNMU thành bốn cột ngày 22/07/2026

Theo yêu cầu trực tiếp của project lead, giữ nguyên phụ lục kỹ thuật và toàn bộ hệ số thống kê; chỉ refactor generator bản tóm tắt. Mỗi summary có ba khối mở đầu ngắn, hai khối kết quả và bốn cột: cách đo dẫn chứng, trước điều chỉnh, sau điều chỉnh, diễn giải chính. Logic diễn giải dựa trên bằng chứng thống kê và độ lớn thực tế, không chỉ dựa vào dấu hệ số. Mã đối chiếu, số mẫu và yếu tố kiểm soát không lặp trong bảng HNMU; mã chỉ nằm trong phụ lục, còn quy mô và yếu tố kiểm soát được nêu một lần ở phần giới hạn. Workbook được render để kiểm tra trực quan và vẫn chỉ có một sheet.

## Thu gọn file 05 root thành một câu hỏi ngày 23/07/2026

Theo yêu cầu trực tiếp của project lead, chỉ refactor file `05_phan_tich_fragment_va_ket_qua_cham_giua_cac_khoi.xlsx`. File root chỉ trả lời câu hỏi liệu tỷ lệ tiêu chí có dẫn fragment cao hơn có đi kèm trạng thái đạt chính thức cao hơn hay không, bằng các khối văn bản phổ thông và không hiển thị thuật ngữ hoặc số liệu thống kê. Bốn file summary theo lớp và toàn bộ phụ lục kỹ thuật phải giữ nguyên. Kết luận được sinh từ đúng cặp `fragment_criterion_coverage × official_pass`; builder và validator phải bảo toàn 1.050 mẫu, các trạng thái canonical và toàn bộ hệ số, p-value, sample count, `estimable` trong phụ lục.

## Tách report HNMU và bảng kỹ thuật dễ kiểm tra ngày 23/07/2026

Theo yêu cầu trực tiếp của project lead, thay workbook tóm tắt root bằng `05_report_fragment_va_ty_le_dat.md`, chỉ trả lời câu hỏi `fragment_criterion_coverage × official_pass` bằng ngôn ngữ phổ thông và nội dung sinh từ dữ liệu. Tổ chức lại `05_phu_luc_ky_thuat_phan_tich_fragment.xlsx` thành năm sheet đọc/kiểm tra và sheet cuối `99_Du_lieu_ky_thuat_goc`; sheet đầu có đúng tám kết quả, còn sheet cuối phải giữ nguyên toàn bộ 396 dòng × 29 cột trước refactor. Không thay đổi dữ liệu, phương pháp, hệ số, p-value, số mẫu hoặc trạng thái `estimable`.

## Tiêu chí hoàn thành

- Mỗi file trong thư mục lớp chỉ chứa đúng mẫu của lớp đó.
- Có đúng 1.050 `sample_id` trong bốn file chuẩn hóa: 238, 224, 280 và 308; không mất hoặc trùng.
- Bốn file checklist chi tiết hợp lại có 18.900 dòng và khóa `(sample_id, criterion_id)` duy nhất.
- File thiếu/sai trường và ứng viên trùng lặp bảo toàn các dòng canonical tương ứng, chỉ bổ sung truy vết từ join.
- File trống vẫn có header; README từng lớp ghi rõ số bản ghi bằng 0.
- Bảng root có số lượng, tỷ lệ của `pass`, `need_human_review`, `failed`, `non_pass` cho từng lớp và toàn bộ.
- Báo cáo tổng quan có kiểm định chi-square và Cramér’s V trên bảng lớp × ba trạng thái loại trừ nhau.
- Bảng độ phủ root và từng lớp đều tính lại từ riêng mẫu pass sau join theo `sample_id`.
- Mỗi workbook có đúng một sheet dữ liệu chính, ngoại trừ phụ lục kỹ thuật fragment ở root có sáu sheet theo đặc tả ngày 23/07/2026.
- SHA-256 của 15 nguồn và checksum bundle v1 không đổi; builder không đọc ngoài allowlist.
- Validator mở lại mọi workbook và CSV, đối chiếu nội dung đầy đủ với nguồn canonical.
- Xóa bundle v2 cấu trúc sai rồi tạo lại đúng cùng đường dẫn; không stage, commit, push hoặc upload.
- Build và validation hoàn tất thì dừng để project lead review.
