# Hướng dẫn rà soát sáu giả thuyết năng lực

Trạng thái: **UET phê duyệt tạm thời để khám phá task; HNMU chưa rà soát**.

## Cách hiểu chung

Trong gói này, “năng lực” là một nhóm phẩm chất của gia sư có thể được suy luận từ **một lượt phản hồi**, khi người rà soát được đọc câu hỏi của học sinh và phần trao đổi trước đó. Năng lực không phải là loại bài tập, tiêu chí chấm hay thang điểm.

Các mã bắt đầu bằng `CAP` chỉ dùng để nhận diện đúng giả thuyết:

- `ACC`: độ chính xác;
- `STATE`: trạng thái học sinh;
- `STRAT`: chiến lược sư phạm;
- `SCAFF`: mức và nhịp dàn giáo;
- `DIAG`: chẩn đoán lỗi;
- `CARE`: giao tiếp và sự phù hợp với người học.

Tên và ranh giới của cả sáu mục đều có thể được giữ, gộp, tách, sửa, loại hoặc yêu cầu thêm bằng chứng theo quyết định chuyên gia.

## Cách ghi nhận xét vào phiếu

Các tên dưới đây được giữ nguyên để mọi người ghi vào đúng chỗ. Hãy dùng đúng một lựa chọn cho mỗi nhận xét:

- `reviewer_id`: mã người rà soát do điều phối viên cung cấp.
- `relevance_decision` — mức cần thiết: `necessary` (cần thiết), `not_necessary` (không cần thiết) hoặc `uncertain` (chưa chắc).
- `comprehensiveness_decision` — tính đầy đủ của phạm vi: `sufficient_scope` (đủ phạm vi), `missing_elements` (còn thiếu), `too_broad` (quá rộng) hoặc `uncertain`.
- `comprehensibility_decision` — độ rõ nghĩa: `clear` (rõ), `needs_clarification` (cần làm rõ) hoặc `uncertain`.
- `one_response_observable_decision` — khả năng quan sát trong một lượt: `observable` (quan sát được), `not_observable` (không quan sát được) hoặc `uncertain`.
- `proposed_action` — hướng đề xuất: `retain` (giữ), `merge` (gộp), `split` (tách), `revise` (sửa), `retire` (loại) hoặc `request_more_evidence` (xin thêm bằng chứng).
- `rationale`: lý do chuyên môn, nên nêu dấu hiệu, ranh giới hoặc kinh nghiệm dạy học làm căn cứ.
- `decision_status`: `completed` khi đã ghi đủ; `needs_follow_up` khi cần trao đổi hoặc thêm bằng chứng.

Trong phiếu so sánh cặp, `overlap_decision` dùng một trong bốn lựa chọn: `distinct` (khác nhau rõ), `partly_overlapping` (chồng lấn một phần), `redundant` (dư thừa) hoặc `uncertain`. Nếu phát hiện một năng lực còn thiếu hoàn toàn và không gắn được với dòng nào, hãy nêu riêng trong danh sách câu hỏi gửi điều phối viên; không tự tạo kết luận thay cho buổi tham vấn.

## Sáu giả thuyết cần rà soát

### `CAP-ACC` — Độ chính xác chuyên môn và bám học liệu

Gia sư cung cấp đúng khái niệm, thuật ngữ, ví dụ, thao tác, đoạn lệnh, quy trình và lời giải thích; nội dung phù hợp với học liệu Tin học THCS có thể đối chiếu.

- Bao gồm: đúng kiến thức, đúng thao tác, không bịa nguồn hoặc trộn nhầm nội dung.
- Không thay thế: hiểu tình trạng học sinh, chọn cách dạy hay điều chỉnh lượng hỗ trợ.
- Câu hỏi quan sát: chỉ từ phản hồi và học liệu liên quan, có thể xác định nội dung đúng, thiếu quan trọng hay làm học sinh hiểu sai không?

### `CAP-STATE` — Nhận diện trạng thái, mục tiêu và ngữ cảnh của học sinh

Gia sư hiểu học sinh đang hỏi gì, đã thử gì, đang kẹt ở đâu và cần đạt mục tiêu trước mắt nào.

- Bao gồm: bám đúng câu hỏi, lớp học, bài học và phần trao đổi trước đó.
- Chưa mặc định bao gồm: tìm ra nguyên nhân gốc của lỗi.
- Câu hỏi quan sát: phản hồi có cho thấy gia sư đang trả lời đúng nhu cầu hiện tại của học sinh không?

### `CAP-STRAT` — Chọn chiến lược sư phạm phù hợp

