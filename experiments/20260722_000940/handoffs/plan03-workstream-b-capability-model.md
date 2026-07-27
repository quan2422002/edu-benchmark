# Bàn giao Workstream B — mô hình năng lực

- Mã phân công: `PLAN03-BCD-SPEC-001`
- Chuyên gia: `benchmark-specification-designer`
- Trạng thái: `stopped_after_workstream_b`
- Luồng chuyên gia: `/root/plan03_specification_draft`

## Nhiệm vụ được giao

Tổng hợp Workstream B–D từ nền tảng đo lường, các bài báo gia sư, phương pháp HNMU và mẫu khám phá. Sau lượt đầu chưa tạo đủ tệp, nhiệm vụ được chia tuần tự và giới hạn ở Workstream B. Theo yêu cầu của người phụ trách dự án, chuyên gia dừng sau B, không triển khai C–D.

## Điều chỉnh trong quá trình thực hiện

- Chia trình tự B → C → D để kiểm từng phụ thuộc.
- Sửa truy vết vì bản đầu dùng nguồn về độ tin cậy, phân tích câu hỏi và thiên lệch mô hình vượt quá vai trò khoa học.
- Dừng sau Workstream B.
- Điều phối viên hoàn thiện phần sửa ở chế độ một tác nhân với hướng dẫn chuyên gia chuẩn.

## Đầu vào đã đọc

- Plan 03;
- nền tảng đo lường của Workstream A;
- ba benchmark gia sư AI đã rà trước Plan 03;
- phương pháp mức nhận thức và dàn giáo HNMU;
- đặc tả cũ chỉ như hạt giống lịch sử.

## Kết quả tạo ra

- Bản nguồn: `outputs/benchmark_specification/specialist_draft/construct_v1_draft/`
- Bản công bố nội bộ: `outputs/benchmark_specification/construct_v1_draft/`
- Tệp kê khai công bố: `outputs/benchmark_specification/plan03_workstream_b_publication_manifest.json`

## Tóm tắt kết quả

Bản hiện tại có 6 giả thuyết năng lực, 6 dòng bằng chứng quan sát, đủ 15 cặp chồng lấn, 6 dòng truy vết cấp năng lực, 6 nguồn hợp nhất và 25 liên kết hỗ trợ nghiên cứu. Nguồn `MTF-S013` bổ sung căn cứ cho ranh giới `STRAT–SCAFF` và từng phần cho `STATE–DIAG`. Không có mục nào ở trạng thái `confirmed`.

Các lỗi đã sửa:

1. tách nguồn đo lường khỏi nguồn tiền lệ về hành vi gia sư;
2. loại nguồn không phù hợp khỏi căn cứ trực tiếp cho năng lực;
3. bổ sung nguồn gốc mã và ma trận giải thích bài báo hỗ trợ từng năng lực;
4. sửa lỗi định dạng CSV;
5. chuẩn hóa tài liệu dành cho người đọc sang tiếng Việt.

## Quyết định của điều phối viên

Chấp nhận đây là mô hình năng lực bản nháp để HNMU/UET rà soát, không phải mô hình cuối. Không khởi chạy mã hóa chuyên môn của C hoặc xây tiêu chí của D.

## Điểm chưa chắc chắn

- `CAP-STATE` và `CAP-DIAG` là cặp cần kiểm định ranh giới giữa mô tả trạng thái và giải thích nguyên nhân.
- `CAP-STRAT` và `CAP-SCAFF` là cặp cần kiểm định ranh giới giữa chọn phương tiện và điều tiết hỗ trợ; `MTF-S013` là căn cứ trực tiếp cho cách tách này.
- Căn cứ trực tiếp của `CAP-CARE` còn yếu và cần phân ranh với cổng lỗi nghiêm trọng.
- Chưa có rà soát độc lập, chỉ số đồng thuận hoặc phân xử của HNMU/UET.

## Quyết định con người tiếp theo

- Sáu giả thuyết đã đủ và phù hợp lớp 6–9 chưa?
- Mỗi năng lực có thể quan sát trong đúng một lượt phản hồi không?
- Cặp nào cần giữ, gộp, tách, sửa hoặc yêu cầu thêm bằng chứng?
