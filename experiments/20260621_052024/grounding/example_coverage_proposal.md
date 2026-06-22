# Example coverage proposal

## Trạng thái

`APPROVED_FOR_EXAMPLE_AUTHORING`

## Quyết định của project lead — 2026-06-21

- Type 1 — `EXPLAIN_CONCEPT`: 2 mẫu.
- Type 2 — `EVALUATE_DIGITAL_SITUATION`: 3 mẫu.
- Type 3 — `FEEDBACK_ON_REASONING`: 2 mẫu.
- Type 4 — `PLAN_DIGITAL_PRODUCT`: 2 mẫu.
- Type 5 — `REVIEW_DIGITAL_PRODUCT`: 2 mẫu.
- Type 6 — `CONSTRUCT_ALGORITHM`: 3 mẫu.
- Type 7 — `DIAGNOSE_ALGORITHM`: 2 mẫu.
- Type 8 — `EXPLORE_CAREER_FIT`: 2 mẫu.
- Tổng: 18 mẫu lõi.
- Type 9: không đưa vào gói hiện tại.
- Bảng tính nâng cao và làm video: không đưa vào gói hiện tại.
- Môi trường lập trình/phần mềm chưa được xác nhận: mẫu phải độc lập công cụ hoặc ghi rõ `provisional/open_question`.

Phân loại này phục vụ lựa chọn số lượng mẫu minh họa. Nó không phải taxonomy benchmark của P05. Curriculum coverage đã có căn cứ; tutoring behaviors vẫn là `provisional` cho tới khi P02 và expert teachers review.

## Quy tắc gán loại

Mỗi example chỉ gán một loại chính theo thứ tự:

1. Nếu thiếu kiến thức/kĩ năng THCS trước đó đang chặn task lớp 9 → Type 9.
2. Nếu mục tiêu chính là hướng nghiệp → Type 8.
3. Nếu đã có bài làm/sản phẩm của học sinh:
   - câu trả lời bằng lời hoặc quyết định → Type 3;
   - sản phẩm số hoặc kết quả mô phỏng → Type 5;
   - thuật toán, sơ đồ khối hoặc chương trình → Type 7.
4. Nếu chưa có bài làm:
   - cần giải thích khái niệm → Type 1;
   - cần đánh giá thông tin/hành vi số → Type 2;
   - cần lập kế hoạch sản phẩm số → Type 4;
   - cần xây dựng thuật toán → Type 6.

Quy tắc này tránh đếm trùng một sample chỉ vì nó đồng thời là scenario và open response.

## Type 1 — Giải thích khái niệm lớp 9

- `example_type_id`: `EXPLAIN_CONCEPT`
- Mục tiêu: giúp học sinh hiểu khái niệm hoặc quan hệ trước khi làm task.
- Curriculum: `CURR-G9-DL-001`, `CURR-G9-ICT-001`, `CURR-G9-CS-004`.
- Student state: chưa có bài làm; có thể có hiểu sai ban đầu.
- Tutoring behavior: giải thích, nối ví dụ quen thuộc, kiểm tra lại mức hiểu.
- Interaction: thường single-turn, có thể có follow-up ngắn.
- Response openness: thấp–trung bình.
- Teacher-judgment load: trung bình.
- Khác biệt: mục tiêu là hiểu khái niệm, không review quyết định/sản phẩm.
- Biến thể: một clarification thông thường và một misconception.
- Tối thiểu: 2.
- Tốt hơn: 3.
- Effort: khoảng 2–3 giờ/mẫu.

## Type 2 — Đánh giá thông tin hoặc hành vi số

- `example_type_id`: `EVALUATE_DIGITAL_SITUATION`
- Mục tiêu: giúp học sinh đưa ra và giải thích quyết định trong tình huống số.
- Curriculum: `CURR-G9-DL-002` đến `CURR-G9-DL-004`.
- Student state: có claim, nguồn tin, hành động hoặc quyết định dự kiến; chưa có câu trả lời phát triển đầy đủ.
- Tutoring behavior: yêu cầu bằng chứng, phân biệt tiêu chí, chỉ ra hệ quả, hướng dẫn quyết định an toàn/có căn cứ.
- Interaction: single-turn hoặc multi-turn ngắn.
- Response openness: trung bình.
- Teacher-judgment load: cao, nhất là ví dụ pháp lí và đạo đức.
- Khác biệt: đánh giá/phán đoán trong bối cảnh, không chỉ nhớ quy tắc.
- Biến thể bắt buộc: reasoning phù hợp và reasoning có vấn đề/không an toàn.
- Tối thiểu: 3.
- Tốt hơn: 4.
- Effort: khoảng 3–4 giờ/mẫu.

## Type 3 — Phản hồi câu giải thích hoặc quyết định của học sinh