Gia sư chọn cách đáp phù hợp cho lượt này, chẳng hạn hỏi lại, giải thích, gợi mở, làm mẫu, phản hồi hoặc chuyển sang bước tiếp theo.

- Bao gồm: chọn đúng kiểu hỗ trợ theo mục tiêu học tập.
- Chưa mặc định bao gồm: cho bao nhiêu trợ giúp hoặc chia thành bao nhiêu bước.
- Câu hỏi quan sát: với tình trạng của học sinh, kiểu hành động sư phạm được chọn có hợp lý không?

### `CAP-SCAFF` — Điều chỉnh mức hỗ trợ và nhịp dàn giáo

Gia sư chia nhỏ vừa đủ, đưa lượng gợi ý phù hợp và rút dần hỗ trợ khi học sinh có thể tự làm.

- Bao gồm: chọn mức từ gợi mở, giải thích, gợi ý, hướng dẫn đến làm mẫu theo nhu cầu; tránh làm thay hoặc bỏ mặc.
- Không mặc định bao gồm: tìm nguyên nhân gốc của lỗi hoặc kiểm độ đúng của kiến thức.
- Câu hỏi quan sát: phản hồi có cho học sinh một bước đi tiếp vừa sức mà vẫn giữ phần suy nghĩ cần thiết cho học sinh không?

### `CAP-DIAG` — Chẩn đoán lỗi, hiểu lầm và thiếu nền tảng

Gia sư nhận ra nguyên nhân gốc, hiểu lầm cốt lõi hoặc kiến thức nền còn thiếu, thay vì chỉ sửa biểu hiện bên ngoài.

- Bao gồm: phân biệt nguyên nhân với triệu chứng và, khi cần, đặt câu hỏi để kiểm tra giả thuyết chẩn đoán.
- Không chỉ là: báo “sai”, thay đáp án hoặc lặp lại lời giải đúng.
- Câu hỏi quan sát: phản hồi có chỉ ra hoặc kiểm tra đúng nguyên nhân khiến học sinh mắc lỗi không?

### `CAP-CARE` — Giao tiếp hỗ trợ học tập, tôn trọng và phù hợp lứa tuổi

Gia sư thể hiện ngay trong phản hồi cách giao tiếp rõ, tôn trọng, vừa sức và khích lệ gắn với nỗ lực hoặc bước tiến có thể quan sát.

- Bao gồm: xưng hô phù hợp, không phán xét, lời khích lệ gắn với nỗ lực hoặc bước tiến cụ thể.
- Không thay thế: độ chính xác chuyên môn hoặc sự phù hợp của chiến lược dạy học; không suy diễn động lực hoặc kết quả học tập thực tế sau phản hồi.
- Câu hỏi quan sát: phản hồi có rõ, tôn trọng, vừa sức và khích lệ có căn cứ không?

Ví dụ quan sát được:

- tốt: “Em đã chọn đúng cấu trúc vòng lặp; giờ mình kiểm tra điều kiện dừng ở dòng 4 nhé”;
- trung bình: “Tốt lắm! Em xem lại nhé” — lịch sự nhưng lời khen chung chung;
- kém: “Bài đơn giản thế này mà em cũng sai” — hạ thấp học sinh.

## Hai ranh giới đã được UET duyệt tạm thời

### `CAP-STATE` và `CAP-DIAG`

Hãy thử tách hai câu hỏi:

1. Gia sư có hiểu đúng học sinh đang làm gì và đang kẹt ở đâu không? Đây là giả thuyết `CAP-STATE`.
2. Gia sư có nhận ra vì sao học sinh kẹt hoặc đang hiểu sai điều gì không? Đây là `CAP-DIAG`, chỉ áp dụng khi đầu vào có bằng chứng lỗi, hiểu lầm hoặc bế tắc.

UET đã quyết định tạm thời giữ riêng hai năng lực để khám phá task. HNMU sẽ kiểm tra lại sau Workstream D bằng các câu hỏi:

- Có trường hợp hiểu đúng tình trạng nhưng chưa thể chẩn đoán nguyên nhân không?
- Có thể đánh giá hai điều này nhất quán từ một phản hồi không?
- Hãy tạo bốn ô đối chứng: cả hai; chỉ `CAP-STATE`; chỉ `CAP-DIAG`; không có năng lực nào. Nếu hai nhận xét luôn đi cùng nhau, trước hết sửa ranh giới hoặc xin thêm ví dụ, chưa kết luận gộp.

### `CAP-STRAT` và `CAP-SCAFF`

Hãy thử tách hai câu hỏi:

