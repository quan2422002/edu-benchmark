# Bàn giao sửa sau rà soát Workstream A–B

- Mã công việc: `PLAN03-AB-POSTREVIEW-CORRECTION-001`
- Chế độ thực hiện: một tác nhân, sử dụng hướng dẫn chuẩn của `research-methodologist`, `benchmark-specification-designer` và `teacher-collaboration-designer`
- Trạng thái: `completed`
- Luồng chuyên gia mới: không có

## Yêu cầu của người phụ trách dự án

Sửa tình trạng lẫn tiếng Anh–tiếng Việt trong tài liệu dành cho người đọc; giải thích nguồn gốc các `research_id`; và bổ sung bằng chứng cho biết từng bài báo hỗ trợ mỗi năng lực như thế nào.

## Đầu vào đã đọc

- kết quả Workstream A và Workstream B;
- ba tóm tắt benchmark gia sư AI trước Plan 03;
- Plan 03, roadmap, báo cáo và các bàn giao hiện hành;
- gói tham vấn HNMU/UET vòng 1;
- hướng dẫn chuẩn của ba chuyên gia liên quan.

## Kết quả tạo hoặc sửa

- chuẩn hóa tiếng Việt trong các tài liệu Workstream A–B dành cho người đọc;
- bổ sung `research_source_registry.csv`;
- bổ sung `research_support_matrix.csv`;
- bổ sung `capability_research_basis.md` ở bản đặc tả và gói HNMU;
- mở rộng `tutor_capabilities.csv` với nguồn gốc mã, tóm tắt hỗ trợ và đường dẫn truy vết;
- mở rộng schema, cơ chế kiểm tra và cơ chế công bố để bắt buộc giữ các tệp mới;
- đồng bộ Plan 03, roadmap, báo cáo, kiến trúc và bàn giao.

## Tóm tắt kết quả

Ba mã `TR-P001`–`TR-P003` được xác định là ba benchmark gia sư AI trước Plan 03. `MTF-S001`–`MTF-S002` thuộc nền tảng đo lường; `MTF-S013` là nền tảng sư phạm bổ sung, được gán trực tiếp cho các năng lực liên quan để truy vết ranh giới dàn giáo. Ma trận mới có 25 liên kết năng lực–nguồn hoặc mô hình–nguồn.

`CAP-CARE` được ghi rõ là giả thuyết có căn cứ trực tiếp yếu nhất; ba benchmark chỉ hỗ trợ từng phần hoặc gián tiếp cho sự rõ ràng, giọng điệu, tránh quá tải và phù hợp người học.

## Kết quả kiểm tra

- ma trận bằng chứng Workstream A: đạt;
- bản công bố Workstream B: 6 năng lực, 6 nguồn, 25 liên kết, 0 mục `confirmed`;
- gói HNMU/UET gồm 9 tệp và không điền trước quyết định: đạt;
- toàn bộ kiểm thử: `107 passed`;
- trình thông dịch: `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.

## Quyết định của điều phối viên

Giữ Workstream B ở trạng thái bản nháp chờ HNMU/UET rà soát. Không mở lại Workstream C hoặc D.

## Điểm chưa chắc chắn và quyết định con người tiếp theo

- HNMU/UET xác nhận sáu giả thuyết có đầy đủ và phù hợp Tin học THCS hay không.
- Kiểm hai cặp cần kiểm định ranh giới: `STATE–DIAG` và `STRAT–SCAFF`, không mặc định gộp.
- HNMU xem xét riêng mức phù hợp của `CAP-CARE` vì căn cứ trực tiếp còn yếu.
- Các kết luận nghiên cứu hiện tại không thay thế kiểm định địa phương và phân xử chuyên gia.