- `example_type_id`: `FEEDBACK_ON_REASONING`
- Mục tiêu: minh họa phản hồi sau khi học sinh đã trả lời bằng lời.
- Curriculum: có thể dùng Topic A, C, D, E hoặc G.
- Student evidence: câu trả lời đầy đủ hoặc một phần.
- Tutoring behavior: xác nhận phần đúng, định vị điểm yếu quan trọng đầu tiên, yêu cầu sửa, không viết thay.
- Interaction: ưu tiên feedback–revision hai lượt.
- Response openness: trung bình–cao.
- Teacher-judgment load: cao.
- Khác biệt: phát triển reasoning đã tồn tại; Types 1–2 bắt đầu trước câu trả lời của học sinh.
- Biến thể bắt buộc: câu trả lời khá tốt và câu trả lời cần sửa.
- Tối thiểu: 2.
- Tốt hơn: 4.
- Effort: khoảng 3–4 giờ/mẫu.

## Type 4 — Lập kế hoạch hoạt động hoặc sản phẩm số

- `example_type_id`: `PLAN_DIGITAL_PRODUCT`
- Mục tiêu: giúp chọn công cụ, phương tiện và các bước trước khi tạo sản phẩm.
- Curriculum: `CURR-G9-ICT-001` đến `CURR-G9-ICT-004`.
- Student evidence: mục tiêu hoặc kế hoạch thô, chưa có sản phẩm hoàn chỉnh.
- Tutoring behavior: làm rõ mục đích/đối tượng, chọn công cụ/phương tiện, sắp xếp bước, kiểm tra tính khả thi.
- Interaction: multi-turn planning.
- Response openness: cao.
- Teacher-judgment load: cao vì điều kiện phần mềm/lớp học khác nhau.
- Khác biệt: quyết định trước khi tạo sản phẩm; Type 5 dựa trên sản phẩm/kết quả đã có.
- Biến thể: kế hoạch khả thi và kế hoạch chọn công cụ/phương tiện chưa phù hợp.
- Tối thiểu: 2, không tính chủ đề lựa chọn.
- Tốt hơn: 3, không tính chủ đề lựa chọn.
- Effort: khoảng 4–6 giờ/mẫu.

## Type 5 — Review và cải thiện sản phẩm số/kết quả mô phỏng

- `example_type_id`: `REVIEW_DIGITAL_PRODUCT`
- Mục tiêu: phản hồi dựa trên sản phẩm hoặc kết quả quan sát được.
- Curriculum: `CURR-G9-ICT-001` đến `CURR-G9-ICT-004`.
- Student evidence: sản phẩm, ảnh chụp, mô tả sản phẩm hoặc kết quả mô phỏng.
- Tutoring behavior: so sánh evidence với mục tiêu, chỉ ra điểm mạnh và ưu tiên sửa, mời học sinh cải thiện.
- Interaction: multi-turn review–revision.
- Response openness: cao.
- Teacher-judgment load: cao.
- Khác biệt: có evidence sản phẩm/kết quả, không chỉ kế hoạch.
- Biến thể bắt buộc: sản phẩm hiệu quả và sản phẩm có vấn đề.
- Tối thiểu: 2, không tính chủ đề lựa chọn.
- Tốt hơn: 4, không tính chủ đề lựa chọn.
- Effort: khoảng 5–7 giờ/mẫu.

## Type 6 — Xây dựng giải pháp thuật toán

- `example_type_id`: `CONSTRUCT_ALGORITHM`
- Mục tiêu: hỗ trợ chuyển từ bài toán sang thuật toán có thứ tự.
- Curriculum: `CURR-G9-CS-001` đến `CURR-G9-CS-003`.
- Student state: hiểu nhiệm vụ nhưng chưa có thuật toán hoàn chỉnh; có thể có ý tưởng một phần.
- Tutoring behavior: làm rõ input/output, phân rã, đưa hint nhỏ nhất hữu ích, yêu cầu hoàn thành bước tiếp.
- Interaction: multi-turn hinting.
- Response openness: trung bình.
- Teacher-judgment load: trung bình–cao.
- Khác biệt: xây giải pháp mới, không chẩn đoán bài đã hoàn thành.
- Biến thể: hướng đi ban đầu tốt và hướng đi bị kẹt/sai cấu trúc.
- Tối thiểu: 3.
- Tốt hơn: 4.
- Effort: khoảng 4–6 giờ/mẫu.

## Type 7 — Chẩn đoán và sửa thuật toán/chương trình

- `example_type_id`: `DIAGNOSE_ALGORITHM`
- Mục tiêu: tìm lỗi mà không đưa ngay toàn bộ lời sửa.
- Curriculum: `CURR-G9-CS-001` đến `CURR-G9-CS-004`.
- Student evidence: thuật toán, sơ đồ khối hoặc chương trình có lỗi/thiếu/sai kết quả.
- Tutoring behavior: tìm lỗi quan trọng đầu tiên, yêu cầu trace/test, đưa hint tập trung, kiểm tra revision.
- Interaction: multi-turn diagnose–test–revise.
- Response openness: trung bình.
- Teacher-judgment load: cao vì phụ thuộc môi trường/ngôn ngữ tại trường.
- Khác biệt: có computational work để chẩn đoán; Type 6 bắt đầu trước giải pháp hoàn chỉnh.
- Biến thể: học sinh định vị đúng lỗi và học sinh chẩn đoán nhầm.
- Tối thiểu: 2.
- Tốt hơn: 4.
- Effort: khoảng 5–7 giờ/mẫu.
- Boundary: testing terminology, data types, optimization và advanced debugging là cumulative/provisional nếu chưa được giáo viên xác nhận.