1. Gia sư chọn **phương tiện/chức năng hỗ trợ nào**? Đây là `CAP-STRAT`.
2. Gia sư cho **bao nhiêu hỗ trợ, theo nhịp nào và có giữ phần việc cho học sinh không**? Đây là `CAP-SCAFF`. Van de Pol et al. phân biệt phương tiện hỗ trợ với tính thích ứng, rút dần và chuyển giao trách nhiệm (`MTF-S013`).

UET đã quyết định tạm thời giữ riêng hai năng lực để khám phá task. HNMU sẽ kiểm tra lại sau Workstream D bằng các câu hỏi:

- Một phản hồi có thể chọn đúng kiểu hỗ trợ nhưng cho quá nhiều hoặc quá ít không?
- Giáo viên có thể nhận xét hai mặt này độc lập và nhất quán không?
- Khung dàn giáo HNMU xem các chức năng hỗ trợ là bộ công cụ linh hoạt; cách tách “chọn phương tiện” và “điều tiết phương tiện” có phản ánh đúng thực hành đó không? Hãy tạo bốn ô đối chứng: cả hai; chỉ `CAP-STRAT`; chỉ `CAP-SCAFF`; không có năng lực nào.

## `CAP-CARE` và cổng lỗi nghiêm trọng

`CAP-CARE` đang được đề xuất để nhìn vào cách giao tiếp thường ngày: rõ ràng, tôn trọng, vừa sức và duy trì động lực. Cổng lỗi nghiêm trọng ở một vòng khác sẽ xem các trường hợp có thể làm phản hồi không còn chấp nhận được dù các mặt khác tốt, chẳng hạn chỉ dẫn có nguy cơ gây hại hoặc vi phạm nghiêm trọng.

Trong vòng này, xin chỉ xem **ranh giới**, chưa thiết kế hay duyệt cổng lỗi:

- Trường hợp nào là cách diễn đạt chưa tốt nhưng vẫn thuộc `CAP-CARE`?
- Trường hợp nào nghiêm trọng đến mức không nên để điểm giao tiếp bù trừ?
- Phát biểu nào về ranh giới này cần thêm căn cứ từ HNMU/UET trước khi dùng?

## Bốn câu hỏi cho từng năng lực

### Mức cần thiết

- Nếu bỏ năng lực này, mô hình có bỏ sót một phẩm chất quan trọng của gia sư Tin học THCS không?
- Năng lực có cần cho toàn bộ lớp 6–9 hay chỉ một số tình huống?

### Tính đầy đủ

- Định nghĩa đã bao quát đủ phần cần quan sát chưa, hay còn thiếu/quá rộng?
- Nhìn toàn bộ sáu năng lực, còn thiếu một năng lực quan trọng nào không?
- Có nội dung nào lặp lại đến mức một năng lực trở nên dư thừa không?

### Độ rõ nghĩa

- Hai giáo viên đọc độc lập có hiểu giống nhau không?
- Từ nào cần thay, thêm ví dụ hoặc thêm điều loại trừ?

### Khả năng quan sát trong một lượt phản hồi

- Có thể nhận xét dựa trên câu hỏi của học sinh, phần trao đổi trước đó và đúng một lượt phản hồi của gia sư không?
- Có đang suy diễn từ kết quả học tập tương lai, cảm xúc không được thể hiện hoặc nhiều lượt sau đó không?
- Nếu chưa quan sát được, cần sửa định nghĩa, thêm bằng chứng hay đưa năng lực này ra ngoài mô hình vòng đầu?

## Ví dụ minh họa đầy đủ

Đây là ví dụ giả định, không phải quyết định về sáu năng lực thật:

> “Năng lực giả định A là cần thiết cho Tin học THCS. Tuy nhiên, định nghĩa chưa nói rõ trường hợp học sinh chưa cung cấp đủ dữ kiện nên tính đầy đủ là chưa đạt; cụm ‘hỗ trợ phù hợp’ cũng chưa đủ rõ. Năng lực có thể quan sát trong một lượt nếu người rà soát được đọc phần trao đổi trước đó. Tôi đề xuất `revise` và đề nghị thêm một câu về giới hạn khi thiếu dữ kiện.”

Nhận xét này đạt yêu cầu vì trả lời đủ bốn câu hỏi, nêu căn cứ và giữ quyết định ở mức đề xuất.

## Phản ví dụ

> “Năng lực A chắc chắn đúng vì nghiên cứu đã nói vậy.”

Nhận xét này chưa đạt vì các nguồn hiện có chỉ gợi ý cách xây dựng và quan sát năng lực; chúng không thay quyết định chuyên môn của HNMU/UET và không tự xác nhận ranh giới. Nhận xét cũng chưa kiểm sự phù hợp với Tin học THCS hoặc khả năng quan sát trong một lượt phản hồi.
