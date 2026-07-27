# Báo cáo Workstreams A–B — nền tảng đo lường và mô hình năng lực tạm thời

Ngày cập nhật: 26/07/2026  
Thử nghiệm: `20260722_000940`  
Trạng thái: **A hoàn tất; B được đại diện UET phê duyệt tạm thời; kiến trúc C đã đồng bộ sang sáu nguyên tắc nhưng chưa mã hóa; HNMU review chuyển sang gói tích hợp sau D.**

> Cập nhật kiến trúc 26/07/2026: Workstream C không tiếp tục hệ phân loại tám nhiệm vụ. Thiết kế hiện hành có một nhiệm vụ benchmark, sáu nguyên tắc KMP và sáu năng lực. Toàn bộ artifact tám nhiệm vụ/20 nhãn thử đã chuyển sang `outputs/benchmark_specification/legacy/eight_task_candidate_branch/`. Các phần A–B dưới đây vẫn giữ giá trị lịch sử.

## 1. Phạm vi đã hoàn tất

- Workstream A: tổng hợp căn cứ khoa học về đo lường và sửa ma trận bằng chứng về đúng 19 cột.
- Workstream B: xây sáu giả thuyết năng lực, kiểm đủ 15 cặp chồng lấn, lập chuỗi truy vết nghiên cứu và ghi cổng UET tạm thời.
- Chuẩn bị cơ học cho C: khóa input, thống kê 2.028 ứng viên và lấy mẫu 160 ứng viên thuộc 160 hội thoại gốc, đủ 40 ứng viên mỗi lớp.
- Bổ sung validator kiểm cả header và số cột của từng dòng CSV; lỗi dịch cột không còn có thể vượt qua kiểm tra chỉ vì header đúng.

Chưa thực hiện chính thức:

- mã hóa, hiệu chỉnh, hai người gán nhãn độc lập, đo đồng thuận hoặc kiểm bão hòa ở Workstream C;
- hệ tiêu chí hai tầng, cổng lỗi nghiêm trọng và ngữ cảnh đánh giá ở Workstream D;
- sinh hoặc chấm phản hồi mô hình ở Workstreams E–G.

## 2. Kết quả Workstream A

Thư mục `literature_notes/plan03_measurement_foundations/` có giao thức, nhật ký tìm kiếm, 13 nguồn, ma trận bằng chứng, ma trận phát biểu và bản tổng hợp phương pháp. Các kết luận vận hành chính là:

1. thiết kế theo chuỗi **năng lực cần đo → nhiệm vụ → bằng chứng → cách chấm**;
2. rà soát nội dung của chuyên gia là cần thiết nhưng chưa đủ để khẳng định hiệu lực;
3. phải kiểm độ nhất quán người chấm, khả năng phân biệt, hiệu ứng sàn/trần và thiên lệch mô hình chấm;
4. `gold_response` là phản hồi tham chiếu, không phải cách diễn đạt hợp lệ duy nhất.

Đợt rà cuối phát hiện các dòng `MTF-S002`–`MTF-S012` bị thiếu cột dù header đúng. Các dòng đã được tái lập đúng ý nghĩa; riêng `MTF-S007` nay tách đúng kết quả chính, giới hạn, mức liên quan, vị trí bằng chứng và ghi chú rà soát.

## 3. Kết quả Workstream B

Bản công bố nội bộ tại `outputs/benchmark_specification/construct_v1_draft/` gồm:

- 6 giả thuyết năng lực và 6 dòng bằng chứng quan sát;
- đủ 15/15 cặp trong ma trận chồng lấn;
- 6 dòng truy vết cấp năng lực;
- 6 nguồn trong danh mục hợp nhất và 25 liên kết hỗ trợ;
- 0 năng lực ở trạng thái `confirmed`.

Đại diện UET tạm thời giữ riêng:

- `CAP-STATE` và `CAP-DIAG`: mô tả trạng thái hiện tại khác với giải thích nguyên nhân;
- `CAP-STRAT` và `CAP-SCAFF`: chọn phương tiện/chức năng khác với điều tiết mức độ, thời điểm và chuyển giao hỗ trợ.

`CAP-CARE` chỉ quan sát giao tiếp rõ ràng, tôn trọng, vừa sức và khích lệ có căn cứ trong chính phản hồi; không đo thay đổi động lực hoặc kết quả học tập thật. Khả năng quan sát của từng năng lực được giới hạn ở bằng chứng có trong prompt, lịch sử và phản hồi đích.

## 4. Truy vết nghiên cứu

- `research_source_registry.csv` giải thích nguồn gốc mỗi mã, bài báo, vị trí bằng chứng, vai trò và giới hạn.
- `research_support_matrix.csv` nêu bài báo hỗ trợ phần nào của mỗi năng lực và phần nào chỉ là suy luận thiết kế.
- `capability_research_basis.md` diễn giải toàn bộ chuỗi bằng tiếng Việt và được đồng bộ vào gói review.
- `MTF-S013` là Van de Pol và cộng sự (2010), hỗ trợ trực tiếp ranh giới chiến lược–dàn giáo và hỗ trợ từng phần ranh giới trạng thái–chẩn đoán.
- Hai phương pháp HNMU được truy bằng đường dẫn tài liệu địa phương, không giả làm paper hoặc cấp mã nghiên cứu.

## 5. Cổng UET và kế hoạch HNMU

UET đã duyệt tạm thời sáu năng lực để làm giả thuyết đầu vào của C. Đây không phải xác nhận mô hình cuối. HNMU sẽ review một gói tích hợp sau D gồm năng lực, nhiệm vụ, tiêu chí, cổng lỗi và ví dụ tốt–trung bình–kém.

Hai task card review/phân xử cũ trong `teacher_review_packets/workstream_b_round1/` đã được đánh dấu rõ là mẫu tham khảo đã hoãn. Chúng không còn mô tả một vòng HNMU đang hoạt động.

## 6. Trạng thái Workstream C

Các input cơ học vẫn sẵn sàng: census 2.028 ứng viên, mẫu 160 hội thoại và bảng coding input. Sau quyết định UET:

- `benchmark_tasks.csv` chỉ còn `TASK-NEXT-TUTOR-RESPONSE`;
- `pedagogical_principles.csv` định nghĩa sáu nguyên tắc KMP;
- codebook hiện hành quy định một nguyên tắc chính, tối đa một nguyên tắc phụ và `coverage_gap_reason`;
- tám nhiệm vụ, 20 nhãn thử và packet C1 cũ là legacy, không được tính vào coverage hoặc hiệu chỉnh;
- số nhãn nguyên tắc chính thức vẫn là 0; bước tiếp theo là lô 40 đầu tiên.

## 7. Kết quả kiểm tra

Trình thông dịch dùng để kiểm tra:

`/home/quannda/miniconda3/envs/benchmark_env/bin/python`

Kết quả cuối:

- validator ma trận bằng chứng: đạt;
- validator/cơ chế công bố Workstream B: đạt;
- validator gói UET/HNMU: đạt;
- kiểm toàn bộ CSV liên quan về độ rộng dòng: đạt;
- toàn bộ kiểm thử kho mã: `112 passed`;
- kiểm tra khoảng trắng thay đổi: đạt.

## 8. Kết luận

Workstreams A–B đủ điều kiện làm nền cho Workstream C. Việc tiếp theo là mã hóa sáu nguyên tắc trên lô 40 đầu tiên; không review hoặc tái sử dụng tám nhiệm vụ/20 nhãn legacy làm kết quả hiện hành.