## Type 8 — Khám phá nghề nghiệp không định kiến

- `example_type_id`: `EXPLORE_CAREER_FIT`
- Mục tiêu: hỗ trợ tìm hiểu và phản tư về nghề Tin học.
- Curriculum: `CURR-G9-MIX-001`.
- Student evidence: sở thích, giả định, thông tin đã tìm hiểu hoặc lựa chọn ban đầu.
- Tutoring behavior: hỏi lí do/bằng chứng, phân biệt nhóm nghề, sửa định kiến, giữ quyền lựa chọn của học sinh.
- Interaction: multi-turn reflection.
- Response openness: cao.
- Teacher-judgment load: cao.
- Khác biệt: sở thích cá nhân là evidence hợp lệ; không có một nghề “đúng” duy nhất.
- Biến thể: phản tư có căn cứ và nhận định định kiến/thiếu căn cứ.
- Tối thiểu: 2.
- Tốt hơn: 3.
- Effort: khoảng 3–5 giờ/mẫu.

## Type 9 — Bù đắp prerequisite THCS

- `example_type_id`: `REPAIR_PREREQUISITE`
- Trạng thái: module có điều kiện, không nằm trong core nếu project lead chưa cho phép.
- Mục tiêu: quay lại một kĩ năng lớp trước đang chặn task lớp 9 rồi trở lại requirement lớp 9.
- Student evidence: thất bại ở task lớp 9 được truy nguyên tới prerequisite cụ thể.
- Tutoring behavior: chẩn đoán prerequisite, refresher ngắn, quay lại task lớp 9.
- Interaction: multi-turn.
- Response openness: thấp–trung bình.
- Teacher-judgment load: rất cao.
- Khác biệt: tutoring target tức thời thuộc lớp trước, nhưng mục tiêu cuối vẫn là lớp 9.
- Biến thể: chỉ cần cue nhẹ và cần reteaching rõ hơn.
- Tối thiểu nếu được phép: 2.
- Tốt hơn: 3.
- Effort: khoảng 4–6 giờ/mẫu.
- Boundary: mỗi case phải có cả Grade-9 target và earlier requirement; không gọi nội dung nâng cao/chưa học là prerequisite.

## Chủ đề lựa chọn

Bảng tính nâng cao và làm video không nằm trong core cho tới khi project lead xác nhận được dạy tại bối cảnh mục tiêu.

Với mỗi chủ đề được chọn:

- Tối thiểu: thêm 2 mẫu — một Type 4 và một Type 5.
- Tốt hơn: thêm 3 mẫu — một Type 4 và hai Type 5 đối lập.
- Nếu chọn cả hai: giữ hai nhóm riêng; mẫu bảng tính không đại diện cho video.

## Tổng số đề xuất

| Phạm vi | Tối thiểu | Tốt hơn |
|---|---:|---:|
| Tám type lõi | 18 | 29 |
| Module prerequisite nếu cho phép | +2 | +3 |
| Mỗi chủ đề lựa chọn được xác nhận | +2 | +3 |
| Core + prerequisite + một chủ đề lựa chọn | 22 | 35 |
| Core + prerequisite + cả hai chủ đề lựa chọn | 24 | 38 |

Ước tính effort:

- 18 mẫu core: khoảng 65–95 giờ chuẩn bị;
- 29 mẫu core: khoảng 105–155 giờ chuẩn bị;
- chưa tính independent expert-teacher review.

## Coverage check

| Phần chương trình lớp 9 | Example types |
|---|---|
| Topic A — máy tính và cộng đồng | 1, 3 |
| Topic C/D — chất lượng thông tin, đạo đức/pháp luật số | 2, 3 |
| Topic E core — mô phỏng, trình bày/hợp tác | 1, 4, 5 |
| Topic E lựa chọn — bảng tính/video | 4, 5 sau xác nhận |
| Topic F — giải quyết vấn đề/thuật toán | 1, 6, 7 |
| Topic G — hướng nghiệp | 3, 8 |
| Prerequisite lớp trước | 9 nếu được cho phép |

## Decision gate

Không tạo `reference_grounded_examples.md` trước khi project lead quyết định:

1. số lượng cho từng Type 1–8;
2. có dùng Type 9 hay không và bao nhiêu mẫu;
3. chủ đề lựa chọn nào được dạy;
4. có bắt buộc cả positive/problematic variant trong mỗi type hay không;
5. môi trường/ngôn ngữ cho Types 6–7;
6. công cụ số có sẵn;
7. sản phẩm số dùng artifact/screenshot hay mô tả chữ;
8. số lượng sample multi-turn;
9. giới hạn effort và năng lực teacher review.
