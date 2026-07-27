# Nhiệm vụ UET — rà soát sổ tay mã hóa trước lô khám phá đầu tiên

**Vai trò phụ trách:** người rà soát, đại diện UET (`UET-REVIEWER-01`).
**Nơi nhận kết quả:** điều phối viên experiment `20260722_000940`.
**Quyết định được phép:** giữ, sửa, gộp, tách, chuyển thành hành vi phụ, yêu cầu thêm ví dụ; cho phép hoặc chưa cho phép mở lô 40.
**Trạng thái tài liệu:** tạm thời, chưa được HNMU xác nhận.
**Khi có bất đồng:** ghi rõ trường hợp và lý do; giữ mở để đưa vào gói HNMU tích hợp sau Workstream D.

## Mục tiêu

Kiểm tra xem tám nhiệm vụ hạt giống và các ranh giới có đủ rõ để AI dùng trong lô khám phá 40 ứng viên đầu tiên hay chưa.

## Vì sao cần nhiệm vụ này

Nếu mã hóa trước khi thống nhất trạng thái học sinh, mục tiêu chính và bằng chứng đáp ứng, các nhãn sẽ phản ánh cách hiểu nhất thời của AI. Cổng này giúp phát hiện sớm nhiệm vụ trùng nhau, nhiệm vụ chỉ là chiến lược phụ và quy tắc chưa thể quan sát trong một phản hồi.

## Bạn nhận được gì

- tám hợp đồng nhiệm vụ hạt giống;
- căn cứ nghiên cứu và giới hạn của từng hạt giống;
- ví dụ đạt và phản ví dụ;
- bảy cặp ranh giới dễ nhầm;
- ba phiếu ghi quyết định ở cấp nhiệm vụ, ranh giới và toàn sổ tay.

## Các bước thực hiện

1. Đọc phần quy tắc chung và sự khác nhau giữa `required_response_evidence` với bằng chứng kiểm tra hội thoại thô.
2. Với từng nhiệm vụ, kiểm ba phần: trạng thái học sinh, mục tiêu gia sư và dấu hiệu tối thiểu trong phản hồi.
3. Đánh dấu nhiệm vụ có hợp đồng riêng hay chỉ là cách thực hiện một nhiệm vụ khác.
4. Đọc ví dụ và phản ví dụ; sửa nếu chúng chưa đúng với Tin học THCS.
5. Kiểm từng cặp ranh giới bằng câu hỏi quyết định.
6. Ghi lý do cụ thể cho mọi đề xuất sửa, gộp hoặc chuyển thành hành vi phụ.
7. Chỉ cho phép mở lô 40 khi sổ tay đủ rõ để AI đề xuất nhãn có thể kiểm tra lại.

## Ví dụ đạt yêu cầu

“Giữ tạm `TASK-DIAG` trong lô đầu, nhưng chỉ gán khi phản hồi phải kiểm một giả thuyết nguyên nhân. Trường hợp chỉ nhận xét đoạn mã sai ở đâu thuộc `TASK-ASSESS`; trường hợp nguyên nhân đã rõ và cần bước tự sửa thuộc `TASK-SCAFFOLD`. Sau lô đầu, nếu không có ví dụ đạt hợp đồng riêng thì chuyển chẩn đoán thành hành vi phụ.”

Nhận xét này chỉ rõ điều kiện dùng, hai ranh giới và tiêu chí xem xét lại bằng dữ liệu.

## Ví dụ cần sửa

“Tám nhiệm vụ trông hợp lý, cứ chạy thử.”

Nhận xét này chưa kiểm hợp đồng, không xử lý ba nhãn còn thiếu bằng chứng dữ liệu và không tạo quy tắc để rà nhãn AI.

## Bạn cần nộp gì

1. Quyết định cho đủ tám nhiệm vụ.
2. Quyết định cho đủ bảy cặp ranh giới.
3. Một quyết định chung: cho phép mở lô 40, cho phép có điều kiện, hoặc yêu cầu sửa trước.

Mọi quyết định sửa/gộp/chuyển loại phải có lý do và ít nhất một ví dụ hoặc quy tắc thay thế.

## Checklist tự kiểm tra

- [ ]  Tôi đã kiểm đủ tám nhiệm vụ và bảy ranh giới.
- [ ]  Tôi phân biệt nhiệm vụ với năng lực và chiến lược sư phạm phụ.
- [ ]  Tôi chỉ yêu cầu dấu hiệu có thể quan sát trong một phản hồi.
- [ ]  Tôi không coi `gold_response` là cách trả lời duy nhất.
- [ ]  Tôi đã xem riêng `TASK-DIAG`, `TASK-MODEL` và `TASK-PRACTICE`.
- [ ]  Quyết định mở lô 40 có lý do và điều kiện rõ.
- [ ]  Tôi không trình bày quyết định UET như xác nhận của HNMU.

## Thời gian dự kiến

Khoảng 45–60 phút cho toàn bộ sổ tay; có thể chia thành 25 phút cho tám nhiệm vụ, 20 phút cho ranh giới và 10 phút cho quyết định chung.

## Khi cần hỗ trợ

Nếu một định nghĩa thiếu ví dụ Tin học, đánh dấu yêu cầu bổ sung thay vì tự xác nhận. Nếu hai nhiệm vụ chỉ phân biệt được bằng cách đọc `gold_response`, yêu cầu sửa ranh giới trước khi mở lô 40.
